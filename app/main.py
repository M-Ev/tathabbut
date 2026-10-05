"""تثبّت · Tathabbut: web app and API."""
import contextlib
import json
import logging
import re
import time
from collections import defaultdict, deque
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import llm
from .config import settings
from .pipeline import check_text
from .quran import get_quran

logging.basicConfig(level=logging.INFO)
try:  # the MCP endpoint is an extra; the site must start without it
    from . import mcp_server
except Exception as e:  # noqa: BLE001
    logging.getLogger("tathabbut").warning("MCP endpoint disabled: %s", e)
    mcp_server = None
STATIC = Path(__file__).resolve().parent.parent / "static"

@contextlib.asynccontextmanager
async def _lifespan(_app):
    get_quran()
    if settings.llm_backend == "llamacpp":
        import asyncio

        asyncio.create_task(llm.backend.warm())  # download/load ALLaM in the background
    if mcp_server is None:
        yield
        return
    async with mcp_server.mcp.session_manager.run():  # the /mcp endpoint (agents call the check as a tool)
        yield


app = FastAPI(
    lifespan=_lifespan,
    title="تثبّت · Tathabbut",
    description=(
        "Traces every Quran verse and hadith in a text to its Arabic source and shows the approved hadith "
        "scholars' gradings verbatim. It never issues a ruling: when nothing is found it says so and refers "
        "to a specialist. Note: user text is not stored; only extracted hadith wording is sent to Dorar."
    ),
    version="0.1.0",
)


class CheckRequest(BaseModel):
    text: str = Field(..., min_length=3, description="The post, lecture or chatbot answer to check (Arabic or English).")
    deep: bool = Field(False, description="Also ask the language model (ALLaM) to find citations the rules missed. Slower.")


# Simple per-IP limit to protect the demo and the sources we call.
_hits: dict[str, deque] = defaultdict(deque)
RATE = 20  # requests per 10 minutes per IP


def _rate_limit(ip: str):
    now, q = time.monotonic(), _hits[ip]
    while q and now - q[0] > 600:
        q.popleft()
    if len(q) >= RATE:
        raise HTTPException(429, "Too many requests, please wait a few minutes.")
    q.append(now)


def _client_ip(request: Request) -> str:
    """Behind the Hugging Face proxy every visitor arrives from the proxy's address, so they would all share one
    limit (plan item 16). The proxy appends the visitor's address to X-Forwarded-For; its last entry is the one
    the proxy added, so a visitor cannot choose it."""
    fwd = request.headers.get("x-forwarded-for", "")
    if fwd.strip():
        return fwd.split(",")[-1].strip()
    return request.client.host if request.client else "?"


@app.post("/api/check")
async def api_check(req: CheckRequest, request: Request):
    _rate_limit(_client_ip(request))
    return await check_text(req.text, deep=req.deep)


@app.get("/api/health")
async def health():
    """What works right now (plan item 17): the Quran check needs nothing outside; hadith need Dorar."""
    from . import dorar

    q = get_quran()
    return {
        "ok": True,
        "version": _VERSION,
        "quran_verses": len(q.ayat),
        "model_backend": llm.backend.name,
        "model_ready": llm.backend.ready(),
        "models": llm.describe(),
        "dorar_enabled": settings.dorar_enabled,
        "dorar_reachable": dorar.reachable() if settings.dorar_enabled else False,
        "dorar_last_ok": dorar.STATUS["last_ok"],
        "dorar_last_error": dorar.STATUS["last_error"],
        "dorar_last_error_at": dorar.STATUS["last_error_at"],
        "fatwa_search": settings.fatwa_search,
    }


from .version import VERSION as _VERSION  # noqa: E402


@app.get("/api/sources")
async def sources():
    """Every source the tool uses, for API users to cite. All are from the challenge's scientific package except
    the level د referral: the package says to refer to a qualified body and names none, so the team chose the
    two scholars' published fatwas first (shown verbatim with their source, app/fatwa.py) and then the official fatwa body."""
    from .pipeline import FATWA_BODY, FATWA_REFERENCES
    from .scholars import SCHOLARS

    return {
        "package": "المرجعية العلمية المعتمدة، الحزمة العلمية لتحدي الذكاء الاصطناعي في خدمة المحتوى الإسلامي",
        "quran": get_quran().source,
        "quran_links": "quranpedia.net",
        "hadith": "الموسوعة الحديثية، الدرر السنية (dorar.net/hadith)",
        "approved_scholars": [
            {"ar": s.name_ar, "en": s.name_en, "died_ah": s.died_ah, "group": s.group} for s in SCHOLARS
        ],
        "terms": "موسوعة الجمهرة - مفردات المحتوى الإسلامي (islamic-content.com/dictionary)",
        "fatwa_referral": FATWA_BODY,
        "fatwa_references": FATWA_REFERENCES,
        "fatwa_referral_note": "Team's choice for level د: the package says «يحيل إلى جهة مؤهلة» and names no body. The tool shows the two scholars' published fatwas on close questions verbatim with source and link (Ibn Baz in full; Ibn al-Uthaymeen question and opening line, as the foundation reserves its rights). They are found by each site's own search and ordered by word overlap; the language model never writes or picks a fatwa.",
    }


@app.middleware("http")
async def _revalidate(request: Request, call_next):
    """After every rebuild visitors must get the new pages and scripts, not a cached copy."""
    response = await call_next(request)
    if request.url.path == "/" or request.url.path.startswith("/static/"):
        response.headers["Cache-Control"] = "no-cache"
    return response


