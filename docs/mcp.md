# Tathabbut over MCP (Model Context Protocol)

An AI agent (an Islamic chatbot built on any model) can call Tathabbut as a tool before it answers, instead of
calling the HTTP API itself. The server runs inside the same app at `/mcp` (streamable HTTP, stateless, JSON
replies) and shares the web API's per-visitor rate limit.

    https://3rb-tathabbut.hf.space/mcp

This is the organizers' answer path (challenge slides 18 and 21) with Tathabbut as the "check the references"
step: the agent drafts, calls `check_citations`, and shows the answer only if `decision.action` allows it; when
evidence is missing the citation is referred, never filled in.

| Tool | What it returns | Never does |
|---|---|---|
| `check_citations(text)` | per citation: status, evidence tier, the Mushaf text or the approved scholars' gradings verbatim with book, number and link, or a referral; `decision` (pass / annotate / block), `coverage`, `disclaimer`, `versions` | rewrite the answer, grade a hadith, write a fatwa |
| `get_ayah(surah, ayah, to_ayah?)` | the King Fahd Complex Mushaf text (Hafs) with its link and the Complex's English translation | return an ayah that does not exist (it says the surah's count) |
| `list_sources()` | the sources, the 13 approved hadith scholars and the level د references | add a source that is not listed |

Text sent to `check_citations` is treated as data: instructions inside it change nothing (the same guard as the
API, `tests/test_pipeline.py::test_injected_instructions_in_the_text_change_nothing`).

## Connect

Claude Code: `claude mcp add --transport http tathabbut https://3rb-tathabbut.hf.space/mcp`

Python (the `mcp` package):

```python
import asyncio, json
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

async def main():
    async with streamablehttp_client("https://3rb-tathabbut.hf.space/mcp") as (r, w, _):
        async with ClientSession(r, w) as s:
            await s.initialize()
            res = await s.call_tool("check_citations", {"text": "قال تعالى: ﴿إن مع العسر يسرا﴾ (البقرة: 286)"})
            print(json.loads(res.content[0].text)["decision"])

asyncio.run(main())
```

Tests: `tests/test_mcp.py`.
