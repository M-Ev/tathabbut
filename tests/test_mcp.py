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


def test_allam_first_then_the_fallback_and_the_report_names_who_answered(monkeypatch):
    from app import llm

    class Off(llm._Backend):
        name, label = "llamacpp", "ALLaM-7B-Instruct-preview"

        def ready(self):
            return False

    class Strong(llm._Backend):
        name, label = "openai", "Qwen/Qwen3-235B-A22B-Instruct-2507"

        def ready(self):
            return True

        async def chat(self, messages, max_tokens=256, schema=None):
            return '{"arabic": "إنما الأعمال بالنيات"}'

    monkeypatch.setattr(llm, "backend", Off())
    monkeypatch.setattr(llm, "fallback", Strong())
    usage = {"calls": 0, "seconds": 0.0}
    llm.USAGE.set(usage)
    assert asyncio.run(llm.arabic_search_wording("Actions are but by intentions", "hadith")) == "إنما الأعمال بالنيات"
    assert usage["models"] == ["Qwen/Qwen3-235B-A22B-Instruct-2507"]
    assert llm.available() and llm.describe()["fallback"] == "Qwen/Qwen3-235B-A22B-Instruct-2507"

    class On(Off):
        def ready(self):
            return True

        async def chat(self, messages, max_tokens=256, schema=None):
            return '{"arabic": "الطهور شطر الإيمان"}'

    monkeypatch.setattr(llm, "backend", On())
    usage = {"calls": 0, "seconds": 0.0}
    llm.USAGE.set(usage)
    asyncio.run(llm.arabic_search_wording("Cleanliness is half of faith", "hadith"))
    assert usage["models"] == ["ALLaM-7B-Instruct-preview"]  # ALLaM answers whenever it is up


def test_a_model_that_does_not_answer_gives_a_referral_not_an_error(monkeypatch, fake_dorar):
    from app import llm
    from app.pipeline import run

    fake_dorar({})

    class Down(llm._Backend):
        name, label = "openai", "some-model"

        def ready(self):
            return True

        async def chat(self, messages, max_tokens=256, schema=None):
            raise RuntimeError("503")

    monkeypatch.setattr(llm, "backend", Down())
    monkeypatch.setattr(llm, "fallback", None)
    r = run('The Prophet (ﷺ) said: "Cleanliness is half of faith."', deep=True)
    c = r["citations"][0]
    assert c["status"] == "needs_model" and c["referral"] and r["model"]["used"] is False
    assert r["coverage"]["complete"] is False
