"""The checking pipeline: extract citations, trace each one to its source, report verbatim, or refer."""
import asyncio
import logging
import re
import time

from rapidfuzz import fuzz

from . import llm
from .config import settings
from .dorar import DorarResult, get_dorar
from .extract import Candidate, extract
from .glossary import gloss_book, gloss_grade
from .normalize import normalize_ar, skeleton_ar
from .quran import QuranMatch, get_quran
from .scholars import EDITORS, GROUP_LABELS, IMAMS, find_scholar, grade_flags, is_hadith_level_grading

log = logging.getLogger("tathabbut")

STRONG_MATCH = 85
WEAK_MATCH = 60

FATWA_BODY = {
    "ar": "الرئاسة العامة للبحوث العلمية والإفتاء",
    "en": "The General Presidency of Scholarly Research and Ifta (Saudi Arabia)",
    "url": "https://www.alifta.gov.sa",
}
PERSONAL_FATWA = re.compile(
    r"هل يجوز لي|هل يحل لي|هل علي|ما حكم (?:ما فعلت|زواجي|طلاقي|صلاتي|صيامي)|أنا في (?:دولة|بلد)|"
    r"is it (?:halal|haram|permissible|allowed) for me|am i allowed to|can i (?:marry|divorce)|my (?:husband|wife) (?:said|did)",
    re.I,
)


def _strip_harakat(text: str) -> str:
    return re.sub("[ً-ٰٟـ]", "", text)


def _similarity(quote: str, source: str) -> float:
    a, b = skeleton_ar(quote), skeleton_ar(source)
    if not a or not b:
        return 0.0
    return float(fuzz.partial_ratio(a, b))


def _dorar_queries(quote: str) -> list[tuple[str, str]]:
    words = _strip_harakat(quote).split()
    out = []
    if len(words) <= 12:
        out.append((" ".join(words), "w"))
    if len(words) > 8:
        out.append((" ".join(words[:8]), "w"))
    if len(words) >= 4:
        out.append((" ".join(words[:4]), "p"))
    seen, uniq = set(), []
    for q in out:
        if q not in seen:
            seen.add(q)
            uniq.append(q)
    return uniq[:3]


async def _search_dorar(quote: str) -> DorarResult | None:
    if not settings.dorar_enabled:
        return None
    client = get_dorar()
    last = None
    for query, method in _dorar_queries(quote):
        last = await client.search(query, method)
        if last.hadiths:
            return last
    return last


SAHIHAYN = ("صحيح البخاري", "صحيح مسلم")


def _grade_groups(quote: str, res: DorarResult, min_sim: float = WEAK_MATCH) -> dict:
    items, hidden, seen = [], 0, set()
    for h in res.hadiths:
        scholar = find_scholar(h.mohdith, h.mohdith_id)
        if not scholar:
            continue
        if not is_hadith_level_grading(scholar, h.grade):
            hidden += 1
            continue
        sim = _similarity(quote, h.text)
        if sim < min_sim:
            continue
        key = (scholar.key, normalize_ar(h.book), h.number)
        if key in seen:
            continue
        seen.add(key)
        items.append({
            "scholar_key": scholar.key, "scholar_ar": scholar.name_ar, "scholar_en": scholar.name_en,
            "died_ah": scholar.died_ah, "group": scholar.group, "grade": h.grade, "book": h.book,
            "number": h.number, "rawi": h.rawi, "text": h.text, "url": h.url,
            "similarity": round(sim, 1), "flags": grade_flags(h.grade),
            "grade_gloss": gloss_grade(h.grade), "book_en": gloss_book(h.book),
        })
    groups = []
    for g in (IMAMS, EDITORS):
        g_items = sorted((i for i in items if i["group"] == g), key=lambda i: (i["died_ah"], -i["similarity"]))
        if g_items:
            groups.append({"group": g, "label_ar": GROUP_LABELS[g]["ar"], "label_en": GROUP_LABELS[g]["en"], "items": g_items})
    flagged_scholars = sorted({(i["died_ah"], i["scholar_ar"], i["scholar_en"]) for i in items if "fabricated" in i["flags"]})
    flagged = [ar for _, ar, _ in flagged_scholars]
    best = max((i["similarity"] for i in items), default=0.0)
    # The package puts the two Sahihs first. Decided by the source book, not the scholar's name: al-Bukhari
    # and Muslim narrate in other books too, and those are not all authentic (Dorar FAQ 13).
    sahihayn = []
    for book in SAHIHAYN:
        hits = [i for i in items if normalize_ar(i["book"]) == normalize_ar(book) and i["similarity"] >= STRONG_MATCH]
        if hits:
            best_hit = max(hits, key=lambda i: i["similarity"])
            sahihayn.append({"book": book, "book_en": gloss_book(book), "number": best_hit["number"], "url": best_hit["url"]})
    return {
        "query": res.query, "search_url": res.search_url, "groups": groups, "best_similarity": best,
        "fabricated_by": flagged, "fabricated_by_en": [en for _, _, en in flagged_scholars], "hidden_narrator_statements": hidden, "error": res.error or None,
        "count": len(items), "sahihayn": sahihayn,
    }


