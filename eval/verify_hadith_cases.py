"""Check the hadith evaluation set against dorar.net with the app's own Dorar client.

For every case in eval/hadith_cases.jsonl this script sends the same queries the live site sends
(app.pipeline._dorar_queries + app.dorar.DorarClient, filtered to the approved scholars), then records,
verbatim, every approved scholar's entry that Dorar returns: grading, book, number, narrator, text and link.

- verification_status becomes "verified" (an approved scholar's grading of this text was found) or
  "not_found" (none). When Dorar cannot be reached the case keeps its status and the error is recorded:
  an unreachable source is never written down as "not found".
- An expected result is filled in only where it is still empty (status null). It is a snapshot of what the
  app shows for this Dorar data, for the Sharia reviewer to confirm; it never overwrites a value a person set.
- eval/hadith_cases.md (the reviewer's table) is re-rendered; text already written in its
  «رأي المراجِعة» column is kept, matched by case id.

Run (needs access to dorar.net):
    python3 eval/verify_hadith_cases.py
Offline plan, no network and no writes (shows each case's quote, queries and URLs, and extraction mismatches):
    python3 eval/verify_hadith_cases.py --dry-run
Through the live app, when this machine cannot reach dorar.net (Dorar's Cloudflare refuses some clouds):
    python3 eval/verify_hadith_cases.py --via-space https://3rb-tathabbut.hf.space
  This records what the live app shows (its POST /api/check), not Dorar's raw results: only the approved
  scholars' gradings the app displays, marked "source": "live_app". Each case costs the Space one to three
  of its roughly 100 daily Dorar searches. Non-Arabic cases need the model and are skipped.
Re-render only the reviewer's table from the JSONL (offline):
    python3 eval/verify_hadith_cases.py --render-md
"""
import argparse
import asyncio
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.dorar import DorarClient  # noqa: E402
from app.extract import extract  # noqa: E402
from app.normalize import skeleton_ar  # noqa: E402
from app.pipeline import STRONG_MATCH, WEAK_MATCH, _dorar_queries, _grade_groups, _similarity  # noqa: E402
from app.quran import get_quran  # noqa: E402
from app.scholars import EDITORS, IMAMS, SCHOLARS, find_scholar, grade_flags, is_hadith_level_grading  # noqa: E402

CASES = ROOT / "eval" / "hadith_cases.jsonl"
MD = ROOT / "eval" / "hadith_cases.md"
STATUSES = {"verified", "not_found", "pending_live_check"}
REQUIRED = ("id", "selection_group", "text", "quote", "lang", "search_wording", "verification_status",
            "evidence", "expected", "review")


# ---------------------------------------------------------------- shared helpers

