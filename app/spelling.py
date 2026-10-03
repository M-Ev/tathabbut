"""Uthmani (King Fahd Complex Mushaf) spelling -> common (imla'i) spelling, word by word.

Used for matching only: the Mushaf text shown to the reader is never converted. A quote typed in common spelling
(شيئا، إسرائيل، الليل، إبراهيم، ضحاها) is matched against a second index of the Mushaf in this spelling
(app/quran.py). The rules change letters only where standard modern spelling differs from the Uthmani rasm;
where unsure they keep the Uthmani letters. Self-test: `python3 eval/synth_quran.py --selftest`.
"""
import re


FATHA, DAMMA, KASRA, SHADDA = "َ", "ُ", "ِ", "ّ"
SHORT = {FATHA: "a", DAMMA: "u", KASRA: "i"}
# This Mushaf encoding writes "open" tanween with 0657/065E/0656 and sukun with 06E1; 0652 marks a
# letter that is written but not pronounced.
TANWEEN = {"ً": "a", "ٗ": "a", "ٌ": "u", "ٞ": "u", "ٍ": "i", "ٖ": "i"}
SUKUN, SILENT = "ۡ", "ْ"
DAGGER, MADDA, HAMZA_ABOVE, HAMZA_BELOW = "ٰ", "ٓ", "ٔ", "ٕ"
SMALL_WAW, SMALL_YA, SMALL_HIGH_YA, SMALL_HIGH_NOON, SMALL_HIGH_SEEN = "ۥ", "ۦ", "ۧ", "ۨ", "ۜ"
TATWEEL = "ـ"
_BASE = re.compile("[ء-غـ-يٱ]")
_DROP_EARLY = re.compile("[ۖ-ۛ۝۞۩ٜ۬]")  # pause marks, ornaments
_HARAKAT_KEEP = {"ً": "ً", "ٌ": "ٌ", "ٍ": "ٍ", FATHA: FATHA, DAMMA: DAMMA, KASRA: KASRA,
                 SHADDA: SHADDA, "ٗ": "ً", "ٞ": "ٌ", "ٖ": "ٍ", SUKUN: "ْ"}
_ALL_MARKS = re.compile("[ؐ-ًؚ-ٰٟۖ-ۭـ]")
PREFIX = set("وفبلك")
# Words written without the alef that the Uthmani dagger alef stands for.
NO_ALEF = {"هذا", "هذه", "هذان", "هذين", "هؤلاء", "ذلك", "ذلكم", "ذلكما", "ذلكن", "لكن", "لكنا", "لكنه", "لكنهم",
           "لكنكم", "لكني", "الرحمن", "رحمن", "اله", "الهكم", "الهنا", "الهك", "الهه", "الهي", "الهين", "الهما",
           "الههم", "اولئك", "اولئكم", "الله", "اللهم", "هكذا", "اهكذا"}
# Converter rules that change letters the skeleton keeps (so the quote can differ from the Mushaf skeleton).
CHANGING_RULES = {"final_alef", "hamza_ya", "hamza_waw", "hamza_dropped_ya", "alef_maqsura_mid", "small_ya", "small_waw",
                  "small_noon", "lam_rasm", "sad_sin", "waw_hamza_final", "raa", "silent_letter"}


def _parse(word: str) -> list[list[str]]:
    cl: list[list[str]] = []
    for ch in word:
        if _BASE.match(ch):
            cl.append([ch, ""])
        elif cl:
            cl[-1][1] += ch
    return cl


def _vowel(marks: str) -> str | None:
    for ch in marks:
        if ch in SHORT:
            return SHORT[ch]
        if ch in TANWEEN:
            return TANWEEN[ch]
    if SUKUN in marks:
        return "0"
    return None


def _key(cl) -> str:
    k = "".join(b for b, _ in cl if b != TATWEEL)
    return re.sub("[ٱأإآ]", "ا", k)


def _cores(key: str) -> list[str]:
    out = [key]
    for n in (1, 2):
        if len(key) > n + 1 and all(c in PREFIX for c in key[:n]):
            out.append(key[n:])
    return out


def _is_hamza(c) -> bool:
    b, m = c
    return b == "ء" or (b == TATWEEL and HAMZA_ABOVE in m) or (b in "يو" and HAMZA_BELOW in m)


def _split_vocative(cl):
    """يَٰقَوۡمِ -> يا قوم, يَـٰٓأَيُّهَا -> يا أيها, هَٰٓأَنتُمۡ -> ها أنتم (common spelling writes them apart)."""
    k = 1 if len(cl) > 2 and cl[0][0] == "و" and cl[1][0] == "ي" else 0
    if len(cl) > k + 1 and cl[k][0] == "ي" and FATHA in cl[k][1]:
        if DAGGER in cl[k][1]:
            return [cl[:k] + [["ي", FATHA], ["ا", ""]], cl[k + 1 :]]
        if len(cl) > k + 2 and cl[k + 1][0] == TATWEEL and DAGGER in cl[k + 1][1]:
            return [cl[:k] + [["ي", FATHA], ["ا", ""]], cl[k + 2 :]]
    if len(cl) > 1 and cl[0][0] == "ه" and DAGGER in cl[0][1] and cl[1][0] == "أ":
        return [[["ه", FATHA], ["ا", ""]], cl[1:]]
    return [cl]


