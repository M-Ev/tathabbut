"""Plan item 14: does a saying borrow the grading of a hadith it shares most words with?

Each case in eval/trap_cases.jsonl changes or adds words to a known narration. Through the live site's
POST /api/check (Dorar refuses some clouds directly), the script records the approved gradings the site shows,
then applies, offline, the matching rules before and after the coverage guard (4 Oct) to those same results:

- borrowed: the case is reported "graded" (found in that wording), so a grading of another text is lent to it.
- lost: of the Arabic cases in eval/hadith_cases.jsonl that were graded before, how many are no longer graded
  (read from their recorded live gradings), the cost of the guard.

    python3 eval/run_trap_eval.py --via-space https://3rb-tathabbut.hf.space   -> eval/trap_report.md
    python3 eval/run_trap_eval.py   (offline: re-score recorded results only)
"""
import argparse
import asyncio
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from app import pipeline as P  # noqa: E402
from app.dorar import DorarHadith, DorarResult  # noqa: E402
from app.scholars import SCHOLARS  # noqa: E402

HERE = ROOT / "eval"
_IDS = {s.key: (s.name_ar, str(s.died_ah)) for s in (SCHOLARS.values() if isinstance(SCHOLARS, dict) else SCHOLARS)}


def _status(quote: str, gradings: list[dict], guard: bool) -> tuple[str, str]:
    hs = [DorarHadith(text=g["text"], mohdith=_IDS[g["scholar"]][0], mohdith_id=_IDS[g["scholar"]][1],
                      book=g["book"], number=g["number"], grade=g["grade"]) for g in gradings if g.get("scholar") in _IDS]
    keep = P._match_kind
    if not guard:
        P._match_kind = lambda q, t: {"match": "same", "coverage": 100, "missing_words": [], "source_words": 0}
    try:
        info = P._grade_groups(quote, DorarResult(query=quote, method="w", hadiths=hs))
    finally:
        P._match_kind = keep
    st = "graded" if info["best_strong_similarity"] >= P.STRONG_MATCH else ("found_similar" if info["count"] else "not_found")
    r = {"status": st, "notes": [], "hadith": info}
    return st, P._hadith_tier(r) if st == "graded" else ("verify" if st == "found_similar" else "refer")


async def fetch(cases, base):
    import httpx
    async with httpx.AsyncClient(timeout=90) as http:
        for c in cases:
            r = await http.post(base.rstrip("/") + "/api/check", json={"text": c["text"]})
            r.raise_for_status()
            cit = next((x for x in r.json()["citations"] if x["type"] == "hadith"), None)
            items = [i for g in ((cit or {}).get("hadith") or {}).get("groups", []) for i in g["items"]]
            c["live"] = {"checked_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ"), "via": base,
                         "status": cit and cit["status"],
                         "gradings": [{"scholar": i["scholar_key"], "grade": i["grade"], "book": i["book"], "number": i["number"],
                                       "text": i["text"], "url": i["url"], "similarity": i["similarity"]} for i in items]}
            print(c["id"], c["live"]["status"], len(items))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--via-space")
    a = ap.parse_args()
    path = HERE / "trap_cases.jsonl"
    cases = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
    if a.via_space:
        asyncio.run(fetch(cases, a.via_space))
        path.write_text("".join(json.dumps(c, ensure_ascii=False) + "\n" for c in cases), encoding="utf-8")
    rows, before_b, after_b = [], 0, 0
    for c in cases:
        g = (c.get("live") or {}).get("gradings")
        if g is None:
            continue
        b, a2 = _status(c["quote"], g, False), _status(c["quote"], g, True)
        before_b += b[0] == "graded"
        after_b += a2[0] == "graded"
        rows.append((c, b, a2))
    real = [json.loads(l) for l in (HERE / "hadith_cases.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    lost, base_n, lost_ids = 0, 0, []
    for c in real:
        g = [x for x in c["evidence"].get("gradings", []) if x.get("source") == "live_app"]
        if c["lang"] != "ar" or not g:
            continue
        if _status(c["quote"], g, False)[0] == "graded":
            base_n += 1
            if _status(c["quote"], g, True)[0] != "graded":
                lost += 1
                lost_ids.append(c["id"])
    out = ["# Sayings that share words with a hadith (plan item 14)", "",
           f"{len(rows)} cases, each a known narration with words changed or added (drafted by Claude; the Sharia reviewer confirms each).",
           "Gradings: what the live site showed (recorded in `trap_cases.jsonl`); rules applied offline before and after the coverage guard.", "",
           f"**Reported as found in that wording, so another text's grading is lent to it: {before_b} of {len(rows)} before, {after_b} of {len(rows)} after.**",
           f"Cost: of {base_n} hadith in `hadith_cases.jsonl` graded before, {lost} no longer graded after" + (f" ({', '.join(lost_ids)}; they show as a similar wording)." if lost else "."), "",
           "| case | quote | close to | before | after |", "|---|---|---|---|---|"]
    for c, b, a2 in rows:
        out.append(f"| {c['id']} | {c['quote']} | {c['close_to']} | {b[0]} / {b[1]} | {a2[0]} / {a2[1]} |")
    out += ["", "Cases still reported in that wording after the guard, with the narration that matched, for the reviewer:", ""]
    for c, b, a2 in rows:
        if a2[0] != "graded":
            continue
        best = max(c["live"]["gradings"], key=lambda g: (P._match_kind(c["quote"], g["text"])["match"] != "partial", g["similarity"]))
        out.append(f"- {c['id']}: {best['scholar']} «{best['grade']}» on «{best['text'][:120]}» ({best['url']})")
    (HERE / "trap_report.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print("\n".join(out[:7]))


if __name__ == "__main__":
    main()
