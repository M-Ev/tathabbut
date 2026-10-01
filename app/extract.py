"""Rule-based citation extraction (Arabic and English).

Rules catch the common ways people cite: Quran brackets ﴿ ﴾, "قال تعالى", "قال رسول الله ﷺ",
"the Prophet (ﷺ) said", references like (البقرة: 255) or (2:255), and Quran passages quoted
without any marker. The language model can add citations the rules miss (see pipeline.py).
"""
import re
from dataclasses import dataclass

from .normalize import is_arabic, skeleton_ar
from .quran import get_quran

AR_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")
QUOTE_PAIRS = {"«": "»", '"': '"', "“": "”", "„": "“", "'": "'", "‘": "’", "﴿": "﴾", "{": "}"}

HONORIFIC_AR = r"(?:\s*(?:ﷺ|صلى الله عليه (?:وآله )?وسلم|عليه (?:الصلاة و)?السلام|صلوات الله وسلامه عليه))?"
HADITH_AR = re.compile(
    r"(?:(?:قال|يقول|وقال|ويقول|عن|أن|إن|وعن)\s+(?:رسول\s+الله|رسول\s+اللّٰه|النبي|النبيّ|المصطفى|الرسول)"
    + HONORIFIC_AR
    + r"(?:\s*(?:أنه|انه))?(?:\s*(?:قال|يقول))?"
    + r"|(?:قال|يقول|وقال)\s*(?:ﷺ|صلى الله عليه وسلم|عليه الصلاة والسلام)"
    + r"|(?:وفي|في)\s+(?:الحديث|الحديث الشريف|الحديث الصحيح|الأثر)"
    + r"|(?:ورد|جاء)\s+في\s+الحديث"
    + r"|(?:قوله|وقوله)\s*(?:ﷺ|صلى الله عليه وسلم))\s*[:：]?\s*"
)
QURAN_AR = re.compile(
    r"(?:(?:قال|يقول|وقال|ويقول|قول)\s+(?:الله|ربنا)(?:\s+(?:تعالى|عز وجل|سبحانه(?:\s+وتعالى)?|جل وعلا|تبارك وتعالى))?"
    + r"|(?:قال|يقول|وقال|قوله|وقوله)\s+(?:تعالى|عز وجل|سبحانه(?:\s+وتعالى)?|جل وعلا)"
    + r"|في\s+(?:كتابه\s+(?:الكريم|العزيز)|محكم\s+التنزيل|القرآن\s+الكريم))\s*[:：]?\s*"
)
HADITH_EN = re.compile(
    r"(?:the\s+)?(?:Prophet(?:\s+Muhammad)?|Messenger(?:\s+of\s+(?:Allah|God))?|Rasul(?:ullah|\s+Allah))"
    r"(?:\s*\((?:ﷺ|pbuh|p\.b\.u\.h\.?|saw|s\.a\.w\.?|sallallahu\s+alaihi\s+wa\s*sallam|peace\s+be\s+upon\s+him)\)"
    r"|\s*ﷺ|\s+pbuh|\s+\(?peace\s+be\s+upon\s+him\)?)?\s*,?\s+(?:said|says|stated|has\s+said)\s*[:,]?\s*",
    re.I,
)
QURAN_EN = re.compile(
    r"(?:(?:Allah|God)(?:\s+\(?(?:swt|subhanahu\s+wa\s+ta'?ala|the\s+Almighty|Almighty|Most\s+High)\)?)?\s+(?:says|said|states|tells\s+us)"
    r"(?:\s+in\s+the\s+(?:Holy\s+)?Qur'?an)?|the\s+(?:Holy\s+)?Qur'?an\s+(?:says|states|tells\s+us))\s*[:,]?\s*",
    re.I,
)
REF_NUM = re.compile(r"[\(\[]\s*(?:Qur'?an|Quran|Surah|سورة)?\s*(\d{1,3})\s*[:：]\s*(\d{1,3})(?:\s*[-–]\s*\d{1,3})?\s*[\)\]]", re.I)
REF_NAME = re.compile(
    r"[\(\[]\s*(?:سورة\s+|Surah\s+|Surat\s+)?([ء-يٱ ]{2,25}?|[A-Za-z][A-Za-z'\- ]{1,25}?)\s*[:：،,\-]?\s*"
    r"(?:الآية|آية|ayah|verse)?\s*[:：]?\s*([0-9٠-٩]{1,3})(?:\s*[-–]\s*[0-9٠-٩]{1,3})?\s*[\)\]]",
    re.I,
)
SENTENCE_END = re.compile(r"[.!؟?\n]|[\(\[]\s*(?:\d|سورة|Surah|Qur|[ء-ي]+\s*[:：])")


