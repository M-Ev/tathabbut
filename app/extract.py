"""Rule-based citation extraction (Arabic and English).

Rules catch the common ways people cite: Quran brackets ﴿ ﴾, "قال تعالى", "قال رسول الله ﷺ",
"the Prophet (ﷺ) said", references like (البقرة: 255) or (2:255), and Quran passages quoted
without any marker. The language model can add citations the rules miss (see pipeline.py).
"""
import re
from dataclasses import dataclass

from .normalize import quote_lang, skeleton_ar
from .quran import get_quran

AR_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")
QUOTE_PAIRS = {"«": "»", '"': '"', "“": "”", "„": "“", "'": "'", "‘": "’", "﴿": "﴾", "{": "}"}

HONORIFIC_AR = r"(?:\s*(?:ﷺ|صلى الله عليه (?:وآله )?وسلم|عليه (?:الصلاة و)?السلام|صلوات الله وسلامه عليه))?"
HADITH_AR = re.compile(
    r"(?:(?:قال|يقول|وقال|ويقول|عن|أن|إن|وعن|قول|وقول)\s+(?:رسول\s+الله|رسول\s+اللّٰه|النبي|النبيّ|المصطفى|الرسول)"
    + HONORIFIC_AR
    + r"(?:\s*(?:أنه|انه))?(?:\s*(?:قال|يقول))?"
    + r"|(?:قال|يقول|وقال)\s*(?:ﷺ|صلى الله عليه وسلم|عليه الصلاة والسلام)"
    + r"|(?:وفي|في)\s+(?:الحديث\s+الشريف|الحديث\s+الصحيح|الحديث|الأثر)"  # longest first
    + r"|(?:ورد|جاء)\s+في\s+الحديث"
    + r"|(?:قوله|وقوله)\s*(?:ﷺ|صلى الله عليه وسلم))\s*[:：]?\s*"
)
QURAN_AR = re.compile(
    r"(?:(?:قال|يقول|وقال|ويقول|قول)\s+(?:الله|ربنا)(?:\s+(?:تعالى|عز وجل|سبحانه(?:\s+وتعالى)?|جل وعلا|تبارك وتعالى))?"
    + r"|(?:قال|يقول|وقال|قوله|وقوله)\s+(?:تعالى|عز وجل|سبحانه(?:\s+وتعالى)?|جل وعلا)"
    + r"|في\s+(?:كتابه\s+(?:الكريم|العزيز)|محكم\s+التنزيل|القرآن\s+الكريم))"
    # «يقول الله تعالى في سورة الشعراء:» names the surah; the name is a reference, not part of the ayah (item 4).
    + r"(?:\s+في\s+سورة\s+(?P<surah>[ء-ي]+(?:\s+[ء-ي]+)?)(?=\s*[:：]))?\s*[:：]?\s*"
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
REF_NUM = re.compile(r"[\(\[]\s*(?:Qur'?an|Quran|Surah|سورة|QS\.?)?\s*(\d{1,3})\s*[:：]\s*(\d{1,3})(?:\s*[-–]\s*\d{1,3})?\s*[\)\]]", re.I)
REF_NAME = re.compile(
    r"[\(\[]\s*(?:QS\.?\s*)?(?:سورة\s+|Surah\s+|Surat\s+)?([ء-يٱ ]{2,25}?|[A-Za-z][A-Za-z'\- ]{1,25}?)\s*[:：،,\-]?\s*"
    r"(?:الآية|آية|ayah|verse)?\s*[:：]?\s*([0-9٠-٩]{1,3})(?:\s*[-–]\s*[0-9٠-٩]{1,3})?\s*[\)\]]",
    re.I,
)
# A sentence ends at punctuation or where a written reference opens: (2:255), (سورة ...), (البقرة: 255)
# and (البقرة 255) or (آل عمران ٥) without a colon.
SENTENCE_END = re.compile(
    r"[.!؟?\n۔]|[\(\[]\s*(?:\d|سورة|Surah|Qur|[ء-ي]+\s*[:：]|[ء-ي]+(?:\s+[ء-ي]+)?\s*[0-9٠-٩]{1,3}\s*[\)\]])"
)
# «رُوي عن النبي ﷺ أنه قال:» is the cautious form for a narration not established (صيغة التمريض).
HADITH_RUWIYA_AR = re.compile(
    r"(?<![ء-ي])(?:رُوي|روي|ويُروى|يُروى|يروى|ويروى)(?:\s+عن\s+(?:رسول\s+الله|النبي|النبيّ)" + HONORIFIC_AR
    + r"(?:\s*(?:أنه|انه))?(?:\s*قال)?\s*[:：]?|\s*[:：])\s*"
)
# Written attribution to the two Sahihs (plan item 19), Arabic and English.
ATTR_AR = re.compile(
    r"(?:رواه|أخرجه|خرّجه|روى|أخرج)\s+(?:الإمامان\s+|الإمام\s+)?(?P<a>البخاري|مسلم|الشيخان)(?:\s+و\s*(?:الإمام\s+)?(?P<b>مسلم|البخاري))?"
    r"|(?P<both>متفق\s+عليه|في\s+الصحيحين)|في\s+صحيح\s+(?:الإمام\s+)?(?P<c>البخاري|مسلم)"
)
ATTR_EN = re.compile(
    r"\(\s*(?:Sahih\s+)?(?:al-)?(?P<a>Bukhari|Muslim)(?:\s*(?:and|&|,)\s*(?:Sahih\s+)?(?:al-)?(?P<b>Bukhari|Muslim))?[^)]{0,25}\)"
    r"|Sahih\s+(?:al-)?(?P<c>Bukhari|Muslim)|(?:narrated|reported|recorded|related)\s+by\s+(?:al-)?(?P<d>Bukhari|Muslim)"
    r"|(?P<both>agreed\s+upon|in\s+both\s+Sahihs?)",
    re.I,
)
# Plan item 36: the common Urdu, Indonesian and French ways of citing; to be reviewed by a speaker of each language.
_ALLAH_UR = r"الل[ّٰ]*ہ"
QURAN_UR = re.compile(
    r"(?:" + _ALLAH_UR + r"\s*(?:تعالیٰ|تعالی|تعالى|پاک|عزوجل|عز وجل|سبحانہ\s*و\s*تعالیٰ)?\s*(?:نے\s*)?"
    r"(?:ارشاد\s+)?(?:فرماتا\s+ہے|فرمایا|فرماتے\s+ہیں|کا\s+فرمان\s+ہے|کا\s+ارشاد\s+ہے)"
    r"|ارشادِ?\s+باری\s+تعالیٰ\s+ہے|فرمانِ?\s+الٰہی\s+ہے|قرآن\s+(?:مجید|کریم|پاک)\s+میں\s+(?:ہے|فرمایا\s+گیا\s+ہے))"
    r"(?:\s*کہ)?\s*[:：]?\s*"
)
HADITH_UR = re.compile(
    r"(?:(?:رسول\s+" + _ALLAH_UR + r"|نبی\s+(?:کریم|اکرم|پاک)|نبی)\s*(?:ﷺ|صلی\s+" + _ALLAH_UR + r"\s+علیہ\s+وسلم)?"
    r"|(?:آپ|حضور)\s*(?:ﷺ|صلی\s+" + _ALLAH_UR + r"\s+علیہ\s+وسلم))"
    r"\s*(?:نے\s*)?(?:ارشاد\s+)?(?:فرمایا|کا\s+فرمان\s+ہے|کا\s+ارشاد\s+ہے)"
    r"(?:\s*کہ)?\s*[:：]?\s*"
    r"|حدیث\s+(?:شریف\s+)?میں\s+(?:ہے|آتا\s+ہے)(?:\s*کہ)?\s*[:：]?\s*"
)
QURAN_ID = re.compile(
    r"(?:Allah\s*(?:SWT|subhanahu\s+wa\s+ta['’]?ala|ta['’]?ala|azza\s+wa\s+jalla|\(SWT\))?\s*(?:telah\s+)?berfirman"
    r"|firman\s+Allah(?:\s+(?:SWT|ta['’]?ala|\(SWT\)))?|dalam\s+Al[- ]?Qur['’]?an(?:\s+disebutkan)?)"
    r"(?:\s+dalam\s+(?:surat|surah|QS\.?)\s+[A-Za-z'’\-]+(?:\s+ayat\s+\d+)?)?\s*[:,]?\s*",
    re.I,
)
HADITH_ID = re.compile(
    r"(?:(?:Rasulullah|Rasul|Nabi(?:\s+Muhammad)?)\s*(?:SAW|ﷺ|\(SAW\)|shallallahu\s+['’]?alaihi\s+wa\s*sallam)?\s*(?:telah\s+)?bersabda"
    r"|sabda\s+(?:Rasulullah|Nabi)(?:\s+(?:SAW|ﷺ|\(SAW\)))?)\s*[:,]?\s*",
    re.I,
)
QURAN_FR = re.compile(
    r"(?:(?:Allah|Dieu)(?:\s*\((?:swt|exalt[ée] soit-Il|qu['’]Il soit exalt[ée])\))?(?:\s+(?:le\s+Tr[èe]s[- ]Haut|l['’]Exalt[ée]|exalt[ée]\s+soit-Il|Ta['’]?ala))?"
    r"\s+(?:dit|a\s+dit|nous\s+dit|d[ée]clare)(?:\s+dans\s+le\s+(?:saint\s+)?Coran)?"
    r"|le\s+(?:saint\s+)?Coran\s+(?:dit|nous\s+dit|d[ée]clare))\s*[:,]?\s*",
    re.I,
)
HADITH_FR = re.compile(
    r"(?:le\s+Proph[èe]te(?:\s+Muhammad|\s+Mohammed)?|le\s+Messager\s+d['’](?:Allah|Dieu))"
    r"(?:\s*\((?:ﷺ|saw|sws|paix\s+(?:et\s+b[ée]n[ée]dictions?\s+)?sur\s+lui|[^)]{0,40}salut[^)]{0,20})\)|\s*ﷺ)?"
    r"\s+(?:a\s+dit|dit|disait)\s*[:,]?\s*",
    re.I,
)
_BOOK = {"البخاري": "bukhari", "مسلم": "muslim", "bukhari": "bukhari", "muslim": "muslim"}


def _attribution(text: str, start: int, end: int) -> dict | None:
    """A written attribution in the same sentence: after the quote (up to the next quote or line), or before
    the marker («روى البخاري أن النبي ﷺ قال: ...»)."""
    after = re.split(r"[«\n﴿\"“]", text[end : end + 70].lstrip("»\"”' "), maxsplit=1)[0]
    before = re.split(r"[.!؟?\n»]", text[max(0, start - 70) : start])[-1]
    for chunk in (after, before):
        m = ATTR_AR.search(chunk) or ATTR_EN.search(chunk)
        if not m:
            continue
        g = m.groupdict()
        if g.get("both") or g.get("a") == "الشيخان":
            books = ["bukhari", "muslim"]
        else:
            books = [_BOOK[x.lower() if x.isascii() else x] for x in (g.get("a"), g.get("b"), g.get("c"), g.get("d")) if x]
        return {"written": m.group(0).strip(" ()"), "books": list(dict.fromkeys(books))}
    return None


# A follow-on hadith in a list: «وقال: «...»» or «وعنه: ...» right after a hadith already found in the same paragraph.
HADITH_FOLLOW_AR = re.compile(r"(?<![ء-ي])(?:وقال(?:\s+(?:أيضًا|أيضا))?|وعنه)\s*[:：]\s*")


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
    attribution: dict | None = None  # a written «رواه البخاري» / «متفق عليه» near a hadith (plan item 19)
    cautious: bool = False  # attributed with «رُوي» / «يُروى», not with «قال رسول الله ﷺ»

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
    q = q.strip().strip("«»\"“”‘’'{}﴿﴾()[]،,.:؛۔ ")
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
    for rx, kind in ((QURAN_AR, "quran"), (HADITH_AR, "hadith"), (HADITH_RUWIYA_AR, "hadith"), (QURAN_EN, "quran"), (HADITH_EN, "hadith"),
                     (QURAN_UR, "quran"), (HADITH_UR, "hadith"), (QURAN_ID, "quran"), (HADITH_ID, "hadith"),
                     (QURAN_FR, "quran"), (HADITH_FR, "hadith")):
        for m in rx.finditer(text):
            span = _take_quote(text, m.end())
            if not span:
                continue
            s, e = span
            quote = _clean_quote(text[s:e])
            lang = quote_lang(quote)
            if lang == "en" and rx in (QURAN_ID, HADITH_ID):
                lang = "id"  # a short Indonesian quote has too few common words to tell by itself
            elif lang == "en" and rx in (QURAN_FR, HADITH_FR):
                lang = "fr"
            cand = Candidate(kind, quote, m.start(), e, lang, m.group(0).strip())
            named = m.groupdict().get("surah")
            if named and get_quran().surah_number(named):
                cand.ref_surah, cand.ref_label = get_quran().surah_number(named), f"سورة {named}"
            _add(found, cand)

    # 2b) «وقال: «...»» continuing a list of hadith: only after a hadith already found in the same paragraph,
    # so a bare «وقال:» elsewhere (a person speaking) is never taken as a hadith.
    for m in HADITH_FOLLOW_AR.finditer(text):
        before = [c for c in found if c.end <= m.start()]
        last = max(before, key=lambda c: c.end, default=None)
        if not last or last.type != "hadith" or "\n\n" in text[last.end : m.start()]:
            continue
        span = _take_quote(text, m.end())
        if not span:
            continue
        s, e = span
        quote = _clean_quote(text[s:e])
        _add(found, Candidate("hadith", quote, m.start(), e, quote_lang(quote), m.group(0).strip()))

    # 3) Curly braces or quotes followed by a Quran reference.
    for m in re.finditer(r"[{«\"“]([^}»\"”]{6,})[}»\"”]", text):
        if _reference_after(text, m.end()):
            quote = _clean_quote(m.group(1))
            _add(found, Candidate("quran", quote, m.start(), m.end(), quote_lang(quote), "ref"))

    # 4) Unmarked Quran passages inside running Arabic text.
    for cand in _scan_unmarked_quran(text):
        _add(found, cand)

    # References written after a quote are checked against where the text really is.
    for c in found:
        if c.type == "hadith":
            c.attribution = _attribution(text, c.start, c.end)
            lead = text[max(0, c.start - 14) : c.start] + " " + c.marker
            c.cautious = bool(re.search(r"(?<![ء-ي])(?:رُوي|روي|يُروى|يروى|ويُروى|ويروى)(?![ء-ي])", lead))
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
        if sk not in q.full and sk not in q.full_common:
            i += 1
            continue
        j = i + min_words
        while j < len(words):
            nxt = sk + skeleton_ar(words[j][0])
            if nxt not in q.full and nxt not in q.full_common:
                break
            sk, j = nxt, j + 1
        if len(sk) >= min_skeleton:
            start, end = words[i][1], words[j - 1][2]
            out.append(Candidate("quran", text[start:end], start, end, "ar", "unmarked"))
        i = j
    return out
