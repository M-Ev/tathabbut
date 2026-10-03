#!/usr/bin/env python3
"""Large synthetic, offline evaluation of the Quran side of Tathabbut.

Builds a reproducible set of short Arabic texts that quote, misquote, or falsely attribute to Allah,
using only the bundled Mushaf text (data/quran.json, 6,236 ayat). Each text goes through
app.pipeline.check_text with hadith lookup and the language model off (TATHABBUT_DORAR=0,
TATHABBUT_LLM=none are forced below). Writes eval/synth_results.jsonl (one line per case) and
eval/synth_report.md.

    python3 eval/synth_quran.py                 # --n 600 --seed 2026
    python3 eval/synth_quran.py --n 2000 --seed 7
    python3 eval/synth_quran.py --selftest      # only check the spelling converter

Same --n and --seed give the same cases (per-kind random.Random seeded with "<seed>-<kind>").

How each label is kept certain
------------------------------
Passage sampling (kinds 1-4): pick an ayah uniformly at random, then a span of 1, 2 or 3 consecutive
ayat of the same surah (weights 70/20/10). The passage is used only if its consonantal skeleton
(app.normalize.skeleton_ar of the Mushaf text) occurs exactly once in the whole Mushaf, so exactly one
place is right. Repeated ayat (e.g. 55:13) are therefore not in kinds 1-4.

1. exact: 4-60 Mushaf words, copied as is. Expected: verified, ref = the passage. 40% carry a correct
   written reference (expected reference_ok true).
2. wrong_ref: like exact, always with a reference that does not point inside the passage: a nearby
   ayah of the same surah (40%), the same ayah number in another surah (30%), a random ayah of another
   surah (20%), or an ayah number past the end of a surah (10%). The passage occurs once, so no other
   place can make the reference right. Expected: verified, right ref, reference_ok false.
3. substitution: passage of 6-40 words; one internal word (never the first or last: changing an edge
   word leaves a contiguous exact fragment, which is a legitimate partial quote) replaced by a word
   taken from a different ayah with a different skeleton (>= 2 letters). Expected: differs, ref = the
   passage.
4. omission / insertion: same passage rules; an internal word of >= 2 skeleton letters dropped, or a
   word from a different ayah inserted at an internal position. Expected: differs.
   For 3 and 4 the edit is redrawn unless (a) the misquote's skeleton occurs nowhere in the Mushaf (it
   did not turn into other real Quran text) and (b) no window of Mushaf words outside the passage is
   within word-level edit distance 2 of the misquote, so the passage is unambiguously the nearest.
   Random donor words stand in for real slips (synonyms, misremembered words); they are not semantic.
5. negative: sentences written for this evaluation (made-up pious sentences, sentences written to sound
   Quranic, and Arabic proverbs/poetry). No hadith text and nothing circulated as a hadith, so the only
   question is "is this in the Mushaf". A sentence is used only if (a) its longest skeleton substring
   shared with the Mushaf is < 16 letters, and (b) every window of Mushaf words is more than half its
   length away in word edit distance, so it is neither a quote nor a near-misquote. Rejected sentences
   are listed in the report. Attributed to Allah with a Quran marker. Expected: not_in_mushaf.
6. short: whole ayat of <= 3 words, always inside ﴿﴾. Excluded: disconnected-letter openings (الم، طه،
   يس...), ayat whose text repeats as another ayah, and ayat whose skeleton occurs more than 3 times in
   the Mushaf (e.g. ﴿الرحمن﴾, 58 times). Occurrences are recorded; if > 1, any of those places is
   accepted as the ref unless a written reference is given. Expected: verified.

Spelling (kinds 1-4 and 6): Uthmani as in the Mushaf data (30%, copy from a Mushaf app), Uthmani with
all marks stripped (10%), common (imla'i) spelling with harakat (10%) and without (50%; a third of
those also typed casually: hamza dropped from alef, final ى/ي and ة/ه mixed). Common spelling comes
from to_common() below, a rule-based converter checked by SELFTEST. It changes letters only where
standard modern spelling differs from the Uthmani rasm (hamza seats ئ/ؤ, ىٰ inside a word -> ا, small
yaa/waw that are real letters, one-lam الليل/اللذان/اللاتي/اللائي, ننجي, يبسط/بسطة, words ending in ؤا,
رأى, silent letters); where it is unsure it keeps the Uthmani letters, which can only make the tool's
job easier. Where hamza + waw has two accepted spellings (رؤوف/رءوف) it uses ؤ; such words are tagged
"hamza_waw" so they can be separated in the report. Every word whose skeleton differs from the
Mushaf's is recorded in the case ("gaps", with the rule that changed it).

Markers: ﴿﴾, «»/""/{} after a marker, a marker and colon with the quote running to the end of the
sentence, and unmarked prose (exact quotes of >= 6 words only; surrounding words are checked not to
extend the Quran text). Markers include قال تعالى، قال الله تعالى، يقول الله عز وجل، وقال سبحانه، and
"قال الله تعالى في سورة X:". References: (البقرة: 255), (2:255), [البقرة: 255], (سورة البقرة: 255),
(سورة البقرة، الآية 255), Arabic-Indic digits, (البقرة 255).

Metrics: see the report. A case is "extracted" when a returned quran citation overlaps the embedded
quote (skeleton partial ratio >= 50). Latency is wall time of check_text per case after the Mushaf index
is loaded (load time reported separately).
"""
from __future__ import annotations

import argparse
import asyncio
import bisect
import json
import math
import os
import random
import re
import statistics
import sys
import time
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

# Hadith lookup and the language model are network services; this evaluation is offline by design.
os.environ["TATHABBUT_DORAR"] = "0"
os.environ["TATHABBUT_LLM"] = "none"

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from rapidfuzz import fuzz  # noqa: E402
from rapidfuzz.distance import Levenshtein  # noqa: E402

from app.config import settings  # noqa: E402
from app.normalize import skeleton_ar  # noqa: E402

# ---------------------------------------------------------------- Mushaf data

DATA = json.loads((ROOT / "data" / "quran.json").read_text(encoding="utf-8"))
SURAH_NAME = {s["n"]: s["ar"] for s in DATA["surahs"]}
# How people usually write a few names (the bundled names omit some hamzas).
DISPLAY_NAME = {**SURAH_NAME, 14: "إبراهيم", 34: "سبأ", 76: "الإنسان", 78: "النبأ", 82: "الانفطار", 84: "الانشقاق"}
AYAT = [(v[0], v[1], v[2]) for v in DATA["verses"]]  # (surah, ayah, Uthmani text)
N_AYAT = Counter(s for s, _, _ in AYAT)

_ORNAMENTS = re.compile("[۞۩]")  # ۞ rub el hizb, ۩ sajdah: not part of the words


def mushaf_tokens(text: str) -> list[str]:
    return [t for t in (_ORNAMENTS.sub("", w) for w in text.split()) if t]


TOK, TOK_SK, TOK_AYAH, AYAH_TOK = [], [], [], []
for _i, (_, _, _t) in enumerate(AYAT):
    _start = len(TOK)
    for _w in mushaf_tokens(_t):
        TOK.append(_w)
        TOK_SK.append(skeleton_ar(_w))
        TOK_AYAH.append(_i)
    AYAH_TOK.append((_start, len(TOK)))
_VOCAB: dict[str, int] = {}
TOK_ID = [_VOCAB.setdefault(sk, len(_VOCAB)) for sk in TOK_SK]
AYAH_SK = [skeleton_ar(t) for _, _, t in AYAT]
AYAH_OFF, _pos = [], 0
for _sk in AYAH_SK:
    AYAH_OFF.append(_pos)
    _pos += len(_sk)
FULL = "".join(AYAH_SK)
AYAH_SK_COUNT = Counter(AYAH_SK)


def find_all(sk: str) -> list[int]:
    out, p = [], FULL.find(sk)
    while p >= 0:
        out.append(p)
        p = FULL.find(sk, p + 1)
    return out


def ayah_at(offset: int) -> int:
    return bisect.bisect_right(AYAH_OFF, offset) - 1


def ref_of(i: int, j: int) -> str:
    s, a, _ = AYAT[i]
    if AYAT[j][0] != s:  # the tool keeps a result inside one surah
        j = i
    b = AYAT[j][1]
    return f"{s}:{a}" if a == b else f"{s}:{a}-{b}"


def occurrence_refs(sk: str) -> list[str]:
    return [ref_of(ayah_at(p), ayah_at(p + len(sk) - 1)) for p in find_all(sk)]


def near_windows(q_ids: list[int], max_d: int) -> list[tuple[int, int, int]]:
    """Windows of Mushaf words within word-level edit distance max_d of q_ids: (start, end, distance).
    A window at distance d shares >= len(q)-d words with q, which prunes almost every start."""
    n_q, n = len(q_ids), len(TOK_ID)
    qset = set(q_ids)
    cs = [0] * (n + 1)
    acc = 0
    for p, t in enumerate(TOK_ID):
        if t in qset:
            acc += 1
        cs[p + 1] = acc
    need, reach = n_q - max_d, n_q + max_d
    out = []
    for s in range(n):
        if cs[min(n, s + reach)] - cs[s] < need:
            continue
        best = None
        for m in range(max(1, n_q - max_d), reach + 1):
            if s + m > n:
                break
            d = Levenshtein.distance(q_ids, TOK_ID[s : s + m], score_cutoff=max_d)
            if d <= max_d and (best is None or d < best[2]):
                best = (s, s + m, d)
        if best:
            out.append(best)
    return out


def longest_shared_skeleton(sk: str) -> int:
    best = 0
    for i in range(len(sk)):
        j = i + best + 1
        while j <= len(sk) and sk[i:j] in FULL:
            best = j - i
            j += 1
    return best


# ---------------------------------------------------------------- spelling: Uthmani -> common (imla'i)
# The converter lives in app/spelling.py since 4 Oct (the app's second Mushaf index uses it). Same rules.
from app.spelling import (  # noqa: E402
    _ALL_MARKS, _DROP_EARLY, CHANGING_RULES, DAGGER, HAMZA_ABOVE, HAMZA_BELOW, MADDA, NO_ALEF, TATWEEL, _parse,
    strip_marks, to_common_word,
)

ALEFISH_BASE = set("اأإآٱءى")


def casual(word: str, rng: random.Random) -> str:
    if word[:1] in "أإآ" and rng.random() < 0.6:
        word = "ا" + word[1:]
    if word.endswith("ى") and rng.random() < 0.3:
        word = word[:-1] + "ي"
    if word.endswith("ة") and rng.random() < 0.2:
        word = word[:-1] + "ه"
    return word


