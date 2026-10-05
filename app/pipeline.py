"""The checking pipeline: extract citations, trace each one to its source, report verbatim, or refer."""
import asyncio
import json
import logging
import re
import time
from pathlib import Path

from rapidfuzz import fuzz

from . import fatwa, llm
from .config import settings
from .dorar import DorarResult, get_dorar
from .extract import Candidate, extract
from .glossary import gloss_book, gloss_grade
from .normalize import normalize_ar, skeleton_ar, quote_lang
from .quran import QuranMatch, get_quran
from .version import VERSION
from .scholars import EDITORS, GROUP_LABELS, IMAMS, find_scholar, grade_flags, is_hadith_level_grading

log = logging.getLogger("tathabbut")

STRONG_MATCH = 85
WEAK_MATCH = 60
DISPLAY_RULES = json.loads((Path(__file__).resolve().parent.parent / "data" / "display_rules.json").read_text(encoding="utf-8"))
# Plan item 12 (coverage guard), from data/display_rules.json. A quote of SHORT_QUOTE words or fewer must be
# found whole, in order, in the narration; a longer one needs MIN_COVERAGE of its words. Team defaults until
# tuned on the Sharia reviewer's set.
_COV = DISPLAY_RULES.get("coverage", {})
SHORT_QUOTE = _COV.get("short_quote_words", 5)
SHORT_MIN_COVERAGE = _COV.get("short_quote_min_coverage", 1.0)
MIN_COVERAGE = _COV.get("min_coverage", 0.8)
# A narration with more words than this is "longer": its grading may be about the whole narration or what it
# adds, so it is shown but does not decide the quote's status (live check, 4 Oct: Ibn Hajar's «موضوع» on an
# 897-word sermon in al-Matalib al-Aliya containing «من غشنا فليس منا», a hadith of Sahih Muslim).
def _longer(q_words: int, s_words: int) -> bool:
    return s_words > max(2 * q_words, q_words + 8)

# Level د: the package says the tool gives no ruling of its own and refers to a qualified body; it names none.
# Team decision (3 Oct): the reader looks first in the two scholars' published fatwas below; if none covers
# the case, the official fatwa body.
FATWA_BODY = {
    "ar": "جهة الإفتاء الرسمية في بلدك، وفي المملكة: الرئاسة العامة للبحوث العلمية والإفتاء",
    "en": "the official fatwa authority in your country (in Saudi Arabia: the General Presidency of Scholarly Research and Ifta)",
    "url": "https://www.alifta.gov.sa",
}
# The team relies on these two scholars' published fatwas (team's choice; not in the package's reference table).
# app/fatwa.py finds their fatwas on close questions through each site's own search and shows them verbatim with
# their source; the language model never writes, summarises or picks a fatwa.
FATWA_REFERENCES = [
    {"ar": "فتاوى سماحة الشيخ عبدالعزيز بن باز رحمه الله (الموقع الرسمي)",
     "en": "Fatwas of Shaykh Abd al-Aziz ibn Baz (official site)", "url": "https://binbaz.org.sa"},
    {"ar": "فتاوى فضيلة الشيخ محمد بن صالح العثيمين رحمه الله (الموقع الرسمي)",
     "en": "Fatwas of Shaykh Muhammad ibn Salih al-Uthaymeen (official site)", "url": "https://binothaimeen.net"},
    {"ar": "فتاوى اللجنة الدائمة للبحوث العلمية والإفتاء (البوابة الرسمية للإفتاء)",
     "en": "Fatwas of the Permanent Committee for Scholarly Research and Ifta (official portal)", "url": "https://www.alifta.gov.sa"},
]
# Level د (plan item 32): a personal fatwa question, or a chatbot answer issuing one. «هل علي بن أبي طالب...» is a
# question about a person, not a fatwa, so «هل علي» counts only before a word of obligation.
_ME_AR = r"(?:أنا|انا)\s+(?:طلقت|حلفت|نذرت|أفطرت|افطرت|تركت|صليت|اقترضت|أعمل|اعمل|أسكن|اسكن|متزوج|متزوجة|حامل|مريض|مريضة|مسافر|مسافرة|حائض|نفساء)"
PERSONAL_FATWA = re.compile(
    r"هل\s+(?:يجوز|يحل|يصح|يحق)\s+(?:لي|لنا)|هل\s+يجوز\s+(?:أن|ان)\s+أ|هل\s+(?:يصح|يقبل|يبطل)\s+(?:صيامي|صلاتي|زواجي|طلاقي|حجي|وضوئي|عمرتي)"
    r"|هل\s+(?:عل[يّ]ّ?|علينا)\s+(?:أن|ان|إثم|اثم|ذنب|كفارة|قضاء|زكاة|شيء|شي|دم|فدية|غسل)"
    r"|ما\s+حكم\s+(?:ما\s+فعلت|زواجي|طلاقي|صلاتي|صيامي|عملي|مالي|حجي)|(?:أنا|انا)\s+في\s+(?:دولة|بلد)|" + _ME_AR +
    r"|(?<![ء-ي])(?:طلقت\s+(?:زوجتي|امرأتي)|حلفت\s+(?:بالطلاق|بالله|أن|ان)|نذرت\s+(?:أن|ان)|زوجي\s+(?:طلقني|حلف|قال\s+لي)|ماذا\s+(?:يجب\s+)?علي|ماذا\s+أفعل\s+(?:إذا|اذا|لو|وقد))"
    # A chatbot answer that rules on the asker's own case.
    r"|(?:نعم|لا)\s*[،,]?\s*(?:يجوز|يحل)\s+لك|(?:يجب|يحرم)\s+عليك|(?:طلاقك|صيامك|صلاتك|زواجك|حجك|نذرك|يمينك)\s+(?:واقع|يقع|لا\s+يقع|صحيحة?|باطلة?|غير\s+صحيحة?)"
    r"|is\s+it\s+(?:halal|haram|permissible|allowed|ok(?:ay)?)\s+(?:for\s+me|if\s+i)|am\s+i\s+allowed\s+to|do\s+i\s+have\s+to"
    r"|can\s+i\s+(?:marry|divorce|pray|fast|break\s+my\s+fast|eat|drink|combine|skip)|\bi\s+(?:divorced|swore|vowed)\b"
    r"|my\s+(?:husband|wife)\s+(?:said|did|divorced)|yes,?\s+you\s+(?:can|may|are\s+allowed)|it\s+is\s+(?:permissible|haram|halal|forbidden)\s+for\s+you"
    r"|your\s+(?:divorce|fast|prayer|marriage|oath|vow)\s+is\s+(?:valid|invalid|not\s+valid|void)",
    re.I,
)
# A question about a ruling in general («هل يجوز الجمع للمسافر؟», «ما حكم ...»): answered with the two scholars'
# published fatwas, verbatim, like a personal question; the tool itself never rules.
GENERAL_FATWA = re.compile(
    r"(?:^|[.؟?!\n]\s*)(?:هل\s+(?:يجوز|تجوز|يصح|تصح|يحل|تحل|يحرم|تحرم|يلزم|تلزم|يجب|تجب|يشرع|يُشرع|يستحب|يسن|يباح|يكفي|يقع|يبطل|تبطل|يفسد|يفطر|يُفطر|ينقض|تنقض|يأثم|يؤجر)"
    r"|ما\s+(?:حكم|الحكم\s+في|هو\s+حكم|كفارة|فدية|الواجب\s+على|شروط|أركان|مبطلات|نواقض)|حكم\s+[ء-ي]+[^.؟?]*[؟?]"
    r"|كيف\s+(?:أصلي|اصلي|يصلي|تصلي|أتوضأ|اتوضأ|يتوضأ|أقضي|اقضي|يقضي|أغتسل|اغتسل)"
    r"|is\s+it\s+(?:halal|haram|permissible|allowed|sunnah|obligatory)|what\s+is\s+the\s+(?:islamic\s+)?ruling)",
    re.I,
)
_ANSWER_FORM = re.compile(r"لك|عليك|طلاقك|صيامك|صلاتك|زواجك|حجك|نذرك|يمينك|you|your", re.I)


