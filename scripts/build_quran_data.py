"""Build data/quran.json.

Arabic: Uthmani (Hafs) text of the King Fahd Glorious Qur'an Printing Complex, from the npm package
quran-json 3.1.2 (CC BY-SA 4.0), which takes it from QuranEnc. Checked against Quranpedia's King Fahd
Complex snapshot (qpc-hafs): identical on all 6,236 verses after encoding normalisation.

English shown to the reader: the King Fahd Complex translation by Dr. Muhammad Taqi-ud-Din al-Hilali and
Dr. Muhammad Muhsin Khan (Madinah, 1417 AH), QuranEnc english_hilali_khan v1.1.2. It is book 1948 on
quranpedia.net. Text copied verbatim, footnotes kept.

English used only to recognise English quotes: Saheeh International, QuranEnc english_saheeh v1.1.2
(books 1947 and 13638 on quranpedia.net). Most English posts quote this wording.

Both QuranEnc files come from a pinned snapshot in github.com/risan/quran-json and are checked by sha256.

Usage: python scripts/build_quran_data.py <path to quran-json 3.1.2 dist>
"""
import hashlib
import json
import sys
import urllib.request
from pathlib import Path

SNAPSHOT = "https://raw.githubusercontent.com/risan/quran-json/e20bba6abe2cc37f77f5aae5266f39cc55b9ca77/data/quranenc/"
FILES = {
    "english_hilali_khan": "ec5c98ca82f3bd65995b0702c7a00ab1f6689d34056f9d157eb4750545170515",
    "english_saheeh": "c12b5bed64837cb744e075fdd3b79f885aee1522d92468f36c38ff565bfdc439",
}


def quranenc(key: str) -> dict:
    raw = urllib.request.urlopen(SNAPSHOT + key + ".json", timeout=60).read()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != FILES[key]:
        sys.exit(f"{key}: sha256 {digest} does not match the pinned snapshot")
    data = json.loads(raw)
    return {(v["chapter"], v["verse"]): v for s in data.values() for v in s}


dist = Path(sys.argv[1])
ar = json.loads((dist / "quran_en.json").read_text(encoding="utf-8"))
hilali, saheeh = quranenc("english_hilali_khan"), quranenc("english_saheeh")

surahs, verses = [], []
for s in ar:
    surahs.append({"n": s["id"], "ar": s["name"], "en": s["translation"], "tr": s["transliteration"]})
    for v in s["verses"]:
        h = hilali[(s["id"], v["id"])]
        verses.append([s["id"], v["id"], v["text"], h["text"], saheeh[(s["id"], v["id"])]["text"], h.get("footnotes", "")])

out = Path(__file__).resolve().parent.parent / "data" / "quran.json"
out.write_text(
    json.dumps({"source": {
        "arabic": "Uthmani (Hafs) text, King Fahd Glorious Qur'an Printing Complex (via QuranEnc / quran-json 3.1.2)",
        "english": "Al-Hilali & Muhsin Khan, King Fahd Complex 1417 AH, via QuranEnc.com english_hilali_khan v1.1.2",
        "english_match": "Saheeh International, via QuranEnc.com english_saheeh v1.1.2 (matching only)",
    }, "verses_format": ["surah", "ayah", "arabic", "english", "english_match", "english_footnotes"],
        "surahs": surahs, "verses": verses}, ensure_ascii=False, separators=(",", ":")),
    encoding="utf-8",
)
print(f"{len(surahs)} surahs, {len(verses)} verses -> {out}")
