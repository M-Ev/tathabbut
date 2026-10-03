"""Published fatwas of Shaykh Abd al-Aziz ibn Baz and Shaykh Muhammad ibn Salih al-Uthaymeen for level د questions.

Team's choice (owner, 3 Oct 2026): a personal fatwa question is answered with the two scholars' own published
fatwas on close questions, then a referral to the official fatwa body. The tool never writes, summarises or
picks a ruling, and the language model is not used here at all:
- candidates come from each official site's own search,
- they are ordered by word overlap between the user's question and the fatwa's title and question (rapidfuzz),
  and only those above MIN_SCORE are shown, at most PER_SCHOLAR each,
- the text is shown verbatim as published, with its source and link.

Reuse terms differ (checked 3 Oct 2026):
- binbaz.org.sa: «جميع الحقوق محفوظة والنقل متاح لكل مسلم بشرط ذكر المصدر», so the full text is shown with its source.
- binothaimeen.net: «جميع الحقوق محفوظة لمؤسسة الشيخ محمد بن صالح العثيمين الخيرية», and the Shaykh asked that
  his words not be published elsewhere without permission. Until the team decides otherwise, only the question and
  the opening line of the answer are shown, verbatim, with a link to the full fatwa on the foundation's site.

Privacy: only the question sentence (without names, numbers or the rest of the text) is sent to the two sites.
"""
import asyncio
import html
import logging
import re
import time
from urllib.parse import quote

import httpx
from rapidfuzz import fuzz

from .config import settings
from .dorar import _Cache
from .normalize import normalize_ar

log = logging.getLogger("tathabbut")

PER_SCHOLAR = 3
MIN_SCORE = 60  # share of the question's words in a fatwa's title (0-100); measured in eval/fatwa_cases.jsonl
MIN_INTERVAL = 0.5  # seconds between requests to the same site

BINBAZ_SEARCH = "https://binbaz.org.sa/api/search"
BINBAZ_FATWA = "https://binbaz.org.sa/fatwas/{ref}"
BINBAZ_SEARCH_PAGE = "https://binbaz.org.sa/search?q={q}"
UTH_SEARCH = "https://shekhcp.binothaimeen.net/api/search-data"
UTH_SHOW = "https://shekhapi.binothaimeen.net/lessons/audios/show/{id}/0/1?getManySectionsWithAllParent=audio_library&getAllPaths=1"
UTH_PAGE = "https://binothaimeen.net/ar/voice_library/lessonDetails/{search}/{title}/{id}"
UTH_SEARCH_PAGE = "https://binothaimeen.net/ar/Searchpage/{q}"

SCHOLARS = {
    "binbaz": {
        "ar": "سماحة الشيخ عبدالعزيز بن باز رحمه الله", "en": "Shaykh Abd al-Aziz ibn Baz",
        "site_ar": "الموقع الرسمي لسماحة الشيخ عبدالعزيز بن باز", "site_en": "Shaykh Ibn Baz's official site",
        "site": "https://binbaz.org.sa",
        "terms_ar": "النقل متاح لكل مسلم بشرط ذكر المصدر (من تذييل الموقع)",
        "terms_en": "The site allows copying for every Muslim on condition the source is named.",
        "full_text": True,
    },
    "uthaymeen": {
        "ar": "فضيلة الشيخ محمد بن صالح العثيمين رحمه الله", "en": "Shaykh Muhammad ibn Salih al-Uthaymeen",
        "site_ar": "موقع مؤسسة الشيخ محمد بن صالح العثيمين الخيرية", "site_en": "the Shaykh al-Uthaymeen Charitable Foundation's site",
        "site": "https://binothaimeen.net",
        "terms_ar": "الحقوق محفوظة لمؤسسة الشيخ، فنعرض السؤال وأول الجواب بنصه، والفتوى كاملة في موقع المؤسسة",
        "terms_en": "All rights are reserved to the Shaykh's foundation, so we show the question and the opening of the answer verbatim; the full fatwa is on the foundation's site.",
        "full_text": False,
    },
}

# Words that carry no topic: question frames, pronouns, and the package's placeholder «كذا».
_STOP = set(normalize_ar(w) for w in """
هل يجوز يحل لي لنا علي علينا ما ماذا حكم أنا انا أنت نحن في من على إلى الى عن مع أن ان إن أو او ثم و يا
هذا هذه ذلك تلك الذي التي كذا كذلك فعل أفعل افعل أعمل اعمل شيء شي بعض كل عند دولة بلد بلاد الشيخ فضيلة سماحة
أريد اريد أسأل اسال سؤال السؤال قال يقول كان يكون صار لو إذا اذا قد لقد ليس لا نعم هو هي هم أني اني
""".split())


def _is_stop(w: str) -> bool:
    return w in _STOP or (w[:1] in "وف" and w[1:] in _STOP)


def question_terms(sentence: str) -> str:
    """The question's topic words as written (the sites' own search does not unify spelling), without
    question frames. Only these words are sent to the two sites."""
    plain = re.sub("[ً-ٰٟـ]", "", sentence)
    words = [w for w in re.findall(r"[ء-ي]+", plain) if not _is_stop(normalize_ar(w)) and len(w) > 1]
    return " ".join(words[:12])


