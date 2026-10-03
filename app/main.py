"""تثبّت · Tathabbut: web app and API."""
import logging
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
STATIC = Path(__file__).resolve().parent.parent / "static"

app = FastAPI(
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


@app.on_event("startup")
async def _startup():
    get_quran()
    if settings.llm_backend == "llamacpp":
        import asyncio

        asyncio.create_task(llm.backend.warm())  # download/load ALLaM in the background


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
        "model_ready": getattr(llm.backend, "_llm", None) is not None or llm.backend.name == "openai",
        "dorar_enabled": settings.dorar_enabled,
        "dorar_reachable": dorar.reachable() if settings.dorar_enabled else False,
        "dorar_last_ok": dorar.STATUS["last_ok"],
        "dorar_last_error": dorar.STATUS["last_error"],
        "dorar_last_error_at": dorar.STATUS["last_error_at"],
        "fatwa_search": settings.fatwa_search,
    }


def _git_commit() -> str | None:
    """The deployed commit, read from .git without the git program (the Space clones the repo)."""
    from pathlib import Path

    g = Path(__file__).resolve().parent.parent / ".git"
    try:
        head = (g / "HEAD").read_text().strip()
        if head.startswith("ref: "):
            ref = head[5:]
            f = g / ref
            if f.exists():
                return f.read_text().strip()[:7]
            for line in (g / "packed-refs").read_text().splitlines():
                if line.endswith(" " + ref):
                    return line[:7]
            return None
        return head[:7]
    except OSError:
        return None


_VERSION = {"commit": _git_commit()}


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


@app.get("/")
async def index():
    return FileResponse(STATIC / "index.html")


app.mount("/static", StaticFiles(directory=STATIC), name="static")