def _strip_harakat(text: str) -> str:
    return re.sub("[ً-ٰٟـ]", "", text)


def _similarity(quote: str, source: str) -> float:
    a, b = skeleton_ar(quote), skeleton_ar(source)
    if not a or not b:
        return 0.0
    return float(fuzz.partial_ratio(a, b))


def _same_word(a: str, b: str) -> bool:
    """Skeleton words, tolerant of spelling and of a joined و ف ب ل ك («خير» / «وخير»)."""
    if a == b or (min(len(a), len(b)) >= 4 and fuzz.ratio(a, b) >= 80):
        return True
    return (len(b) > 2 and b[0] in "وفبلك" and b[1:] == a) or (len(a) > 2 and a[0] in "وفبلك" and a[1:] == b)


# Prepositions that narrations swap freely («في الصين» / «بالصين»); never a negation such as «لا».
_PARTICLES = {skeleton_ar(w) for w in "في من على عن إلى الى ثم قد".split()}


def _coverage(quote: str, source: str) -> tuple[float, list[str], int]:
    """Share of the quote's words found in order in the narration (spelling-tolerant), the quote's words that
    were not found (as written), and the narration's length in words."""
    q_raw = [w for w in _strip_harakat(quote).split() if skeleton_ar(w)]
    content = [w for w in q_raw if skeleton_ar(w) not in _PARTICLES]
    q_raw = content or q_raw
    q = [skeleton_ar(w) for w in q_raw]
    s = [x for x in (skeleton_ar(w) for w in source.split()) if x][:1500]
    if not q:
        return 0.0, [], len(s)
    # Longest common subsequence of words, keeping which quote words took part.
    prev = [0] * (len(s) + 1)
    rows = []
    for a in q:
        cur = [0] * (len(s) + 1)
        for j, b in enumerate(s, 1):
            cur[j] = prev[j - 1] + 1 if _same_word(a, b) else max(prev[j], cur[j - 1])
        rows.append(cur)
        prev = cur
    used, i, j = set(), len(q), len(s)
    while i > 0 and j > 0:
        if _same_word(q[i - 1], s[j - 1]) and rows[i - 1][j] == (rows[i - 2][j - 1] if i > 1 else 0) + 1:
            used.add(i - 1)
            i, j = i - 1, j - 1
        elif (rows[i - 2][j] if i > 1 else 0) >= rows[i - 1][j - 1]:
            i -= 1
        else:
            j -= 1
    missing = [w for k, w in enumerate(q_raw) if k not in used]
    return len(used) / len(q), missing, len(s)


def _match_kind(quote: str, text: str) -> dict:
    cov, missing, s_len = _coverage(quote, text)
    q_len = len([w for w in _strip_harakat(quote).split() if skeleton_ar(w) and skeleton_ar(w) not in _PARTICLES]) or 1
    need = SHORT_MIN_COVERAGE if q_len <= SHORT_QUOTE else MIN_COVERAGE
    if cov + 1e-9 < need:
        kind = "partial"
    elif _longer(q_len, s_len):
        kind = "longer"
    else:
        kind = "same"
    return {"match": kind, "coverage": round(100 * cov), "missing_words": missing if kind == "partial" else [],
            "source_words": s_len}


