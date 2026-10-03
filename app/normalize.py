"""Arabic and English text normalization for matching.

Two levels for Arabic:
- `normalize_ar`: readable, keeps spaces and letters, removes diacritics and Uthmani marks.
- `skeleton_ar`: consonantal skeleton used for matching. It also drops alef, hamza and spaces,
  so Uthmani spelling (ٱلسَّمَٰوَٰتِ) and common spelling (السماوات) meet on the same string.
"""
import re
import unicodedata

# Harakat, tanween, shadda, sukun, Quranic annotation marks, small high letters, tatweel.
_DIACRITICS = re.compile(
    "[ؐ-ًؚ-ٰٟۖ-ۜ۟-۪ۨ-ۭ࣓-ࣿـ]"
)
_UTHMANI_WAW_ALEF = re.compile("وٰ")  # الصلوٰة -> الصلاة
_AR_LETTERS = re.compile("[^ء-ي\\s]")
_SPACES = re.compile(r"\s+")

_LETTER_MAP = str.maketrans({
    "أ": "ا", "إ": "ا", "آ": "ا", "ٱ": "ا", "ٲ": "ا", "ٳ": "ا",
    "ى": "ي", "ئ": "ي", "ی": "ي",
    "ؤ": "و",
    "ة": "ه",
    "ک": "ك",
})


def normalize_ar(text: str) -> str:
    text = unicodedata.normalize("NFC", text)
    text = _UTHMANI_WAW_ALEF.sub("ا", text)
    text = _DIACRITICS.sub("", text)
    text = text.translate(_LETTER_MAP)
    text = _AR_LETTERS.sub(" ", text)
    return _SPACES.sub(" ", text).strip()


def skeleton_ar(text: str) -> str:
    text = normalize_ar(text)
    return re.sub("[اء\\s]", "", text)


def ar_words(text: str) -> list[str]:
    return normalize_ar(text).split()


def word_skeleton(word: str) -> str:
    return re.sub("[اء]", "", word)


def normalize_en(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = re.sub(r"\[[^\]]*\]|\([^)]*\)", " ", text)  # translators' bracketed glosses and footnote markers
    text = re.sub(r"[^a-zA-Z\s]", " ", text).lower()
    return _SPACES.sub(" ", text).strip()


def is_arabic(text: str) -> bool:
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return False
    arabic = sum(1 for c in letters if "؀" <= c <= "ۿ" or "ݐ" <= c <= "ݿ")
    return arabic / len(letters) > 0.5


# Plan item 36: Urdu and Indonesian quotes are matched against the King Fahd Complex translations.
_UR_MAP = str.maketrans({
    "أ": "ا", "إ": "ا", "آ": "ا", "ٱ": "ا",
    "ي": "ی", "ى": "ی", "ئ": "ی", "ې": "ی",
    "ك": "ک",
    "ه": "ہ", "ة": "ہ", "ۃ": "ہ", "ۂ": "ہ",
    "ؤ": "و",
})
_URDU_ONLY = re.compile("[ٹڈڑںےۓہ]")
_EN_WORDS = re.compile(r"\b(?:the|and|of|to|is|in|that|he|said|you|we|they|this|for|with|who|not|be)\b", re.I)
_ID_WORDS = re.compile(
    r"\b(?:dan|yang|ini|itu|dengan|untuk|dari|tidak|kita|kami|adalah|akan|bahwa|ia|kepada|mereka|orang|atas|kamu|sesungguhnya)\b",
    re.I,
)


def normalize_ur(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)  # ﻻ in the source text -> لا
    text = re.sub(r"\[[^\]]*\]|\([^)]*\)", " ", text)
    text = _DIACRITICS.sub("", text).translate(_UR_MAP)
    text = "".join(c if unicodedata.category(c).startswith("L") else " " for c in text)
    return _SPACES.sub(" ", text).strip()


def normalize_id(text: str) -> str:
    return normalize_en(text.replace("’", "'").replace("'", ""))


def quote_lang(text: str) -> str:
    """ar | ur | en | id: which index a quote is matched against."""
    if is_arabic(text):
        return "ur" if len(_URDU_ONLY.findall(text)) >= 2 else "ar"
    n_id, n_en = len(_ID_WORDS.findall(text)), len(_EN_WORDS.findall(text))
    return "id" if n_id >= 2 and n_id > n_en else "en"