SELFTEST = {
    "ٱلسَّيِّـَٔاتِ": "السيئات", "شَيۡـٔٗا": "شيئا", "يَـُٔودُهُۥ": "يؤوده", "رَءُوفٞ": "رؤوف", "إِسۡرَـٰٓءِيلَ": "إسرائيل",
    "وَٱلَّيۡلِ": "والليل", "إِبۡرَٰهِـۧمَ": "إبراهيم", "ٱلصَّلَوٰةَ": "الصلاة", "يَـٰٓأَيُّهَا": "يا أيها",
    "ٱلۡمَلَؤُاْ": "الملأ", "بِـَٔايَٰتِنَا": "بآياتنا", "تِلۡقَآيِٕ": "تلقاء", "أَفَإِيْن": "أفإن",
    "يُحۡيِۦ": "يحيي", "دَاوُۥدَ": "داود", "يَلۡوُۥنَ": "يلوون", "وَيَبۡصُۜطُ": "ويبسط", "نُـۨجِي": "ننجي",
    "ٱلرَّحۡمَٰنِ": "الرحمن", "ٱلسَّمَٰوَٰتِ": "السماوات", "مَٰلِكِ": "مالك", "ٱلۡقُرۡءَانُ": "القرآن", "ءَامَنُواْ": "آمنوا",
    "مُتَّكِـِٔينَ": "متكئين", "مَسۡـُٔولٗا": "مسؤولا", "يَسۡتَهۡزِءُونَ": "يستهزئون", "جَآءَهُم": "جاءهم",
    "يَتَسَآءَلُونَ": "يتساءلون", "أَءِذَا": "أإذا", "ٱلَّذَيۡنِ": "اللذين", "ٱلَّـٰتِي": "اللاتي", "ٱلَّـٰٓـِٔي": "اللائي",
    "شُرَكَآءِيَ": "شركائي", "وَٱلۡأَفۡـِٔدَةَ": "والأفئدة", "كَهَيۡـَٔةِ": "كهيئة", "هَنِيٓـَٔۢا": "هنيئا", "ٱلۡمَشۡـَٔمَةِ": "المشأمة",
    "يَسۡـَٔلُونَكَ": "يسألونك", "يَسۡتَـٔۡخِرُونَ": "يستأخرون", "يَـٰٓـَٔادَمُ": "يا آدم", "ٱلۡـَٰٔنَ": "الآن",
    "أَسَـٰٓـُٔواْ": "أساءوا", "رُءُوسِهِمۡ": "رؤوسهم", "مَـَٔابٖ": "مآب", "ٱمۡرِيٕٖ": "امرئ", "خَٰسِـِٔينَ": "خاسئين",
    "ٱللُّؤۡلُوِٕ": "اللؤلؤ", "سَأُوْرِيكُمۡ": "سأريكم", "بِأَيۡيْدٖ": "بأيد", "وَمَلَإِيْهِۦ": "وملئه", "نَّبَإِيْ": "نبإ",
    "ءَاتَىٰنِۦَ": "آتاني", "يَسۡتَحۡيِۦٓ": "يستحيي", "إِۦلَٰفِهِمۡ": "إيلافهم", "أُوْلَـٰٓئِكَ": "أولئك",
    "ٱلنَّبِيِّـۧنَ": "النبيين", "جَزَـٰٓؤُاْ": "جزاء", "أَدۡرَىٰكَ": "أدراك", "ٱلتَّوۡرَىٰةَ": "التوراة",
    "إِحۡدَىٰهُمَا": "إحداهما", "وَمَأۡوَىٰهُمۡ": "ومأواهم", "شَيۡءٖ": "شيء", "مِاْئَةَ": "مائة",
    "وَٱلصَّـٰبِـِٔينَ": "والصابئين", "لِيَسُـُٔواْ": "ليسوءوا", "وَٱلَّذِينَ": "والذين", "ذَٰلِكَ": "ذلك",
    "هَٰذَا": "هذا", "إِلَٰهَ": "إله", "بِهِۦ": "به", "عَلَىٰ": "على", "سُوٓءٗا": "سوءا", "وَرَآيِٕ": "وراء", "ٱمۡرُؤٌاْ": "امرؤ", "ٱلسَّيِّيِٕۚ": "السيئ", "ٱلۡأَقۡصَا": "الأقصى",
}


def selftest(verbose: bool = True) -> list[str]:
    # Literals in this file may be stored with a different order of combining marks than the Mushaf
    # data; look each one up by canonical equivalence and test the real Mushaf token.
    tokens = {unicodedata.normalize("NFC", t): t for t in TOK}
    errors = []
    for uth, want in SELFTEST.items():
        real = tokens.get(unicodedata.normalize("NFC", uth))
        if real is None:
            errors.append(f"not a Mushaf token: {uth}")
            continue
        got, _ = to_common_word(real, harakat=False)
        if got != want:
            errors.append(f"{uth}: got {got}, want {want}")
    if verbose:
        print(f"spelling converter self-test: {len(SELFTEST) - len(errors)}/{len(SELFTEST)} ok")
        for e in errors:
            print("  ", e)
    return errors


# ---------------------------------------------------------------- rendering a quote

STYLES = [("uthmani", 30), ("uthmani_plain", 10), ("common_harakat", 10), ("common", 50)]


def pick(rng: random.Random, weighted):
    items, weights = zip(*weighted)
    return rng.choices(items, weights=weights)[0]


def render(tokens: list[str], style: str, rng: random.Random) -> tuple[str, list[dict], bool]:
    """Uthmani words -> quote text in a spelling style, and the words whose skeleton is not the Mushaf's."""
    typed_casually = style == "common" and rng.random() < 1 / 3
    words, gaps = [], []
    for t in tokens:
        rules: set = set()
        if style == "uthmani":
            w = t
        elif style == "uthmani_plain":
            w = strip_marks(t)
            if re.search("و" + DAGGER, t):
                rules.add("stripped_waw_alef")
        else:
            w, rules = to_common_word(t, harakat=(style == "common_harakat"))
            if typed_casually:
                w = " ".join(casual(x, rng) for x in w.split())
        if skeleton_ar(w) != skeleton_ar(t):
            gaps.append({"mushaf": t, "quoted": w, "rules": sorted(rules & (CHANGING_RULES | {"stripped_waw_alef"})) or ["?"]})
        words.append(w)
    return " ".join(words), gaps, typed_casually


# ---------------------------------------------------------------- composing a text

AR_DIGITS = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")
REF_FORMATS = [("name", 30), ("num", 20), ("surah_name", 15), ("surah_aya", 10), ("ar_digits", 10), ("square", 10), ("name_space", 5)]


def fmt_ref(rng: random.Random, s: int, a: int, b: int | None = None, fmt: str | None = None) -> tuple[str, str]:
    fmt = fmt or pick(rng, REF_FORMATS)
    name = DISPLAY_NAME.get(s, str(s))
    ay = f"{a}" if b is None or b == a or rng.random() < 0.5 else f"{a}-{b}"
    r = {
        "name": f"({name}: {ay})", "num": f"({s}:{ay})", "surah_name": f"(سورة {name}: {ay})",
        "surah_aya": f"(سورة {name}، الآية {ay})", "ar_digits": f"({name}: {ay.translate(AR_DIGITS)})",
        "square": f"[{name}: {ay}]", "name_space": f"({name} {ay})",
    }[fmt]
    return r, fmt


INTROS = {
    "marker": ["قال تعالى: ", "قال الله تعالى: ", "يقول الله عز وجل: ", "وقال سبحانه: ", "وقال جل وعلا: "],
    "marker_soft": ["ومن الآيات التي أحبها كثيرًا قوله تعالى: ", "تأملت اليوم قوله سبحانه وتعالى ", "وما أجمل قوله تعالى: "],
    "marker_in_surah": ["قال الله تعالى في سورة {surah}: ", "يقول الله تعالى في سورة {surah}: "],
    "none": [""],
}
PRE = ["", "", "", "في زحمة الحياة ننسى أمورًا كثيرة. ", "كان موضوع درسنا اليوم عن الصبر. ", "سألني ابني عن معنى التوكل. ",
       "كتبت هذه الكلمات لأختي قبل سفرها. "]
QUOTED_OUTROS = ["", ".", "، وهذا أصل عظيم في هذا الباب.", " فلنتدبر هذا المعنى جيدًا.", " صدق الله العظيم.",
                 "، فما أحوجنا إلى هذا المعنى اليوم!"]
COLON_OUTROS = [".", ". وهذه دعوة صريحة للتأمل.", ".\nنسأل الله أن يجعلنا من أهلها.", "\nفلنتأمل هذا المعنى."]
UNMARKED = [
    ("", "{q}{ref}، فلنحرص على هذا المعنى في حياتنا اليومية."),
    ("أحب أن أذكركم اليوم بهذا المعنى العظيم: ", "{q}{ref}. أسأل الله لنا ولكم التوفيق."),
    ("كتب لي صديقي في رسالة الصباح ", "{q}{ref}، فشعرت بطمأنينة كبيرة."),
    ("تذكرت وأنا في طريقي إلى العمل ", "{q}{ref}، فهدأت نفسي."),
    ("", "{q}{ref}. هذه من أحب الآيات إلى قلبي."),
]
OPEN_CLOSE = {"brackets": ("﴿", "﴾"), "guillemets": ("«", "»"), "dquotes": ('"', '"'), "braces": ("{", "}")}
_AR_WORD = re.compile("[ء-يٱؐ-ًؚ-ٰٟۖ-ۭ]+")


def _intro(rng, marker: str, allow_in_surah: bool, has_ref: bool, surah: int | None) -> tuple[str, str]:
    if marker == "brackets":
        choices = [("marker", 50), ("marker_soft", 20), ("none", 15)] + ([("marker_in_surah", 15)] if allow_in_surah else [])
    else:
        choices = [("marker", 75), ("marker_soft", 13)] + ([("marker_in_surah", 12)] if allow_in_surah else [])
        if has_ref and marker in ("guillemets", "dquotes", "braces"):
            choices.append(("none", 15))  # «...» (البقرة: 255) is recognised by its reference
    kind = pick(rng, choices)
    return kind, rng.choice(INTROS[kind]).format(surah=DISPLAY_NAME.get(surah or 0, ""))


def _unmarked_safe(before: str, quote: str, after: str) -> bool:
    """The words around an unmarked quote must not continue the Quran text (the scanner would extend into them)."""
    pre = [skeleton_ar(w) for w in _AR_WORD.findall(before)]
    q = [skeleton_ar(w) for w in _AR_WORD.findall(quote)]
    post = [skeleton_ar(w) for w in _AR_WORD.findall(after)]
    for k in range(1, min(4, len(pre)) + 1):
        if "".join(pre[-k:] + q[: 5 - k]) in FULL:
            return False
    return not (post and "".join(q + post[:1]) in FULL)


