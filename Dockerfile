# Hugging Face Space (Docker SDK) or any container host. Free CPU is enough; ALLaM runs as a 4-bit GGUF.
FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends build-essential cmake && rm -rf /var/lib/apt/lists/*
RUN useradd -m -u 1000 user
WORKDIR /home/user/app

COPY requirements.txt requirements-llm.txt ./
RUN pip install --no-cache-dir -r requirements.txt \
 && pip install --no-cache-dir --prefer-binary \
      --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu -r requirements-llm.txt

COPY --chown=user . .
USER user

ENV HF_HOME=/home/user/.cache/huggingface \
    TATHABBUT_LLM=llamacpp \
    PORT=7860
EXPOSE 7860
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
