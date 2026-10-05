"""Build data/adhkar.json: every dhikr on «الأذكار الموثّقة», checked with Tathabbut itself.

    python3 scripts/build_adhkar.py [https://3rb-tathabbut.hf.space]

Each hadith item of scripts/adhkar_list.py is sent to the live site's POST /api/check as «قال رسول الله ﷺ: «...»».
It is shown only where Dorar returned an authentic or good grading by the approved scholars (or the narration is in
al-Bukhari's or Muslim's Sahih) on a narration that contains every word of the dhikr; under an occasion (morning,
sleep, the sick...) only if that narration names the occasion; with a count only if that narration states it. The
grading is recorded verbatim with its book, number and link. An item that fails stays in the file, not shown. Quran items are copied from the Mushaf file by
reference. Paced under the site's limit (20 checks per 10 minutes).
"""
import json
import sys
import time
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
from adhkar_list import CATEGORIES, HADITH, QURAN  # noqa: E402

BASE = (sys.argv[1] if len(sys.argv) > 1 else "https://3rb-tathabbut.hf.space").rstrip("/")
OUT = ROOT / "data" / "adhkar.json"
ACCEPTED = {"authentic", "good"}


# An occasion-bound dhikr is shown under that occasion only if the authentic narration itself names it: the same
# words said on another occasion (e.g. after hearing the adhan) do not make it a morning dhikr.
CONTEXT = {
    "morning": r"أصبح|يصبح|الصباح|صباح|أصبحت|أصبحنا",
    "evening": r"أمسى|يمسي|المساء|مساء|أمسيت|أمسينا",
    "after_prayer": r"صلاة|الصلاة|سلم|دبر|انصرف|صلى|يصلي|المكتوبة",
    "in_prayer": r"صلاة|الصلاة|ركوع|ركع|سجود|سجد|كبر|استفتح|ركوعه|سجوده",
    "waking": r"استيقظ|من نومه|انتبه|تعار|قام من",
    "sleep": r"مضجع|فراش|نام|النوم|أويت|أوى|اضطجع|منامه|مضجعك",
    "sick": r"مريض|مرض|عاد|وجع|يشفي|اشتكى|شفاء|سقم|يألم|تألم",
    "deceased": r"ميت|جنازة|صلى على|دفن|قبر|مات|توفي|المصيبة|مصيبة",
}
COUNT_WORDS = {3: r"ثلاث", 7: r"سبع", 10: r"عشر", 33: r"ثلاثا وثلاثين|ثلاثًا وثلاثين|ثلاث وثلاثين", 100: r"مائة|مئة|مائةَ|مِائَةَ"}


def _plain(t: str) -> str:
    """Harakat off and the common letter variants unified, nothing else (so a regex keeps its «|»)."""
    import re
    t = re.sub("[ً-ٰٟـۖ-ۭ]", "", t or "")
    return t.translate(str.maketrans({"أ": "ا", "إ": "ا", "آ": "ا", "ٱ": "ا", "ى": "ي", "ة": "ه", "ؤ": "و", "ئ": "ي"}))


def missing_words(dhikr: str, narration: str) -> set:
    """Words of the dhikr not in the narration, a joined «و» or «ف» aside. Stricter than the search's fuzzy
    coverage: «ربي» is not «ربِّ», so a dhikr is shown only in the narration's own words."""
    import re
    have = set(re.findall(r"[ء-ي]+", _plain(narration)))
    return {w for w in re.findall(r"[ء-ي]+", _plain(dhikr)) if not ({w, "و" + w, "ف" + w, w[1:] if w[:1] in "وف" else w} & have)}


