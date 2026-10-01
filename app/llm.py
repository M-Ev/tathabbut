"""Swappable language-model layer (ALLaM by default).

The model has three narrow jobs and never issues a ruling or a grading:
1. spot citations in free text (each one must then be found verbatim in the user's text),
2. suggest Arabic search wording for a non-Arabic quote (used only as a search query, never shown as a source),
3. say which of the Arabic texts found in the sources matches a non-Arabic quote, or none.
"""
import asyncio
import json
import logging
import re

import httpx

from .config import settings

log = logging.getLogger("tathabbut.llm")

SYSTEM = (
    "أنت مساعد تقني داخل أداة تثبّت للتحقق من الاستشهادات. مهمتك استخراج النصوص ومطابقتها فقط. "
    "لا تُصدر حكمًا على حديث، ولا فتوى، ولا تضف معلومات من عندك. أجب بصيغة JSON فقط."
)


class LLMUnavailable(Exception):
    pass


class _Backend:
    name = "none"

    async def chat(self, messages: list[dict], max_tokens: int = 256) -> str:
        raise LLMUnavailable("no language model configured")


class OpenAICompatible(_Backend):
    name = "openai"

    async def chat(self, messages, max_tokens=256):
        if not settings.llm_base_url:
            raise LLMUnavailable("TATHABBUT_LLM_BASE_URL is not set")
        headers = {"Authorization": f"Bearer {settings.llm_api_key}"} if settings.llm_api_key else {}
        async with httpx.AsyncClient(timeout=settings.llm_timeout) as client:
            r = await client.post(
                settings.llm_base_url.rstrip("/") + "/chat/completions",
                headers=headers,
                json={"model": settings.llm_model, "messages": messages, "max_tokens": max_tokens, "temperature": 0},
            )
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]


class LlamaCpp(_Backend):
    """Runs the ALLaM GGUF in-process with llama.cpp (free CPU hosting)."""

    name = "llamacpp"

    def __init__(self):
        self._llm = None
        self._lock = asyncio.Lock()

    def _load(self):
        if self._llm is None:
            from llama_cpp import Llama  # optional dependency

            path = settings.gguf_path
            if not path:
                from huggingface_hub import hf_hub_download

                path = hf_hub_download(settings.gguf_repo, settings.gguf_file)
            self._llm = Llama(model_path=path, n_ctx=settings.n_ctx, n_threads=settings.n_threads, verbose=False)
        return self._llm

    async def warm(self):
        await asyncio.to_thread(self._load)

    async def chat(self, messages, max_tokens=256):
        async with self._lock:
            llm = await asyncio.to_thread(self._load)
            out = await asyncio.to_thread(
                llm.create_chat_completion, messages=messages, max_tokens=max_tokens, temperature=0
            )
        return out["choices"][0]["message"]["content"]


def _make_backend() -> _Backend:
    return {"openai": OpenAICompatible, "llamacpp": LlamaCpp}.get(settings.llm_backend, _Backend)()


backend = _make_backend()


def available() -> bool:
    return backend.name != "none"


def _json(text: str):
    """Parse the first JSON value in a model reply."""
    text = re.sub(r"^```(json)?|```$", "", text.strip(), flags=re.M).strip()
    for opener, closer in (("[", "]"), ("{", "}")):
        i, j = text.find(opener), text.rfind(closer)
        if i >= 0 and j > i:
            try:
                return json.loads(text[i : j + 1])
            except json.JSONDecodeError:
                continue
    raise ValueError("no JSON in model reply")


async def _ask(user: str, max_tokens: int):
    reply = await backend.chat([{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}], max_tokens)
    return _json(reply)


async def extract_citations(text: str) -> list[dict]:
    prompt = (
        "استخرج من النص التالي كل آية قرآنية وكل حديث نبوي مستشهد به، وانسخ كل واحد كما ورد في النص حرفيًا "
        "بلا تعديل ولا إكمال. أعد مصفوفة JSON عناصرها بالشكل "
        '{"type": "quran" أو "hadith", "quote": "النص كما ورد"}. '
        "إن لم يوجد شيء فأعد []\n\nالنص:\n" + text
    )
    data = await _ask(prompt, 400)
    out = []
    for item in data if isinstance(data, list) else []:
        if isinstance(item, dict) and item.get("type") in ("quran", "hadith") and isinstance(item.get("quote"), str):
            out.append({"type": item["type"], "quote": item["quote"].strip()})
    return out


async def arabic_search_wording(quote: str, kind: str) -> str:
    what = "الآية القرآنية" if kind == "quran" else "الحديث النبوي"
    prompt = (
        f"النص التالي ترجمة لـ{what}. اكتب بالعربية الكلمات المتوقعة في نصه الأصلي كما يرد في المصادر، "
        "لاستعمالها في البحث فقط. لا تشرح. أعد JSON بالشكل "
        '{"arabic": "..."}\n\nالنص:\n' + quote
    )
    data = await _ask(prompt, 120)
    return str(data.get("arabic", "")).strip() if isinstance(data, dict) else ""


async def pick_match(quote: str, candidates: list[str]) -> int:
    """Return the 1-based index of the Arabic candidate that matches the quote in meaning, or 0."""
    listing = "\n".join(f"{i}. {c[:300]}" for i, c in enumerate(candidates, 1))
    prompt = (
        "أي النصوص العربية التالية هو أصل النص المترجم؟ إن لم يكن أيٌّ منها أصله فأعد 0. "
        'أعد JSON بالشكل {"match": رقم}\n\n'
        f"النص المترجم:\n{quote}\n\nالنصوص العربية:\n{listing}"
    )
    data = await _ask(prompt, 20)
    try:
        n = int(data.get("match", 0)) if isinstance(data, dict) else 0
    except (TypeError, ValueError):
        return 0
    return n if 0 <= n <= len(candidates) else 0