def compose(rng, marker: str, quote: str, ref: str, surah: int | None, allow_in_surah: bool = True) -> tuple[str, str]:
    pre = rng.choice(PRE)
    if marker == "unmarked":
        order = list(range(len(UNMARKED)))
        rng.shuffle(order)
        for k in order:
            head, tail = UNMARKED[k]
            body = tail.format(q=quote, ref=f" {ref}" if ref else "")
            if _unmarked_safe(pre + head, quote, body[len(quote):]):
                return pre + head + body, "none"
        marker = "brackets"
    intro_kind, intro = _intro(rng, marker, allow_in_surah, bool(ref), surah)
    ref_part = f" {ref}" if ref else ""
    if marker == "colon":
        return pre + intro + quote + ref_part + rng.choice(COLON_OUTROS), intro_kind
    o, c = OPEN_CLOSE[marker]
    return pre + intro + o + quote + c + ref_part + rng.choice(QUOTED_OUTROS), intro_kind


# ---------------------------------------------------------------- generators

MARKERS_EXACT = [("brackets", 35), ("guillemets", 20), ("colon", 20), ("dquotes", 5), ("braces", 5), ("unmarked", 15)]
MARKERS_MISQUOTE = [("brackets", 45), ("guillemets", 25), ("colon", 20), ("dquotes", 5), ("braces", 5)]
MARKERS_NEGATIVE = [("brackets", 20), ("guillemets", 40), ("colon", 30), ("dquotes", 10)]
SKIPS: Counter = Counter()


def sample_passage(rng, min_w: int, max_w: int) -> tuple[int, int]:
    while True:
        i = rng.randrange(len(AYAT))
        k = rng.choices([1, 2, 3], weights=[70, 20, 10])[0]
        j = i + k - 1
        if j >= len(AYAT) or AYAT[j][0] != AYAT[i][0]:
            SKIPS["passage_crosses_surah"] += 1
            continue
        t0, t1 = AYAH_TOK[i][0], AYAH_TOK[j][1]
        if not min_w <= t1 - t0 <= max_w:
            SKIPS["passage_length"] += 1
            continue
        if len(find_all("".join(TOK_SK[t0:t1]))) != 1:
            SKIPS["passage_not_unique"] += 1
            continue
        return i, j


def _base_case(cid, kind, i, j, style, rng):
    t0, t1 = AYAH_TOK[i][0], AYAH_TOK[j][1]
    return {"id": cid, "kind": kind, "variant": "span" if j > i else "single", "style": style,
            "mushaf_ref": ref_of(i, j), "mushaf_words": t1 - t0}


def gen_exact(rng, cid: str, wrong_ref: bool = False) -> dict:
    i, j = sample_passage(rng, 4, 60)
    t0, t1 = AYAH_TOK[i][0], AYAH_TOK[j][1]
    style = pick(rng, STYLES)
    quote, gaps, typed_casually = render(TOK[t0:t1], style, rng)
    case = _base_case(cid, "wrong_ref" if wrong_ref else "exact", i, j, style, rng)
    marker = pick(rng, MARKERS_EXACT)
    if marker == "unmarked" and t1 - t0 < 6:
        marker = "brackets"
    s, a, b = AYAT[i][0], AYAT[i][1], AYAT[j][1]
    ref, ref_fmt, ref_kind, ref_ok = "", "", "", None
    if wrong_ref:
        ref_kind = pick(rng, [("near", 40), ("other_surah_same_ayah", 30), ("random", 20), ("nonexistent", 10)])
        while True:
            if ref_kind == "near":
                ws, wa = s, a + rng.choice([-3, -2, -1, 1, 2, 3]) * 1 + (b - a if rng.random() < 0.5 else 0)
                if not (1 <= wa <= N_AYAT[s]) or a <= wa <= b:
                    ref_kind = rng.choice(["other_surah_same_ayah", "random"]) if N_AYAT[s] < 3 else ref_kind
                    continue
            elif ref_kind == "other_surah_same_ayah":
                ws, wa = rng.randrange(1, 115), a
                if ws == s or N_AYAT[ws] < wa:
                    continue
            elif ref_kind == "random":
                ws = rng.randrange(1, 115)
                wa = rng.randrange(1, N_AYAT[ws] + 1)
                if ws == s:
                    continue
            else:
                ws = s if rng.random() < 0.5 else rng.randrange(1, 115)
                wa = N_AYAT[ws] + rng.randrange(1, 20)
            break
        ref, ref_fmt = fmt_ref(rng, ws, wa)
        ref_ok = False
        case["ref_target"] = f"{ws}:{wa}"
    elif rng.random() < 0.4:
        ref, ref_fmt = fmt_ref(rng, s, a, b)
        ref_ok = True
        case["ref_target"] = case["mushaf_ref"]
    text, intro = compose(rng, marker, quote, ref, s, allow_in_surah=not wrong_ref)
    case.update({"marker": marker if marker != "unmarked" or intro == "none" else marker, "intro": intro,
                 "ref_written": ref, "ref_format": ref_fmt, "wrong_ref_kind": ref_kind, "text": text, "quote": quote,
                 "gaps": gaps, "typed_casually": typed_casually,
                 "expected": {"status": "verified", "ref": case["mushaf_ref"], "accept_refs": [case["mushaf_ref"]],
                              "reference_ok": ref_ok}})
    if marker == "unmarked" and "﴿" in text:
        case["marker"] = "brackets"  # no safe unmarked template for this passage
    return case


def gen_misquote(rng, cid: str, kind: str) -> dict:
    while True:
        i, j = sample_passage(rng, 6, 40)
        t0, t1 = AYAH_TOK[i][0], AYAH_TOK[j][1]
        toks, ids, sks = TOK[t0:t1], TOK_ID[t0:t1], TOK_SK[t0:t1]
        n = len(toks)
        donor = None
        if kind in ("substitution", "insertion"):
            k = rng.randrange(len(TOK))
            if i <= TOK_AYAH[k] <= j or len(TOK_SK[k]) < 2:
                SKIPS[f"{kind}_donor"] += 1
                continue
            donor = k
        if kind == "substitution":
            p = rng.randrange(1, n - 1)
            if TOK_SK[donor] == sks[p]:
                SKIPS[f"{kind}_same_word"] += 1
                continue
            new, new_ids = toks[:p] + [TOK[donor]] + toks[p + 1 :], ids[:p] + [TOK_ID[donor]] + ids[p + 1 :]
            edit = {"op": "substitute", "pos": p, "mushaf_word": toks[p], "quoted_word": TOK[donor]}
        elif kind == "alef":
            # Plan item 11: a full alef typed where the Mushaf word has none, not even a dagger alef
            # («قال» for ﴿قُلۡ﴾). The skeleton is unchanged, which is exactly what the old matcher missed.
            p = rng.randrange(1, n - 1)
            cl = _parse(toks[p])
            spots = [k for k in range(len(cl) - 1)
                     if cl[k][0] not in ALEFISH_BASE and cl[k + 1][0] not in ALEFISH_BASE
                     and not set(cl[k][1]) & {DAGGER, MADDA, HAMZA_ABOVE, HAMZA_BELOW}
                     and not set(cl[k + 1][1]) & {DAGGER, HAMZA_ABOVE, HAMZA_BELOW}
                     and cl[k][0] != TATWEEL and cl[k + 1][0] != TATWEEL]
            if len(sks[p]) < 2 or not spots:
                SKIPS[f"{kind}_no_spot"] += 1
                continue
            k = rng.choice(spots)
            word = "".join(b + m for b, m in cl[: k + 1]) + "ا" + "".join(b + m for b, m in cl[k + 1 :])
            new, new_ids = toks[:p] + [word] + toks[p + 1 :], ids
            edit = {"op": "alef", "pos": p, "mushaf_word": toks[p], "quoted_word": word}
        elif kind == "omission":
            p = rng.randrange(1, n - 1)
            if len(sks[p]) < 2:
                SKIPS[f"{kind}_short_word"] += 1
                continue
            new, new_ids = toks[:p] + toks[p + 1 :], ids[:p] + ids[p + 1 :]
            edit = {"op": "omit", "pos": p, "mushaf_word": toks[p]}
        else:
            p = rng.randrange(1, n)
            new, new_ids = toks[:p] + [TOK[donor]] + toks[p:], ids[:p] + [TOK_ID[donor]] + ids[p:]
            edit = {"op": "insert", "pos": p, "quoted_word": TOK[donor]}
        if donor is not None:
            edit["donor_ref"] = ref_of(TOK_AYAH[donor], TOK_AYAH[donor])
        if kind != "alef" and "".join(skeleton_ar(t) for t in new) in FULL:
            SKIPS[f"{kind}_still_quran"] += 1
            continue
        rivals = [] if kind == "alef" else [w for w in near_windows(new_ids, 2) if not (w[0] < t1 and t0 < w[1])]
        if rivals:
            SKIPS[f"{kind}_nearest_ambiguous"] += 1
            continue
        style = pick(rng, STYLES)
        quote, gaps, typed_casually = render(new, style, rng)
        if kind != "alef" and skeleton_ar(quote) in FULL:
            SKIPS[f"{kind}_still_quran"] += 1
            continue
        break
    case = _base_case(cid, kind, i, j, style, rng)
    marker = pick(rng, MARKERS_MISQUOTE)
    ref, ref_fmt, ref_ok = "", "", None
    if rng.random() < 0.2:
        ref, ref_fmt = fmt_ref(rng, AYAT[i][0], AYAT[i][1], AYAT[j][1])
        ref_ok = True
        case["ref_target"] = case["mushaf_ref"]
    text, intro = compose(rng, marker, quote, ref, AYAT[i][0])
    case.update({"marker": marker, "intro": intro, "ref_written": ref, "ref_format": ref_fmt, "text": text, "quote": quote,
                 "edit": edit, "gaps": gaps, "typed_casually": typed_casually,
                 "expected": {"status": "differs", "ref": case["mushaf_ref"], "accept_refs": [case["mushaf_ref"]],
                              "reference_ok": ref_ok}})
    return case


