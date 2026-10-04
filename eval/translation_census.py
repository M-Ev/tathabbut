"""Plan item 36: how well Urdu, Indonesian and French verse quotes are traced through one approved translation each.

Positives: 300 ayat (seeded) per language; from each, a window of 6 to 14 words as written, the same window
with one word dropped, and with one word swapped for a word of another ayah (900 quotes). A positive counts
as correct when the matcher returns its ayah, or an ayah whose translation holds the same words (repeated
ayat such as 55:13). Negatives: sentences that are not ayat (circulating sayings, hadith meanings and
ordinary da'wa sentences) in eval/negatives/<lang>.txt, written by Claude and awaiting review by a speaker
of each language. Run: python3 eval/translation_census.py  ->  eval/translation_report.md
"""
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from app.quran import get_quran  # noqa: E402

NAMES = {"ur": "الأردية (جوناكري)", "id": "الإندونيسية (المجمع ووزارة الشؤون الدينية)", "fr": "الفرنسية (محمد حميد الله)"}


def positives(idx, rnd):
    out = []
    cands = [i for i, t in enumerate(idx) if len(t.split()) >= 8]
    for i in rnd.sample(cands, 300):
        w = idx[i].split()
        k = rnd.randint(6, min(14, len(w)))
        s = rnd.randint(0, len(w) - k)
        win = w[s : s + k]
        out.append(("as written", i, " ".join(win)))
        d = list(win)
        d.pop(rnd.randrange(len(d)))
        out.append(("one word dropped", i, " ".join(d)))
        r = list(win)
        r[rnd.randrange(len(r))] = rnd.choice(idx[rnd.randrange(len(idx))].split() or ["x"])
        out.append(("one word swapped", i, " ".join(r)))
    return out


def run(lang):
    Q = get_quran()
    tr = Q.translations[lang]
    idx = tr["index"]
    rows = []
    for kind, i, q in positives(idx, random.Random(7)):
        m = Q.match_translation(q, lang)
        j = Q.index.get((m.surah, m.ayah_from)) if m.surah else None
        right = j is not None and (j == i or idx[j] == idx[i] or q in idx[j])
        rows.append({"kind": kind, "status": m.status, "right": right, "wrong": j is not None and not right,
                     "src": f"{Q.ayat[i].surah}:{Q.ayat[i].ayah}", "got": m.ref, "score": m.score})
    negs = [x.strip() for x in (ROOT / "eval" / "negatives" / f"{lang}.txt").read_text(encoding="utf-8").splitlines() if x.strip()]
    neg = []
    for q in negs:
        m = Q.match_translation(q, lang)
        neg.append({"text": q, "status": m.status, "got": m.ref, "score": m.score})
    return rows, neg, tr


def main():
    lines = ["# مسح مطابقة الترجمات (البند ٣٦)", "",
             "يولّده `python3 eval/translation_census.py`. المطابِق هو نفسه الذي في التطبيق (`Quran.match_translation`)، "
             f"بعتبة {get_quran().TR_FLOOR} وتطابق تام من {get_quran().TR_EXACT}.", "",
             "الجمل السالبة كتبها Claude (أقوال شائعة ومعاني أحاديث وجمل دعوية ليست آيات)، وتنتظر مراجعة متحدث بكل لغة. "
             "والعتبة اختيرت على هذه الحالات نفسها، فالأرقام تقدير متفائل حتى تُجرَّب على اقتباسات حقيقية.", ""]
    for lang in ("ur", "id", "fr"):
        rows, neg, tr = run(lang)
        src = tr["source"]
        lines += [f"## {NAMES[lang]}", "",
                  f"المصدر: {src['name_ar']}، كتاب {src['book']} في {src['site']}، بصمة الملف `{tr['sha256'][:16]}…`.", "",
                  "| نوع الاقتباس | العدد | أُرجع إلى آيته | أُرجع إلى آية أخرى | لم يُعثر عليه |", "|---|---|---|---|---|"]
        for kind in ("as written", "one word dropped", "one word swapped"):
            k = [r for r in rows if r["kind"] == kind]
            lines.append(f"| {kind} | {len(k)} | {sum(r['right'] for r in k)} | {sum(r['wrong'] for r in k)} | "
                         f"{sum(r['status'] == 'not_found' for r in k)} |")
        tot = len(rows)
        lines.append(f"| **الكل** | {tot} | {sum(r['right'] for r in rows)} ({100 * sum(r['right'] for r in rows) / tot:.1f}٪) | "
                     f"{sum(r['wrong'] for r in rows)} | {sum(r['status'] == 'not_found' for r in rows)} |")
        fp = [n for n in neg if n["status"] != "not_found"]
        lines += ["", f"الجمل السالبة: {len(neg)}، رُبط منها بآية {len(fp)}. أعلى درجة لجملة سالبة: "
                  f"{max(n['score'] for n in neg):.1f}.", ""]
        wrong = [r for r in rows if r["wrong"]][:8]
        if wrong:
            lines += ["أمثلة لما أُرجع إلى آية أخرى (الأصل ← ما أُرجع إليه، الدرجة):", ""]
            lines += [f"- {r['src']} ← {r['got']} ({r['score']}) — {r['kind']}" for r in wrong]
            lines.append("")
        print(lang, sum(r["right"] for r in rows), "/", tot, "wrong", sum(r["wrong"] for r in rows), "negFP", len(fp))
    (ROOT / "eval" / "translation_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
