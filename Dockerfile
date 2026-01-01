FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

ARG USER_UID=1234
ARG USER_GID="$USER_UID"

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_NO_DEV=1

WORKDIR /app

RUN groupadd --system --gid "$USER_GID" appuser \
    && useradd --system --gid "$USER_GID" --uid "$USER_UID" --create-home appuser


RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project

COPY --chown=appuser:appuser . /app

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked

ENV PATH="/app/.venv/bin:$PATH"

USER appuser

CMD ["echo", "overrideme"]
