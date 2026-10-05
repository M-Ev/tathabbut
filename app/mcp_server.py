"""Tathabbut as an MCP server: the citation check as a tool an AI agent can call (the chatbot use, over MCP).

An Islamic chatbot built on any model can call these tools before it answers. They only look up and compare:
every text returned is copied from the approved sources with its identifier and link, never written by a model,
and nothing here issues a ruling. Served at /mcp (streamable HTTP, stateless) beside the web app.

Tools:
- check_citations: the same check as POST /api/check, returned compactly with the decision for chatbots.
- get_ayah: the Mushaf text of an ayah or a range, so an agent quotes the Quran instead of writing it.
- list_sources: the sources and the approved hadith scholars, for the agent to cite.
"""
from mcp.server.fastmcp import Context, FastMCP
from mcp.server.transport_security import TransportSecuritySettings

from .pipeline import DISCLAIMER, check_text
from .quran import get_quran

INSTRUCTIONS = (
    "Tathabbut checks Quran and hadith citations against approved sources. Call check_citations on a draft answer "
    "before showing it; follow `decision.action` (pass, annotate, block) and show the source text and links it "
    "returns. Never present a grading or an ayah that the tools did not return; when a citation is referred to a "
    "specialist, say so. Use get_ayah to quote the Quran exactly. The tools never rule on a hadith or give a fatwa."
)

mcp = FastMCP(
    "tathabbut",
    instructions=INSTRUCTIONS,
    stateless_http=True,
    json_response=True,
    streamable_http_path="/mcp",
    # The Space sits behind Hugging Face's proxy under its own host name; the check has no user state to protect.
    transport_security=TransportSecuritySettings(enable_dns_rebinding_protection=False),
)

# Set by app.main so MCP calls share the web API's per-visitor rate limit.
guard = None


def _guard(ctx: Context | None):
    request = getattr(getattr(ctx, "request_context", None), "request", None) if ctx else None
    if guard and request is not None:
        guard(request)


def _source(c: dict) -> dict | None:
    q, h = c.get("quran"), c.get("hadith")
    if q and q.get("ref"):
        out = {"kind": "quran", "ref": q["ref"], "surah_ar": q.get("surah_name_ar"), "surah_en": q.get("surah_name_en"),
               "mushaf_text": q.get("mushaf_text"), "url": q.get("url"), "reference_ok": q.get("reference_ok"),
               "differences": [d for d in q.get("diff") or [] if d.get("op") != "equal"]}
        if q.get("cited"):
            out["reference_written"] = {k: q["cited"].get(k) for k in ("surah", "ayah", "surah_name_ar", "text")}
        return out
    if h and h.get("groups"):
        gradings = [{"scholar_ar": i["scholar_ar"], "scholar_en": i["scholar_en"], "died_ah": i["died_ah"],
                     "group": g["label_en"], "grading": i["grade"], "book": i["book"], "number": i["number"],
                     "narration": i["text"], "wording": i.get("match"), "url": i["url"]}
                    for g in h["groups"] for i in g["items"]]
        return {"kind": "hadith", "search_url": h.get("search_url"), "sahihayn": h.get("sahihayn"),
                "gradings_verbatim": gradings}
    return None


@mcp.tool()
async def check_citations(text: str, ctx: Context | None = None) -> dict:
    """Check every Quran verse and hadith quoted in a text (Arabic or English) against the approved sources.

    Returns, per citation, its status, the source text with identifier and link (the Mushaf for ayat; the
    approved scholars' gradings copied verbatim from Dorar for hadith) or a referral to a specialist, plus a
    `decision` for chatbots (pass / annotate / block) and `coverage` saying what could not be checked. For a
    ruling question, `fatwa_referral` holds Ibn Baz's and Ibn al-Uthaymeen's fatwas and `answer`, a sentence
    quoted from one of them and checked letter by letter against it.
    """
    _guard(ctx)
    r = await check_text(text[:8000], deep=False)
    cites = []
    for c in r["citations"]:
        cites.append({
            "n": c["id"], "type": c["type"], "quote": c["quote"], "span": c.get("quote_span"),
            "status": c["status"], "evidence": c.get("tier"), "notes": c.get("notes"),
            "written_attribution": c.get("attribution"), "source": _source(c),
            "referral": c.get("referral"),
        })
    return {"citations": cites, "decision": r["decision"], "coverage": r["coverage"],
            "personal_fatwa_question": bool(r.get("level_d")), "fatwa_referral": r.get("level_d"),
            "asked_about": r.get("asked_about"),
            "disclaimer": DISCLAIMER, "versions": r["versions"]}


@mcp.tool()
async def get_ayah(surah: int, ayah: int, to_ayah: int | None = None, ctx: Context | None = None) -> dict:
    """Return the Mushaf text (King Fahd Complex, Hafs) of an ayah or a range in one surah, with its link and
    the King Fahd Complex English translation. Quote this text instead of writing an ayah from memory."""
    _guard(ctx)
    Q = get_quran()
    last = to_ayah or ayah
    if surah not in Q.surahs or ayah < 1 or last < ayah or last - ayah > 30:
        return {"error": "No such ayah range (one surah, at most 31 ayat)."}
    ayat = [Q.get(surah, n) for n in range(ayah, last + 1)]
    if any(a is None for a in ayat):
        count = sum(1 for (sn, _) in Q.index if sn == surah)
        return {"error": f"Surah {surah} has {count} ayat."}
    s = Q.surahs[surah]
    return {"ref": f"{surah}:{ayah}" + (f"-{last}" if last != ayah else ""), "surah_ar": s.get("ar"), "surah_en": s.get("tr"),
            "ayat": [{"ayah": a.ayah, "text": a.text, "translation_en": a.translation_en} for a in ayat],
            "url": f"https://quranpedia.net/ayahs/{surah}/{ayah}", "source": Q.source}


@mcp.tool()
async def list_sources(ctx: Context | None = None) -> dict:
    """The sources Tathabbut uses and the approved hadith scholars, to cite alongside its results."""
    _guard(ctx)
    from .main import sources

    return await sources()
