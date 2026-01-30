ARG PYTHON_VERSION=3.12.2
FROM python:${PYTHON_VERSION}-slim as base


COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ENV UV_COMPILE_BYTECODE=1

ENV VIRTUAL_ENV=/app/.venv
ENV PATH="/app/.venv/bin:$PATH"
ENV UV_CACHE_DIR="/app/.cache/uv"

ENV UV_LINK_MODE=copy

WORKDIR /app


ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser


COPY pyproject.toml uv.lock ./


RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev


COPY . .

COPY . /app

RUN mkdir -p /app/.cache/uv && chown -R appuser:appuser /app

USER appuser

WORKDIR /app/src

CMD ["uv", "run", "sh", "-c", "alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000"]