def _dorar_queries(quote: str) -> list[tuple[str, str]]:
    words = _strip_harakat(quote).split()
    out = []
    if len(words) <= 12:
        out.append((" ".join(words), "w"))
    if len(words) > 8:
        out.append((" ".join(words[:8]), "w"))
    if len(words) >= 4:
        out.append((" ".join(words[:4]), "p"))
    seen, uniq = set(), []
    for q in out:
        if q not in seen:
            seen.add(q)
            uniq.append(q)
    return uniq[:3]


async def _search_dorar(quote: str) -> DorarResult | None:
    if not settings.dorar_enabled:
        return None
    client = get_dorar()
    last = None
    for query, method in _dorar_queries(quote):
        last = await client.search(query, method)
        if last.hadiths:
            return last
    return last


SAHIHAYN = ("صحيح البخاري", "صحيح مسلم")


def _grade_groups(quote: str, res: DorarResult, min_sim: float = WEAK_MATCH) -> dict:
    items, hidden, seen = [], 0, set()
    for h in res.hadiths:
        scholar = find_scholar(h.mohdith, h.mohdith_id)
        if not scholar:
            continue
        if not is_hadith_level_grading(scholar, h.grade):
            hidden += 1
            continue
        sim = _similarity(quote, h.text)
        if sim < min_sim:
            continue
        key = (scholar.key, normalize_ar(h.book), h.number)
        if key in seen:
            continue
        seen.add(key)
        items.append({
            "scholar_key": scholar.key, "scholar_ar": scholar.name_ar, "scholar_en": scholar.name_en,
            "died_ah": scholar.died_ah, "group": scholar.group, "grade": h.grade, "book": h.book,
            "number": h.number, "rawi": h.rawi, "text": h.text, "url": h.url,
            "similarity": round(sim, 1), "flags": grade_flags(h.grade),
            "grade_gloss": gloss_grade(h.grade), "book_en": gloss_book(h.book),
            **_match_kind(quote, h.text),
        })
    order = {"same": 0, "longer": 1, "partial": 2}
    groups = []
    for g in (IMAMS, EDITORS):
        g_items = sorted((i for i in items if i["group"] == g), key=lambda i: (i["died_ah"], order[i["match"]], -i["similarity"]))
        if g_items:
            groups.append({"group": g, "label_ar": GROUP_LABELS[g]["ar"], "label_en": GROUP_LABELS[g]["en"], "items": g_items})
    def strong(i):
        return i["similarity"] >= STRONG_MATCH and i["match"] != "partial"

    # «موضوع» marks the quote only when it was said of this wording, not of a longer narration containing it.
    flagged_scholars = sorted({(i["died_ah"], i["scholar_ar"], i["scholar_en"]) for i in items
                               if "fabricated" in i["flags"] and strong(i) and i["match"] == "same"})
    flagged = [ar for _, ar, _ in flagged_scholars]
    best = max((i["similarity"] for i in items), default=0.0)
    best_strong = max((i["similarity"] for i in items if strong(i)), default=0.0)
    # The package puts the two Sahihs first. Decided by the source book, not the scholar's name: al-Bukhari
    # and Muslim narrate in other books too, and those are not all authentic. Dorar FAQ 13 (dorar.net/feedback):
    # «عليك التأكد من المصدر هل هو في صحيح البخاري أم لا، فالأحاديث التي رواها البخاري في غير صحيحه ليست كلها صحيحة».
    sahihayn = []
    for book in SAHIHAYN:
        # A longer narration in a Sahih still counts: the quoted words are in it as quoted.
        hits = [i for i in items if normalize_ar(i["book"]) == normalize_ar(book) and strong(i)]
        if hits:
            best_hit = max(hits, key=lambda i: i["similarity"])
            sahihayn.append({"book": book, "book_en": gloss_book(book), "number": best_hit["number"], "url": best_hit["url"]})
    return {
        "query": res.query, "search_url": res.search_url, "groups": groups, "best_similarity": best,
        "best_strong_similarity": best_strong,
        "same_wording": sum(1 for i in items if strong(i) and i["match"] == "same"),
        "longer_only": bool(items) and not any(strong(i) and i["match"] == "same" for i in items) and any(strong(i) for i in items),
        "fabricated_by": flagged, "fabricated_by_en": [en for _, _, en in flagged_scholars], "hidden_narrator_statements": hidden, "error": res.error or None,
        "count": len(items), "sahihayn": sahihayn, "verdicts": _verdicts(items),
    }


_SPECIALIST = {
    "hadith": ("مختص في الحديث", "a hadith specialist"),
    "quran": ("مختص في علوم القرآن", "a specialist in Quranic studies"),
}


def _referral(reason_ar: str, reason_en: str, field: str = "hadith") -> dict:
    ar, en = _SPECIALIST[field]
    return {"ar": f"{reason_ar} يُحال إلى {ar} للتحقق.", "en": f"{reason_en} Please refer to {en}."}


_LANG_NAME = {"ur": ("بالأردية", "in Urdu"), "id": ("بالإندونيسية", "in Indonesian"), "fr": ("بالفرنسية", "in French")}