_PRONOUN = re.compile(r"(?<=...)(?:ها|هم|نا|كم|ي|ه|ك|ت)$")


def _search_stem(w: str) -> str:
    """«صيامي» → «صيام», «أكلت» → «أكل»: a fallback query for a search that matches whole words only."""
    return _PRONOUN.sub("", w)


_PREFIX = re.compile(r"^(?:وال|فال|بال|كال|لل|ال|و|ف)(?=..)")
_SUFFIX = re.compile(r"(?:هما|كما|تي|تم|هم|هن|كم|نا|ها|ات|ون|ين|ه|ي|ك|ة|ت)$")


def _stem(w: str) -> str:
    """A light stem so «زواجي» meets «الزواج» and «صيامي» meets «الصيام»; good enough for ranking, never shown."""
    w = _PREFIX.sub("", w)
    return _SUFFIX.sub("", w) if len(w) > 3 else w


def _score(terms: str, *texts: str) -> float:
    """Share of the question's words found in the fatwa's title or question (0-100), word by word."""
    q = [_stem(w) for w in terms.split()]
    if not q:
        return 0.0
    best = 0.0
    for x in texts:
        if not x:
            continue
        words = [_stem(w) for w in normalize_ar(x).split()]
        hit = sum(1 for a in q if any(a == b or (len(a) >= 3 and fuzz.ratio(a, b) >= 85) for b in words))
        best = max(best, 100.0 * hit / len(q))
    return round(best, 1)


def _text(fragment: str) -> str:
    """HTML to plain text, keeping paragraph breaks and every character of the wording."""
    s = re.sub(r"(?i)<br\s*/?>", "\n", fragment)
    s = re.sub(r"(?i)</p\s*>", "\n", s)
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s).replace("\xa0", " ").replace("\r", "")
    s = re.sub(r"[ \t]+", " ", s)
    return re.sub(r"\n\s*\n+", "\n", s).strip()


def _strip_label(s: str, label: str) -> str:
    return re.sub(rf"^\s*{label}\s*[:：]?\s*", "", s).strip()


def opening(answer: str, max_words: int = 40) -> str:
    """The first sentence of the answer, verbatim, cut at a sentence end (or after max_words with «…»)."""
    a = _strip_label(_strip_label(answer, "الجواب"), "الشيخ")
    first = a.split("\n", 1)[0]
    m = re.search(r"[.؟?!]", first)
    if m and len(first[: m.end()].split()) <= max_words:
        return first[: m.end()].strip()
    words = first.split()
    return " ".join(words[:max_words]) + (" …" if len(words) > max_words else "")


