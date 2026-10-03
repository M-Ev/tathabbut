"""Client for the Dorar hadith encyclopedia (dorar.net/hadith), a source in the challenge's scientific package.

Privacy: only the extracted hadith wording is sent to Dorar, never the user's full text.
Politeness: results are cached, and requests are spaced out (see MIN_INTERVAL).
"""
import asyncio
from datetime import datetime, timezone
import html
import json
import re
import time
from collections import OrderedDict
from dataclasses import dataclass, field
from urllib.parse import urlencode

import httpx
from bs4 import BeautifulSoup

from .config import settings
from .scholars import DORAR_IDS, find_scholar

SITE_URL = "https://www.dorar.net/hadith/search"
API_URL = "https://dorar.net/dorar_api.json"
HADITH_URL = "https://www.dorar.net/h/{id}"
MIN_INTERVAL = 0.6  # seconds between requests to Dorar

LABELS = {
    "rawi": "الراوي",
    "mohdith": "المحدث",
    "book": "المصدر",
    "number": "الصفحة أو الرقم",
    "grade": "خلاصة حكم المحدث",
}


@dataclass
class DorarHadith:
    text: str
    rawi: str = ""
    mohdith: str = ""
    mohdith_id: str | None = None
    book: str = ""
    number: str = ""
    grade: str = ""
    hadith_id: str | None = None

    @property
    def url(self):
        return HADITH_URL.format(id=self.hadith_id) if self.hadith_id else ""


@dataclass
class DorarResult:
    query: str
    method: str
    hadiths: list = field(default_factory=list)
    search_url: str = ""
    error: str = ""


class _Cache:
    def __init__(self, size=2000):
        self.data, self.size = OrderedDict(), size

    def get(self, k):
        if k in self.data:
            self.data.move_to_end(k)
            return self.data[k]

    def set(self, k, v):
        self.data[k] = v
        self.data.move_to_end(k)
        while len(self.data) > self.size:
            self.data.popitem(last=False)


def _clean(text: str) -> str:
    text = re.sub(r"^\s*\d+\s*-\s*", "", text)
    return re.sub(r"\s+", " ", text).strip()


def parse_site_html(page: str) -> list[DorarHadith]:
    """Parse dorar.net/hadith/search results (the non-specialist tab)."""
    soup = BeautifulSoup(page, "html.parser")
    tab = soup.select_one("#home") or soup
    out = []
    for block in tab.select(".border-bottom"):
        children = [c for c in block.children if getattr(c, "name", None)]
        if len(children) < 2:
            continue
        hadith_node, info = children[0], children[1]
        h = DorarHadith(text=_clean(hadith_node.get_text(" ")))
        for strong in info.select("strong"):
            label = strong.get_text(" ").split(":")[0].replace("|", "").strip()
            span = strong.find("span")
            value = span.get_text(" ").strip() if span else ""
            # Longest label first: "خلاصة حكم المحدث" also contains "المحدث".
            for key, expected in sorted(LABELS.items(), key=lambda kv: -len(kv[1])):
                if expected in label:
                    setattr(h, key, re.sub(r"\s+", " ", value))
                    break
        mhd = info.select_one('a[view-card="mhd"]')
        if mhd and mhd.get("card-link"):
            m = re.search(r"\d+", mhd["card-link"])
            h.mohdith_id = m.group(0) if m else None
        tag = block.select_one("a[tag]")
        if tag:
            h.hadith_id = tag.get("tag")
        if h.text and h.mohdith:
            out.append(h)
    return out


def parse_api_json(payload: str | dict) -> list[DorarHadith]:
    """Parse dorar.net/dorar_api.json (15 results, no scholar filter)."""
    data = json.loads(payload) if isinstance(payload, str) else payload
    raw = (data.get("ahadith") or {}).get("result") or ""
    soup = BeautifulSoup(html.unescape(raw), "html.parser")
    out = []
    for info in soup.select(".hadith-info"):
        hadith_node = info.find_previous_sibling("div", class_="hadith")
        values = []
        for sub in info.select(".info-subtitle"):
            parts = []
            for sib in sub.next_siblings:
                if getattr(sib, "get", None) and "info-subtitle" in (sib.get("class") or []):
                    break
                parts.append(sib.get_text(" ") if hasattr(sib, "get_text") else str(sib))
            values.append(re.sub(r"\s+", " ", "".join(parts)).strip())
        values += [""] * (5 - len(values))
        out.append(DorarHadith(
            text=_clean(hadith_node.get_text(" ")) if hadith_node else "",
            rawi=values[0], mohdith=values[1], book=values[2], number=values[3], grade=values[4],
        ))
    return [h for h in out if h.text]


class DorarClient:
    def __init__(self, transport: httpx.AsyncBaseTransport | None = None):
        self.cache = _Cache()
        self._lock = asyncio.Lock()
        self._last = 0.0
        self._transport = transport
        self.requests_made = 0

    async def _get(self, url: str) -> str:
        cached = self.cache.get(url)
        if cached is not None:
            return cached
        async with self._lock:
            wait = MIN_INTERVAL - (time.monotonic() - self._last)
            if wait > 0:
                await asyncio.sleep(wait)
            async with httpx.AsyncClient(
                timeout=settings.dorar_timeout, transport=self._transport, follow_redirects=True,
                headers={"User-Agent": settings.user_agent, "Accept-Language": "ar,en;q=0.8"},
            ) as client:
                r = await client.get(url)
            self._last = time.monotonic()
            self.requests_made += 1
        r.raise_for_status()
        self.cache.set(url, r.text)
        return r.text

    def site_url(self, query: str, method: str = "w", approved_only: bool = True) -> str:
        params = [("q", query), ("st", method)]
        if approved_only:
            params += [("m[]", i) for i in DORAR_IDS]
        return f"{SITE_URL}?{urlencode(params)}"

    async def search(self, query: str, method: str = "w") -> DorarResult:
        """Search Dorar filtered to the approved scholars. Falls back to the public JSON API,
        then keeps only approved scholars by name."""
        url = self.site_url(query, method)
        res = DorarResult(query=query, method=method, search_url=self.site_url(query, method, False))
        try:
            res.hadiths = parse_site_html(await self._get(url))
            _mark(True)
            if res.hadiths:
                return res
        except Exception as e:  # noqa: BLE001 - any failure falls through to the API
            res.error = f"site: {type(e).__name__}"
        try:
            api = f"{API_URL}?{urlencode({'skey': query})}"
            hadiths = parse_api_json(await self._get(api))
            res.hadiths = [h for h in hadiths if find_scholar(h.mohdith)]
            _mark(True)
        except Exception as e:  # noqa: BLE001
            res.error = (res.error + "; " if res.error else "") + f"api: {type(e).__name__}"
        if res.error and not res.hadiths:
            _mark(False, res.error)
        return res


# Plan item 17: what /api/health reports about Dorar (times are UTC, ISO 8601).
STATUS = {"last_ok": None, "last_error": None, "last_error_at": None}


def _mark(ok: bool, err: str = "") -> None:
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    if ok:
        STATUS["last_ok"] = now
    else:
        STATUS["last_error"], STATUS["last_error_at"] = err, now


def reachable() -> bool | None:
    """True or False from the latest search, None before any search since the server started."""
    ok, bad = STATUS["last_ok"], STATUS["last_error_at"]
    if ok is None and bad is None:
        return None
    return bad is None or (ok is not None and ok >= bad)


_client: DorarClient | None = None


def get_dorar() -> DorarClient:
    global _client
    if _client is None:
        _client = DorarClient()
    return _client