async def check_hadith(c: Candidate, out: dict) -> None:
    quote = c.quote
    if c.lang in _LANG_NAME:
        # Plan item 36: no approved Urdu or Indonesian hadith translation to match against, and the model
        # does not cover these languages, so the hadith is referred rather than guessed.
        ar, en = _LANG_NAME[c.lang]
        out["status"] = "language_referral"
        out["referral"] = _referral(
            f"النص {ar}، وليس لدينا مصدر معتمد لترجمة الحديث {ar} نطابقه عليه، فلم نبحث عن أصله آليًا.",
            f"The text is {en}; there is no approved {en.split()[-1]} hadith translation to match it against, so its source was not searched automatically.",
        )
        return
    if c.lang != "ar":
        if not llm.available():
            out["status"] = "needs_model"
            out["referral"] = _referral(
                "النص بغير العربية ويحتاج إلى النموذج اللغوي للبحث عن أصله، وهو غير مفعّل الآن.",
                "This quote is not in Arabic and needs the language model to find its source, which is off right now.",
            )
            return
        try:
            wordings = await llm.arabic_search_wordings(quote, "hadith")
        except Exception as e:  # noqa: BLE001 - the model not answering is a referral, not an error
            log.warning("model did not answer: %s", e)
            out["status"] = "needs_model"
            out["referral"] = _referral(
                "النص بغير العربية ويحتاج إلى النموذج اللغوي للبحث عن أصله، ولم يستجب النموذج الآن.",
                "This quote is not in Arabic and needs the language model to find its source, which did not answer just now.",
            )
            return
        arabic = wordings[0] if wordings else ""
        out["search_wording_ar"] = arabic
        out["search_wordings_ar"] = wordings
        out["notes"].append("search_wording_by_model")
        quote = arabic
        if not arabic:
            out["status"] = "not_found"
            out["referral"] = _referral("لم نتمكن من البحث عن أصل هذا النص.", "We could not search for this text.")
            return

    q = get_quran().match_arabic(quote) if c.lang == "ar" else None
    if q and q.status == "exact":
        out["notes"].append("hadith_is_quran")
        out["quran"] = q.to_dict()

    res = await _search_dorar(quote)
    per_wording = [res] if res is not None else []
    if c.lang != "ar" and res is not None:
        # Each other wording the model proposed is searched too; the source is then picked among all of them.
        for w in out.get("search_wordings_ar", [])[1:]:
            more = await _search_dorar(w)
            if more is not None and more.hadiths:
                per_wording.append(more)
                seen = {(h.text, h.mohdith, h.book, h.number) for h in res.hadiths}
                res.hadiths += [h for h in more.hadiths if (h.text, h.mohdith, h.book, h.number) not in seen]
    if res is None:
        out["status"] = "source_offline"
        return
    if not res.hadiths and res.error:
        out["status"] = "source_error"
        out["hadith"] = {"query": res.query, "search_url": res.search_url, "error": res.error, "groups": []}
        out["referral"] = _referral("تعذّر الوصول إلى الموسوعة الحديثية الآن.", "The hadith encyclopedia could not be reached.")
        return

    if c.lang != "ar":
        # The model picks which Arabic text is the source of the translated quote; we then keep the
        # gradings of that text only. The user always sees the Arabic text to judge for themselves.
        texts = []
        lists = [[h.text for h in r.hadiths if find_scholar(h.mohdith, h.mohdith_id)] for r in per_wording] or [[]]
        for i in range(max(len(x) for x in lists)):  # take from each wording's results in turn
            for x in lists:
                if i < len(x) and x[i] not in texts and len(texts) < 4:
                    texts.append(x[i])
        try:
            pick = await llm.pick_match(c.quote, texts) if texts else 0
        except Exception as e:  # noqa: BLE001 - no pick means nothing is shown, and the quote is referred
            log.warning("model did not answer: %s", e)
            pick = 0
        if pick == 0:
            out["status"] = "not_found"
            out["hadith"] = _grade_groups(quote, res, min_sim=101)  # nothing shown
            out["referral"] = _referral("لم نجد أصلًا عربيًا مطابقًا لهذا النص المترجم.", "No matching Arabic source was found for this translated text.")
            return
        quote = texts[pick - 1]
        # Plan item 22: the model's pick must share the wording it proposed itself, or it is not accepted.
        if max(_similarity(w, quote) for w in out.get("search_wordings_ar") or [arabic]) < WEAK_MATCH:
            out["status"] = "not_found"
            out["notes"].append("model_pick_rejected")
            out["hadith"] = _grade_groups(quote, res, min_sim=101)
            out["referral"] = _referral("لم نجد أصلًا عربيًا مطابقًا لهذا النص المترجم.", "No matching Arabic source was found for this translated text.")
            return
        out["matched_arabic"] = quote
        out["notes"].append("match_by_model")

    info = _grade_groups(quote, res)
    out["hadith"] = info
    if info["count"] and info["best_strong_similarity"] >= STRONG_MATCH:
        out["status"] = "graded"
    elif info["count"]:
        out["status"] = "found_similar"
        out["notes"].append("wording_differs")
    else:
        out["status"] = "not_found"
        out["referral"] = _referral(
            "لم نجد حكمًا لأحد علماء الحديث المعتمدين على هذا النص.",
            "We found no grading of this text by the approved hadith scholars.",
        )


