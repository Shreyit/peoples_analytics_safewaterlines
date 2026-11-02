FROM python:3.14-slim

WORKDIR /app

# Install uv from official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy dependency specifications
COPY pyproject.toml uv.lock ./

# Install python dependencies without the root package
RUN uv sync --frozen --no-dev --no-install-project

# Copy necessary application data and code
COPY dashboard/ dashboard/
COPY docs/ docs/
COPY reports/ reports/
COPY presentation/ presentation/
COPY data/ data/

# Set environment variables for Cloud Run
ENV HOST=0.0.0.0
ENV PORT=8080
ENV PYTHONUNBUFFERED=1
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8080

CMD ["python", "dashboard/assistant/server.py"]

