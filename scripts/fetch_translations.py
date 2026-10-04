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
