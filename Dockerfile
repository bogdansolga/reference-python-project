# Minimal container for the reference Flask app.
# Imports inside src/ are top-level (`from lib.db import ...`), so we run gunicorn
# with --chdir src to put src/ on the path. SQLite is auto-seeded on boot (ephemeral).
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Runtime deps (mirrors pyproject.toml) + gunicorn as the production WSGI server.
RUN pip install --no-cache-dir \
    "flask>=3.0" \
    "pydantic>=2.0" \
    "anthropic[vertex]>=0.40" \
    "python-dotenv>=1.0" \
    gunicorn

COPY src/ ./src/

EXPOSE 8000

# Flask's app.run() binds 127.0.0.1 — gunicorn binds 0.0.0.0 (reachable in-cluster).
# 1 worker: the datastore is a single SQLite file (avoid write contention).
CMD ["gunicorn", "--chdir", "src", "--workers", "1", "--bind", "0.0.0.0:8000", "app:create_app()"]
