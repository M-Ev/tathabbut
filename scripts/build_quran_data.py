"""Build data/quran.json from the quran-json npm package (v3.1.2, CC-BY-4.0).

Arabic: Uthmani text of the King Fahd Glorious Qur'an Printing Complex, via QuranEnc.
English: Saheeh International, via Tanzil.

Usage: python scripts/build_quran_data.py <path to quran-json/dist>
"""
import json
import sys
from pathlib import Path

dist = Path(sys.argv[1])
en = json.loads((dist / "quran_en.json").read_text(encoding="utf-8"))

surahs, verses = [], []
for s in en:
    surahs.append({"n": s["id"], "ar": s["name"], "en": s["translation"], "tr": s["transliteration"]})
    for v in s["verses"]:
        verses.append([s["id"], v["id"], v["text"], v["translation"]])

out = Path(__file__).resolve().parent.parent / "data" / "quran.json"
out.write_text(
    json.dumps({"source": {
        "arabic": "Uthmani text, King Fahd Glorious Qur'an Printing Complex (via QuranEnc / quran-json 3.1.2)",
        "english": "Saheeh International (via Tanzil / quran-json 3.1.2)",
    }, "surahs": surahs, "verses": verses}, ensure_ascii=False, separators=(",", ":")),
    encoding="utf-8",
)
print(f"{len(surahs)} surahs, {len(verses)} verses -> {out}")