def _common_word(cl, rules: set) -> list[list[str]]:
    cl = [list(c) for c in cl]
    key = _key(cl)
    cores = _cores(key)
    no_alef = any(c in NO_ALEF for c in cores)

    # A. whole-word spellings
    if any(c in ("اليل", "الذان", "الي") for c in cores) or ("الذين" in cores and any(b == "ذ" and FATHA in m for b, m in cl)) \
            or ("التي" in cores and any(b == TATWEEL and DAGGER in m for b, m in cl)):
        if not ("الي" in cores and not any(_is_hamza(c) for c in cl)):
            k = next(i for i, c in enumerate(cl) if c[0] == "ٱ")
            cl.insert(k + 1, ["ل", ""])  # الليل، اللذان، اللذين (dual)، اللاتي، اللائي
            rules.add("lam_rasm")
    if key in ("رءا", "ورءا", "فرءا"):
        cl = cl[:-3] + [["ر", FATHA], ["أ", FATHA], ["ى", ""]]
        rules.add("raa")
    if key == "ليسوا" and any(_is_hamza(c) for c in cl):
        cl = [["ل", KASRA], ["ي", FATHA], ["س", DAMMA], ["و", ""], ["ء", DAMMA], ["و", ""], ["ا", SILENT]]  # ليسوءوا
        rules.add("hamza_waw")
    if any(c in ("الاقصا", "طغا", "تترا") for c in cores) and cl[-1][0] == "ا":
        cl[-1] = ["ى", ""]  # الأقصى، طغى، تترى (the rasm writes a final alef)
        rules.add("final_alef")
    if key in ("ويبصط", "يبصط", "بصطة"):
        for c in cl:
            if c[0] == "ص":
                c[0] = "س"
                rules.add("sad_sin")
    if len(cl) >= 2 and cl[-1][0] == "ا" and SILENT in cl[-1][1] and cl[-2][0] == "ؤ":
        p = cl[-3] if len(cl) >= 3 else ["", ""]
        alef_before = p[0] in ("ا",) or DAGGER in p[1]
        seat = "ء" if alef_before else ("ؤ" if _vowel(p[1]) == "u" else "أ")
        cl = cl[:-2] + [[seat, ""]]  # الملؤا -> الملأ, العلمؤا -> العلماء, امرؤا -> امرؤ
        rules.add("waw_hamza_final")

    # B. silent letters, small letters
    out = []
    for i, (b, m) in enumerate(cl):
        nxt = cl[i + 1][0] if i + 1 < len(cl) else ""
        if SILENT in m and b == "و" and not any(c.startswith("اول") for c in cores):
            rules.add("silent_letter")  # سأوريكم -> سأريكم
            continue
        if SILENT in m and b == "ي":
            if out and out[-1][0] == "إ" and len(out) >= 2 and out[-2][0] == "ل" and "مل" in key:
                out[-1][0] = "ئ"  # ملإيه -> ملئه
            else:
                rules.add("silent_letter")  # أفإين -> أفإن، نبإي -> نبإ، بأييد -> بأيد
            continue
        if SILENT in m and b == "ا" and (nxt == "ي" or (out and out[-1][0] == "أ")):
            continue  # لشاىء -> لشيء، لأاذبحنه -> لأذبحنه
        m = m.replace(SILENT, "").replace(SMALL_HIGH_SEEN, "")
        extra = None
        if SMALL_YA in m:
            m = m.replace(SMALL_YA, "")
            if b != "ه":
                extra = ["ي", ""]  # يحيي، إيلافهم، آتاني (after ه it is the pronoun's long vowel: به)
                rules.add("small_ya")
        if SMALL_HIGH_YA in m:
            m = m.replace(SMALL_HIGH_YA, "")
            rules.add("small_ya")
            if b == TATWEEL:
                b = "ي"  # إبراهيم، النبيين
            else:
                extra = ["ي", ""]
        if SMALL_WAW in m:
            m = m.replace(SMALL_WAW, "")
            if b == TATWEEL:
                b = "و"  # ليسوءوا
                rules.add("small_waw")
            elif b != "ه" and not any(c == "داود" for c in cores):
                extra = ["و", ""]  # يلوون، الغاوون، ووري
                rules.add("small_waw")
        if SMALL_HIGH_NOON in m:
            m = m.replace(SMALL_HIGH_NOON, "")
            if b == TATWEEL:
                b = "ن"  # ننجي
                rules.add("small_noon")
        out.append([b, m])
        if extra:
            out.append(extra)
    cl = out

    # C. hamza seats
    out = []
    i = 0
    while i < len(cl):
        b, m = cl[i]
        if not _is_hamza(cl[i]):
            out.append([b, m])
            i += 1
            continue
        v = _vowel(m)
        prevs = [c for c in out if c[0] != TATWEEL or DAGGER in c[1]]
        rest = [c for c in cl[i + 1 :] if c[0] != TATWEEL or set(c[1]) & {DAGGER, HAMZA_ABOVE}]
        nxt_alef = DAGGER in m or (rest and (rest[0][0] == "ا" or (rest[0][0] == TATWEEL and DAGGER in rest[0][1])))
        tanween_alef = any(ch in m for ch in ("ً", "ٗ")) and len(rest) == 1 and rest[0][0] == "ا"
        initial = not prevs or (len(prevs) <= 3 and all(c[0] in PREFIX for c in prevs)) \
            or (len(prevs) == 1 and prevs[0][0] == "أ" and b == "ء")
        p = prevs[-1] if prevs else None
        pv = _vowel(p[1]) if p else None
        alef_long = bool(p) and (p[0] in ("ا", "آ") or DAGGER in p[1])
        ya_sakin = bool(p) and p[0] == "ي" and pv in (None, "0")
        waw_sakin = bool(p) and p[0] == "و" and pv in (None, "0")
        if initial:
            seat = "إ" if v == "i" else "أ"
        elif not rest:  # final hamza
            if alef_long or ya_sakin or waw_sakin or pv == "0":
                seat = "ء"
            else:
                seat = {"i": "ئ", "u": "ؤ"}.get(pv, "أ")
        elif alef_long or waw_sakin:
            seat = "ئ" if v == "i" else "ء"  # إسرائيل / تساءلون، سوءة، الموءودة، أساءوا
        elif v == "i" or pv == "i" or ya_sakin:
            seat = "ئ"  # شيئا، السيئات، متكئين، يستهزئون
        elif v == "u" or pv == "u":
            seat = "ؤ"  # يؤوده، رؤوف، مسؤولا، رؤوس
        else:
            seat = "أ"
        marks = "".join(ch for ch in m if ch in _HARAKAT_KEEP)
        skip_next = False
        if seat in ("أ",) and v == "a" and nxt_alef and not tanween_alef:
            seat, marks = "آ", ""  # بآيات، القرآن، الآن، مآب
            skip_next = DAGGER not in m
        if tanween_alef and seat == "أ":
            skip_next = True  # خطأً، ملجأً
        if seat in ("ئ", "ؤ") and b in ("ء", TATWEEL):
            rules.add("hamza_waw" if seat == "ؤ" else "hamza_ya")
        if b == "ي" and seat != "ئ":
            rules.add("hamza_dropped_ya")  # تلقاء، وراء، آناء (Uthmani writes the hamza on a ي)
        out.append([seat, marks])
        i += 1
        if skip_next:
            while i < len(cl) and cl[i][0] == TATWEEL and DAGGER not in cl[i][1]:
                i += 1
            if i < len(cl) and (cl[i][0] == "ا" or (cl[i][0] == TATWEEL and DAGGER in cl[i][1])):
                i += 1
    cl = out

    # D. alef forms
    out = []
    for i, (b, m) in enumerate(cl):
        later = any(c[0] not in (TATWEEL,) for c in cl[i + 1 :])
        if b == "ٱ":
            b = "ا"
        if DAGGER in m:
            m = m.replace(DAGGER, "")
            if b == "ى":
                if later:
                    b = "ا"  # ضحاها، مأواهم، التوراة
                    rules.add("alef_maqsura_mid")
            elif b == "و" and _vowel(m) is None:
                b = "ا"  # الصلاة، الزكاة، الحياة
                if i + 1 < len(cl) and cl[i + 1][0] == "ا":
                    cl[i + 1] = [TATWEEL, ""]  # الربوا -> الربا
            elif b == TATWEEL:
                if no_alef:
                    continue
                b = "ا"
            elif not no_alef:
                out.append([b, m.replace(MADDA, "")])
                out.append(["ا", ""])
                continue
        m = m.replace(MADDA, "").replace(HAMZA_ABOVE, "").replace(HAMZA_BELOW, "")
        if b == TATWEEL:
            continue
        out.append([b, m])
    return out


def to_common_word(token: str, harakat: bool) -> tuple[str, set]:
    """One Uthmani word -> common spelling (one or two words) and the rules that changed letters."""
    rules: set = set()
    cl = _parse(_DROP_EARLY.sub("", token))
    words = []
    for part in _split_vocative(cl):
        conv = _common_word(part, rules)
        if harakat:
            words.append("".join(b + ("" if b == "آ" else "".join(_HARAKAT_KEEP.get(ch, "") for ch in m)) for b, m in conv))
        else:
            words.append("".join(b for b, _ in conv))
    return " ".join(w for w in words if w), rules


def strip_marks(token: str) -> str:
    return _ALL_MARKS.sub("", _DROP_EARLY.sub("", token))
