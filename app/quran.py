"""Quran lookup against the Mushaf text (King Fahd Complex Uthmani script).

The Quran text is never generated: every result shows the Mushaf text loaded from data/quran.json.
"""
import bisect
import difflib
import hashlib
import json
import re
import unicodedata
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

from rapidfuzz import fuzz, process

from .normalize import ar_words, normalize_ar, normalize_en, normalize_fr, normalize_id, normalize_ur, skeleton_ar, word_skeleton
from .spelling import to_common_word

DATA = Path(__file__).resolve().parent.parent / "data" / "quran.json"

# Minimum skeleton length for a span to count as a Quran quote (avoids matching common short phrases).
MIN_SKELETON = 10
MIN_SKELETON_FUZZY = 12
# A quote the author marked as Quran (﴿﴾, «قال تعالى», a written reference) may be a whole short ayah
# (﴿والعصر﴾، ﴿الله الصمد﴾). It is matched word for word, never inside a word; below this it is too short to check.
MIN_SKELETON_MARKED = 3
_ORNAMENTS = re.compile("[۞۩]")


def _tokens(text: str) -> list[str]:
    return [t for t in (_ORNAMENTS.sub("", w) for w in text.split()) if t]


# Alef check (plan item 2). The skeleton drops every alef, so «قال» and ﴿قُلۡ﴾ meet. For words whose skeleton
# matches, a full alef (or hamza) typed where the Mushaf has none, not even a dagger alef, is a real difference.
_DIAC = re.compile("[ؐ-ًؚ-ٯٱ-ۭ]")
_ALEFISH = set("اأإآٱءٰٕٔ")


def alef_gaps(text: str) -> list[int]:
    """For each place between skeleton letters, how many alef/hamza signs are written there."""
    gaps = [0]
    t = unicodedata.normalize("NFC", text).replace("وٰ", "ا")
    for ch in t:
        if ch in _ALEFISH:
            gaps[-1] += 1
        elif ch in "ىئیي":
            gaps.append(0)
        elif ch == "ؤ":
            gaps.append(0)
        elif "ء" <= ch <= "ي" or ch in "کة":
            gaps.append(0)
        # other marks, tatweel and spaces carry no letter
    return gaps


def extra_alef(quoted: str, mushaf: str, common: str = "") -> bool:
    q = alef_gaps(quoted)
    best = None
    for ref in (mushaf, common):
        if not ref:
            continue
        r = alef_gaps(ref)
        if len(r) != len(q):
            continue
        best = r if best is None else [max(x, y) for x, y in zip(best, r)]
    if best is None:
        return False
    # The two edge gaps can hold the neighbouring word's alef in the Mushaf; only inner gaps are compared,
    # plus the first gap of the quote when it starts a word (an alef typed before the first letter).
    return any(a > b for a, b in zip(q[1:-1], best[1:-1])) or q[0] > best[0]


@dataclass
class Ayah:
    surah: int
    ayah: int
    text: str
    translation_en: str  # King Fahd Complex translation (al-Hilali & Muhsin Khan), shown to the reader
    skeleton: str
    norm_en: str
    norm_en_saheeh: str  # Saheeh International, used only to recognise English quotes


@dataclass
class QuranMatch:
    status: str  # exact | differs | not_found
    surah: int | None = None
    ayah_from: int | None = None
    ayah_to: int | None = None
    surah_name_ar: str = ""
    surah_name_en: str = ""
    mushaf_text: str = ""
    translation_en: str = ""
    score: float = 0.0
    ayat: list = field(default_factory=list)  # [{"ayah": n, "text": Mushaf text}] for display with ayah markers
    diff: list = field(default_factory=list)  # [{"op": "equal|replace|delete|insert", "quoted": str, "mushaf": str}]
    occurrences: int = 0
    via: str = ""  # arabic | english | english_llm
    matched_translation: str = ""  # which translation the quote matched (hilali | saheeh | ur_junagarhi | id_kfc | fr_hamidullah)
    translation: dict | None = None  # Urdu, Indonesian or French quotes: the approved translation's text, name and link
    reference_given: str = ""
    reference_ok: bool | None = None
    # What actually sits at the reference the author wrote, to explain a wrong reference.
    cited: dict | None = None

    def to_dict(self):
        return self.__dict__ | {"ref": self.ref, "url": self.url, "translation_url": self.translation_url}

    @property
    def ref(self):
        if self.surah is None:
            return ""
        if self.ayah_from == self.ayah_to:
            return f"{self.surah}:{self.ayah_from}"
        return f"{self.surah}:{self.ayah_from}-{self.ayah_to}"

    @property
    def url(self):
        if self.surah is None:
            return ""
        return f"https://quranpedia.net/ayahs/{self.surah}/{self.ayah_from}"

    @property
    def translation_url(self):
        """The King Fahd Complex English translation (book 1948) on quranpedia.net, with the translators' notes."""
        if self.surah is None:
            return ""
        return f"https://quranpedia.net/surah/1/{self.surah}/book/1948"


