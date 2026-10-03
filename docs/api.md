# فحص إجابة روبوت المحادثة قبل عرضها · Checking a chatbot answer before it is shown

الاستخدام الثاني لتثبّت: يرسل روبوت المحادثة الإسلامي إجابته إلى `POST /api/check` قبل أن يراها المستخدم، فيعود لكل استشهاد حالته وموضعه في النص، ولكل الإجابة قرار من سياسة مكتوبة قابلة للتعديل (`data/chatbot_policy.json`). الأداة لا تعيد كتابة الإجابة أبدًا، والإجابة التي لم تُفحص كاملة لا تمر.

An Islamic chatbot sends its answer to `POST /api/check` before the user sees it. Each citation comes back with its status and position, and the whole answer gets a decision from a written, editable policy (`data/chatbot_policy.json`). The tool never rewrites the answer, and an answer it could not check in full never passes.

## الطلب والرد · Request and reply

```json
POST /api/check
{"text": "the chatbot's answer", "deep": false}
```

| Field | Meaning |
|---|---|
| `decision.action` | `pass` (show as is), `annotate` (show with the notes), `block` (do not show the cited text as such) |
| `decision.reasons[]` | per citation: `citation` (id), `action`, `tier`, `status`; or a `rule`: `fatwa_question`, `not_fully_checked` |
| `decision.policy` | policy `name` and `version` that decided |
| `citations[].span` | `[start, end]` character offsets of the citation (marker and quote) in the text sent |
| `citations[].quote_span` | offsets of the quoted words alone |
| `citations[].tier` | `documented`, `supported`, `not_supported`, `verify`, `refer` |
| `coverage` | `complete`, `gaps` (`text_truncated`, `citations_truncated`, `citations_unchecked`, `unsupported_language`; `rules_only` is informative), counts |
| `level_d` | a personal fatwa question: the two scholars' published fatwas and the official body |
| `disclaimer` | `ar` / `en` line to show with any result |
| `versions` | `app` commit, `display_rules` status, `chatbot_policy` version, `model` backend |

Limits: 8000 characters and 12 citations per request (beyond that `coverage.complete` is false), 20 requests per 10 minutes per visitor.

## Python

```python
import httpx

def check_answer(answer: str) -> str:
    r = httpx.post("https://3rb-tathabbut.hf.space/api/check", json={"text": answer}, timeout=60)
    r.raise_for_status()
    res = r.json()
    action = res["decision"]["action"]
    if action == "pass":
        return answer
    if action == "block":
        return "لم تُعرض هذه الإجابة لأن فيها استشهادًا لم يثبت في المصادر المعتمدة."
    notes = []
    for c in res["citations"]:
        if c["tier"] in ("verify", "refer"):
            start, end = c["span"]
            notes.append(f"«{answer[start:end]}»: يحتاج مزيدًا من التحقق")
    return answer + "\n\n" + "\n".join(notes) + "\n" + res["disclaimer"]["ar"]
```

## JavaScript

```js
async function checkAnswer(answer) {
  const r = await fetch("https://3rb-tathabbut.hf.space/api/check", {
    method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ text: answer }),
  });
  if (!r.ok) throw new Error(`Tathabbut ${r.status}`);  // on error, do not show the answer as checked
  const res = await r.json();
  const { action } = res.decision;
  if (action === "pass") return { show: answer };
  if (action === "block") return { show: null, reasons: res.decision.reasons };
  const notes = res.citations.filter((c) => ["verify", "refer"].includes(c.tier))
    .map((c) => ({ at: c.span, quote: answer.slice(...c.span), tier: c.tier }));
  return { show: answer, notes, disclaimer: res.disclaimer.ar };
}
```

## العرض · Demo

`/static/chatbot.html` on the live site shows an answer as the chatbot wrote it beside what its user would see under the default policy.

## تعديل السياسة · Changing the policy

`data/chatbot_policy.json` lists which tiers and statuses block and which annotate. An operator can make it stricter (block `verify` too) or gentler (annotate `not_found`). `never_pass_when_unchecked` should stay `true`: an answer whose citations were cut or could not be reached is not certified.