# Made up for this evaluation, or proverbs/poetry. Never hadith text, nothing circulated as a hadith.
NEGATIVES = [
    ("pious", "إن الله يحب العبد الذي يبتسم في وجه جيرانه كل صباح"),
    ("pious", "من حافظ على ورده اليومي فتح الله له أبواب التوفيق في عمله"),
    ("pious", "من رتب مكتبه قبل أن ينام يسر الله له أمره في الصباح"),
    ("pious", "إن الله ينظر إلى من يقرأ كتابا نافعا قبل نومه فيرضى عنه"),
    ("pious", "من شارك هذه الرسالة مع عشرة من أصدقائه رزقه الله خيرا كثيرا"),
    ("pious", "يا عبادي لا تتركوا الدعاء في أوقات الزحام والتعب"),
    ("pious", "من صبر على زحمة الطريق كتب الله له أجر الصابرين"),
    ("pious", "إني أحب من عبادي من يحسن إلى والديه بالكلمة الطيبة كل يوم"),
    ("pious", "من قرأ هذا الدعاء ثلاث مرات في الصباح حفظه الله من كل هم"),
    ("pious", "إن الرزق يأتي لمن يسعى إليه بقلب راض ونية صادقة"),
    ("pious", "وما ضاقت نفس عبد إلا وسعها ذكر ربه"),
    ("pious", "لن يضيع تعب من سهر على تعليم أبنائه"),
    ("pious", "إن السعادة الحقيقية في رضا القلب بما قسمه الله"),
    ("pious", "من ابتسم في وجه الحزين جبر الله خاطره"),
    ("pious", "اجعلوا لأنفسكم ساعة كل يوم تخلون فيها بالقراءة والتفكر"),
    ("pious", "من حافظ على نظافة حيه طهر الله قلبه من الهم"),
    ("pious", "يا ابن آدم إن الوقت أغلى ما تملك فلا تضيعه في اللهو"),
    ("pious", "إن الله يكافئ الطالب المجتهد بنجاح يفرح به أهله"),
    ("pious", "من أحسن إلى عامل النظافة أحسن الله إليه في رزقه"),
    ("pious", "إن الله لا ينسى من يساعد الغريب في المدينة"),
    ("pious", "من بدأ يومه بالشكر أنهاه بالرضا"),
    ("pious", "قلوب الصادقين مطمئنة وإن كثرت حولهم الأحزان"),
    ("pious", "من كظم غيظه في العمل رفع الله قدره بين زملائه"),
    ("pious", "لا تحزن إذا تأخرت أمنيتك فإن الله يدخر لك الأفضل"),
    ("pious", "إن الله يحب المتقنين لأعمالهم في كل زمان"),
    ("pious", "وعد الله المحسنين في أعمالهم بالطمأنينة والسكينة"),
    ("pious", "من نام على وضوء استيقظ مسرورا ببركة ربه"),
    ("pious", "الرضا مفتاح السعادة في الدنيا"),
    ("pious", "النية الصادقة تسبق العمل وتباركه"),
    ("pious", "من جعل القرآن رفيقه في السفر لم يشعر بالوحدة أبدا"),
    ("quranic", "وجعلنا الصبر نورا للمؤمنين في كل حين"),
    ("quranic", "إن مع الصبر نصرا ومع الشكر زيادة"),
    ("quranic", "ولا تيأسوا من فرج ربكم فإنه قريب من الصابرين"),
    ("quranic", "واذكروا ربكم في الأسواق كما تذكرونه في المساجد"),
    ("quranic", "وبشر الصابرين على تعب الحياة بجنة عرضها كعرض الأرض"),
    ("quranic", "يا أيها الذين آمنوا أحسنوا إلى جيرانكم في السراء والضراء"),
    ("quranic", "وقل للناس قولا لينا تكسبوا قلوبهم"),
    ("quranic", "ومن يتوكل على ربه في عمله يرزقه من حيث لا يدري"),
    ("quranic", "وأحسنوا إلى أنفسكم بالنوم المبكر والطعام الطيب"),
    ("quranic", "والذين يصدقون في تجارتهم أولئك لهم البركة في أموالهم"),
    ("quranic", "وما الحياة إلا فرصة للعمل الصالح فلا تضيعوها"),
    ("quranic", "ويحب الله من عباده الذين يبتسمون في وجوه الناس"),
    ("quranic", "ولا تمشوا في الأرض عابسين فإن الابتسامة نور"),
    ("quranic", "وجعلنا القراءة غذاء للعقول كما جعلنا الطعام غذاء للأبدان"),
    ("quranic", "إن الله لا يضيع دعوة الأم لولدها في جوف الليل"),
    ("quranic", "فاصبروا على ما أصابكم من تعب الدنيا إن الفرج قريب"),
    ("quranic", "ولقد خلقنا الإنسان ليعمر الأرض بالعلم والعمل"),
    ("proverb", "الوقت كالسيف إن لم تقطعه قطعك"),
    ("proverb", "من جد وجد ومن زرع حصد"),
    ("proverb", "لكل مجتهد نصيب"),
    ("proverb", "الصديق وقت الضيق"),
    ("proverb", "خير الكلام ما قل ودل"),
    ("proverb", "في التأني السلامة وفي العجلة الندامة"),
    ("proverb", "العقل السليم في الجسم السليم"),
    ("proverb", "من سار على الدرب وصل"),
    ("proverb", "رب أخ لك لم تلده أمك"),
    ("proverb", "ما كل ما يتمنى المرء يدركه تجري الرياح بما لا تشتهي السفن"),
    ("proverb", "إذا كان الكلام من فضة فالسكوت من ذهب"),
    ("proverb", "العلم نور والجهل ظلام"),
    ("proverb", "العدل أساس الملك"),
    ("proverb", "من طلب العلا سهر الليالي"),
    ("proverb", "دع الأيام تفعل ما تشاء وطب نفسا إذا حكم القضاء"),
    ("proverb", "على قدر أهل العزم تأتي العزائم"),
    ("proverb", "الأم مدرسة إذا أعددتها أعددت شعبا طيب الأعراق"),
    ("proverb", "اصبر على مر الجفا من معلم فإن رسوب العلم في نفراته"),
]


def _sentence_ids(text: str) -> list[int]:
    words = text.split()
    merged, k = [], 0
    while k < len(words):  # Uthmani writes the vocative attached: يَـٰٓأَيُّهَا
        if words[k] in ("يا", "ها") and k + 1 < len(words):
            merged.append(words[k] + words[k + 1])
            k += 2
        else:
            merged.append(words[k])
            k += 1
    return [_VOCAB.get(skeleton_ar(w), -1 - n) for n, w in enumerate(merged)]