class Quran:
    def __init__(self, path: Path = DATA):
        data = json.loads(path.read_text(encoding="utf-8"))
        self.source = data["source"]
        self.surahs = {s["n"]: s for s in data["surahs"]}
        self.ayat = [
            Ayah(s, a, t, e, skeleton_ar(t), normalize_en(e), normalize_en(sah)) for s, a, t, e, sah, _notes in data["verses"]
        ]
        self.index = {(x.surah, x.ayah): i for i, x in enumerate(self.ayat)}
        # Whole-Quran skeleton with offsets, so a quote that spans several ayat is still an exact match.
        self.starts, parts, pos = [], [], 0
        for x in self.ayat:
            self.starts.append(pos)
            parts.append(x.skeleton)
            pos += len(x.skeleton)
        self.full = "".join(parts)
        self._sk = [x.skeleton for x in self.ayat]
        # Second index in common (imla'i) spelling (plan item 1): شيئا، إسرائيل، الليل، إبراهيم، ضحاها.
        # Built once from the Mushaf by app/spelling.py; used for matching only, never shown.
        self.tok, self.tok_sk, self.tok_common, self.tok_ayah = [], [], [], []
        common_ayah = []
        for i, x in enumerate(self.ayat):
            parts = []
            for w in _tokens(x.text):
                cw = to_common_word(w, harakat=False)[0]
                self.tok.append(w)
                self.tok_sk.append(skeleton_ar(w))
                self.tok_common.append(cw)
                self.tok_ayah.append(i)
                parts.append(cw)
            common_ayah.append(skeleton_ar(" ".join(parts)))
        self.common_starts, pos = [], 0
        for sk in common_ayah:
            self.common_starts.append(pos)
            pos += len(sk)
        self.full_common = "".join(common_ayah)
        # Offsets where a word starts, so a quote of whole words is preferred to one that starts inside a word.
        self.word_starts, self.common_word_starts, pos, cpos = set(), set(), 0, 0
        for w, c in zip(self.tok_sk, self.tok_common):
            self.word_starts.add(pos)
            pos += len(w)
            for part in c.split():
                self.common_word_starts.add(cpos)
                cpos += len(skeleton_ar(part))
        self.word_starts.add(pos)
        self.common_word_starts.add(cpos)
        self._by_first: dict[str, list[int]] = {}
        for k, (a, b) in enumerate(zip(self.tok_sk, self.tok_common)):
            for key in {a, skeleton_ar(b.split()[0]) if b else a}:
                self._by_first.setdefault(key, []).append(k)
        self._windows: dict[int, tuple[list, list]] = {}
        self._en = {"hilali": [x.norm_en for x in self.ayat], "saheeh": [x.norm_en_saheeh for x in self.ayat]}
        self.translations = self._load_translations(path.parent / "translations")
        self.display_translations = self._load_display(path.parent / "translations")
        names = {}
        for s in self.surahs.values():
            names[normalize_ar(s["ar"])] = s["n"]
            names[normalize_en(s["tr"])] = s["n"]
            names[normalize_en(s["en"])] = s["n"]
        self.surah_names = names

    # ---------- lookups ----------
    def _ayah_at(self, offset: int) -> int:
        return bisect.bisect_right(self.starts, offset) - 1

    def _build(self, i: int, j: int, status: str, quote: str, score: float, via: str, occurrences=1) -> QuranMatch:
        first, last = self.ayat[i], self.ayat[j]
        if first.surah != last.surah:  # keep results inside one surah
            j = i
            last = first
        span = self.ayat[i : j + 1]
        mushaf = " ".join(x.text for x in span)
        s = self.surahs[first.surah]
        m = QuranMatch(
            status=status, surah=first.surah, ayah_from=first.ayah, ayah_to=last.ayah,
            surah_name_ar=s["ar"], surah_name_en=s["tr"], mushaf_text=mushaf,
            translation_en=" ".join(x.translation_en for x in span), score=round(score, 1),
            occurrences=occurrences, via=via,
            ayat=[{"ayah": x.ayah, "text": x.text} for x in span],
        )
        if via == "arabic" and status == "differs":
            m.diff = word_diff(quote, mushaf)
        return m

    def match_arabic(self, quote: str, prefer: tuple[int, int] | None = None, marked: bool = False) -> QuranMatch:
        """prefer=(surah, ayah): when the phrase occurs in several places, pick the one the author cited.
        marked: the author presented the text as Quran (﴿﴾, «قال تعالى», a reference), so a short ayah is checked."""
        q = skeleton_ar(quote)
        if len(q) < MIN_SKELETON:
            if not marked or len(q) < MIN_SKELETON_MARKED:
                return QuranMatch(status="not_found", via="arabic")
            m = self._match_words(quote, prefer)
            if m:
                return m
            # One word cannot be told apart from a slip or another reading; two or more were searched word for word.
            return QuranMatch(status="too_short" if len(ar_words(quote)) < 2 else "not_found", via="arabic")
        for full, starts, bounds in ((self.full, self.starts, self.word_starts),
                                     (self.full_common, self.common_starts, self.common_word_starts)):
            positions, pos = [], full.find(q)
            while pos >= 0:
                positions.append(pos)
                pos = full.find(q, pos + 1)
            if positions:
                whole = [p for p in positions if p in bounds and p + len(q) in bounds]
                positions = whole + [p for p in positions if p not in whole]
                at = lambda p: bisect.bisect_right(starts, p) - 1  # noqa: E731
                spans = list(dict.fromkeys((at(p), at(p + len(q) - 1)) for p in positions))
                if prefer:
                    i, j = self._preferred(spans, prefer)
                    return self._exact(i, j, quote, len(positions))
                # Prefer a place where the words match as written (﴿إِنَّ مَعَ ٱلۡعُسۡرِ يُسۡرٗا﴾ 94:6 over «فَإِنَّ» 94:5).
                first = None
                for i, j in spans[:20]:
                    m = self._exact(i, j, quote, len(positions))
                    if m.status == "exact":
                        return m
                    first = first or m
                return first
        if len(q) < MIN_SKELETON_FUZZY:
            if marked:
                m = self._match_words(quote, prefer)
                if m:
                    return m
            return QuranMatch(status="not_found", via="arabic")
        return self._fuzzy_arabic(quote, q)

    def _preferred(self, spans, prefer):
        if prefer:
            for a, b in spans:
                if self.ayat[a].surah == prefer[0] and (prefer[1] is None or self.ayat[a].ayah <= prefer[1] <= self.ayat[b].ayah):
                    return a, b
        return spans[0]

    def _exact(self, i: int, j: int, quote: str, occurrences: int) -> QuranMatch:
        """Same skeleton as the Mushaf; still a difference if a word carries an alef the Mushaf does not."""
        m = self._build(i, j, "exact", quote, 100.0, "arabic", occurrences)
        diff = word_diff(quote, m.mushaf_text)
        if any(d["op"] != "equal" for d in diff):
            m.status, m.diff, m.score = "differs", diff, 99.0
        return m

    def _match_words(self, quote: str, prefer) -> QuranMatch | None:
        """Whole words only, in either spelling: a short quote must equal a run of Mushaf words."""
        words = [skeleton_ar(w) for w in ar_words(quote)]
        words = [w for w in words if w]
        if not words:
            return None
        hits = []
        for k in self._by_first.get(words[0], []):
            for src in (self.tok_sk, None):
                seq, n = [], k
                while len(seq) < len(words) and n < len(self.tok):
                    if src is None:
                        seq.extend(skeleton_ar(x) for x in self.tok_common[n].split())
                    else:
                        seq.append(src[n])
                    n += 1
                if seq == words and self.ayat[self.tok_ayah[k]].surah == self.ayat[self.tok_ayah[n - 1]].surah:
                    hits.append((self.tok_ayah[k], self.tok_ayah[n - 1]))
                    break
        hits = list(dict.fromkeys(hits))
        if not hits:
            return None
        i, j = self._preferred(hits, prefer)
        return self._exact(i, j, quote, len(hits))

    def _windows_for(self, length: int) -> tuple[list, list]:
        bucket = max(20, -(-length // 20) * 20)
        if bucket in self._windows:
            return self._windows[bucket]
        windows, spans = [], []
        n = len(self.ayat)
        for i in range(n):
            j, text = i, self._sk[i]
            while (len(text) < bucket or j == i) and j + 1 < n and j - i < 6 and self.ayat[j + 1].surah == self.ayat[i].surah:
                j += 1
                text += self._sk[j]
            # At the end of a surah the window would stay shorter than the quote: reach back instead (item 5).
            i0 = i
            while len(text) < bucket and i0 - 1 >= 0 and i - i0 < 6 and self.ayat[i0 - 1].surah == self.ayat[i].surah:
                i0 -= 1
                text = self._sk[i0] + text
            windows.append(text)
            spans.append((i0, j))
        if len(self._windows) > 40:
            self._windows.clear()
        self._windows[bucket] = (windows, spans)
        return windows, spans

    def _fuzzy_arabic(self, quote: str, q: str) -> QuranMatch:
        # Windows of consecutive ayat at least as long as the quote, so a short ayah can never "contain" a
        # long quote and a quote spanning ayat is still found. Built once per length bucket (plan item 10).
        windows, spans = self._windows_for(len(q))
        best = process.extractOne(q, windows, scorer=fuzz.partial_ratio, score_cutoff=70)
        if not best:
            return QuranMatch(status="not_found", via="arabic")
        _, score, k = best
        i, j = spans[k]
        align = fuzz.partial_ratio_alignment(q, windows[k])
        if align is not None:
            # Narrow the span to the ayat the quote actually covers.
            base = self.starts[i]
            i2 = self._ayah_at(base + align.dest_start)
            j2 = self._ayah_at(base + max(align.dest_end - 1, align.dest_start))
            i, j = max(i, i2), min(j, max(i2, j2))
        # Short passages score lower for one changed word (plan item 6): 80 says "differs" rather than
        # "not in the Mushaf"; measured on eval/synth_quran.py negatives (still 0 tied to an ayah).
        threshold = 80 if len(q) < 30 else 82
        if score < threshold:
            return QuranMatch(status="not_found", via="arabic", score=round(score, 1))
        m = self._build(i, j, "differs", quote, score, "arabic")
        if m.diff and all(d["op"] == "equal" for d in m.diff):
            m.status = "exact"
        return m

    def _load_translations(self, folder: Path) -> dict:
        """Plan item 36: the Urdu, Indonesian and French translations, fetched from quranpedia.net
        by scripts/fetch_translations.py with a pinned sha256. A missing file only turns that language off."""
        out = {}
        for lang, file, norm in (("ur", "ur_junagarhi.json", normalize_ur), ("id", "id_kfc.json", normalize_id),
                                ("fr", "fr_hamidullah.json", normalize_fr)):
            p = folder / file
            if not p.exists():
                continue
            doc = json.loads(p.read_text(encoding="utf-8"))
            blob = json.dumps(doc["verses"], ensure_ascii=False, sort_keys=True).encode()
            if hashlib.sha256(blob).hexdigest() != doc["sha256"] or len(doc["verses"]) != len(self.ayat):
                continue  # a changed or partial file is never used; the language is then said to be unchecked
            texts = [doc["verses"].get(f"{x.surah}:{x.ayah}", "") for x in self.ayat]
            if lang == "ur":
                texts = [unicodedata.normalize("NFKC", t) for t in texts]  # the source writes لا as the glyph ﻻ
            # Every number in these translations is a footnote marker (Indonesian: 1 to 1610 in order; Urdu: one,
            # at 6:28). The file keeps them as fetched so its sha256 matches; they are dropped for matching and display.
            texts = [re.sub(r" +([,.;:!?])", r"\1", re.sub(r"\d+(?:b(?=\W))?", "", t)).replace("  ", " ") for t in texts]
            out[lang] = {"name": file.removesuffix(".json"), "source": doc["source"], "sha256": doc["sha256"],
                         "texts": texts, "index": [norm(t) for t in texts], "norm": norm}
        return out

    def match_translation(self, quote: str, lang: str, prefer: tuple[int, int] | None = None) -> QuranMatch:
        """An Urdu or Indonesian quote, matched against that language's approved translation only."""
        tr = self.translations.get(lang)
        if not tr:
            return QuranMatch(status="not_found", via=lang)
        m = self._match_tr(tr["norm"](quote), tr, prefer, lang)
        if m.surah is not None:
            i, j = self.index[(m.surah, m.ayah_from)], self.index[(m.surah, m.ayah_to)]
            src = tr["source"]
            m.translation = {
                "lang": lang, "text": " ".join(tr["texts"][k] for k in range(i, j + 1)),
                "name_ar": src["name_ar"], "name_en": src["name_en"],
                "url": src["url"].replace("{s}", str(m.surah)), "sha256": tr["sha256"],
            }
        return m

    DISPLAY = (("es", "es_garcia.json"), ("zh", "zh_makin.json"), ("ja", "ja_mita.json"), ("bn", "bn_zakaria.json"),
               ("tr", "tr_kfc.json"), ("hi", "hi_umari.json"))

    def _load_display(self, folder: Path) -> dict:
        """Translations shown to readers of these languages beside the Mushaf; never used to match quotes.
        Same checks as the matching translations: the sha256 and the verse count must hold, or it is not loaded."""
        out = {}
        for lang, file in self.DISPLAY:
            p = folder / file
            if not p.exists():
                continue
            doc = json.loads(p.read_text(encoding="utf-8"))
            blob = json.dumps(doc["verses"], ensure_ascii=False, sort_keys=True).encode()
            if hashlib.sha256(blob).hexdigest() != doc["sha256"] or len(doc["verses"]) != len(self.ayat):
                continue
            texts = [doc["verses"].get(f"{x.surah}:{x.ayah}", "") for x in self.ayat]
            # Footnote marks as published ([1], [১], a trailing number) and a leading verse number («6.») are dropped.
            texts = [re.sub(r"^\s*\d+\s*[.．]\s*", "", t) for t in texts]
            texts = [re.sub(r"\s*\[[\d০-৯]+\]", "", t) for t in texts]
            texts = [re.sub(r"\s+", " ", re.sub(r"(?<=\D)\d+(?=[\s,.;:!?،。、]|$)", "", t)).strip() for t in texts]
            out[lang] = {"name": file.removesuffix(".json"), "source": doc["source"], "sha256": doc["sha256"], "texts": texts}
        return out

    def translations_for(self, surah: int, ayah_from: int, ayah_to: int) -> dict:
        """The approved translations of an ayah range in every loaded language, for readers of that language.
        Copied from the King Fahd Complex files as they are; nothing is translated here."""
        i, j = self.index.get((surah, ayah_from)), self.index.get((surah, ayah_to))
        if i is None or j is None:
            return {}
        out = {}
        for lang, tr in {**self.translations, **self.display_translations}.items():
            src = tr["source"]
            out[lang] = {"text": " ".join(tr["texts"][k] for k in range(i, j + 1)), "name_ar": src["name_ar"],
                         "name_en": src["name_en"], "name": src.get("name", src["name_en"]),
                         "url": src["url"].replace("{s}", str(surah))}
        return out

    # Measured by eval/translation_census.py: token_set_ratio alone lets an invented sentence made of common
    # words reach 85; also requiring the words in order (partial_ratio) leaves no invented sentence above 77.
    TR_FLOOR, TR_EXACT = 80, 95

    def _match_tr(self, q: str, tr: dict, prefer, via: str) -> QuranMatch:
        if len(q.split()) < 5:
            return QuranMatch(status="not_found", via=via)
        index = tr["index"]
        top = process.extract(q, index, scorer=fuzz.token_set_ratio, limit=10, score_cutoff=50)
        ks = [k for _, _, k in top]
        if prefer and prefer in self.index and self.index[prefer] not in ks:
            ks.append(self.index[prefer])
        scored = [(min(fuzz.token_set_ratio(q, index[k]), fuzz.partial_ratio(q, index[k])), k) for k in ks]
        if not scored:
            return QuranMatch(status="not_found", via=via)
        score, i = max(scored, key=lambda x: (x[0], -x[1]))
        if prefer and prefer in self.index:
            k = self.index[prefer]
            s2 = dict((b, a) for a, b in scored).get(k, 0)
            if s2 >= score - 3 and s2 >= self.TR_FLOOR:  # identical or near-identical ayat: accept the cited one
                i, score = k, s2
        if score < self.TR_FLOOR:
            return QuranMatch(status="not_found", via=via, score=round(score, 1))
        m = self._build(i, i, "exact" if score >= self.TR_EXACT else "differs", q, score, via)
        m.matched_translation = tr["name"]
        return m

    def match_english(self, quote: str, prefer: tuple[int, int] | None = None) -> QuranMatch:
        return self._match_index(normalize_en(quote), self._en, prefer, "english")

    def _match_index(self, q: str, indexes: dict, prefer, via: str) -> QuranMatch:
        if len(q.split()) < 5:
            return QuranMatch(status="not_found", via=via)
        # The quote may follow either translation; keep whichever matches better.
        found = []
        for name, index in indexes.items():
            best = process.extractOne(q, index, scorer=fuzz.token_set_ratio, score_cutoff=60)
            if not best:
                continue
            _, score, i = best
            if prefer and prefer in self.index:
                k = self.index[prefer]
                s2 = fuzz.token_set_ratio(q, index[k])
                if s2 >= score - 10 and s2 >= 85:  # near-identical ayat (94:5 and 94:6): accept the cited one
                    i, score = k, s2
            found.append((score, i, name))
        if not found:
            return QuranMatch(status="not_found", via=via)
        score, i, name = max(found)
        if score < 75:
            return QuranMatch(status="not_found", via=via, score=round(score, 1))
        m = self._build(i, i, "exact" if score >= 90 else "differs", q, score, via)
        m.matched_translation = name
        return m

    def get(self, surah: int, ayah: int) -> Ayah | None:
        i = self.index.get((surah, ayah))
        return self.ayat[i] if i is not None else None

    def check_reference(self, m: QuranMatch, surah: int, ayah: int, label: str) -> None:
        """Compare the reference the author wrote (e.g. البقرة: 255) with where the text actually is."""
        m.reference_given = label
        if m.surah is None:
            m.reference_ok = None
            return
        # A surah named without an ayah («في سورة الشعراء:») is checked for the surah only.
        m.reference_ok = m.surah == surah and (ayah is None or m.ayah_from <= ayah <= m.ayah_to)
        if m.reference_ok is False and ayah is not None:
            s = self.surahs.get(surah)
            x = self.get(surah, ayah)
            m.cited = {
                "surah": surah, "ayah": ayah,
                "surah_name_ar": s["ar"] if s else "", "surah_name_en": s["tr"] if s else "",
                "text": x.text if x else "",
                "exists": x is not None,
                "surah_ayat": len([a for a in self.ayat if a.surah == surah]) if s else 0,
            }

    def surah_number(self, name: str) -> int | None:
        name = name.strip()
        if name.isdigit():
            n = int(name)
            return n if 1 <= n <= 114 else None
        key = normalize_ar(name) if re.search("[؀-ۿ]", name) else normalize_en(name)
        key = re.sub("^(سوره|surah|sura|surat) ", "", key)
        key = re.sub("^(al|an|ar|as|at|ad|adh|az|ash) ", "", key) if key.isascii() else key
        if key in self.surah_names:
            return self.surah_names[key]
        for k, n in self.surah_names.items():
            if k.replace("ال", "", 1) == key.replace("ال", "", 1) or (k.isascii() and re.sub("^(al|an|ar|as|at|ad|adh|az|ash) ", "", k) == key):
                return n
        return None


def word_diff(quoted: str, mushaf: str) -> list:
    """Word-level differences between a quote and the Mushaf text, compared by skeleton.
    A word typed in common spelling (شيئا for ﴿شَيۡـٔٗا﴾) is the same word; a word with an alef the
    Mushaf does not have («قال» for ﴿قُلۡ﴾) is a difference (op "replace", kind "alef")."""
    a, b = ar_words(quoted), mushaf.split()
    # Show the user's own spelling in the result, not the normalized form.
    original = [w for w in re.split(r"\s+", quoted) if re.search("[\u0621-\u064A]", w)]
    shown = [w.strip("«»\"“”(){}﴿﴾،,.:؛") for w in original] if len(original) == len(a) else a
    b_sk = [word_skeleton(w) for w in ar_words(mushaf)]
    if len(b_sk) != len(b):  # normalization changed word count; fall back to normalized words
        b = ar_words(mushaf)
    common = [to_common_word(w, harakat=False)[0] for w in b]
    to_uthmani = {}
    for u, c in zip(b_sk, common):
        if " " not in c:
            to_uthmani.setdefault(word_skeleton(normalize_ar(c)), u)
    a_sk = [word_skeleton(w) for w in a]
    a_sk = [x if x in b_sk else to_uthmani.get(x, x) for x in a_sk]
    sm = difflib.SequenceMatcher(a=a_sk, b=b_sk, autojunk=False)
    ops = sm.get_opcodes()
    # Trim leading/trailing Mushaf words outside the quoted span.
    while ops and ops[0][0] == "insert":
        ops = ops[1:]
    while ops and ops[-1][0] == "insert":
        ops = ops[:-1]
    ops = [list(o) for o in ops]
    # A replace at either edge can swallow Mushaf words outside the quote: keep only as many as were quoted.
    if ops and ops[-1][0] == "replace":
        o = ops[-1]
        o[4] = min(o[4], o[3] + (o[2] - o[1]))
    if ops and ops[0][0] == "replace":
        o = ops[0]
        o[3] = max(o[3], o[4] - (o[2] - o[1]))
    out = []
    for op, i1, i2, j1, j2 in ops:
        if op == "equal" and i2 - i1 > 1:  # compare word by word so an alef difference names its word
            for k in range(i2 - i1):
                out.extend(_pair(shown[i1 + k], b[j1 + k], common[j1 + k], "equal"))
            continue
        out.extend(_pair(" ".join(shown[i1:i2]), " ".join(b[j1:j2]), " ".join(common[j1:j2]), op))
    # A quote may start or end inside a Mushaf word («إن» of ﴿فَإِنَّ﴾): that is a partial quote, not a change.
    for k, test in ((0, str.endswith), (-1, str.startswith)):
        if out and out[k]["op"] == "replace" and out[k].get("kind") != "alef" and " " not in out[k]["quoted"]:
            sq, sm = skeleton_ar(out[k]["quoted"]), skeleton_ar(out[k]["mushaf"])
            if sq and " " not in out[k]["mushaf"] and test(sm, sq):
                out[k]["op"] = "equal"
    return out


def _pair(quoted: str, mush: str, common: str, op: str) -> list:
    sq = skeleton_ar(quoted)
    same = sq == skeleton_ar(mush) or (common and sq == skeleton_ar(common))
    if op != "equal" and same:
        op = "equal"  # spelling only (يا أيها / يَـٰٓأَيُّهَا, شيئا / شَيۡـٔٗا)
    if op == "equal" and quoted and extra_alef(quoted, mush, common):
        return [{"op": "replace", "quoted": quoted, "mushaf": mush, "kind": "alef"}]
    return [{"op": op, "quoted": quoted, "mushaf": mush}]


@lru_cache(maxsize=1)
def get_quran() -> Quran:
    return Quran()
