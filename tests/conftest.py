import asyncio
from pathlib import Path

import httpx
import pytest

from app import dorar, fatwa, llm

FIX = Path(__file__).parent / "fixtures"


def dorar_transport(routes: dict):
    """routes: substring of the q= parameter -> fixture file name (site search). Unknown -> empty page."""

    def handler(request: httpx.Request):
        url = str(request.url)
        if "dorar_api.json" in url:
            return httpx.Response(200, text=(FIX / "dorar_api.json").read_text(encoding="utf-8"))
        q = request.url.params.get("q", "")
        for key, name in routes.items():
            if key in q:
                return httpx.Response(200, text=(FIX / name).read_text(encoding="utf-8"))
        return httpx.Response(200, text="<html><div id='home'></div></html>")

    return httpx.MockTransport(handler)


@pytest.fixture
def fake_dorar(monkeypatch):
    def install(routes):
        client = dorar.DorarClient(transport=dorar_transport(routes))
        monkeypatch.setattr(dorar, "MIN_INTERVAL", 0)
        monkeypatch.setattr(dorar, "_client", client)
        return client

    return install


class FakeBackend(llm._Backend):
    name = "fake"

    def __init__(self, replies):
        self.replies = list(replies)
        self.calls = []

    async def chat(self, messages, max_tokens=256, schema=None):
        self.calls.append(messages[-1]["content"])
        self.schemas = getattr(self, "schemas", []) + [schema]
        return self.replies.pop(0) if self.replies else "{}"


@pytest.fixture
def fake_llm(monkeypatch):
    def install(replies):
        b = FakeBackend(replies)
        monkeypatch.setattr(llm, "backend", b)
        return b

    return install


def run(coro):
    return asyncio.run(coro)


def fatwa_transport(empty: bool = False):
    """The two scholars' sites, from structural fixtures. Tests never reach the network."""

    def handler(request: httpx.Request):
        url = str(request.url)
        if empty:
            body = '{"Search": {"results": []}}' if "binbaz" in url else '{"data": []}'
            return httpx.Response(200, text=body)
        if "binbaz.org.sa/api/search" in url:
            return httpx.Response(200, text=(FIX / "binbaz_search.json").read_text(encoding="utf-8"))
        if "binbaz.org.sa/fatwas/" in url:
            return httpx.Response(200, text=(FIX / "binbaz_fatwa.html").read_text(encoding="utf-8"))
        if "search-data" in url:
            return httpx.Response(200, text=(FIX / "uth_search.json").read_text(encoding="utf-8"))
        if "lessons/audios/show" in url:
            return httpx.Response(200, text=(FIX / "uth_show.json").read_text(encoding="utf-8"))
        return httpx.Response(404)

    return httpx.MockTransport(handler)


@pytest.fixture(autouse=True)
def fake_fatwa_sites(monkeypatch):
    monkeypatch.setattr(fatwa, "MIN_INTERVAL", 0)
    monkeypatch.setattr(fatwa, "_client", fatwa.FatwaClient(transport=fatwa_transport()))

    def empty():
        monkeypatch.setattr(fatwa, "_client", fatwa.FatwaClient(transport=fatwa_transport(empty=True)))

    return empty