_SPECIALIST = {
    "hadith": ("مختص في الحديث", "a hadith specialist"),
    "quran": ("مختص في علوم القرآن", "a specialist in Quranic studies"),
}


def _referral(reason_ar: str, reason_en: str, field: str = "hadith") -> dict:
    ar, en = _SPECIALIST[field]
    return {"ar": f"{reason_ar} يُحال إلى {ar} للتحقق.", "en": f"{reason_en} Please refer to {en}."}


async def check_hadith(c: Candidate, out: dict) -> None:
    quote = c.quote
    if c.lang != "ar":
        if not llm.available():
            out["status"] = "needs_model"
            out["referral"] = _referral(
                "النص بغير العربية ويحتاج إلى النموذج اللغوي للبحث عن أصله، وهو غير مفعّل الآن.",
                "This quote is not in Arabic and needs the language model to find its source, which is off right now.",
            )
            return
        arabic = await llm.arabic_search_wording(quote, "hadith")
        out["search_wording_ar"] = arabic
        out["notes"].append("search_wording_by_model")
        quote = arabic
        if not arabic:
            out["status"] = "not_found"
            out["referral"] = _referral("لم نتمكن من البحث عن أصل هذا النص.", "We could not search for this text.")
            return

    q = get_quran().match_arabic(quote) if c.lang == "ar" else None
    if q and q.status == "exact":
        out["notes"].append("hadith_is_quran")
        out["quran"] = q.to_dict()

    res = await _search_dorar(quote)
    if res is None:
        out["status"] = "source_offline"
        return
    if not res.hadiths and res.error:
        out["status"] = "source_error"
        out["hadith"] = {"query": res.query, "search_url": res.search_url, "error": res.error, "groups": []}
        out["referral"] = _referral("تعذّر الوصول إلى الموسوعة الحديثية الآن.", "The hadith encyclopedia could not be reached.")
        return

    if c.lang != "ar":
        # The model picks which Arabic text is the source of the translated quote; we then keep the
        # gradings of that text only. The user always sees the Arabic text to judge for themselves.
        texts = []
        for h in res.hadiths:
            if find_scholar(h.mohdith, h.mohdith_id) and h.text not in texts:
                texts.append(h.text)
        texts = texts[:4]
        pick = await llm.pick_match(c.quote, texts) if texts else 0
        if pick == 0:
            out["status"] = "not_found"
            out["hadith"] = _grade_groups(quote, res, min_sim=101)  # nothing shown
            out["referral"] = _referral("لم نجد أصلًا عربيًا مطابقًا لهذا النص المترجم.", "No matching Arabic source was found for this translated text.")
            return
        quote = texts[pick - 1]
        out["matched_arabic"] = quote
        out["notes"].append("match_by_model")

    info = _grade_groups(quote, res)
    out["hadith"] = info
    if info["count"] and info["best_similarity"] >= STRONG_MATCH:
        out["status"] = "graded"
    elif info["count"]:
        out["status"] = "found_similar"
        out["notes"].append("wording_differs")
    else:
        out["status"] = "not_found"
        out["referral"] = _referral(
            "لم نجد حكمًا لأحد علماء الحديث المعتمدين على هذا النص.",
            "We found no grading of this text by the approved hadith scholars.",
        )