# MCP over streamable HTTP at /mcp, sharing the web API's per-visitor limit.
if mcp_server is not None:
    mcp_server.guard = lambda request: _rate_limit(_client_ip(request))
    app.router.routes.extend(mcp_server.mcp.streamable_http_app().routes)


@app.get("/api/archive")
async def archive():
    """The public archive: commonly circulated citations as the tool checked them (scripts/build_archive.py)."""
    f = Path(__file__).resolve().parent.parent / "data" / "archive.json"
    if not f.exists():
        return {"entries": [], "checked_at": None, "reviewed": False}
    return FileResponse(f, media_type="application/json")


# The verses on the pillars page, from the Mushaf file as it is, with the approved translations of their meanings.
_PILLAR_VERSES = {"shahada": (47, 19, 19), "salah": (2, 238, 238), "zakah": (2, 43, 43), "sawm": (2, 183, 183),
                  "hajj": (3, 97, 97), "fatiha": (1, 1, 7)}


@app.get("/api/pillars")
async def pillars():
    q = get_quran()
    out = {}
    for key, (s, a, b) in _PILLAR_VERSES.items():
        ayat = [q.ayat[q.index[(s, n)]] for n in range(a, b + 1)]
        en = [re.sub(r"\s*\[\d+\]", "", re.sub(r"^\s*\d+\.\s*", "", x.translation_en)).strip() for x in ayat]
        out[key] = {"surah": s, "ayah_from": a, "ayah_to": b, "surah_ar": q.surahs[s]["ar"], "surah_en": q.surahs[s]["tr"],
                    "ayat": [{"ayah": x.ayah, "text": x.text} for x in ayat],
                    "translations": {"en": {"text": " ".join(en), "name": "Al-Hilali & Muhsin Khan (King Fahd Complex)"},
                                     **{k: {"text": v["text"], "name": v["name"]} for k, v in q.translations_for(s, a, b).items()}}}
    return out


_DATA = Path(__file__).resolve().parent.parent / "data"


def _verse(q, s: int, a: int, b: int, lang: str | None = None) -> dict:
    ayat = [q.ayat[q.index[(s, n)]] for n in range(a, b + 1)]
    out = {"surah": s, "ayah_from": a, "ayah_to": b, "surah_ar": q.surahs[s]["ar"], "surah_en": q.surahs[s]["tr"],
           "ayat": [{"ayah": x.ayah, "text": x.text} for x in ayat]}
    if lang == "en":
        out["meaning"] = {"text": " ".join(re.sub(r"\s*\[\d+\]", "", re.sub(r"^\s*\d+\.\s*", "", x.translation_en)).strip() for x in ayat),
                          "name": "Al-Hilali & Muhsin Khan (King Fahd Complex)"}
    elif lang and lang != "ar":
        tr = q.translations_for(s, a, b).get(lang)
        if tr:
            out["meaning"] = {"text": tr["text"], "name": tr["name"]}
    return out


@app.get("/api/adhkar")
async def adhkar(lang: str = "ar"):
    """The verified adhkar (scripts/build_adhkar.py): hadith items with the grading that supports each where it is
    shown, and Quran items copied from the Mushaf with the reader's approved translation."""
    f = _DATA / "adhkar.json"
    if not f.exists():
        return {"categories": [], "hadith": [], "quran": []}
    d = json.loads(f.read_text(encoding="utf-8"))
    q = get_quran()
    for x in d.get("quran", []):
        x.update(_verse(q, x["surah"], x["ayah_from"], x["ayah_to"], lang))
    for x in d.get("hadith", []):  # the page needs the supporting narration's text; the others by name and link only
        c = x.get("check", {})
        c["narrations"] = [{k: n.get(k) for k in ("scholar_ar", "grade", "book", "number", "url", "authentic")}
                           for n in c.get("narrations", [])[:6]]
        c.pop("sahihayn", None)
    return d


@app.get("/api/mushaf/{surah}")
async def mushaf(surah: int, lang: str = "ar", ayah: int | None = None):
    """A surah from the Mushaf file (or one ayah of it), each ayah with its approved translation in `lang`."""
    q = get_quran()
    if surah not in q.surahs:
        raise HTTPException(404, "no such surah")
    n = max(a.ayah for a in q.ayat if a.surah == surah)
    a, b = (ayah, ayah) if ayah and 1 <= ayah <= n else (1, n)
    out = _verse(q, surah, a, b, None)
    if lang != "ar":
        for x in out["ayat"]:
            m = _verse(q, surah, x["ayah"], x["ayah"], lang).get("meaning")
            if m:
                x["meaning"] = m["text"]
                out["meaning_name"] = m["name"]
    return {**out, "url": f"https://quranpedia.net/surah/1/{surah}"}


@app.get("/api/mushaf")
async def mushaf_index():
    q = get_quran()
    counts: dict = {}
    for a in q.ayat:
        counts[a.surah] = counts.get(a.surah, 0) + 1
    return {"total": len(q.ayat), "surahs": [{"n": n, "ar": s["ar"], "tr": s["tr"], "ayat": counts[n]} for n, s in sorted(q.surahs.items())]}


@app.get("/api/asma")
async def asma(lang: str = "ar"):
    d = json.loads((_DATA / "asma.json").read_text(encoding="utf-8"))
    q = get_quran()
    for x in d["names"]:
        x["verse"] = _verse(q, x["surah"], x["ayah"], x["ayah"], lang)
    return d


@app.get("/")
async def index():
    return FileResponse(STATIC / "index.html")


app.mount("/static", StaticFiles(directory=STATIC), name="static")