async def check_quran(c: Candidate, out: dict) -> None:
    Q = get_quran()
    prefer = (c.ref_surah, c.ref_ayah) if c.ref_surah else None
    marked = c.marker not in ("unmarked", "model", "bare")  # the author presented it as Quran
    if c.lang == "ar":
        m: QuranMatch = Q.match_arabic(c.quote, prefer, marked)
    elif c.lang in Q.translations:
        m = Q.match_translation(c.quote, c.lang, prefer)
    else:
        m = Q.match_english(c.quote, prefer)
    if m.status == "not_found" and c.lang == "en" and llm.available():
        try:
            arabic = await llm.arabic_search_wording(c.quote, "quran")
        except Exception as e:  # noqa: BLE001 - without the model the quote stays "not found", as with the model off
            log.warning("model did not answer: %s", e)
            arabic = ""
        out["search_wording_ar"] = arabic
        if arabic:
            m2 = Q.match_arabic(arabic)
            if m2.status != "not_found":
                m = m2
                m.via = "english_llm"
                m.status = "differs"
                m.diff = []
                out["notes"].append("match_by_model")
    if c.ref_surah:
        Q.check_reference(m, c.ref_surah, c.ref_ayah, c.ref_label)
    out["quran"] = m.to_dict()
    if m.surah is not None:  # the verse in each approved translation, for readers of Urdu and Indonesian
        out["quran"]["translations"] = Q.translations_for(m.surah, m.ayah_from, m.ayah_to)
    if m.status == "exact":
        out["status"] = "verified"
    elif m.status == "differs":
        out["status"] = "differs"
    elif m.status == "too_short":
        # Plan item 3: a few letters cannot be told apart from a slip automatically; say so, never "not found".
        out["status"] = "too_short"
        out["referral"] = _referral("النص أقصر من أن نتحقق منه آليًا.", "The text is too short to check automatically.", "quran")
    else:
        out["status"] = "not_in_mushaf"
        if c.lang == "ar":
            # Often a hadith or a saying circulated as if it were an ayah.
            res = await _search_dorar(c.quote)
            if res and res.hadiths:
                # Only a strong match is shown under a quote that is not in the Mushaf: a distant hadith's
                # grading would read as a grading of what the user wrote.
                info = _grade_groups(c.quote, res, min_sim=STRONG_MATCH)
                if info["count"]:
                    out["hadith"] = info
                    out["notes"].append("quran_claim_found_in_hadith")
        found_as_hadith = "quran_claim_found_in_hadith" in out["notes"]
        if c.lang == "ar":
            why = ("لم نجد هذا النص في المصحف.", "This text was not found in the Mushaf.")
        elif c.lang in _LANG_NAME:
            why = (f"لم نجد آية تقابل هذا النص في ترجمة المجمع المعتمدة {_LANG_NAME[c.lang][0]}.",
                   f"We could not match this to any verse of the approved translation {_LANG_NAME[c.lang][1]}.")
        else:
            why = ("لم نجد آية تقابل هذه الترجمة.", "We could not match this to any verse.")
        out["referral"] = _referral(*why, "hadith" if found_as_hadith else "quran")
    if m.reference_ok is False:
        out["notes"].append("wrong_reference")


async def _model_candidates(text: str, existing: list[Candidate]) -> tuple[list[Candidate], int]:
    """Ask the model for citations the rules missed. Anything not found verbatim in the text is dropped."""
    try:
        items = await llm.extract_citations(text[:3000])
    except Exception as e:  # noqa: BLE001 - model trouble must never break the check
        log.warning("model extraction failed: %s", e)
        return [], 0
    text_sk = skeleton_ar(text)
    have = [skeleton_ar(c.quote) or c.quote.lower() for c in existing]
    out, dropped = [], 0
    for it in items:
        quote = it["quote"]
        sk = skeleton_ar(quote)
        ar = bool(sk)
        present = (sk in text_sk) if ar else (quote.lower() in text.lower())
        if not present or len(quote) < 6:
            dropped += 1
            continue
        key = sk or quote.lower()
        if any(key in h or h in key for h in have):
            continue
        pos = text.find(quote)
        out.append(Candidate(it["type"], quote, max(pos, 0), max(pos, 0) + len(quote), "ar" if ar else "en", "model", found_by="model"))
        have.append(key)
    return out, dropped


# A text that is only a quote, or a question about one («هل حديث ... صحيح؟», "Is the hadith ... authentic?"):
# people paste a saying alone to ask about it, with no «قال ﷺ» before it.
_BARE_HEAD_AR = re.compile(
    r"^\s*(?P<ask>هل|ما\s+(?:مدى\s+)?(?:صحة|درجة|حكم|حال|مصدر|أصل)|كم\s+درجة|أريد\s+(?:التحقق\s+من|معرفة\s+صحة))?\s*"
    r"(?P<kw>(?:ال)?(?:حديث|أثر|مقولة|عبارة)(?:\s+(?:النبي|الرسول)\s*(?:ﷺ|صلى الله عليه وسلم)?)?)?\s*[:：]?\s*")
_BARE_TAIL_AR = re.compile(
    r"\s*(?:(?:هل\s+)?(?:هو|هذا)\s+)?(?:(?:حديث|الحديث)\s+)?(?:صحيح|ضعيف|موضوع|ثابت|صحيح\s+أم\s+(?:لا|ضعيف|موضوع))?\s*[؟?!.]*\s*$")
_BARE_HEAD_EN = re.compile(
    r"^\s*(?P<ask>is\s+(?:the|this)|is\s+it\s+(?:true|authentic)\s+that|check)?\s*(?P<kw>(?:the\s+)?(?:hadith|narration|saying))?\s*[:,]?\s*", re.I)
_BARE_TAIL_EN = re.compile(r"\s*(?:(?:a\s+)?(?:authentic|sahih|true|real|weak|fabricated)(?:\s+hadith)?)?\s*[?!.]*\s*$", re.I)


