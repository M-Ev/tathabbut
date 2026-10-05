"""Ask the live site the 25 visitors' questions in eval/personas.json and say which got what they should.

    python3 scripts/persona_check.py [https://3rb-tathabbut.hf.space]

Paced under the site's limit (20 checks per 10 minutes), so a full run takes about 13 minutes."""
import json
import sys
import time
from pathlib import Path

import httpx

BASE = (sys.argv[1] if len(sys.argv) > 1 else "https://3rb-tathabbut.hf.space").rstrip("/")
CASES = json.loads((Path(__file__).resolve().parent.parent / "eval" / "personas.json").read_text(encoding="utf-8"))


def fatwa_count(r):
    return sum(len(sc.get("fatwas") or []) for sc in ((r.get("level_d") or {}).get("fatwas") or {}).get("scholars", []))


def problems(r, e):
    cits = r.get("citations", [])
    hd = [c for c in cits if c["type"] == "hadith"]
    q = " ".join((c.get("hadith") or {}).get("query", "") for c in hd)
    out = []
    if e.get("not_blank") and not cits and not r.get("level_d"):
        out.append("blank report")
    if "hadith_query_has" in e and e["hadith_query_has"] not in q:
        out.append(f"hadith searched as «{q}»")
    if "hadith_query_lacks" in e and e["hadith_query_lacks"] in q.split():
        out.append(f"hadith searched as «{q}»")
    if e.get("fatwas") and not fatwa_count(r):
        out.append("no fatwa found")
    if e.get("answer") and not (r.get("level_d") or {}).get("answer"):
        out.append("no verbatim answer")
    if e.get("fabricated") and not any((c.get("hadith") or {}).get("fabricated_by") for c in hd):
        out.append("fabrication not shown")
    if e.get("wrong_reference") and not any("wrong_reference" in c["notes"] for c in cits):
        out.append("wrong surah not caught")
    if e.get("quran_verified") and not any(c["type"] == "quran" and c["status"] == "verified" for c in cits):
        out.append("verse not found")
    if e.get("asked_about") and r.get("asked_about") != e["asked_about"]:
        out.append(f"read as {r.get('asked_about')}")
    if e.get("hadith_not_supported_or_loose") and not any(
            c["tier"] in ("not_supported", "refer") or (c.get("hadith") or {}).get("loose_only") for c in hd):
        out.append("not marked as unsupported")
    return out


def main():
    version = httpx.get(BASE + "/api/health", timeout=60).json().get("version", {}).get("commit", "?")
    print("version:", version)
    bad, rows = 0, []
    for case in CASES:
        t0 = time.time()
        try:
            r = httpx.post(BASE + "/api/check", json={"text": case["text"]}, timeout=120).json()
            p = problems(r, case["expect"])
        except Exception as e:  # noqa: BLE001
            p = [f"request failed: {e}"]
        bad += bool(p)
        secs = time.time() - t0
        rows.append(f"| {case['who']} | {case['text'][:70]} | {'✗ ' + '; '.join(p) if p else '✓'} | {secs:.1f} |")
        print(("FAIL " if p else "ok   ") + f"{case['who']:<20} {secs:5.1f}s  " + "; ".join(p), flush=True)
        time.sleep(max(0, 32 - (time.time() - t0)))
    print(f"\n{len(CASES) - bad}/{len(CASES)} as expected")
    report = Path(__file__).resolve().parent.parent / "eval" / "personas_report.md"
    report.write_text(
        "# Visitors' questions on the live site\n\n"
        f"Run {time.strftime('%Y-%m-%d %H:%M', time.gmtime())} UTC on {BASE} (commit `{version}`) by `scripts/persona_check.py`; "
        f"cases and what each must get: `eval/personas.json`.\n\n**{len(CASES) - bad}/{len(CASES)} as expected.**\n\n"
        "| Visitor | Question | Result | Seconds |\n|---|---|---|---|\n" + "\n".join(rows) + "\n", encoding="utf-8")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