def validate_negatives() -> tuple[list[tuple[int, str, str]], list[dict]]:
    ok, rejected = [], []
    for n, (group, text) in enumerate(NEGATIVES):
        shared = longest_shared_skeleton(skeleton_ar(text))
        ids = _sentence_ids(text)
        near = near_windows(ids, len(ids) // 2)
        if shared >= 16 or near:
            best = min(near, key=lambda w: w[2]) if near else None
            rejected.append({"text": text, "shared_letters": shared,
                             "nearest": (ref_of(TOK_AYAH[best[0]], TOK_AYAH[best[1] - 1]), best[2]) if best else None})
        else:
            ok.append((n, group, text))
    return ok, rejected


def gen_negative(rng, cid: str, pool) -> dict:
    n, group, sentence = pool
    marker = pick(rng, MARKERS_NEGATIVE)
    ref = ""
    if rng.random() < 0.25:
        s = rng.randrange(1, 115)
        ref, _ = fmt_ref(rng, s, rng.randrange(1, N_AYAT[s] + 1))
    text, intro = compose(rng, marker, sentence, ref, None, allow_in_surah=False)
    return {"id": cid, "kind": "negative", "variant": group, "style": "common", "marker": marker, "intro": intro,
            "ref_written": ref, "sentence_id": n, "text": text, "quote": sentence, "gaps": [],
            "expected": {"status": "not_in_mushaf", "ref": "", "accept_refs": [], "reference_ok": None}}


MUQATTAAT = {"لم", "لمص", "لر", "لمر", "كهيعص", "طه", "طسم", "طس", "يس", "ص", "حم", "عسق", "ق", "ن"}


def short_pool() -> list[int]:
    pool = []
    for i, (_, _, t) in enumerate(AYAT):
        t0, t1 = AYAH_TOK[i]
        if not 1 <= t1 - t0 <= 3:
            continue
        if all(TOK_SK[k] in MUQATTAAT for k in range(t0, t1)):
            SKIPS["short_muqattaat"] += 1
            continue
        if AYAH_SK_COUNT[AYAH_SK[i]] > 1:
            SKIPS["short_repeated_ayah"] += 1
            continue
        if len(find_all(AYAH_SK[i])) > 3:
            SKIPS["short_occurs_over_3_times"] += 1
            continue
        pool.append(i)
    return pool


def gen_short(rng, cid: str, i: int) -> dict:
    t0, t1 = AYAH_TOK[i]
    style = pick(rng, STYLES)
    quote, gaps, typed_casually = render(TOK[t0:t1], style, rng)
    case = _base_case(cid, "short", i, i, style, rng)
    occ = occurrence_refs(AYAH_SK[i])
    ref, ref_fmt, ref_ok = "", "", None
    if rng.random() < 0.3:
        ref, ref_fmt = fmt_ref(rng, AYAT[i][0], AYAT[i][1])
        ref_ok = True
        case["ref_target"] = case["mushaf_ref"]
    text, intro = compose(rng, "brackets", quote, ref, AYAT[i][0])
    accept = [case["mushaf_ref"]] if ref else sorted(set(occ) | {case["mushaf_ref"]})
    case.update({"marker": "brackets", "intro": intro, "ref_written": ref, "ref_format": ref_fmt, "text": text,
                 "quote": quote, "gaps": gaps, "typed_casually": typed_casually, "occurrences": len(occ),
                 "skeleton_len": len(AYAH_SK[i]),
                 "expected": {"status": "verified", "ref": case["mushaf_ref"], "accept_refs": accept, "reference_ok": ref_ok}})
    return case


KIND_SHARE = [("exact", 0.20), ("wrong_ref", 0.13), ("substitution", 0.15), ("omission", 0.12), ("insertion", 0.12),
              ("negative", 0.15), ("short", 0.13)]
EXACT_KINDS = ("exact", "wrong_ref", "short")
MISQUOTE_KINDS = ("substitution", "omission", "insertion", "alef")
# Added on 4 Oct (plan item 11) on top of the original 600 cases, so the 600 stay exactly the same for a given seed.
EXTRA_KINDS = [("alef", 0.10)]


def generate(n: int, seed: int) -> tuple[list[dict], dict]:
    counts = {k: int(n * w) for k, w in KIND_SHARE}
    counts["exact"] += n - sum(counts.values())
    counts.update({k: int(n * w) for k, w in EXTRA_KINDS})
    neg_ok, neg_rejected = validate_negatives()
    pool6 = short_pool()
    cases = []
    for kind, _ in KIND_SHARE + EXTRA_KINDS:
        rng = random.Random(f"{seed}-{kind}")
        if kind == "negative":
            order = []
            while len(order) < counts[kind]:
                batch = list(neg_ok)
                rng.shuffle(batch)
                order += batch
        elif kind == "short":
            order = rng.sample(pool6, min(counts[kind], len(pool6)))
            while len(order) < counts[kind]:
                order.append(rng.choice(pool6))
        for k in range(counts[kind]):
            cid = f"{kind}-{k + 1:03d}"
            if kind == "exact":
                cases.append(gen_exact(rng, cid))
            elif kind == "wrong_ref":
                cases.append(gen_exact(rng, cid, wrong_ref=True))
            elif kind in MISQUOTE_KINDS:
                cases.append(gen_misquote(rng, cid, kind))
            elif kind == "negative":
                cases.append(gen_negative(rng, cid, order[k]))
            else:
                cases.append(gen_short(rng, cid, order[k]))
    meta = {"negatives_used": len(neg_ok), "negatives_rejected": neg_rejected, "short_pool": len(pool6),
            "skips": dict(SKIPS)}
    return cases, meta


# ---------------------------------------------------------------- running and scoring


def _got(c: dict | None) -> dict:
    if c is None:
        return {"status": "missed"}
    q = c.get("quran") or {}
    return {
        "type": c["type"], "status": c["status"], "quote": c["quote"], "marker": c.get("marker", ""),
        "ref": q.get("ref", ""), "score": q.get("score"), "occurrences": q.get("occurrences"),
        "reference_given": q.get("reference_given", ""), "reference_ok": q.get("reference_ok"),
        "diff": [d for d in (q.get("diff") or []) if d["op"] != "equal"], "notes": c.get("notes", []),
    }


def score_case(case: dict, result: dict) -> dict:
    exp_sk = skeleton_ar(case["quote"])
    best, best_score = None, -1.0
    for c in result["citations"]:
        sk = skeleton_ar(c["quote"])
        s = fuzz.partial_ratio(exp_sk, sk) if exp_sk and sk else 0.0
        if s > best_score:
            best, best_score = c, s
    found = best is not None and best_score >= 50 and best["type"] == "quran"
    got = _got(best if found else None)
    exp = case["expected"]
    ev = {"found": found, "extra_citations": len(result["citations"]) - (1 if found else 0)}
    ev["status_ok"] = got["status"] == exp["status"]
    if exp["ref"]:
        ev["ref_ok"] = got.get("ref") in exp["accept_refs"]
        ev["ref_overlap"] = _overlaps(got.get("ref", ""), exp["ref"])
    if exp["reference_ok"] is not None:
        ev["reference_check_ok"] = got.get("reference_ok") is exp["reference_ok"]
    ev["correct"] = ev["status_ok"] and ev.get("ref_ok", True) and ev.get("reference_check_ok", True)
    return got, ev


def _span(ref: str):
    m = re.match(r"(\d+):(\d+)(?:-(\d+))?$", ref or "")
    if not m:
        return None
    return int(m.group(1)), int(m.group(2)), int(m.group(3) or m.group(2))


def _overlaps(a: str, b: str) -> bool:
    x, y = _span(a), _span(b)
    return bool(x and y and x[0] == y[0] and x[1] <= y[2] and y[1] <= x[2])


async def run_cases(cases: list[dict]) -> list[dict]:
    from app.pipeline import check_text

    rows = []
    for case in cases:
        t0 = time.perf_counter()
        result = await check_text(case["text"])
        dt = (time.perf_counter() - t0) * 1000
        got, ev = score_case(case, result)
        row = dict(case)
        row.update({"got": got, "eval": ev, "latency_ms": round(dt, 2), "n_citations": len(result["citations"]),
                    "all_statuses": [c["status"] for c in result["citations"]]})
        row["cause"] = classify(row) if not ev["correct"] else ""
        rows.append(row)
    return rows


# ---------------------------------------------------------------- failure causes


def classify(row: dict) -> str:
    kind, got, exp, ev = row["kind"], row["got"], row["expected"], row["eval"]
    st = got["status"]
    q_sk = skeleton_ar(row["quote"])
    if st == "missed":
        if kind == "short" and len(row["quote"]) < 6:
            return "extract_too_short"
        if row["marker"] == "unmarked":
            return "unmarked_not_found" + ("+norm_gap" if row["gaps"] else "")
        return "extract_other"
    g_sk = skeleton_ar(got["quote"])
    boundary = ""
    if g_sk != q_sk:
        if q_sk in g_sk:
            ref_digits = re.findall(r"[0-9٠-٩]+", row.get("ref_written", ""))
            if row.get("ref_written") and ref_digits and any(d in got["quote"] for d in ref_digits):
                boundary = "ref_in_quote"
            elif got["quote"].startswith("في سورة"):
                boundary = "surah_phrase_in_quote"
            else:
                boundary = "extra_text_in_quote"
        elif g_sk in q_sk:
            boundary = "quote_truncated"
        else:
            boundary = "quote_differs"
    contaminated = boundary in ("ref_in_quote", "surah_phrase_in_quote", "extra_text_in_quote")
    status_or_ref_wrong = not ev["status_ok"] or not ev.get("ref_ok", True)
    if contaminated and (status_or_ref_wrong or (not ev.get("reference_check_ok", True) and boundary == "ref_in_quote")):
        return "boundary:" + boundary

    def ref_cause() -> str:
        if got.get("reference_given"):
            return "ref_check_other"
        target = _span(row.get("ref_target", ""))
        if target and target[0] in (38, 50) and row.get("ref_format") != "num":
            return "ref_missed:one_letter_surah"
        if boundary == "quote_truncated":
            return "ref_missed:quote_cut"
        return "ref_missed:not_parsed"

    if kind in EXACT_KINDS:
        if st != "verified":
            if len(q_sk) < 10:
                return "min_skeleton"
            if row["gaps"]:
                return "norm_gap" if len(skeleton_ar(row["quote"])) >= 12 else "norm_gap+short"
            return "exact_other"
        if not ev.get("ref_ok", True):
            return "wrong_location"
        if not ev.get("reference_check_ok", True):
            return ref_cause()
        return "other"
    if kind in MISQUOTE_KINDS:
        if st == "verified":
            return "false_verified" + (":" + boundary if boundary else "")
        if st == "not_in_mushaf":
            return "misquote_missed:below_threshold" + ("+norm_gap" if row["gaps"] else "")
        if st == "differs" and not ev.get("ref_ok", True):
            g = _span(got.get("ref", ""))
            if ev.get("ref_overlap") and g and g[2] == N_AYAT[g[0]] and _span(exp["ref"])[2] == g[2]:
                return "nearest_span:surah_end"
            return "nearest_span" if ev.get("ref_overlap") else "nearest_wrong_place"
        if not ev.get("reference_check_ok", True):
            return ref_cause()
        return "other"
    if kind == "negative":
        return "false_quran_match" if st in ("verified", "differs") else "other"
    return "other"


async def census() -> dict:
    """Every ayah of the Mushaf quoted alone inside ﴿﴾, as copied (Uthmani) and in common spelling."""
    from app.pipeline import check_text

    out = {}
    for style in ("uthmani", "uthmani_plain", "common"):
        rows = []
        for i, (s_, a_, _) in enumerate(AYAT):
            t0, t1 = AYAH_TOK[i]
            if all(TOK_SK[k] in MUQATTAAT for k in range(t0, t1)):
                continue
            if style == "uthmani":
                quote, gap_rules, gap_words = " ".join(TOK[t0:t1]), [], []
            elif style == "uthmani_plain":
                quote = " ".join(strip_marks(w) for w in TOK[t0:t1])
                gap_words = [strip_marks(w) for w in TOK[t0:t1] if skeleton_ar(strip_marks(w)) != skeleton_ar(w)]
                gap_rules = ["stripped_waw_alef"] if gap_words else []
            else:
                conv = [to_common_word(w, harakat=False) for w in TOK[t0:t1]]
                quote = " ".join(w for w, _ in conv)
                gap = [(w, r, t) for (w, r), t in zip(conv, TOK[t0:t1]) if skeleton_ar(w) != skeleton_ar(t)]
                gap_rules = sorted({x for _, r, _ in gap for x in r & CHANGING_RULES})
                gap_words = [w for w, _, _ in gap]
            r = await check_text("﴿" + quote + "﴾")
            st = r["citations"][0]["status"] if r["citations"] else "missed"
            rows.append({"i": i, "words": t1 - t0, "status": st, "gap_rules": gap_rules, "gap_words": gap_words,
                         "short_sk": len(AYAH_SK[i]) < 10})
        out[style] = rows
    return out


# One-line reproductions of the failure causes, re-run against the current code when the report is written.
REPROS = [
    ("norm_gap", "قال تعالى: ﴿يا بني إسرائيل اذكروا نعمتي التي أنعمت عليكم﴾", "verified 2:40"),
    ("norm_gap", "قال الله تعالى: ﴿الله لا إله إلا هو الحي القيوم لا تأخذه سنة ولا نوم له ما في السماوات وما في الأرض "
                 "من ذا الذي يشفع عنده إلا بإذنه يعلم ما بين أيديهم وما خلفهم ولا يحيطون بشيء من علمه إلا بما شاء وسع "
                 "كرسيه السماوات والأرض ولا يؤوده حفظهما وهو العلي العظيم﴾ (البقرة: 255)", "verified 2:255, reference_ok true"),
    ("norm_gap", "﴿والليل إذا يغشى والنهار إذا تجلى﴾", "verified 92:1-2"),
    ("norm_gap", "قال تعالى: ﴿سبحان الذي أسرى بعبده ليلا من المسجد الحرام إلى المسجد الأقصى﴾", "verified 17:1"),
    ("norm_gap+short", "قال تعالى: ﴿والشمس وضحاها﴾", "verified 91:1"),
    ("norm_gap (stripped Uthmani)", "﴿ٱلله نور ٱلسموت وٱلأرض مثل نوره كمشكوة فيها مصباح﴾", "verified 24:35"),
    ("min_skeleton", "قال تعالى: ﴿الله الصمد﴾ (الإخلاص: 2)", "verified 112:2, reference_ok true"),
    ("min_skeleton", "قال تعالى: ﴿ويسر لي أمري﴾", "verified 20:26"),
    ("boundary:ref_in_quote", "قال تعالى: ولتكن منكم أمة يدعون إلى الخير ويأمرون بالمعروف وينهون عن المنكر وأولئك هم "
                              "المفلحون (آل عمران: 104).", "verified 3:104, reference_ok true"),
    ("boundary:ref_in_quote", "قال تعالى: إن مع العسر يسرا (البقرة 286).", "verified 94:5, reference_ok false"),
    ("boundary:surah_phrase_in_quote", "قال الله تعالى في سورة الطلاق: «ومن يتق الله يجعل له مخرجا»", "verified 65:2"),
    ("ref_missed:one_letter_surah", "قال تعالى: ﴿ما يلفظ من قول إلا لديه رقيب عتيد﴾ (ق: 30)", "verified 50:18, reference_ok false"),
]


async def run_repros() -> list[dict]:
    from app.pipeline import check_text

    out = []
    for cause, text, expected in REPROS:
        r = await check_text(text)
        cits = [c for c in r["citations"] if c["type"] == "quran"]
        if not cits:
            got = "no citation"
        else:
            c = cits[0]
            q = c.get("quran") or {}
            got = f"{c['status']} {q.get('ref') or '–'}"
            if q.get("reference_given") or "reference_ok" in expected:
                got += f", reference_given «{q.get('reference_given') or ''}», reference_ok {str(q.get('reference_ok')).lower()}"
            if skeleton_ar(c["quote"]) != skeleton_ar(re.sub(r"^.*?[:﴿«]\s*", "", text, count=1).rstrip(".﴾»")) and c.get("marker") != "﴿﴾":
                got += f"; quote taken: «{c['quote'][-60:]}»" if len(c["quote"]) > 60 else f"; quote taken: «{c['quote']}»"
            diff = [d for d in (q.get("diff") or []) if d["op"] != "equal"]
            if diff:
                got += "; flagged as changed: " + ", ".join(f"«{d['quoted']}»" for d in diff[:3])
        out.append({"cause": cause, "text": text, "expected": expected, "got": got})
    return out


def loc(rel: str, needle: str) -> str:
    try:
        for n, line in enumerate((ROOT / rel).read_text(encoding="utf-8").splitlines(), 1):
            if needle in line:
                return f"{rel}:{n}"
    except OSError:
        pass
    return rel


def cause_doc() -> dict:
    q, x, p, nrm = "app/quran.py", "app/extract.py", "app/pipeline.py", "app/normalize.py"
    not_in = loc(p, 'out["status"] = "not_in_mushaf"')
    all_equal = loc(q, 'if m.diff and all(d["op"] == "equal"')
    return {
        "norm_gap": (
            "Correct ayah in common spelling reported as misquoted",
            f"Matching is an exact substring search on a consonantal skeleton ({loc(q, 'self.full.find(q)')}). "
            f"skeleton_ar ({loc(nrm, 'def skeleton_ar')}) only removes alef, hamza and marks, but the Uthmani rasm differs from "
            "standard spelling in letters too: hamza on a kursi or on the line where common spelling uses ئ/ؤ (شيئا، السيئات، "
            "إسرائيل، يؤوده، رؤوف), ىٰ inside a word (ضحىٰها → ضحاها، مأوىٰهم → مأواهم), small yaa/waw that are real letters "
            "(إبراهيم، النبيين، يحيي، يلوون), one-lam الليل/اللذين/اللاتي/اللائي, ننجي, يبسط. _DIACRITICS "
            f"({loc(nrm, '_DIACRITICS = re.compile(')}) deletes the small letters and _LETTER_MAP maps ئ→ي, ؤ→و, ى→ي, so the "
            "two spellings of the same word get different skeletons. The exact search fails and _fuzzy_arabic "
            f"({loc(q, 'def _fuzzy_arabic')}) returns 'differs', with the correctly quoted word shown as a change."),
        "norm_gap+short": (
            "Short correct quote in common spelling reported as not in the Mushaf",
            f"Same spelling gap as above, but the skeleton is under MIN_SKELETON_FUZZY = 12 ({loc(q, 'MIN_SKELETON_FUZZY =')}), "
            f"so there is no fuzzy fallback and check_quran ({not_in}) reports not_in_mushaf "
            "with the referral 'not found in the Mushaf' (e.g. ﴿والشمس وضحاها﴾)."),
        "min_skeleton": (
            "Short ayah reported as not in the Mushaf",
            f"match_arabic returns not_found for any quote whose skeleton is under MIN_SKELETON = 10 letters "
            f"({loc(q, 'MIN_SKELETON = 10')}, {loc(q, 'if len(q) < MIN_SKELETON:')}), even inside ﴿﴾ and even with a correct "
            f"written reference; check_quran ({not_in}) then tells the reader the text was "
            "not found in the Mushaf. About a third of the ayat of <= 3 words are under 10 letters (﴿الله الصمد﴾، ﴿ويسر لي أمري﴾، "
            "﴿والعصر﴾). The threshold protects free-text scanning; inside ﴿﴾ or with a reference it should not apply."),
        "boundary:ref_in_quote": (
            "Written reference swallowed into an unbracketed quote",
            f"After a marker without quotation marks, _take_quote ({loc(x, 'def _take_quote')}) runs to SENTENCE_END "
            f"({loc(x, 'SENTENCE_END = re.compile')}), which stops at '(' only before a digit, 'سورة', or ONE Arabic word and a "
            "colon. '(آل عمران: 104)', '(البقرة، الآية 104)', '(البقرة 104)' and '[...]' are kept inside the quote, so the "
            "quote no longer matches exactly ('differs') and, since the candidate ends after the reference, "
            f"_reference_after ({loc(x, 'def _reference_after')}) never sees it."),
        "boundary:surah_phrase_in_quote": (
            "'قال الله تعالى في سورة X:' puts 'في سورة X' into the quote",
            f"QURAN_AR ({loc(x, 'QURAN_AR = re.compile(')}) ends at 'تعالى'; _take_quote ({loc(x, 'def _take_quote')}) then "
            "skips only spaces and colons, finds no quotation mark at 'في', and takes the rest of the sentence. The quote "
            "becomes 'في سورة البقرة: «...' and is reported as 'differs' (or not found). With ﴿﴾ it is fine because the "
            "bracket rule runs first."),
        "boundary:extra_text_in_quote": (
            "Text after an unbracketed quote absorbed into it",
            f"_take_quote ({loc(x, 'def _take_quote')}) ends an unbracketed quote only at SENTENCE_END; anything between the "
            "ayah and the next full stop is matched as part of the ayah."),
        "ref_missed:not_parsed": (
            "Written reference not read",
            f"_reference_after ({loc(x, 'def _reference_after')}) looks only 60 characters after the candidate and needs the "
            "reference to start within 12 of them; REF_NAME/REF_NUM accept a limited set of forms. A wrong reference that is "
            "not read is never flagged."),
        "ref_missed:one_letter_surah": (
            "Reference to surah ق or ص not read",
            f"REF_NAME ({loc(x, 'REF_NAME = re.compile(')}) requires a surah name of at least 2 letters "
            "('[ء-يٱ ]{2,25}?'), so (ق: 18) and (ص: 29) are ignored: a wrong reference to these surahs is never flagged and a "
            "right one is never confirmed."),
        "ref_missed:quote_cut": (
            "Long unbracketed quote cut at 500 characters, reference not read",
            f"_take_quote caps an unbracketed quote at 500 characters ({loc(x, 'end = min(end, pos + 500)')}). A fully "
            "diacritized ayah is longer; the candidate ends mid-ayah and the reference after the real end is more than 12 "
            "characters away, so it is not checked. The match itself is still exact (a prefix)."),
        "extract_too_short": (
            "Quote shorter than 6 characters not extracted",
            f"_add drops candidates under 6 characters ({loc(x, 'if len(cand.quote) < 6:')}), so ﴿ق﴾-like or 2-letter-"
            "skeleton quotes inside ﴿﴾ are silently ignored."),
        "unmarked_not_found": (
            "Unmarked quote not found",
            f"_scan_unmarked_quran ({loc(x, 'def _scan_unmarked_quran')}) needs five consecutive words whose skeleton is in "
            "the Mushaf."),
        "unmarked_not_found+norm_gap": (
            "Unmarked quote in common spelling not found",
            f"_scan_unmarked_quran ({loc(x, 'def _scan_unmarked_quran')}) needs five consecutive words whose skeleton is an "
            "exact Mushaf substring; one word with a spelling gap (see norm_gap) breaks every window that contains it."),
        "misquote_missed:below_threshold": (
            "Misquote not recognised (reported as not in the Mushaf)",
            f"_fuzzy_arabic ({loc(q, 'threshold = 88 if len(q) < 30 else 82')}) needs partial_ratio >= 88 (skeleton < 30) "
            "or >= 82; a one-word change in a short passage falls below it. Safe direction (refers the reader), but the "
            "reader is told the text is not in the Mushaf at all."),
        "misquote_missed:below_threshold+norm_gap": (
            "Misquote in common spelling not recognised",
            "The deliberate one-word change plus spelling-gap words (see norm_gap) push the fuzzy score under the threshold."),
        "nearest_span": (
            "Misquote matched to the right place, wrong ayah range",
            f"_fuzzy_arabic narrows the window with partial_ratio_alignment ({loc(q, 'align = fuzz.partial_ratio_alignment')}); "
            "an inserted or omitted word near an ayah boundary moves the alignment so the range gains or loses an ayah."),
        "nearest_span:surah_end": (
            "Misquote ending at a surah's last ayah narrowed to that ayah; correct words shown as additions",
            f"_fuzzy_arabic builds windows 'at least as long as the quote' ({loc(q, 'while (len(text) < len(q) or j == i)')}), "
            "but the loop stops at the end of the surah, so the window that starts at a surah's last ayah is just that ayah, "
            "shorter than the quote. partial_ratio then measures how well the short window fits inside the quote, which is "
            "100 when the last ayah is quoted correctly. That window wins, the range is narrowed to the last ayah and the "
            "correctly quoted ayah before it appears in the diff as words the author added. Reproduce: "
            "Quran.match_arabic('ويل يومئذ للكافرين فبأي حديث بعده يؤمنون') → differs 77:50, score 100, "
            "diff 'delete ويل يومئذ للكافرين' (nearest is 77:49-50, one word changed)."),
        "nearest_wrong_place": (
            "Misquote matched to another place",
            f"_fuzzy_arabic ({loc(q, 'best = process.extractOne(q, windows')}) picks the best partial_ratio window; partial "
            "matching on a skeleton string can prefer a window elsewhere that shares a long run of letters."),
        "false_quran_match": (
            "Non-Quran sentence matched to an ayah",
            f"partial_ratio on the consonantal skeleton ({loc(q, 'best = process.extractOne(q, windows')}) scores a short "
            "sentence against the best-aligned substring of any 1-7 ayah window; common Quranic phrases push it over 82/88."),
        "false_verified": (
            "Misquote reported as verified",
            f"_fuzzy_arabic marks a fuzzy match 'exact' when word_diff shows no change ({all_equal})."),
        "wrong_location": ("Verified at a different place than expected", "See the example."),
        "exact_other": ("Other", "See the example."),
        "extract_other": ("Not extracted", "See the example."),
        "ref_check_other": ("Reference read but judged wrongly", f"See {loc(q, 'def check_reference')}."),
        "other": ("Other", "See the example."),
    }


# ---------------------------------------------------------------- report


def pct(a: int, b: int) -> str:
    return f"{a}/{b} ({100 * a / b:.1f}%)" if b else "n/a"


def wilson(a: int, b: int) -> str:
    if not b:
        return ""
    z, p = 1.96, a / b
    d = 1 + z * z / b
    c = (p + z * z / (2 * b)) / d
    h = z * math.sqrt(p * (1 - p) / b + z * z / (4 * b * b)) / d
    return f"{100 * max(0, c - h):.1f}–{100 * min(1, c + h):.1f}%"


def quantile(xs: list[float], q: float) -> float:
    xs = sorted(xs)
    if not xs:
        return 0.0
    k = (len(xs) - 1) * q
    f = math.floor(k)
    return xs[f] + (xs[min(f + 1, len(xs) - 1)] - xs[f]) * (k - f)


def write_report(rows: list[dict], meta: dict, args, path: Path) -> list[str]:
    docs = cause_doc()
    by_kind = defaultdict(list)
    for r in rows:
        by_kind[r["kind"]].append(r)
    exact = [r for r in rows if r["kind"] in EXACT_KINDS]
    mis = [r for r in rows if r["kind"] in MISQUOTE_KINDS]
    neg = by_kind["negative"]
    flagged = lambda r: r["got"]["status"] in ("differs", "not_in_mushaf")  # noqa: E731
    refs_given = [r for r in rows if r["expected"]["reference_ok"] is not None]
    right_refs = [r for r in refs_given if r["expected"]["reference_ok"] is True]
    wrong_refs = [r for r in refs_given if r["expected"]["reference_ok"] is False]
    right_ref_alarm = [r for r in right_refs if r["got"].get("reference_ok") is False]
    ex_flag = [r for r in exact if flagged(r)]
    ex_any_false = [r for r in exact if flagged(r) or (r["expected"]["reference_ok"] is True and r["got"].get("reference_ok") is False)]
    lat = [r["latency_ms"] for r in rows]
    found = sum(r["eval"]["found"] for r in rows)
    L = []
    L += ["# Tathabbut: synthetic Quran evaluation", ""]
    L += [f"Generated by `python3 eval/synth_quran.py --n {args.n} --seed {args.seed}`: {len(rows)} cases built from the bundled "
          f"Mushaf text ({len(AYAT):,} ayat), run through `app.pipeline.check_text` offline (hadith lookup and language model "
          f"off). Raw rows: `eval/synth_results.jsonl`. How every label is kept certain is in the script's docstring. "
          f"95% Wilson intervals in brackets.", ""]
    L += ["**Read the common-spelling numbers with care.** Since 4 Oct the app matches against a second Mushaf index built "
          "with the same converter (`app/spelling.py`) that writes this evaluation's common-spelling cases, so those cases "
          "partly test the converter against itself. Spelling the converter did not produce is tested separately with "
          "hand-typed quotes in `tests/test_quran_spelling.py`. The Uthmani cases and the alef cases do not depend on it.", ""]
    L += ["## Headline", "", "| Metric | Value |", "|---|---|"]
    L += [f"| Extraction recall (all cases) | {pct(found, len(rows))} |"]
    L += [f"| **False error on correct Quran text** (exact, wrong-ref and short cases reported `differs` or `not_in_mushaf`) | "
          f"**{pct(len(ex_flag), len(exact))}** [{wilson(len(ex_flag), len(exact))}] |"]
    for label, styles in (("… copied from the Mushaf (Uthmani with marks)", ("uthmani",)),
                          ("… Uthmani with marks stripped", ("uthmani_plain",)),
                          ("… common spelling (with or without harakat)", ("common", "common_harakat"))):
        sub = [r for r in exact if r["style"] in styles]
        L += [f"| {label} | {pct(sum(flagged(r) for r in sub), len(sub))} [{wilson(sum(flagged(r) for r in sub), len(sub))}] |"]
    sub = [r for r in exact if r["kind"] != "short"]
    L += [f"| … excluding very short ayat (≤ 3 words) | {pct(sum(flagged(r) for r in sub), len(sub))} |"]
    if meta.get("census"):
        for st, label in (("uthmani", "copied from the Mushaf"), ("common", "in common spelling")):
            cr = meta["census"][st]
            bad = sum(r["status"] != "verified" for r in cr)
            long_ = [r for r in cr if r["words"] >= 20]
            L += [f"| Census, every ayah alone in ﴿﴾ {label}: flagged | {pct(bad, len(cr))}; ayat of ≥ 20 words: "
                  f"{pct(sum(r['status'] != 'verified' for r in long_), len(long_))} |"]
    L += [f"| Correct written reference reported as wrong | {pct(len(right_ref_alarm), len(right_refs))} |"]
    L += [f"| Any false alarm on correct Quran text (status or reference) | {pct(len(ex_any_false), len(exact))} |"]
    caught = [r for r in wrong_refs if r["got"].get("reference_ok") is False]
    L += [f"| Wrong written reference caught (`reference_ok` false) | {pct(len(caught), len(wrong_refs))} [{wilson(len(caught), len(wrong_refs))}] |"]
    fv = [r for r in mis if r["got"]["status"] == "verified"]
    L += [f"| **False `verified` on misquotes** | **{pct(len(fv), len(mis))}** [{wilson(len(fv), len(mis))}] |"]
    md = [r for r in mis if r["got"]["status"] == "differs"]
    mdr = [r for r in md if r["eval"].get("ref_ok")]
    L += [f"| Misquotes reported `differs` | {pct(len(md), len(mis))} |"]
    L += [f"| … and at the right ayah range | {pct(len(mdr), len(mis))} |"]
    na = [r for r in neg if r["got"]["status"] == "not_in_mushaf"]
    fq = [r for r in neg if r["got"]["status"] in ("verified", "differs")]
    L += [f"| Negatives correctly `not_in_mushaf` (abstention) | {pct(len(na), len(neg))} [{wilson(len(na), len(neg))}] |"]
    L += [f"| Negatives wrongly tied to an ayah (`verified`/`differs`) | {pct(len(fq), len(neg))} |"]
    L += [f"| Latency per case, median / p95 / max | {statistics.median(lat):.1f} / {quantile(lat, 0.95):.1f} / {max(lat):.1f} ms |"]
    L += [f"| Mushaf index load (once per process) | {meta['load_ms']:.0f} ms |", ""]

    L += ["## By kind", "", "| Kind | n | Extracted | Status right | Status + ref right | Fully right* | verified / differs / not_in_mushaf / missed |",
          "|---|---|---|---|---|---|---|"]
    for kind, _ in KIND_SHARE + EXTRA_KINDS:
        rs = by_kind[kind]
        c = Counter(r["got"]["status"] for r in rs)
        sr = [r for r in rs if r["eval"]["status_ok"] and r["eval"].get("ref_ok", True)]
        L += [f"| {kind} | {len(rs)} | {pct(sum(r['eval']['found'] for r in rs), len(rs))} | "
              f"{pct(sum(r['eval']['status_ok'] for r in rs), len(rs))} | {pct(len(sr), len(rs))} | "
              f"{pct(sum(r['eval']['correct'] for r in rs), len(rs))} | "
              f"{c['verified']} / {c['differs']} / {c['not_in_mushaf']} / {c['missed']} |"]
    L += ["", "\\* status, ref and, when a reference is written, `reference_ok` all as expected. Misquote `ref` is the passage's "
          "exact range; " + pct(sum(r["eval"].get("ref_overlap", False) for r in md), len(md)) +
          " of the misquotes reported `differs` overlap the right ayat.", ""]

    L += ["## Correct Quran text by spelling and marker", "",
          "Cases: exact + wrong_ref + short. \"Flagged\" = reported `differs` or `not_in_mushaf`.", "",
          "| Spelling | n | verified | differs | not_in_mushaf | missed | flagged | with a spelling-gap word | flagged among those |",
          "|---|---|---|---|---|---|---|---|---|"]
    for st, _ in STYLES:
        rs = [r for r in exact if r["style"] == st]
        c = Counter(r["got"]["status"] for r in rs)
        g = [r for r in rs if r["gaps"]]
        L += [f"| {st} | {len(rs)} | {c['verified']} | {c['differs']} | {c['not_in_mushaf']} | {c['missed']} | "
              f"{pct(sum(flagged(r) for r in rs), len(rs))} | {len(g)} | {pct(sum(flagged(r) for r in g), len(g))} |"]
    L += ["", "| Marker | n | flagged | missed |", "|---|---|---|---|"]
    for mk in ("brackets", "guillemets", "colon", "dquotes", "braces", "unmarked"):
        rs = [r for r in exact if r["marker"] == mk]
        if rs:
            L += [f"| {mk} | {len(rs)} | {pct(sum(flagged(r) for r in rs), len(rs))} | {sum(r['got']['status'] == 'missed' for r in rs)} |"]
    no_gap = [r for r in exact if not r["gaps"] and r["kind"] != "short"]
    L += ["", f"Exact and wrong-ref cases with no spelling-gap word: {pct(sum(flagged(r) for r in no_gap), len(no_gap))} flagged.", ""]
    rule_counts, rule_flag = Counter(), Counter()
    for r in exact:
        rr = {x for gp in r["gaps"] for x in gp["rules"]}
        for x in rr:
            rule_counts[x] += 1
            rule_flag[x] += flagged(r)
    if rule_counts:
        L += ["Spelling rules behind the gap words (a case can have several):", "", "| Rule | Cases | Flagged |", "|---|---|---|"]
        for x, n in rule_counts.most_common():
            L += [f"| {x} | {n} | {rule_flag[x]} |"]
        L += [""]

    L += ["## Short ayat (≤ 3 words, inside ﴿﴾)", ""]
    sh = by_kind["short"]
    lo = [r for r in sh if r["skeleton_len"] < 10]
    hi = [r for r in sh if r["skeleton_len"] >= 10]
    L += [f"- skeleton < 10 letters: {pct(sum(r['got']['status'] == 'verified' for r in lo), len(lo))} verified",
          f"- skeleton ≥ 10 letters: {pct(sum(r['got']['status'] == 'verified' for r in hi), len(hi))} verified",
          f"- pool after exclusions: {meta['short_pool']} ayat; occurrences of the sampled ones: "
          f"{dict(sorted(Counter(r['occurrences'] for r in sh).items()))}", ""]

    L += ["## Reference check", "", "| Written reference | n | read by the tool | verdict right |", "|---|---|---|---|"]
    for label, rs in (("correct", right_refs), ("wrong", wrong_refs)):
        L += [f"| {label} | {len(rs)} | {pct(sum(bool(r['got'].get('reference_given')) for r in rs), len(rs))} | "
              f"{pct(sum(r['eval'].get('reference_check_ok', False) for r in rs), len(rs))} |"]
    L += ["", "| Format | n | read | verdict right |", "|---|---|---|---|"]
    for fmt, _ in REF_FORMATS:
        rs = [r for r in refs_given if r.get("ref_format") == fmt]
        if rs:
            L += [f"| {fmt} | {len(rs)} | {pct(sum(bool(r['got'].get('reference_given')) for r in rs), len(rs))} | "
                  f"{pct(sum(r['eval'].get('reference_check_ok', False) for r in rs), len(rs))} |"]
    L += ["", "| Wrong-reference kind | n | caught |", "|---|---|---|"]
    for k in ("near", "other_surah_same_ayah", "random", "nonexistent"):
        rs = [r for r in wrong_refs if r.get("wrong_ref_kind") == k]
        if rs:
            L += [f"| {k} | {len(rs)} | {pct(sum(r['got'].get('reference_ok') is False for r in rs), len(rs))} |"]
    L += [""]

    L += ["## Negatives", "", f"{meta['negatives_used']} sentences passed the not-near-the-Mushaf check and were reused "
          f"across markers; {len(meta['negatives_rejected'])} were rejected as too close to an ayah and not used.", "",
          "| Group | n | not_in_mushaf | differs | verified | missed |", "|---|---|---|---|---|---|"]
    for g in ("pious", "quranic", "proverb"):
        rs = [r for r in neg if r["variant"] == g]
        c = Counter(r["got"]["status"] for r in rs)
        L += [f"| {g} | {len(rs)} | {c['not_in_mushaf']} | {c['differs']} | {c['verified']} | {c['missed']} |"]
    if meta["negatives_rejected"]:
        L += ["", "Rejected sentences: " + "; ".join(
            f"«{x['text']}» (shared {x['shared_letters']} letters" + (f", {x['nearest'][1]} words from {x['nearest'][0]}" if x["nearest"] else "") + ")"
            for x in meta["negatives_rejected"])]
    L += [""]

    L += ["## Latency", "", "| Kind | median ms | p95 ms |", "|---|---|---|"]
    for kind, _ in KIND_SHARE + EXTRA_KINDS:
        xs = [r["latency_ms"] for r in by_kind[kind]]
        L += [f"| {kind} | {statistics.median(xs):.1f} | {quantile(xs, 0.95):.1f} |"]
    L += ["", "Exact matches return after a substring search; everything else pays for `_fuzzy_arabic`, which rebuilds "
          "6,236 ayah windows in Python on every call.", ""]

    fails = [r for r in rows if r["cause"]]
    causes = Counter(r["cause"] for r in fails)
    L += ["## Failure causes", "", "| Cause | Cases | Kinds | What it is |", "|---|---|---|---|"]
    for c, n in causes.most_common():
        kinds = Counter(r["kind"] for r in fails if r["cause"] == c)
        L += [f"| `{c}` | {n} | {', '.join(f'{k} {v}' for k, v in kinds.most_common())} | {docs.get(c, ('',))[0]} |"]
    L += [""]

    L += ["## Error analysis", "", "Up to 15 failing cases, chosen round-robin across causes (shortest text first within a "
          "cause). Diagnoses point at the working tree at the time of the run.", ""]
    picked, queues = [], {c: sorted([r for r in fails if r["cause"] == c], key=lambda r: len(r["text"])) for c, _ in causes.most_common()}
    while len(picked) < 15 and any(queues.values()):
        for c in list(queues):
            if queues[c] and len(picked) < 15:
                picked.append(queues[c].pop(0))
    for n, r in enumerate(picked, 1):
        g, e = r["got"], r["expected"]
        exp = f"`{e['status']}`" + (f", ref {e['ref']}" if e["ref"] else "") + (
            f", reference_ok {str(e['reference_ok']).lower()}" if e["reference_ok"] is not None else "")
        gt = f"`{g['status']}`"
        if g["status"] != "missed":
            gt += f", ref {g.get('ref') or '–'}, score {g.get('score')}"
            if r["expected"]["reference_ok"] is not None:
                gt += f", reference_given «{g.get('reference_given') or ''}», reference_ok {str(g.get('reference_ok')).lower()}"
            if g.get("diff"):
                gt += "; diff: " + ", ".join(f"{d['op']} «{d['quoted']}»→«{d['mushaf']}»" for d in g["diff"][:3])
            if skeleton_ar(g["quote"]) != skeleton_ar(r["quote"]):
                gt += f"; extracted quote «{g['quote'][:120]}»"
        title, doc = docs.get(r["cause"], ("Other", ""))
        extra = ""
        if r["gaps"]:
            extra = " Gap words here: " + ", ".join(f"«{x['quoted']}» vs Mushaf «{x['mushaf']}» ({'/'.join(x['rules'])})" for x in r["gaps"][:4]) + "."
        if r.get("edit"):
            ed = r["edit"]
            extra += f" Edit: {ed['op']} {ed.get('mushaf_word', '')}{' → ' if ed['op'] == 'substitute' else ''}{ed.get('quoted_word', '')} at word {ed['pos']}."
        text = r["text"].replace("\n", " ⏎ ")
        L += [f"**{n}. {r['id']}** ({r['kind']}, {r['style']}, {r['marker']}) — {title}", "",
              f"- Input: {text[:260]}{'…' if len(text) > 260 else ''}",
              f"- Expected: {exp}", f"- Got: {gt}", f"- Diagnosis: {doc}{extra}", ""]

    if meta.get("census"):
        cen = meta["census"]
        buckets = [("1–3", 1, 3), ("4–9", 4, 9), ("10–19", 10, 19), ("20–39", 20, 39), ("40+", 40, 999)]
        L += ["## Census: every ayah quoted alone in ﴿﴾", "",
              f"Not a sample: all {len(cen['uthmani'])} ayat (disconnected-letter openings excluded), each wrapped in ﴿﴾ "
              "and checked as copied from the Mushaf, with all marks stripped, and in common spelling (no harakat, no casual typing). "
              "Every one of them is a correct quote, so anything but `verified` is a false error.", "",
              "| Spelling | Ayat | verified | differs | not_in_mushaf | missed |", "|---|---|---|---|---|---|"]
        for st in ("uthmani", "uthmani_plain", "common"):
            c = Counter(r["status"] for r in cen[st])
            n = len(cen[st])
            L += [f"| {st} | {n} | {pct(c['verified'], n)} | {c['differs']} | {c['not_in_mushaf']} | {c['missed']} |"]
        L += ["", "| Words in the ayah | Ayat | verified (Uthmani) | verified (common) | common: ayat with a gap word | flagged among those |",
              "|---|---|---|---|---|---|"]
        for label, lo, hi in buckets:
            u = [r for r in cen["uthmani"] if lo <= r["words"] <= hi]
            c_ = [r for r in cen["common"] if lo <= r["words"] <= hi]
            g = [r for r in c_ if r["gap_rules"]]
            L += [f"| {label} | {len(u)} | {pct(sum(r['status'] == 'verified' for r in u), len(u))} | "
                  f"{pct(sum(r['status'] == 'verified' for r in c_), len(c_))} | {pct(len(g), len(c_))} | "
                  f"{pct(sum(r['status'] != 'verified' for r in g), len(g))} |"]
        short_u = [r for r in cen["uthmani"] if r["short_sk"]]
        L += ["", f"Uthmani failures are all ayat whose skeleton is under 10 letters: "
              f"{sum(r['status'] != 'verified' for r in short_u)} of {len(short_u)} such ayat flagged, "
              f"{sum(r['status'] != 'verified' for r in cen['uthmani'] if not r['short_sk'])} flagged among the rest.", ""]
        only_variant = [r for r in cen["common"] if r["status"] != "verified" and r["gap_rules"] == ["hamza_waw"]]
        L += [f"Common spelling, leaving out the {len(only_variant)} flagged ayat whose only gap is a hamza + waw word with two "
              f"accepted spellings (رؤوف/رءوف): {pct(sum(r['status'] != 'verified' for r in cen['common']) - len(only_variant), len(cen['common']) - len(only_variant))} flagged. "
              f"Stripped Uthmani: {sum(r['status'] != 'verified' for r in cen['uthmani_plain'] if r['gap_rules'] and not r['short_sk'])} "
              f"ayat flagged because of a word with و + dagger alef (الصلوة، الزكوة، الحيوة), "
              f"{sum(r['status'] != 'verified' for r in cen['uthmani_plain'] if not r['gap_rules'] and not r['short_sk'])} flagged otherwise "
              "(short ayat aside).", ""]
        words, rules = Counter(), Counter()
        for r in cen["common"]:
            if r["status"] != "verified":
                words.update(set(r["gap_words"]))
                rules.update(r["gap_rules"])
        if rules:
            L += ["Common spelling: rules behind the flagged ayat (an ayah can have several): " +
                  ", ".join(f"{k} {v}" for k, v in rules.most_common()) + ".", "",
                  "Words that most often make a correctly quoted ayah fail: " +
                  "، ".join(f"{w} ({n})" for w, n in words.most_common(25)) + ".", ""]

    if meta.get("repros"):
        L += ["## Minimal reproductions", "", "Re-run against the current code when this report was written.", "",
              "| Cause | Input | Expected | Got |", "|---|---|---|---|"]
        for x in meta["repros"]:
            text = x["text"] if len(x["text"]) < 120 else x["text"][:60] + " … " + x["text"][-50:]
            L += [f"| `{x['cause']}` | {text} | {x['expected']} | {x['got']} |"]
        L += [""]

    L += ["## Method notes and limits", "",
          "- Distribution is synthetic: passages are uniform over ayat, not weighted toward the ayat people actually quote; "
          "edits are random words, not plausible slips. Rates are properties of this mix (stated in the script), not of real "
          "traffic. Per-style and per-marker tables let you re-weight.",
          "- Common spelling comes from a rule-based converter (self-test in the script). Where hamza + waw has two accepted "
          "spellings it writes ؤ (رؤوف, يؤوده); those cases are tagged `hamza_waw` in the rule table above.",
          "- Kinds 1–4 only use passages that occur once in the Mushaf, so the tool's handling of repeated ayat is not measured "
          f"here (skipped while sampling: {meta['skips'].get('passage_not_unique', 0)} draws).",
          f"- Misquote draws rejected to keep labels certain: " + ", ".join(f"{k} {v}" for k, v in sorted(meta["skips"].items()) if not k.startswith("passage") and not k.startswith("short")) + ".",
          "- Hadith lookup was off, so `not_in_mushaf` negatives were not cross-checked against the hadith encyclopedia; "
          "the label is about the Mushaf only.", ""]
    path.write_text("\n".join(L) + "\n", encoding="utf-8")
    return L


# ---------------------------------------------------------------- main


async def main(args) -> int:
    if selftest(verbose=True):
        return 1
    if args.selftest:
        return 0
    assert not settings.dorar_enabled and settings.llm_backend == "none", "run offline: TATHABBUT_DORAR=0, TATHABBUT_LLM=none"
    t0 = time.perf_counter()
    cases, meta = generate(args.n, args.seed)
    print(f"generated {len(cases)} cases in {time.perf_counter() - t0:.1f}s; negatives rejected: {len(meta['negatives_rejected'])}")
    from app.quran import get_quran

    t0 = time.perf_counter()
    get_quran()
    meta["load_ms"] = (time.perf_counter() - t0) * 1000
    rows = await run_cases(cases)
    meta["repros"] = await run_repros()
    if not args.no_census:
        t0 = time.perf_counter()
        meta["census"] = await census()
        print(f"census of {len(meta['census']['uthmani'])} ayat x 3 spellings in {time.perf_counter() - t0:.0f}s")
    with open(args.results, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    lines = write_report(rows, meta, args, Path(args.report))
    print("\n".join(lines[4:30]))
    print(f"\nwrote {args.results} and {args.report}")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--n", type=int, default=600)
    ap.add_argument("--seed", type=int, default=2026)
    ap.add_argument("--results", default=str(ROOT / "eval" / "synth_results.jsonl"))
    ap.add_argument("--report", default=str(ROOT / "eval" / "synth_report.md"))
    ap.add_argument("--selftest", action="store_true", help="only run the spelling converter self-test")
    ap.add_argument("--no-census", action="store_true", help="skip the every-ayah census (a few minutes)")
    sys.exit(asyncio.run(main(ap.parse_args())))
