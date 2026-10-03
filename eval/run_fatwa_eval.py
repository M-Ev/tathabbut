"""Item 45: does a fitting fatwa appear among the three shown per scholar?

Live: queries binbaz.org.sa and binothaimeen.net with each case's question (topic words only, as the app does).
`acceptable` in eval/fatwa_cases.jsonl lists fatwa URLs the team's Sharia reviewer judges fitting; until she
fills it, the report lists what was shown so she can mark it, and no hit rate is claimed.

    python eval/run_fatwa_eval.py   -> eval/fatwa_report.md
"""
import asyncio
import json
import sys
import time
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app import fatwa  # noqa: E402

HERE = Path(__file__).resolve().parent


async def main():
    cases = [json.loads(l) for l in (HERE / "fatwa_cases.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    rows, marked, hits, times = [], 0, 0, []
    for c in cases:
        t = time.perf_counter()
        res = await fatwa.find_fatwas(c["question"])
        times.append(time.perf_counter() - t)
        shown = [(s["key"], f["title"], f["url"], f["score"]) for s in res["scholars"] for f in s["fatwas"]]
        errors = [s["key"] for s in res["scholars"] if s.get("error")]
        hit = None
        if c["acceptable"]:
            marked += 1
            hit = any(u in c["acceptable"] for _, _, u, _ in shown)
            hits += hit
        rows.append((c, res["terms"], shown, errors, hit))

    out = [f"# Fatwa matching, item 45 ({date.today().isoformat()}, live)", ""]
    out.append(f"{len(cases)} questions. Shown per question: up to {fatwa.PER_SCHOLAR} fatwas per scholar above {fatwa.MIN_SCORE}% word overlap.")
    if marked:
        out.append(f"**A fitting fatwa among those shown: {hits} of {marked}** questions the Sharia reviewer marked.")
    else:
        out.append("**No hit rate yet.** The Sharia reviewer has not marked fitting fatwas; the questions are drafts (see `origin`). Mark the URLs she accepts in `acceptable`.")
    empty = sum(1 for r in rows if not r[2])
    out.append(f"Questions with nothing shown (referral only): {empty} of {len(cases)}. Median time: {sorted(times)[len(times)//2]:.1f} s.")
    out.append("")
    for c, terms, shown, errors, hit in rows:
        mark = "" if hit is None else (" ✓" if hit else " ✗")
        out.append(f"## {c['id']}{mark}: {c['question']}")
        out.append(f"Words searched: «{terms}». Origin: {c['origin']}." + (f" Site errors: {', '.join(errors)}." if errors else ""))
        out.append("")
        if not shown:
            out.append("Nothing above the floor: referral to the official body only.")
        for key, title, url, score in shown:
            out.append(f"- {key} · {score:.0f}% · [{title}]({url})")
        out.append("")
    (HERE / "fatwa_report.md").write_text("\n".join(out), encoding="utf-8")
    print("\n".join(out[:6]))


if __name__ == "__main__":
    asyncio.run(main())
