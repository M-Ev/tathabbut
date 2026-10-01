import asyncio
from pathlib import Path

import httpx
import pytest

from app import dorar, llm

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

    async def chat(self, messages, max_tokens=256):
        self.calls.append(messages[-1]["content"])
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
