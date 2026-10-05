#!/usr/bin/env python3
"""Build data/archive.json: the public archive of commonly circulated citations, as the tool checked them.

Each entry is one citation from the team's evaluation files (eval/hadith_cases.jsonl, the Quran cases of
eval/cases.jsonl), sent to a running Tathabbut (`POST /api/check`) and stored as the site showed it: the source
text, the approved scholars' gradings verbatim with book, number and link, the evidence status, and the date.
Nothing is written by hand or by a model; the archive is a record of what the tool returned, marked as not yet
reviewed by the team's Sharia reviewer until she reviews it.

    python3 scripts/build_archive.py https://3rb-tathabbut.hf.space
"""
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from app.pipeline import _verdicts  # noqa: E402  same grouping as the site


def cases():
    for line in (ROOT / "eval" / "hadith_cases.jsonl").read_text(encoding="utf-8").splitlines():
        c = json.loads(line)
        yield c["id"], c["text"], c.get("selection_group", "")
    for line in (ROOT / "eval" / "cases.jsonl").read_text(encoding="utf-8").splitlines():
        c = json.loads(line)
        if c["id"].startswith("q-"):
            yield c["id"], c["text"], "quran"


def compact(c: dict) -> dict:
    out = {"type": c["type"], "quote": c["quote"], "lang": c["lang"], "status": c["status"], "tier": c["tier"],
           "notes": c.get("notes", [])}
    q, h = c.get("quran"), c.get("hadith")
    if q and q.get("ref"):
        out["quran"] = {k: q.get(k) for k in ("ref", "surah_name_ar", "surah_name_en", "mushaf_text", "url", "reference_ok", "diff")}
        out["quran"]["diff"] = [d for d in q.get("diff") or [] if d.get("op") != "equal"]
        if q.get("cited"):
            out["quran"]["cited_ref"] = f'{q["cited"].get("surah")}:{q["cited"].get("ayah")}'
    if h and h.get("groups") is not None:
        items = [i for g in h["groups"] for i in g["items"]]
        out["hadith"] = {
            "search_url": h.get("search_url"), "sahihayn": h.get("sahihayn") or [],
            "verdicts": h.get("verdicts") or _verdicts(items),
            "gradings": [{k: i.get(k) for k in ("scholar_ar", "scholar_en", "died_ah", "grade", "book", "number", "text", "url", "match")}
                         for i in sorted(items, key=lambda i: i["died_ah"]) if i.get("similarity", 0) >= 85][:8],
        }
    if c.get("search_wording_ar"):
        out["search_wording_ar"] = c["search_wording_ar"]
    if c.get("referral"):
        out["referral"] = c["referral"]
    return out


def main(site: str):
    entries = []
    with httpx.Client(timeout=300) as http:
        for cid, text, group in cases():
            for _ in range(10):  # the site allows 20 checks per 10 minutes per visitor
                r = http.post(site.rstrip("/") + "/api/check", json={"text": text, "deep": True})
                if r.status_code != 429:
                    break
                time.sleep(60)
            r.raise_for_status()
            d = r.json()
            for c in d["citations"]:
                entries.append({"id": cid if len(d["citations"]) == 1 else f'{cid}-{c["id"]}', "group": group,
                                "text": text, **compact(c), "model": d["model"].get("answered_by") or []})
            print(cid, [c["tier"] for c in d["citations"]], flush=True)
            time.sleep(30)
    out = {"_about": "Commonly circulated citations as Tathabbut checked them (scripts/build_archive.py). Gradings are "
                     "quoted verbatim from Dorar with their links; not yet reviewed by the team's Sharia reviewer.",
           "checked_at": datetime.now(timezone.utc).strftime("%Y-%m-%d"), "site": site, "reviewed": False,
           "entries": entries}
    (ROOT / "data" / "archive.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(len(entries), "entries")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "https://3rb-tathabbut.hf.space")
