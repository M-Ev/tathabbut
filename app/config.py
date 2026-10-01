"""Runtime settings, all from environment variables so the model layer can be swapped without code changes."""
import os
from dataclasses import dataclass


def _env(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


@dataclass
class Settings:
    # LLM backend: "llamacpp" (ALLaM GGUF in-process), "openai" (any OpenAI-compatible endpoint), or "none".
    llm_backend: str = _env("TATHABBUT_LLM", "none")
    # llamacpp
    gguf_repo: str = _env("TATHABBUT_GGUF_REPO", "bartowski/ALLaM-AI_ALLaM-7B-Instruct-preview-GGUF")
    gguf_file: str = _env("TATHABBUT_GGUF_FILE", "ALLaM-AI_ALLaM-7B-Instruct-preview-Q4_K_M.gguf")
    gguf_path: str = _env("TATHABBUT_GGUF_PATH")
    n_ctx: int = int(_env("TATHABBUT_N_CTX", "4096"))
    n_threads: int = int(_env("TATHABBUT_N_THREADS", "0")) or (os.cpu_count() or 2)
    # openai-compatible
    llm_base_url: str = _env("TATHABBUT_LLM_BASE_URL")
    llm_api_key: str = _env("TATHABBUT_LLM_API_KEY")
    llm_model: str = _env("TATHABBUT_LLM_MODEL", "ALLaM-7B-Instruct-preview")
    llm_timeout: float = float(_env("TATHABBUT_LLM_TIMEOUT", "180"))
    # Dorar
    dorar_enabled: bool = _env("TATHABBUT_DORAR", "1") != "0"
    dorar_timeout: float = float(_env("TATHABBUT_DORAR_TIMEOUT", "20"))
    user_agent: str = _env(
        "TATHABBUT_USER_AGENT",
        "Tathabbut/0.1 (citation checker for the Islamic Content AI Challenge; +https://github.com/M-Ev/tathabbut)",
    )
    max_text_chars: int = int(_env("TATHABBUT_MAX_CHARS", "8000"))
    max_citations: int = int(_env("TATHABBUT_MAX_CITATIONS", "12"))


settings = Settings()