def _bare_candidate(text: str) -> Candidate | None:
    t = text.strip()
    if not t or len(t) > 400 or "\n\n" in t or PERSONAL_FATWA.search(t) or GENERAL_FATWA.search(t):
        return None
    ar = bool(re.search("[ء-ي]", t))
    head, tail = (_BARE_HEAD_AR, _BARE_TAIL_AR) if ar else (_BARE_HEAD_EN, _BARE_TAIL_EN)
    m = head.match(t)
    core = t[m.end():] if m else t
    core = tail.sub("", core).strip()
    quoted = re.fullmatch(r"[«\"“'](.+?)[»\"”']", core)
    core = (quoted.group(1) if quoted else core).strip(" :،,")
    asked, kw = bool(m and m.group("ask")), bool(m and m.group("kw"))
    words = core.split()
    if not 2 <= len(words) <= 40 or re.search(r"[.!؟?]\s+\S", core):
        return None
    if asked and not kw and not quoted:
        return None  # «هل يجوز ...؟» is a question, not a quote
    lang = quote_lang(core)
    if lang not in ("ar", "en"):
        return None
    Q = get_quran()
    q = Q.match_arabic(core) if lang == "ar" else Q.match_english(core)
    kind = "quran" if q.status == "exact" or (q.status == "differs" and q.score >= 85 and not kw) else "hadith"
    start = text.find(core)
    return Candidate(kind, core, max(start, 0), max(start, 0) + len(core), lang, "bare", asked=kw or bool(quoted))


_VERDICT_BUCKETS = (("accepted", ("authentic", "good")), ("weak", ("weak", "very_weak")), ("fabricated", ("fabricated",)))


def _verdicts(items: list) -> list:
    """Who graded this very wording how, grouped as the scholars' own words fall (accepted, weak, fabricated).
    It reports the gradings side by side; it never weighs one scholar against another or adds a grading."""
    out = []
    for key, cats in _VERDICT_BUCKETS:
        names = []
        for i in sorted(items, key=lambda i: i["died_ah"]):
            cat = (i.get("grade_gloss") or {}).get("category")
            if key == "fabricated":
                hit = "fabricated" in i["flags"] or cat in cats
            else:
                hit = cat in cats and "fabricated" not in i["flags"]
            if hit and i["similarity"] >= STRONG_MATCH and i.get("match", "same") == "same":
                pair = (i["scholar_ar"], i["scholar_en"])
                if pair not in names:
                    names.append(pair)
        if names:
            out.append({"verdict": key, "scholars_ar": [a for a, _ in names], "scholars_en": [e for _, e in names]})
    return out


async def check_text(text: str, deep: bool = False) -> dict:
    t0 = time.monotonic()
    usage = {"calls": 0, "seconds": 0.0}
    llm.USAGE.set(usage)
    # Plan item 18: nothing is cut silently; the report says how much was checked.
    truncated = {"text_chars": len(text), "checked_chars": min(len(text), settings.max_text_chars)}
    text = text[: settings.max_text_chars]
    cands = extract(text)
    dropped = 0
    if deep and llm.available():
        extra, dropped = await _model_candidates(text, cands)
        cands = sorted(cands + extra, key=lambda c: c.start)
    if not cands:
        bare = _bare_candidate(text)
        cands = [bare] if bare else []
    truncated.update(citations_found=len(cands), citations_checked=min(len(cands), settings.max_citations))
    cands = cands[: settings.max_citations]

    results = []
    for i, c in enumerate(cands, 1):
        out = {
            "id": i, "type": c.type, "quote": c.quote, "lang": c.lang, "found_by": c.found_by,
            "marker": c.marker, "status": "", "quran": None, "hadith": None, "referral": None, "notes": [],
        }
        try:
            if c.type == "quran":
                await check_quran(c, out)
            else:
                await check_hadith(c, out)
        except Exception as e:  # noqa: BLE001
            log.exception("check failed")
            out["status"] = "error"
            out["error"] = type(e).__name__
            out["referral"] = _referral("حدث خطأ أثناء التحقق.", "An error occurred while checking.")
        if c.type == "hadith":
            out["cautious"] = c.cautious
            out["attribution"] = _compare_attribution(c.attribution, out)
        out["tier"] = evidence_tier(out)
        if out["tier"] == "not_supported" and c.type == "hadith" and not c.cautious and c.found_by == "rules":
            out["notes"].append("firm_form")  # «قال رسول الله ﷺ» for what the sources do not support
        results.append(out)

    # Plain text pasted alone (no «حديث», no quotation marks) is reported only if the sources know it: a sentence
    # of one's own is not "a hadith not found".
    keep = [i for i, (o, c) in enumerate(zip(results, cands))
            if not (c.marker == "bare" and not c.asked and c.lang == "ar" and o["status"] in ("not_found", "not_in_mushaf", "too_short", "source_offline", "source_error"))]
    if len(keep) != len(results):
        results = [results[i] for i in keep]
        cands = [cands[i] for i in keep]
    level_d = None
    m = PERSONAL_FATWA.search(text)
    form = ("ruling_in_answer" if _ANSWER_FORM.search(m.group(0)) else "question") if m else None
    if not m and not [c for c in cands if c.marker != "bare"]:
        m = GENERAL_FATWA.search(text)  # a question about a ruling, not a text with citations in it
        form = "general" if m else None
    if m:
        level_d = {"detected": True, "body": FATWA_BODY, "references": FATWA_REFERENCES, "fatwas": None,
                   "form": form, "matched": m.group(0).strip()}
        if settings.fatwa_search:
            try:
                where = m.start()
                if level_d["form"] == "ruling_in_answer":  # search with the question the answer replies to, if quoted
                    q_end = text.rfind("؟", 0, where)
                    q_end = q_end if q_end >= 0 else text.rfind("?", 0, where)
                    where = q_end if q_end >= 0 else where
                level_d["fatwas"] = await asyncio.wait_for(fatwa.find_fatwas(_sentence_at(text, where)), 25)
            except Exception as e:  # noqa: BLE001 - the referral itself must always be shown
                log.warning("fatwa search failed: %s", e)
    # Positions in the text as received (plan item 24), so an API user can place each note.
    for out, c in zip(results, cands):
        out["span"] = [c.start, c.end]  # marker and quote («قال رسول الله ﷺ: «...»»)
        q = text.find(c.quote, c.start, c.end + 2)
        out["quote_span"] = [q, q + len(c.quote)] if q >= 0 else [c.start, c.end]  # the quoted words alone
    result = {
        "citations": results,
        "truncated": truncated if (truncated["text_chars"] > truncated["checked_chars"]
                                   or truncated["citations_found"] > truncated["citations_checked"]) else None,
        "unsupported_language": unsupported_language(text),
        "level_d": level_d,
        "summary": _summary(results),
        "display_rules": {k: DISPLAY_RULES[k] for k in ("status", "reviewed_by", "reviewed_on")},
        "model": {"backend": llm.backend.name, "available": llm.available(), "requested": deep,
                  "used": bool(usage.get("models")), "calls": usage["calls"], "seconds": round(usage["seconds"], 1),
                  "answered_by": usage.get("models", []), "configured": llm.describe(),
                  "dropped_unverifiable": dropped},
        "elapsed_ms": int((time.monotonic() - t0) * 1000),
    }
    result["coverage"] = _coverage_report(result, truncated, deep)
    result["decision"] = chatbot_decision(result)
    result["disclaimer"] = DISCLAIMER
    result["versions"] = {"app": VERSION["commit"], "display_rules": DISPLAY_RULES["status"],
                          "chatbot_policy": POLICY["version"],
                          "model": "+".join(usage.get("models", [])) or llm.backend.name}
    return result