async def check_quran(c: Candidate, out: dict) -> None:
    Q = get_quran()
    prefer = (c.ref_surah, c.ref_ayah) if c.ref_surah else None
    m: QuranMatch = Q.match_arabic(c.quote, prefer) if c.lang == "ar" else Q.match_english(c.quote, prefer)
    if m.status == "not_found" and c.lang != "ar" and llm.available():
        arabic = await llm.arabic_search_wording(c.quote, "quran")
        out["search_wording_ar"] = arabic
        if arabic:
            m2 = Q.match_arabic(arabic)
            if m2.status != "not_found":
                m = m2
                m.via = "english_llm"
                m.status = "differs"
                m.diff = []
                out["notes"].append("match_by_model")
    if c.ref_surah:
        Q.check_reference(m, c.ref_surah, c.ref_ayah, c.ref_label)
    out["quran"] = m.to_dict()
    if m.status == "exact":
        out["status"] = "verified"
    elif m.status == "differs":
        out["status"] = "differs"
    else:
        out["status"] = "not_in_mushaf"
        if c.lang == "ar":
            # Often a hadith or a saying circulated as if it were an ayah.
            res = await _search_dorar(c.quote)
            if res and res.hadiths:
                info = _grade_groups(c.quote, res)
                if info["count"]:
                    out["hadith"] = info
                    out["notes"].append("quran_claim_found_in_hadith")
        found_as_hadith = "quran_claim_found_in_hadith" in out["notes"]
        why = (("لم نجد هذا النص في المصحف.", "This text was not found in the Mushaf.") if c.lang == "ar"
               else ("لم نجد آية تقابل هذه الترجمة.", "We could not match this to any verse."))
        out["referral"] = _referral(*why, "hadith" if found_as_hadith else "quran")
    if m.reference_ok is False:
        out["notes"].append("wrong_reference")


async def _model_candidates(text: str, existing: list[Candidate]) -> tuple[list[Candidate], int]:
    """Ask the model for citations the rules missed. Anything not found verbatim in the text is dropped."""
    try:
        items = await llm.extract_citations(text[:3000])
    except Exception as e:  # noqa: BLE001 - model trouble must never break the check
        log.warning("model extraction failed: %s", e)
        return [], 0
    text_sk = skeleton_ar(text)
    have = [skeleton_ar(c.quote) or c.quote.lower() for c in existing]
    out, dropped = [], 0
    for it in items:
        quote = it["quote"]
        sk = skeleton_ar(quote)
        ar = bool(sk)
        present = (sk in text_sk) if ar else (quote.lower() in text.lower())
        if not present or len(quote) < 6:
            dropped += 1
            continue
        key = sk or quote.lower()
        if any(key in h or h in key for h in have):
            continue
        pos = text.find(quote)
        out.append(Candidate(it["type"], quote, max(pos, 0), max(pos, 0) + len(quote), "ar" if ar else "en", "model", found_by="model"))
        have.append(key)
    return out, dropped


async def check_text(text: str, deep: bool = False) -> dict:
    t0 = time.monotonic()
    text = text[: settings.max_text_chars]
    cands = extract(text)
    dropped = 0
    if deep and llm.available():
        extra, dropped = await _model_candidates(text, cands)
        cands = sorted(cands + extra, key=lambda c: c.start)
    cands = cands[: settings.max_citations]

    results = []
    for i, c in enumerate(cands, 1):
        out = {
            "id": i, "type": c.type, "quote": c.quote, "lang": c.lang, "found_by": c.found_by,
            "marker": c.marker, "status": "", "quran": None, "hadith": None, "referral": None, "notes": [],
        }
        try:
            if c.type == "quran":
                await check_quran(c, out)
            else:
                await check_hadith(c, out)
        except Exception as e:  # noqa: BLE001
            log.exception("check failed")
            out["status"] = "error"
            out["error"] = type(e).__name__
            out["referral"] = _referral("حدث خطأ أثناء التحقق.", "An error occurred while checking.")
        out["tier"] = evidence_tier(out)
        results.append(out)

    fatwa = bool(PERSONAL_FATWA.search(text))
    return {
        "citations": results,
        "level_d": {"detected": True, "body": FATWA_BODY} if fatwa else None,
        "summary": _summary(results),
        "model": {"backend": llm.backend.name, "used": deep and llm.available(), "dropped_unverifiable": dropped},
        "elapsed_ms": int((time.monotonic() - t0) * 1000),
    }


def evidence_tier(r: dict) -> str:
    """The track's success criterion asks to tell apart what the sources support, what needs more
    verification, and what must be referred. Every citation gets exactly one of these:
    documented (traced to its source), verify (needs more verification), refer (to a specialist)."""
    if r["referral"]:
        return "refer"
    if r["status"] in ("verified", "graded") and not {"wrong_reference", "match_by_model"} & set(r["notes"]):
        return "documented"
    return "verify"


def _summary(results: list[dict]) -> dict:
    """Counts only. "documented" means traced to its source, not that the text is authentic."""
    s = {"total": len(results), "quran": 0, "hadith": 0, "documented": 0, "verify": 0, "refer": 0, "fabricated_flag": 0}
    for r in results:
        s[r["type"]] += 1
        s[r["tier"]] += 1
        if (r.get("hadith") or {}).get("fabricated_by"):
            s["fabricated_flag"] += 1
    return s


def run(text: str, deep: bool = False) -> dict:
    return asyncio.run(check_text(text, deep))