@dataclass
class Candidate:
    type: str  # quran | hadith
    quote: str
    start: int
    end: int
    lang: str
    marker: str = ""
    ref_surah: int | None = None
    ref_ayah: int | None = None
    ref_label: str = ""
    found_by: str = "rules"

    def overlaps(self, other: "Candidate") -> bool:
        return self.start < other.end and other.start < self.end


def _take_quote(text: str, pos: int) -> tuple[int, int] | None:
    """From pos, take a quoted span if one opens right away, else the rest of the sentence."""
    while pos < len(text) and text[pos] in " \t:：":
        pos += 1
    if pos >= len(text):
        return None
    ch = text[pos]
    if ch in QUOTE_PAIRS:
        close = text.find(QUOTE_PAIRS[ch], pos + 1)
        if close > pos + 1:
            return pos + 1, close
    m = SENTENCE_END.search(text, pos)
    end = m.start() if m else len(text)
    end = min(end, pos + 500)
    return (pos, end) if end - pos >= 6 else None


def _clean_quote(q: str) -> str:
    q = q.strip().strip("«»\"“”‘’'{}﴿﴾()[]،,.:؛ ")
    q = re.sub(r"\s*(?:ﷺ|صلى الله عليه وسلم)\s*", " ", q)
    return re.sub(r"\s+", " ", q).strip()


def _reference_after(text: str, end: int):
    """A Quran reference written right after a quote, e.g. ﴾ (الحجرات: 6) or "..." (49:6)."""
    window = text[end : end + 60]
    q = get_quran()
    m = REF_NUM.search(window)
    if m and m.start() < 12:
        s, a = int(m.group(1)), int(m.group(2))
        if 1 <= s <= 114:
            return s, a, m.group(0).strip()
    m = REF_NAME.search(window)
    if m and m.start() < 12:
        s = q.surah_number(m.group(1))
        if s:
            return s, int(m.group(2).translate(AR_DIGITS)), m.group(0).strip()
    return None


def _add(found: list, cand: Candidate):
    if len(cand.quote) < 6:
        return
    if any(cand.overlaps(c) for c in found):
        return
    found.append(cand)


def extract(text: str) -> list[Candidate]:
    found: list[Candidate] = []

    # 1) Quran brackets: always Quran.
    for m in re.finditer(r"﴿([^﴾]{3,})﴾", text):
        _add(found, Candidate("quran", _clean_quote(m.group(1)), m.start(), m.end(), "ar", "﴿﴾"))

    # 2) Marker + quote.
    for rx, kind in ((QURAN_AR, "quran"), (HADITH_AR, "hadith"), (QURAN_EN, "quran"), (HADITH_EN, "hadith")):
        for m in rx.finditer(text):
            span = _take_quote(text, m.end())
            if not span:
                continue
            s, e = span
            quote = _clean_quote(text[s:e])
            lang = "ar" if is_arabic(quote) else "en"
            _add(found, Candidate(kind, quote, m.start(), e, lang, m.group(0).strip()))

    # 3) Curly braces or quotes followed by a Quran reference.
    for m in re.finditer(r"[{«\"“]([^}»\"”]{6,})[}»\"”]", text):
        if _reference_after(text, m.end()):
            quote = _clean_quote(m.group(1))
            _add(found, Candidate("quran", quote, m.start(), m.end(), "ar" if is_arabic(quote) else "en", "ref"))

    # 4) Unmarked Quran passages inside running Arabic text.
    for cand in _scan_unmarked_quran(text):
        _add(found, cand)

    # References written after a quote are checked against where the text really is.
    for c in found:
        if c.type == "quran":
            ref = _reference_after(text, c.end)
            if ref:
                c.ref_surah, c.ref_ayah, c.ref_label = ref

    found.sort(key=lambda c: c.start)
    return found


_WORD = re.compile(r"[ء-يٱؐ-ًؚ-ٰٟۖ-ۭ]+")


def _scan_unmarked_quran(text: str, min_words: int = 5, min_skeleton: int = 20) -> list[Candidate]:
    q = get_quran()
    words = [(m.group(0), m.start(), m.end()) for m in _WORD.finditer(text)]
    out, i = [], 0
    while i + min_words <= len(words):
        sk = "".join(skeleton_ar(w[0]) for w in words[i : i + min_words])
        if sk not in q.full:
            i += 1
            continue
        j = i + min_words
        while j < len(words):
            nxt = sk + skeleton_ar(words[j][0])
            if nxt not in q.full:
                break
            sk, j = nxt, j + 1
        if len(sk) >= min_skeleton:
            start, end = words[i][1], words[j - 1][2]
            out.append(Candidate("quran", text[start:end], start, end, "ar", "unmarked"))
        i = j
    return out