class FatwaClient:
    def __init__(self, transport: httpx.AsyncBaseTransport | None = None):
        self.http = httpx.AsyncClient(
            timeout=15, follow_redirects=True, transport=transport,
            headers={"User-Agent": settings.user_agent, "Accept-Language": "ar"},
        )
        self.cache = _Cache(500)
        self._last: dict[str, float] = {}
        self._locks = {"binbaz": asyncio.Lock(), "uthaymeen": asyncio.Lock()}

    async def _req(self, site: str, method: str, url: str, **kw):
        key = (method, url, repr(sorted(kw.get("params", {}).items())) if kw.get("params") else repr(kw.get("json")))
        hit = self.cache.get(key)
        if hit is not None:
            return hit
        async with self._locks[site]:
            wait = MIN_INTERVAL - (time.monotonic() - self._last.get(site, 0))
            if wait > 0:
                await asyncio.sleep(wait)
            r = await self.http.request(method, url, **kw)
            self._last[site] = time.monotonic()
        r.raise_for_status()
        self.cache.set(key, r)
        return r

    # Ibn Baz ---------------------------------------------------------------------------------------------
    async def binbaz(self, terms: str) -> list[dict]:
        r = await self._req("binbaz", "GET", BINBAZ_SEARCH, params={"q": terms, "type": "fatwa", "page": 1})
        found = []
        for it in (r.json().get("Search") or {}).get("results", [])[:10]:
            # «id» opens the fatwa (the site redirects to its canonical address); «reference» is another number.
            ref, title = it.get("id"), (it.get("title") or "").strip()
            if ref and title:
                found.append({"ref": ref, "title": title, "score": _score(terms, title)})
        found = [f for f in sorted(found, key=lambda f: -f["score"]) if f["score"] >= MIN_SCORE][:PER_SCHOLAR]
        out = []
        for f in found:
            try:
                out.append(await self._binbaz_fatwa(f["ref"], f["score"]))
            except Exception as e:  # noqa: BLE001 - one fatwa failing must not hide the others
                log.warning("binbaz fatwa %s failed: %s", f["ref"], e)
                out.append(self._entry("binbaz", f["title"], "", "", BINBAZ_FATWA.format(ref=f["ref"]), "", f["score"]))
        return out

    async def _binbaz_fatwa(self, ref, score) -> dict:
        r = await self._req("binbaz", "GET", BINBAZ_FATWA.format(ref=ref))
        page = r.text
        title = _text((re.search(r'<h1 class="article-title[^"]*">(.*?)</h1>', page, re.S) or [None, ""])[1])
        q = re.search(r'<h2 class="article-title article-title__question[^"]*"[^>]*>(.*?)</h2>', page, re.S)
        question = _strip_label(_text(q.group(1)), "السؤال") if q else ""
        body = re.search(r'itemprop="articleBody"[^>]*>(.*?)</div>\s*</article>', page, re.S)
        answer = _strip_label(_text(body.group(1)), "الجواب") if body else ""
        return self._entry("binbaz", title, question, answer, str(r.url), "", score)

    # Ibn Uthaymeen ---------------------------------------------------------------------------------------
    async def uthaymeen(self, terms: str) -> list[dict]:
        # The foundation's search needs most words to match; drop words from the end until it finds fatwas.
        words, items = terms.split(), []
        stems = [_search_stem(w) for w in words]
        tries = [words, words[:3], stems, stems[:3], stems[:2]]
        for q in dict.fromkeys(" ".join(t) for t in tries if t):
            r = await self._req("uthaymeen", "POST", UTH_SEARCH,
                                json={"pageSize": 30, "searchTerm": q, "page": 1, "mode": "similar", "type": "audios"})
            items = r.json().get("data", [])
            if len(items) >= PER_SCHOLAR:
                break
        found = []
        for it in items:  # the site does not order by relevance, so every result is scored
            title = _text((it.get("title") or {}).get("ar", ""))
            content = _text((it.get("content") or {}).get("ar", ""))
            # Lessons in a book series («كتاب الطلاق (الشرح الثاني) - 7») are not fatwas.
            if not it.get("id") or not title or "السؤال" not in content or re.search(r"-\s*\d+\s*$", title):
                continue
            question = content.split("الجواب", 1)[0][:400]
            found.append({"id": it["id"], "title": title, "score": _score(terms, title, question)})
        found = [f for f in sorted(found, key=lambda f: -f["score"]) if f["score"] >= MIN_SCORE][:PER_SCHOLAR]
        out = []
        for f in found:
            url = UTH_PAGE.format(search=quote("البحث"), title=quote(f["title"]), id=f["id"])
            try:
                out.append(await self._uthaymeen_fatwa(f["id"], f["title"], url, f["score"]))
            except Exception as e:  # noqa: BLE001
                log.warning("uthaymeen fatwa %s failed: %s", f["id"], e)
                out.append(self._entry("uthaymeen", f["title"], "", "", url, "", f["score"]))
        return out

    async def _uthaymeen_fatwa(self, fid, title, url, score) -> dict:
        r = await self._req("uthaymeen", "GET", UTH_SHOW.format(id=fid))
        d = r.json().get("data") or {}
        full = _text(((d.get("objective") or {}).get("content") or {}).get("ar", ""))
        q, _, a = full.partition("الجواب")
        source = []
        for sec in d.get("many_sections") or []:
            chain, p = [], sec
            while p:
                chain.append(((p.get("title") or {}).get("ar") or "").strip())
                p = p.get("all_parent")
            if len(chain) > 1:  # a series (e.g. فتاوى نور على الدرب) rather than a topic tag
                source = [chain[1], chain[0]]
                break
        return self._entry("uthaymeen", title, _strip_label(q, "السؤال"), a.lstrip(" :：\n"), url, "، ".join(source), score)

    def _entry(self, who, title, question, answer, url, source, score) -> dict:
        s = SCHOLARS[who]
        e = {"scholar": who, "title": title, "question": question, "opening": opening(answer) if answer else "",
             "url": url, "source": source, "score": score}
        if s["full_text"] and answer:
            e["answer"] = answer
        return e


_client: FatwaClient | None = None


def get_client() -> FatwaClient:
    global _client
    if _client is None:
        _client = FatwaClient()
    return _client


async def find_fatwas(sentence: str) -> dict:
    """Published fatwas of the two scholars on questions close to `sentence`. Never raises."""
    terms = question_terms(sentence)
    out = {"terms": terms, "scholars": []}
    if not terms or not re.search("[ء-ي]", terms):
        return out
    client = get_client()
    results = await asyncio.gather(client.binbaz(terms), client.uthaymeen(terms), return_exceptions=True)
    for who, res in zip(("binbaz", "uthaymeen"), results):
        s = SCHOLARS[who]
        search = (BINBAZ_SEARCH_PAGE if who == "binbaz" else UTH_SEARCH_PAGE).format(q=quote(terms))
        block = {"key": who, "ar": s["ar"], "en": s["en"], "site": s["site"], "site_ar": s["site_ar"], "site_en": s["site_en"],
                 "terms_ar": s["terms_ar"], "terms_en": s["terms_en"], "full_text": s["full_text"], "search_url": search,
                 "fatwas": [], "error": None}
        if isinstance(res, Exception):
            log.warning("%s search failed: %s", who, res)
            block["error"] = type(res).__name__
        else:
            block["fatwas"] = res
        out["scholars"].append(block)
    return out