DISCLAIMER = {
    "ar": "تثبّت أداة آلية مدعومة بالذكاء الاصطناعي وليست عالمًا ولا مفتيًا. تحققت من الاستشهادات وحدها، لا من صحة الشرح أو الاستدلال.",
    "en": "Tathabbut is an automated, AI-assisted tool, not a scholar or a mufti. It checked the citations only, not the explanation or the reasoning.",
    "ur": "تثبّت مصنوعی ذہانت سے مدد یافتہ ایک خودکار آلہ ہے، نہ عالم ہے نہ مفتی۔ اس نے صرف حوالے جانچے ہیں، شرح یا استدلال نہیں۔",
    "id": "Tathabbut adalah alat otomatis berbantuan AI, bukan ulama dan bukan mufti. Alat ini hanya memeriksa kutipan, bukan penjelasan atau penalarannya.",
}
POLICY = json.loads((Path(__file__).resolve().parent.parent / "data" / "chatbot_policy.json").read_text(encoding="utf-8"))
_UNCHECKED = {"source_error", "source_offline", "needs_model", "language_referral", "error"}


def _coverage_report(result: dict, truncated: dict, deep: bool) -> dict:
    """What was and was not checked: an answer is "complete" only if nothing was cut or left unchecked."""
    unchecked = [c["id"] for c in result["citations"] if c["status"] in _UNCHECKED]
    gaps = []
    if truncated["text_chars"] > truncated["checked_chars"]:
        gaps.append("text_truncated")
    if truncated["citations_found"] > truncated["citations_checked"]:
        gaps.append("citations_truncated")
    if unchecked:
        gaps.append("citations_unchecked")
    if result["unsupported_language"]:
        gaps.append("unsupported_language")
    if not deep or not result["model"]["used"]:
        gaps.append("rules_only")  # citations written without any marker may be missed; informative, not a gap in itself
    return {**truncated, "unchecked_citations": unchecked, "gaps": gaps,
            "complete": not [g for g in gaps if g != "rules_only"]}


def chatbot_decision(result: dict, policy: dict | None = None) -> dict:
    """pass / annotate / block for a chatbot answer, from data/chatbot_policy.json (plan item 24)."""
    p = policy or POLICY
    reasons, action = [], "pass"
    for c in result["citations"]:
        b = p["block"]
        if (c["tier"] in b["tiers"] or (c["type"] == "quran" and c["status"] in b["quran_statuses"])
                or (c["type"] == "hadith" and c["status"] in b["hadith_statuses"])):
            reasons.append({"citation": c["id"], "action": "block", "tier": c["tier"], "status": c["status"]})
        elif c["tier"] in p["annotate"]["tiers"]:
            reasons.append({"citation": c["id"], "action": "annotate", "tier": c["tier"], "status": c["status"]})
    if result.get("level_d") and p["annotate"].get("fatwa_question"):
        reasons.append({"citation": None, "action": "annotate", "rule": "fatwa_question"})
    if p.get("never_pass_when_unchecked") and not result["coverage"]["complete"]:
        reasons.append({"citation": None, "action": "annotate", "rule": "not_fully_checked", "gaps": result["coverage"]["gaps"]})
    acts = {r["action"] for r in reasons}
    action = "block" if "block" in acts else ("annotate" if acts else "pass")
    return {"action": action, "reasons": reasons, "policy": {"name": p["name"], "version": p["version"]},
            "rewrites_answer": False}



_BOOK_KEY = {"صحيح البخاري": "bukhari", "صحيح مسلم": "muslim"}


