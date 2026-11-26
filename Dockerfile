FROM python:3.15-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project
COPY . .
ENV PATH="/app/.venv/bin:$PATH"
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]