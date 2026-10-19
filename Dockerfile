#---- STAGE 1: build the virtualenv ----#
FROM python:3.12-slim-bookworm AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project


#---- STAGE 2: runtime ----#
FROM python:3.12-slim-bookworm AS runtime

RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --system --gid 10001 appuser \
    && useradd --system --uid 10001 --gid appuser --create-home --shell /usr/sbin/nologin appuser

WORKDIR /app

# Root-owned and read-only to the app
COPY --from=builder /app/.venv /app/.venv
COPY backend ./backend

# The only writable areas
RUN mkdir -p /app/backend/artifacts /app/.cache/numba /app/.cache/huggingface \
    && chown -R appuser:appuser /app/backend/artifacts /app/.cache

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    NUMBA_CACHE_DIR=/app/.cache/numba \
    HF_HOME=/app/.cache/huggingface \
    HF_HUB_OFFLINE=1 \
    TRANSFORMERS_OFFLINE=1 

ENV FFMPEG_PATH="/usr/bin/ffmpeg"

USER appuser
EXPOSE 8000
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]