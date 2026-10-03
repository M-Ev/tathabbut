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


@app.post("/api/check")
async def api_check(req: CheckRequest, request: Request):
    _rate_limit(request.client.host if request.client else "?")
    return await check_text(req.text, deep=req.deep)


@app.get("/api/health")
async def health():
    q = get_quran()
    return {
        "ok": True,
        "quran_verses": len(q.ayat),
        "model_backend": llm.backend.name,
        "model_ready": getattr(llm.backend, "_llm", None) is not None or llm.backend.name == "openai",
        "dorar_enabled": settings.dorar_enabled,
    }


@app.get("/api/sources")
async def sources():
    """Every source the tool uses, for API users to cite. All are from the challenge's scientific package except
    the level د referral: the package says to refer to a qualified body and names none, so the team chose the
    official fatwa body and the two scholars' fatwa sites (links only)."""
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
        "fatwa_referral_note": "Team's choice for level د: the package says «يحيل إلى جهة مؤهلة» and names no body. The tool links to these and never quotes or relies on a fatwa in its results.",
    }


@app.get("/")
async def index():
    return FileResponse(STATIC / "index.html")


app.mount("/static", StaticFiles(directory=STATIC), name="static")
