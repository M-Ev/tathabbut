import asyncio
import json

import httpx

from app import mcp_server
from app.main import app
from app.normalize import skeleton_ar


def test_mcp_tools_return_source_text_and_the_chatbot_decision(fake_dorar):
    fake_dorar({})
    r = asyncio.run(mcp_server.check_citations("قال تعالى: ﴿إن مع العسر يسرا﴾ (البقرة: 286)"))
    c = r["citations"][0]
    assert c["status"] == "verified" and c["source"]["ref"] == "94:6" and c["source"]["reference_ok"] is False
    assert skeleton_ar(c["source"]["mushaf_text"]) == skeleton_ar("إن مع العسر يسرا") and c["source"]["url"].endswith("/94/6")
    assert r["decision"]["action"] in ("annotate", "block") and r["decision"]["rewrites_answer"] is False
    a = asyncio.run(mcp_server.get_ayah(49, 6))
    assert a["ref"] == "49:6" and skeleton_ar("فتبينوا") in skeleton_ar(a["ayat"][0]["text"])
    assert "error" in asyncio.run(mcp_server.get_ayah(1, 8))  # no invented ayah


def test_mcp_endpoint_lists_the_tools():
    async def run():
        async with app.router.lifespan_context(app):
            transport = httpx.ASGITransport(app=app)
            async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
                headers = {"accept": "application/json, text/event-stream", "content-type": "application/json"}
                r = await client.post("/mcp", headers=headers, json={"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
                return r

    r = asyncio.run(run())
    assert r.status_code == 200
    names = {t["name"] for t in json.loads(r.text)["result"]["tools"]}
    assert names == {"check_citations", "get_ayah", "list_sources"}
