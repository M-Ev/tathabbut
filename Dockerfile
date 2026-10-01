# Hugging Face Space (Docker SDK) or any container host.
# ALLaM runs on a separate GPU endpoint by default (TATHABBUT_LLM=openai, set in the Space settings).
# To run ALLaM inside this container on CPU instead: build with --build-arg WITH_LLAMACPP=1 and set TATHABBUT_LLM=llamacpp.
FROM python:3.11-slim

ARG WITH_LLAMACPP=0
RUN if [ "$WITH_LLAMACPP" = "1" ]; then apt-get update && apt-get install -y --no-install-recommends build-essential cmake && rm -rf /var/lib/apt/lists/*; fi
RUN useradd -m -u 1000 user
WORKDIR /home/user/app

COPY requirements.txt requirements-llm.txt ./
RUN pip install --no-cache-dir -r requirements.txt \
 && if [ "$WITH_LLAMACPP" = "1" ]; then pip install --no-cache-dir --prefer-binary \
      --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu -r requirements-llm.txt; fi

COPY --chown=user . .
USER user

ENV HF_HOME=/home/user/.cache/huggingface \
    TATHABBUT_LLM=none \
    PORT=7860
EXPOSE 7860
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
