"""Run the evaluation set and write eval/report.md.

Metrics:
- extraction recall: expected citations that were found;
- tracing accuracy: found citations whose status (and reference, when given) is as expected;
- abstention: of the cases that should be referred (not found / not in Mushaf), how many were referred,
  and how many citations were wrongly referred.
"""
import argparse
import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.pipeline import check_text  # noqa: E402

ABSTAIN = {"not_found", "not_in_mushaf"}


def _ok(exp: dict, got: dict) -> bool:
    if got["status"] != exp["status"]:
        return False
    q = got.get("quran") or {}
    if "ref" in exp and q.get("ref") != exp["ref"]:
        return False
    if "reference_ok" in exp and q.get("reference_ok") != exp["reference_ok"]:
        return False
    h = got.get("hadith") or {}
    if exp.get("fabricated") and not h.get("fabricated_by"):
        return False
    if exp.get("scholars_any"):
        keys = {i["scholar_key"] for g in h.get("groups", []) for i in g["items"]}
        if not keys & set(exp["scholars_any"]):
            return False
    return True


async def main(deep: bool, path: Path):
    cases = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
    expected = found = traced = should_abstain = abstained = false_abstain = extra = 0
    rows = []
    for case in cases:
        r = await check_text(case["text"], deep=deep)
        got = r["citations"]
        extra += max(0, len(got) - len(case["expected"]))
        for k, exp in enumerate(case["expected"]):
            expected += 1
            g = next((c for c in got if c["type"] == exp["type"]), got[k] if k < len(got) else None)
            if g is None:
                rows.append((case["id"], exp["status"], "missed", "✗"))
                continue
            found += 1
            ok = _ok(exp, g)
            traced += ok
            if exp["status"] in ABSTAIN:
                should_abstain += 1
                abstained += g["status"] in ABSTAIN
            elif g["status"] in ABSTAIN:
                false_abstain += 1
            rows.append((case["id"], exp["status"], g["status"], "✓" if ok else "✗"))
    pct = lambda a, b: f"{100 * a / b:.0f}%" if b else "n/a"  # noqa: E731
    lines = [
        "# Tathabbut evaluation report", "",
        f"Cases: {len(cases)} · expected citations: {expected} · deep model: {deep}", "",
        "| Metric | Value |", "|---|---|",
        f"| Extraction recall | {found}/{expected} ({pct(found, expected)}) |",
        f"| Tracing accuracy | {traced}/{expected} ({pct(traced, expected)}) |",
        f"| Correct abstention | {abstained}/{should_abstain} ({pct(abstained, should_abstain)}) |",
        f"| Wrongly referred | {false_abstain} |",
        f"| Extra citations (not expected) | {extra} |", "",
        "| Case | Expected | Got | OK |", "|---|---|---|---|",
        *[f"| {a} | {b} | {c} | {d} |" for a, b, c, d in rows],
    ]
    (ROOT / "eval" / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[:12]))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--deep", action="store_true")
    ap.add_argument("--cases", default=str(ROOT / "eval" / "cases.jsonl"))
    a = ap.parse_args()
    asyncio.run(main(a.deep, Path(a.cases)))