def load(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def dump(cases: list[dict], path: Path) -> None:
    path.write_text("".join(json.dumps(c, ensure_ascii=False) + "\n" for c in cases), encoding="utf-8")


def arabic_wording(case: dict) -> str:
    """The Arabic text searched on Dorar: the quote itself, or, for a non-Arabic quote, the Arabic wording
    the case author wrote down to stand in for the language model's search wording."""
    return case["quote"] if case["lang"] == "ar" else case.get("search_wording_ar", "")


def search_plan(case: dict, client: DorarClient) -> list[dict]:
    return [{"q": q, "st": st, "app_url": client.site_url(q, st), "public_url": client.site_url(q, st, False)}
            for q, st in _dorar_queries(arabic_wording(case))]


def extracted_quote(case: dict) -> str | None:
    hadith = [c for c in extract(case["text"]) if c.type == "hadith"]
    return hadith[0].quote if hadith else None


def same_text(a: str | None, b: str | None) -> bool:
    if a is None or b is None:
        return a == b
    return (skeleton_ar(a) or a.strip().lower()) == (skeleton_ar(b) or b.strip().lower())


def check_schema(case: dict) -> list[str]:
    problems = [f"missing field {k}" for k in REQUIRED if k not in case]
    if case.get("verification_status") not in STATUSES:
        problems.append(f"verification_status must be one of {sorted(STATUSES)}")
    if case.get("lang") != "ar" and not case.get("search_wording_ar"):
        problems.append("non-Arabic case needs search_wording_ar")
    if not isinstance(case.get("expected"), list) or not case["expected"]:
        problems.append("expected must be a non-empty list")
    return problems


# ---------------------------------------------------------------- live check

def _entry(h, quote: str, checked_at: str) -> dict | None:
    scholar = find_scholar(h.mohdith, h.mohdith_id)
    if not scholar:
        return None
    sim = round(_similarity(quote, h.text), 1)
    hadith_level = is_hadith_level_grading(scholar, h.grade)
    return {
        "scholar": scholar.key, "scholar_ar": scholar.name_ar, "group": scholar.group,
        "mohdith": h.mohdith, "grade": h.grade, "book": h.book, "number": h.number, "rawi": h.rawi,
        "text": h.text, "hadith_url": h.url, "similarity": sim,
        "narrator_statement": not hadith_level,
        "shown_by_app": hadith_level and sim >= WEAK_MATCH,
        "flags": grade_flags(h.grade), "source": "live_check", "checked_at": checked_at,
    }


def _derive_expected(case: dict, info: dict) -> dict:
    exp = dict(case["expected"][0])
    best, count = info["best_similarity"], info["count"]
    if case["lang"] != "ar":  # deep mode: the model picks one Arabic text, which then matches itself
        exp["status"] = "graded" if count else "not_found"
    elif count and best >= STRONG_MATCH:
        exp["status"] = "graded"
    elif count:
        exp["status"] = "found_similar"
    else:
        exp["status"] = "not_found"
    keys = sorted({i["scholar_key"] for g in info["groups"] for i in g["items"]})
    if keys:
        exp["scholars_any"] = keys
    if info["fabricated_by"]:
        exp["fabricated"] = True
    return exp


async def verify_case(case: dict, client: DorarClient) -> str:
    checked_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    quote = arabic_wording(case)
    plan = search_plan(case, client)
    tried, res = [], None
    for step in plan:
        res = await client.search(step["q"], step["st"])
        tried.append({"q": step["q"], "st": step["st"], "url": step["app_url"],
                      "results": len(res.hadiths), "error": res.error or None})
        if res.hadiths:
            break
    ev = case["evidence"]
    ev["live_check"] = {"checked_at": checked_at, "queries": tried}
    if res is None or (not res.hadiths and res.error):
        ev["live_check"]["outcome"] = "source_error"
        return "source_error"

    entries = [e for e in (_entry(h, quote, checked_at) for h in res.hadiths) if e]
    ev["gradings"] = [g for g in ev.get("gradings", []) if g.get("source") != "live_check"] + entries
    case["verification_status"] = "verified" if any(e["shown_by_app"] for e in entries) else "not_found"
    ev["live_check"]["outcome"] = case["verification_status"]
    ev["live_check"]["approved_entries"] = len(entries)

    if case["expected"][0].get("status") is None:
        case["expected"][0] = _derive_expected(case, _grade_groups(quote, res))
        case["expected_source"] = f"live_check_snapshot {checked_at}: what the app shows for this Dorar data; reviewer to confirm"
    return case["verification_status"]


async def verify_case_via_space(case: dict, base: str, http) -> str:
    """The live app's answer for the case's text: what a judge would see on the site."""
    checked_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    if case["lang"] != "ar":
        return "skipped_needs_model"
    try:
        r = await http.post(base.rstrip("/") + "/api/check", json={"text": case["text"], "deep": False})
        r.raise_for_status()
        data = r.json()
    except Exception as e:  # noqa: BLE001 - an unreachable app is never "not found"
        case["evidence"]["live_check"] = {"checked_at": checked_at, "via": base, "outcome": "source_error", "error": type(e).__name__}
        return "source_error"
    cits = [c for c in data.get("citations", []) if c.get("type") == "hadith"]
    c = next((c for c in cits if same_text(c.get("quote"), case["quote"])), cits[0] if cits else None)
    ev = case["evidence"]
    ev["live_check"] = {"checked_at": checked_at, "via": base + "/api/check", "app_status": c and c.get("status"),
                        "app_tier": c and c.get("tier"), "search_url": c and (c.get("hadith") or {}).get("search_url")}
    if c is None:
        ev["live_check"]["outcome"] = "not_extracted"
        return "not_extracted"
    if c["status"] == "source_error":
        ev["live_check"]["outcome"] = "source_error"
        return "source_error"
    entries = []
    for g in (c.get("hadith") or {}).get("groups", []):
        for i in g.get("items", []):
            entries.append({
                "scholar": i.get("scholar_key"), "scholar_ar": i.get("scholar_ar"), "group": i.get("group"),
                "grade": i.get("grade"), "book": i.get("book"), "number": i.get("number"), "rawi": i.get("rawi"),
                "text": i.get("text"), "hadith_url": i.get("url"), "similarity": i.get("similarity"),
                "narrator_statement": False, "shown_by_app": True, "flags": i.get("flags", []),
                "source": "live_app", "checked_at": checked_at})
    ev["gradings"] = [g for g in ev.get("gradings", []) if g.get("source") not in ("live_check", "live_app")] + entries
    case["verification_status"] = "verified" if entries else "not_found"
    ev["live_check"]["outcome"] = case["verification_status"]
    ev["live_check"]["approved_entries"] = len(entries)
    if case["expected"][0].get("status") is None:
        exp = dict(case["expected"][0])
        exp["status"] = c["status"]
        keys = sorted({e["scholar"] for e in entries if e["scholar"]})
        if keys:
            exp["scholars_any"] = keys
        if any("fabricated" in e["flags"] for e in entries):
            exp["fabricated"] = True
        case["expected"][0] = exp
        case["expected_source"] = f"live_app_snapshot {checked_at}: what the live app showed; reviewer to confirm"
    return case["verification_status"]


async def verify_all(cases: list[dict], via_space: str | None = None) -> dict:
    tally: dict[str, int] = {}
    if via_space:
        import httpx
        async with httpx.AsyncClient(timeout=90) as http:
            for case in cases:
                outcome = await verify_case_via_space(case, via_space, http)
                tally[outcome] = tally.get(outcome, 0) + 1
                print(f"{case['id']:<28} {outcome}")
        return tally
    client = DorarClient()
    for case in cases:
        outcome = await verify_case(case, client)
        tally[outcome] = tally.get(outcome, 0) + 1
        print(f"{case['id']:<28} {outcome}")
    return tally


# ---------------------------------------------------------------- dry run (offline)

def dry_run(cases: list[dict]) -> int:
    client, problems = DorarClient(), 0
    for case in cases:
        issues = check_schema(case)
        got = extracted_quote(case)
        if not same_text(got, case["quote"]):
            issues.append(f"extractor gives {got!r}, case expects {case['quote']!r}")
        plan = search_plan(case, client)
        stored = [{"q": s["q"], "st": s["st"]} for s in case.get("search_wording", [])]
        if stored != [{"q": p["q"], "st": p["st"]} for p in plan]:
            issues.append("stored search_wording differs from what the app would send now")
        problems += bool(issues)
        print(f"{case['id']}  [{case['verification_status']}]  {case['text']}")
        for p in plan:
            print(f"    {p['st']}  {p['q']}\n       {p['app_url']}")
        for i in issues:
            print(f"    ! {i}")
    statuses = {}
    for c in cases:
        statuses[c["verification_status"]] = statuses.get(c["verification_status"], 0) + 1
    print(f"\n{len(cases)} cases: " + ", ".join(f"{k} {v}" for k, v in sorted(statuses.items()))
          + f"; {problems} with notes (see ! lines). No network used, nothing written.")
    return 0


# ---------------------------------------------------------------- reviewer table

GROUP_AR = {
    "sahihayn": "نصوص اختيرت على أنها في الصحيحين",
    "outside_sahihayn": "نصوص اختيرت على أنها صحيحة أو حسنة خارج الصحيحين",
    "weak": "نصوص اختيرت على أنها ضعيفة",
    "fabricated": "نصوص اختيرت على أنها موضوعة أو لا أصل لها",
    "misattribution": "نصوص اختيرت على أنها تُنسب إلى النبي ﷺ وأصلها آية أو قول صحابي أو مثل",
}
SCHOLAR_GROUP_AR = {IMAMS: "أئمة الحديث", EDITORS: "المحققون المعاصرون"}
STATUS_AR = {
    "graded": "يعرض أحكام علماء الحديث المعتمدين بنصّها",
    "found_similar": "يعرض أحكامًا لنص قريب وينبّه إلى اختلاف اللفظ",
    "not_found": "لا يجد حكمًا لعالم معتمد فيحيل إلى مختص في الحديث",
}
VERIFICATION_AR = {
    "verified": "تحقّقنا منه في الدرر",
    "not_found": "لم تُظهر الدرر حكمًا لعالم معتمد على هذا النص",
    "pending_live_check": "بانتظار الفحص الحي (لم تُقرأ الدرر لهذا النص بعد)",
}
SCHOLAR_NAMES_AR = {s.key: s.name_ar for s in SCHOLARS}


def _cell(text: str) -> str:
    return str(text).replace("|", "¦").replace("\n", " ").strip()


def _grading_line(g: dict) -> str:
    link = f" [الحديث]({g['hadith_url']})" if g.get("hadith_url") else ""
    return f"{g['scholar_ar']}: «{_cell(g['grade'])}» — {_cell(g['book'])} ({_cell(g['number'])}){link}"


def _gradings_cell(case: dict) -> str:
    ev = case["evidence"]
    gradings = ev.get("gradings", [])
    live = [g for g in gradings if g.get("source") == "live_check"]
    if live:
        primary = [g for g in live if g.get("shown_by_app")]
        others = [g for g in live if not g.get("shown_by_app")]
    else:
        primary, others = gradings, []
    lines = []
    if not primary:
        lines.append(VERIFICATION_AR.get(case["verification_status"], "") + ".")
    for group in (IMAMS, EDITORS):
        items = [g for g in primary if g["group"] == group]
        if items:
            lines.append(f"**{SCHOLAR_GROUP_AR[group]}:**")
            lines += [_grading_line(g) for g in items]
    if others:
        lines.append("نتائج أخرى لعلماء معتمدين لا تعرضها الأداة (لفظ بعيد أو كلام في راوٍ):")
        lines += [_grading_line(g) for g in others[:5]]
    for page in ev.get("pages_read", []):
        lines.append(f"[الصفحة التي قُرئت]({page['url']}) ({page['read_at']})")
    if live:
        lines.append(f"فحص حي: {ev['live_check']['checked_at']}")
    first = case["search_wording"][0] if case["search_wording"] else None
    if first:
        url = DorarClient().site_url(first["q"], first["st"], approved_only=True)
        lines.append(f"[البحث في الدرر]({url}) (مقيّد بالعلماء المعتمدين)")
    return "<br>".join(lines)


def _expected_cell(case: dict) -> str:
    exp = case["expected"][0]
    parts = []
    if exp.get("status") is None:
        parts.append("يُحدَّد بعد الفحص الحي")
    else:
        parts.append(f"{STATUS_AR.get(exp['status'], exp['status'])} (`{exp['status']}`)")
    if exp.get("scholars_any"):
        names = "، ".join(SCHOLAR_NAMES_AR.get(k, k) for k in exp["scholars_any"])
        parts.append(f"ومن بينها حكم: {names}")
    if exp.get("fabricated"):
        parts.append("وينبّه إلى أن عالمًا معتمدًا حكم عليه بالوضع أو بأنه لا أصل له")
    if exp.get("ref"):
        parts.append(f"وينبّه إلى أن النص آية من القرآن ({exp['ref']})")
    if case.get("needs_model"):
        parts.append("(يحتاج النموذج اللغوي: شغّل التقييم بـ `--deep`)")
    if case.get("expected_source", "").startswith("live_check_snapshot"):
        parts.append("— لقطة من الفحص الحي، تحتاج تأكيدك")
    return " ".join(parts)


def _existing_reviews(path: Path) -> dict:
    reviews = {}
    if not path.exists():
        return reviews
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("| `"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            case_id = cells[0].strip("`")
            if cells[-1]:
                reviews[case_id] = cells[-1]
    return reviews


def render_md(cases: list[dict], path: Path = MD) -> None:
    reviews = _existing_reviews(path)
    counts = {}
    for c in cases:
        counts[c["verification_status"]] = counts.get(c["verification_status"], 0) + 1
    out = [
        "# مجموعة تقييم الأحاديث — للمراجعة الشرعية",
        "",
        "هذا الجدول مولَّد من `eval/hadith_cases.jsonl` بالسكربت `eval/verify_hadith_cases.py`. "
        "يُرجى كتابة الرأي في عمود «رأي المراجِعة» فقط؛ يُحفظ ما فيه عند إعادة التوليد. "
        "(تجنّبي الرمز | داخل الخلية.)",
        "",
        f"الحالات: {len(cases)} — "
        + "، ".join(f"{VERIFICATION_AR.get(k, k)}: {v}" for k, v in sorted(counts.items())),
        "",
        "- **ما تُظهره الدرر** يُنقل بنصه كما في الموسوعة الحديثية للدرر السنية، مقيّدًا بالعلماء الثلاثة عشر المعتمدين، "
        "ومقسومًا إلى **أئمة الحديث** ثم **المحققين المعاصرين**. لا يُكتب فيه حكم من الذاكرة؛ ما لم يُقرأ بعد يبقى فارغًا "
        "ومعه رابط البحث.",
        "- **السلوك المتوقع من الأداة** هو ما ينبغي أن تعرضه «تثبّت» لهذا النص. إن كُتب أنه «لقطة من الفحص الحي» فهو ما عرضته "
        "الأداة عند الفحص، وينتظر تأكيدك.",
        "- **عنوان المجموعة** هو سبب اختيار النص (فرضية عند الاختيار)، وليس حكمًا عليه؛ الحكم ما تُظهره الدرر وما تقرّرينه.",
        "",
    ]
    for group, title in GROUP_AR.items():
        rows = [c for c in cases if c["selection_group"] == group]
        if not rows:
            continue
        out += [f"## {title}", "",
                "| الحالة | النص كما يُكتب في المنشور | ما تُظهره الدرر للعلماء المعتمدين | السلوك المتوقع من الأداة | رأي المراجِعة |",
                "|---|---|---|---|---|"]
        for c in rows:
            words = "، ".join(f"«{s['q']}»" for s in c["search_wording"][:1])
            text = f"{_cell(c['text'])}<br><small>عبارة البحث: {words}</small>"
            if c.get("notes_ar"):
                text += f"<br><small>{_cell(c['notes_ar'])}</small>"
            out.append(f"| `{c['id']}` | {text} | {_gradings_cell(c)} | {_expected_cell(c)} | {reviews.get(c['id'], '')} |")
        out.append("")
    path.write_text("\n".join(out), encoding="utf-8")


# ---------------------------------------------------------------- main

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--cases", default=str(CASES))
    ap.add_argument("--md", default=str(MD), help="reviewer table to re-render")
    ap.add_argument("--dry-run", action="store_true", help="offline: show the plan, write nothing")
    ap.add_argument("--render-md", action="store_true", help="offline: only re-render the reviewer table")
    ap.add_argument("--via-space", metavar="URL", help="check through the live app's POST /api/check instead of dorar.net")
    a = ap.parse_args()
    path, md = Path(a.cases), Path(a.md)
    cases = load(path)
    if a.dry_run:
        return dry_run(cases)
    if a.render_md:
        render_md(cases, md)
        print(f"wrote {md}")
        return 0
    tally = asyncio.run(verify_all(cases, a.via_space))
    dump(cases, path)
    render_md(cases, md)
    print("\n" + ", ".join(f"{k}: {v}" for k, v in sorted(tally.items())) + f"\nwrote {path} and {md}")
    if tally.get("source_error"):
        print("Some cases could not reach Dorar; they keep their previous status. Run again later.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