def verify(text: str) -> dict:
    r = httpx.post(BASE + "/api/check", json={"text": f"قال رسول الله ﷺ: «{text}»"}, timeout=180)
    r.raise_for_status()
    res = r.json()
    hd = [c for c in res["citations"] if c["type"] == "hadith"]
    if not hd or not hd[0].get("hadith"):
        return {"narrations": [], "reason": "not_found", "checked_on_commit": res["versions"]["app"]}
    h = hd[0]["hadith"]
    sahih_books = {s["book"] for s in h.get("sahihayn", [])}
    narrations = []
    for g in h.get("groups", []):
        for i in g["items"]:
            if i.get("missing_words"):  # the narration lacks some of the dhikr's words
                continue
            narrations.append({**{k: i.get(k) for k in ("scholar_ar", "scholar_en", "grade", "book", "book_en", "number", "url", "text", "died_ah")},
                               "authentic": (i.get("grade_gloss") or {}).get("category") in ACCEPTED or i["book"] in sahih_books,
                               "in_sahihayn": i["book"] in sahih_books})
    return {"query": h.get("query"), "search_url": h.get("search_url"), "sahihayn": h.get("sahihayn", []),
            "fabricated_by": h.get("fabricated_by", []), "narrations": narrations, "checked_on_commit": res["versions"]["app"]}


def place(item: dict) -> list:
    """Where the dhikr is shown: each category with the authentic narration that supports it there."""
    import re
    check = item["check"]
    if check.get("fabricated_by"):
        return []
    good = sorted((n for n in check.get("narrations", []) if n["authentic"] and not missing_words(item["text"], n["text"])),
                  key=lambda n: (not n["in_sahihayn"], n["died_ah"] or 0))
    out = []
    for cat in item["categories"]:
        pat = CONTEXT.get(cat)
        hits = [n for n in good if not pat or re.search(_plain(pat), _plain(n["text"]))]
        if not hits:
            continue
        n = hits[0]
        cw = COUNT_WORDS.get(item["count"])
        out.append({"category": cat, "source": n,
                    "count": item["count"] if item["count"] > 1 and cw and re.search(_plain(cw), _plain(n["text"])) else None})
    return out


def main():
    old = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}
    done = {x["id"]: x for x in old.get("hadith", []) if x.get("check")}
    out = {"built_at": time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime()), "site": BASE,
           "categories": [{"key": k, "ar": a, "en": e} for k, a, e in CATEGORIES], "hadith": [], "quran": []}
    for hid, cats, text, count, cited in HADITH:
        prev = done.get(hid)
        if prev and prev["text"] == text and "--again" not in sys.argv and not str(prev["check"].get("reason", "")).startswith("request_failed"):
            prev["categories"], prev["count"] = cats, count
            prev["shown"] = place(prev)
            out["hadith"].append(prev)
            continue
        t0 = time.time()
        try:
            check = verify(text)
        except Exception as e:  # noqa: BLE001
            check = {"narrations": [], "reason": f"request_failed: {type(e).__name__}"}
        item = {"id": hid, "categories": cats, "text": text, "count": count, "cited": cited, "check": check}
        item["shown"] = place(item)
        out["hadith"].append(item)
        print(("ok   " if item["shown"] else "FAIL ") + hid, [p["category"] for p in item["shown"]], "of", cats, flush=True)
        OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
        time.sleep(max(0, 32 - (time.time() - t0)))
    by_id = {x["id"]: x for x in out["hadith"]}
    for qid, cats, s, a, b in QURAN:
        shown = []
        for cat, ev in cats.items():
            if ev is None:  # the verse is itself the du'a: its text is the Mushaf's
                shown.append({"category": cat, "evidence": None, "count": None})
                continue
            hit = next((p for p in by_id.get(ev, {}).get("shown", []) if p["category"] == cat), None)
            if hit:  # placed under an occasion only on a verified hadith that names it
                shown.append({"category": cat, "evidence": {"id": ev, "text": by_id[ev]["text"], **hit}, "count": hit["count"]})
        out["quran"].append({"id": qid, "surah": s, "ayah_from": a, "ayah_to": b, "shown": shown,
                             "not_shown": [c for c in cats if c not in {x["category"] for x in shown}]})
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    n = sum(1 for x in out["hadith"] if x["shown"])
    print(f"\n{n}/{len(out['hadith'])} hadith items verified; {len(out['quran'])} Quran items from the Mushaf")


if __name__ == "__main__":
    main()