def _compare_attribution(written: dict | None, out: dict) -> dict | None:
    """Plan item 19: a written «رواه البخاري» / «متفق عليه» against the Sahihayn line of Dorar's results.
    Said as what the search found, never as «ليس في البخاري»."""
    if not written:
        return None
    hd = out.get("hadith") or {}
    if out["status"] in _UNCHECKED or not hd:
        return {**written, "checked": False, "confirmed": [], "not_found_in": []}
    found = {_BOOK_KEY[x["book"]] for x in hd.get("sahihayn", []) if x["book"] in _BOOK_KEY}
    return {**written, "checked": True, "confirmed": [b for b in written["books"] if b in found],
            "not_found_in": [b for b in written["books"] if b not in found]}


def _hadith_tier(r: dict) -> str:
    tier = _hadith_tier_from_gradings(r)
    if tier == "supported" and (r.get("attribution") or {}).get("not_found_in"):
        return "verify"  # the written attribution did not match what the search found
    return tier


def _hadith_tier_from_gradings(r: dict) -> str:
    """Apply data/display_rules.json (written and signed by the Sharia reviewer) to the gradings found.
    Only the gradings of the matching text count; the tool never prefers one scholar over another."""
    rules = DISPLAY_RULES
    hd = r.get("hadith") or {}
    if r["status"] != "graded" or {"wrong_reference", "match_by_model"} & set(r["notes"]):
        return "verify"
    in_sahihayn = rules["sahihayn_is_supported"] and hd.get("sahihayn")
    if in_sahihayn and hd.get("fabricated_by"):
        return "verify"  # never settled by the tool: the scholars' words are shown side by side
    if in_sahihayn:
        return "supported"
    if hd.get("fabricated_by"):
        return "not_supported"
    # Only gradings of this wording decide; a grading of a longer narration is shown, not counted.
    items = [i for g in hd.get("groups", []) for i in g["items"]
             if i["similarity"] >= STRONG_MATCH and (i.get("match", "same") == "same"
                                                     or (i.get("match") == "longer" and _COV.get("longer_narration_counts")))]
    cats = set()
    for i in items:
        gl = i.get("grade_gloss") or {}
        cat = gl.get("category")
        if cat in rules["accepted_categories"] and gl.get("chain_only") and not rules["chain_only_counts_as_accepted"]:
            cat = "chain_only"
        cats.add(cat)
    if cats and cats <= set(rules["accepted_categories"]):
        return "supported"
    if cats and cats <= set(rules["not_supported_categories"]):
        return "not_supported"
    return "verify"


# Plan item 8: v1 checks Arabic and English; plan item 36 adds Urdu, Indonesian and French Quran quotes. Text in another language is said to be unchecked,
# never reported as "no citation found".
_URDU_PERSIAN = re.compile("[ٹڈڑںےۓھہپچژگ]")
_EN = re.compile(r"\b(?:the|and|of|to|is|in|that|he|said|allah|prophet|you|we|they|this|for|with)\b", re.I)
_OTHER_LATIN = {
    "fr": re.compile(r"\b(?:le|la|les|des|est|et|une|dans|que|qui|pour|sur|il|nous|vous|du|au)\b", re.I),
    "id": re.compile(r"\b(?:dan|yang|ini|itu|dengan|untuk|dari|tidak|kita|kami|adalah|akan|bahwa|ia)\b", re.I),
    "tr": re.compile(r"\b(?:ve|bir|bu|için|ile|olan|çok|da|de|gibi|ama|ki)\b", re.I),
}


def unsupported_language(text: str) -> str | None:
    arabic_script = len(re.findall("[؀-ۿ]", text))
    if arabic_script and len(_URDU_PERSIAN.findall(text)) >= max(3, arabic_script // 100):
        return None if re.search("[ٹڈڑںےۓ]", text) else "fa"
    words = re.findall(r"[A-Za-zÀ-ÿçğışöü]+", text)
    if len(words) >= 6:
        en = len(_EN.findall(text))
        lang, n = max(((k, len(rx.findall(text))) for k, rx in _OTHER_LATIN.items()), key=lambda x: x[1])
        if n >= 3 and n > 2 * en:
            return None if lang in ("id", "fr") else lang
    return None


def _sentence_at(text: str, pos: int) -> str:
    """The sentence holding the fatwa question: only its topic words are sent to the two scholars' sites."""
    start = max(text.rfind(ch, 0, pos) for ch in ".!؟?\n") + 1
    ends = [i for i in (text.find(ch, pos) for ch in ".!؟?\n") if i != -1]
    return text[start : min(ends) if ends else len(text)].strip()


def evidence_tier(r: dict) -> str:
    """The track's success criterion asks to tell apart what the sources support, what needs more
    verification, and what must be referred. A Quran quote matching the Mushaf is "documented"; a hadith
    is "supported" or "not_supported" only by the reviewer's rules; anything else is "verify" or "refer"."""
    if r["referral"]:
        return "refer"
    if r["type"] == "hadith":
        return _hadith_tier(r)
    if r["status"] == "verified" and not {"wrong_reference", "match_by_model"} & set(r["notes"]):
        return "documented"
    return "verify"


def _summary(results: list[dict]) -> dict:
    """Counts only. "documented" means a Quran quote matches the Mushaf; hadith tiers follow the reviewer's rules."""
    s = {"total": len(results), "quran": 0, "hadith": 0, "documented": 0, "supported": 0, "not_supported": 0,
         "verify": 0, "refer": 0, "fabricated_flag": 0}
    for r in results:
        s[r["type"]] += 1
        s[r["tier"]] += 1
        if (r.get("hadith") or {}).get("fabricated_by"):
            s["fabricated_flag"] += 1
    return s


def run(text: str, deep: bool = False) -> dict:
    return asyncio.run(check_text(text, deep))
