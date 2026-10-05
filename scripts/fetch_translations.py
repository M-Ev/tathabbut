"""Plan item 36: snapshot of King Fahd Complex translations as published on quranpedia.net (named in the
challenge's scientific package), for matching quotes in Urdu and Indonesian.

    python3 scripts/fetch_translations.py ur   -> data/translations/ur_junagarhi.json
    python3 scripts/fetch_translations.py id   -> data/translations/id_kfc.json

One page per surah, one second apart. Each surah's verse count must equal the Mushaf's, or the run stops.
The output records the source URL pattern, the fetch date and a sha256 of the verse text.
"""
import hashlib
import html
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent.parent
BOOKS = {
    "ur": {"book": 1966, "file": "ur_junagarhi.json", "name_ar": "الترجمة الأردية، محمد إبراهيم جوناكري",
           "name_en": "Urdu translation by Muhammad Ibrahim Junagarhi (King Fahd Complex print)"},
    "id": {"book": 1961, "file": "id_kfc.json", "name_ar": "الترجمة الإندونيسية - المجمع، وزارة الشؤون الإسلامية الإندونيسية",
           "name_en": "Indonesian translation (King Fahd Complex), Indonesian Ministry of Religious Affairs"},
    "fr": {"book": 27812, "file": "fr_hamidullah.json", "name_ar": "الترجمة الفرنسية، محمد حميد الله",
           "name_en": "French translation by Muhammad Hamidullah"},
    # Shown to readers of these languages beside the Mushaf (owner's decision, 5 Oct); not used to match quotes.
    "es": {"book": 1950, "file": "es_garcia.json", "name_ar": "الترجمة الإسبانية، محمد عيسى غارسيا",
           "name_en": "Spanish translation by Muhammad Isa Garcia", "name": "Traducción de Muhammad Isa García"},
    "zh": {"book": 1974, "file": "zh_makin.json", "name_ar": "الترجمة الصينية، محمد مكين",
           "name_en": "Chinese translation by Muhammad Makin (Ma Jian)", "name": "马坚译本"},
    "ja": {"book": 1976, "file": "ja_mita.json", "name_ar": "الترجمة اليابانية، رايتشي ميتا",
           "name_en": "Japanese translation by Ryoichi Mita", "name": "三田了一訳"},
    "bn": {"book": 1967, "file": "bn_zakaria.json", "name_ar": "الترجمة البنغالية، أبو بكر محمد زكريا",
           "name_en": "Bengali translation by Abu Bakr Muhammad Zakaria", "name": "আবু বকর মুহাম্মাদ যাকারিয়া অনূদিত"},
    "tr": {"book": 1959, "file": "tr_kfc.json", "name_ar": "الترجمة التركية، مجمع الملك فهد",
           "name_en": "Turkish translation (King Fahd Complex)", "name": "Kral Fahd Kompleksi Türkçe meali"},
    "hi": {"book": 1986, "file": "hi_umari.json", "name_ar": "الترجمة الهندية، عزيز الحق العمري",
           "name_en": "Hindi translation by Aziz ul-Haq al-Umari", "name": "अज़ीज़ुल हक़ उमरी अनुवाद"},
}
URL = "https://quranpedia.net/surah/1/{s}/book/{b}"
_PROSE = re.compile(r'<article class="verse-block".*?<div class="prose[^>]*>(.*?)</div>\s*(?:<div class="(?:foot-notes|hamesh|margin)|\s*</div>)', re.S)


def _clean(fragment: str) -> str:
    fragment = re.split(r'<div class="(?:foot-notes|hamesh|margin)', fragment)[0]
    t = html.unescape(re.sub(r"<[^>]+>", " ", fragment))
    return re.sub(r"\s*\*+(?=\s|$)", "", re.sub(r"\s+", " ", t)).strip()  # «*» marks a footnote


def parse(page: str) -> list[str]:
    return [_clean(m.group(1)) for m in _PROSE.finditer(page)]


def main(lang: str) -> int:
    meta = BOOKS[lang]
    quran = json.loads((ROOT / "data" / "quran.json").read_text(encoding="utf-8"))
    counts = {}
    for v in quran["verses"]:  # [surah, ayah, arabic, ...]
        counts[v[0]] = counts.get(v[0], 0) + 1
    out, http = {}, httpx.Client(timeout=60, follow_redirects=True, headers={"User-Agent": "Tathabbut (islamicaich challenge; quranpedia.net snapshot)"})
    for s in range(1, 115):
        page = http.get(URL.format(s=s, b=meta["book"])).text
        verses = parse(page)
        if len(verses) != counts[s]:
            print(f"surah {s}: {len(verses)} verses parsed, Mushaf has {counts[s]}; stopping", file=sys.stderr)
            return 1
        for a, text in enumerate(verses, 1):
            out[f"{s}:{a}"] = text
        print(s, len(verses), flush=True)
        time.sleep(1)
    blob = json.dumps(out, ensure_ascii=False, sort_keys=True)
    doc = {"source": meta | {"url": URL.replace("{b}", str(meta["book"])), "site": "quranpedia.net"},
           "fetched_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
           "sha256": hashlib.sha256(blob.encode()).hexdigest(), "verses": out}
    p = ROOT / "data" / "translations" / meta["file"]
    p.parent.mkdir(exist_ok=True)
    p.write_text(json.dumps(doc, ensure_ascii=False, indent=0), encoding="utf-8")
    print("wrote", p, len(out))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
