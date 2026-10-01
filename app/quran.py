"""Quran lookup against the Mushaf text (King Fahd Complex Uthmani script).

The Quran text is never generated: every result shows the Mushaf text loaded from data/quran.json.
"""
import bisect
import difflib
import json
import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

from rapidfuzz import fuzz, process

from .normalize import ar_words, normalize_ar, normalize_en, skeleton_ar, word_skeleton

DATA = Path(__file__).resolve().parent.parent / "data" / "quran.json"

# Minimum skeleton length for a span to count as a Quran quote (avoids matching common short phrases).
MIN_SKELETON = 10
MIN_SKELETON_FUZZY = 12


@dataclass
class Ayah:
    surah: int
    ayah: int
    text: str
    translation_en: str
    skeleton: str
    norm_en: str


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
    reference_given: str = ""
    reference_ok: bool | None = None
    # What actually sits at the reference the author wrote, to explain a wrong reference.
    cited: dict | None = None

    def to_dict(self):
        return self.__dict__ | {"ref": self.ref, "url": self.url}

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
        return f"https://quranenc.com/ar/browse/english_saheeh/{self.surah}#{self.ayah_from}"


class Quran:
    def __init__(self, path: Path = DATA):
        data = json.loads(path.read_text(encoding="utf-8"))
        self.source = data["source"]
        self.surahs = {s["n"]: s for s in data["surahs"]}
        self.ayat = [
            Ayah(s, a, t, e, skeleton_ar(t), normalize_en(e)) for s, a, t, e in data["verses"]
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
        self._en = [x.norm_en for x in self.ayat]
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

    def match_arabic(self, quote: str, prefer: tuple[int, int] | None = None) -> QuranMatch:
        """prefer=(surah, ayah): when the phrase occurs in several places, pick the one the author cited."""
        q = skeleton_ar(quote)
        if len(q) < MIN_SKELETON:
            return QuranMatch(status="not_found", via="arabic")
        positions, pos = [], self.full.find(q)
        while pos >= 0:
            positions.append(pos)
            pos = self.full.find(q, pos + 1)
        if positions:
            spans = [(self._ayah_at(p), self._ayah_at(p + len(q) - 1)) for p in positions]
            i, j = spans[0]
            if prefer:
                for a, b in spans:
                    if self.ayat[a].surah == prefer[0] and self.ayat[a].ayah <= prefer[1] <= self.ayat[b].ayah:
                        i, j = a, b
                        break
            return self._build(i, j, "exact", quote, 100.0, "arabic", len(positions))
        if len(q) < MIN_SKELETON_FUZZY:
            return QuranMatch(status="not_found", via="arabic")
        return self._fuzzy_arabic(quote, q)

    def _fuzzy_arabic(self, quote: str, q: str) -> QuranMatch:
        # Windows of consecutive ayat at least as long as the quote, so a short ayah
        # can never "contain" a long quote and a quote spanning ayat is still found.
        windows, spans = [], []
        n = len(self.ayat)
        for i in range(n):
            j, text = i, self._sk[i]
            while (len(text) < len(q) or j == i) and j + 1 < n and j - i < 6 and self.ayat[j + 1].surah == self.ayat[i].surah:
                j += 1
                text += self._sk[j]
            windows.append(text)
            spans.append((i, j))
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
        threshold = 88 if len(q) < 30 else 82
        if score < threshold:
            return QuranMatch(status="not_found", via="arabic", score=round(score, 1))
        m = self._build(i, j, "differs", quote, score, "arabic")
        if m.diff and all(d["op"] == "equal" for d in m.diff):
            m.status = "exact"
        return m

    def match_english(self, quote: str, prefer: tuple[int, int] | None = None) -> QuranMatch:
        q = normalize_en(quote)
        if len(q.split()) < 5:
            return QuranMatch(status="not_found", via="english")
        best = process.extractOne(q, self._en, scorer=fuzz.token_set_ratio, score_cutoff=60)
        if not best:
            return QuranMatch(status="not_found", via="english")
        _, score, i = best
        if prefer and prefer in self.index:
            k = self.index[prefer]
            s2 = fuzz.token_set_ratio(q, self._en[k])
            if s2 >= score - 10 and s2 >= 85:  # near-identical ayat (94:5 and 94:6): accept the cited one
                i, score = k, s2
        if score >= 90:
            return self._build(i, i, "exact", quote, score, "english")
        if score >= 75:
            return self._build(i, i, "differs", quote, score, "english")
        return QuranMatch(status="not_found", via="english", score=round(score, 1))

    def get(self, surah: int, ayah: int) -> Ayah | None:
        i = self.index.get((surah, ayah))
        return self.ayat[i] if i is not None else None

    def check_reference(self, m: QuranMatch, surah: int, ayah: int, label: str) -> None:
        """Compare the reference the author wrote (e.g. البقرة: 255) with where the text actually is."""
        m.reference_given = label
        if m.surah is None:
            m.reference_ok = None
            return
        m.reference_ok = m.surah == surah and m.ayah_from <= ayah <= m.ayah_to
        if m.reference_ok is False:
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
    """Word-level differences between a quote and the Mushaf text, compared by skeleton."""
    a, b = ar_words(quoted), mushaf.split()
    # Show the user's own spelling in the result, not the normalized form.
    original = [w for w in re.split(r"\s+", quoted) if re.search("[\u0621-\u064A]", w)]
    shown = [w.strip("«»\"“”(){}﴿﴾،,.:؛") for w in original] if len(original) == len(a) else a
    a_sk = [word_skeleton(w) for w in a]
    b_sk = [word_skeleton(w) for w in ar_words(mushaf)]
    if len(b_sk) != len(b):  # normalization changed word count; fall back to normalized words
        b = ar_words(mushaf)
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
        quoted, mush = " ".join(shown[i1:i2]), " ".join(b[j1:j2])
        if op != "equal" and skeleton_ar(quoted) == skeleton_ar(mush):
            op = "equal"  # spelling only (يا أيها / يَـٰٓأَيُّهَا)
        out.append({"op": op, "quoted": quoted, "mushaf": mush})
    return out


@lru_cache(maxsize=1)
def get_quran() -> Quran:
    return Quran()
