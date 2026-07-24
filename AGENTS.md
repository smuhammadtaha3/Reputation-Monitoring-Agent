# AGENTS.md

This repository contains an AI reputation monitoring service built with FastAPI, Celery, Supabase, and transformer-based sentiment analysis. Agents should preserve the existing structure and keep changes small, explicit, and environment-driven.

## Project map
- Main API entrypoints: [app/main.py](app/main.py) and [app/api/routes.py](app/api/routes.py)
- Background jobs: [app/workers/tasks.py](app/workers/tasks.py) and [app/workers/celery_app.py](app/workers/celery_app.py)
- Service layer: [app/services/sentiment.py](app/services/sentiment.py), [app/services/draft.py](app/services/draft.py), [app/services/alert.py](app/services/alert.py), and [app/services/scraper.py](app/services/scraper.py)
- Config and data access: [app/core/config.py](app/core/config.py) and [app/core/database.py](app/core/database.py)
- Project overview and runbook: [README.md](README.md)

## Working conventions
- Prefer Python 3.12-compatible code and keep dependencies declared in [requirements.txt](requirements.txt).
- Use the local virtual environment if present, such as `.venv` or `venv`.
- Run the app locally with:
  - `uvicorn app.main:app --reload`
  - `celery -A app.workers.celery_app worker -B`
- Many features depend on environment variables. Do not hardcode secrets. Use the existing `.env` pattern and keep secrets out of source control.
- Common environment values include `GROQ_API_KEY`, `SUPABASE_URL`, `SUPABASE_KEY`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `REDIS_URL`, and `MODEL_NAME`.

## Architecture notes
- The API and Celery worker share the same review-processing flow. Avoid duplicating logic between [app/api/routes.py](app/api/routes.py) and [app/workers/tasks.py](app/workers/tasks.py).
- Sentiment inference is lazily loaded in [app/services/sentiment.py](app/services/sentiment.py). Keep related changes lightweight and avoid unnecessary model reloads.
- Startup behavior in [app/main.py](app/main.py) preloads the model and starts the scheduler. Changes there should be conservative and well tested.
- Supabase inserts are used for persisted reviews. If you change the review payload, keep the stored fields consistent with the existing schema and downstream consumers.

## Assisted permissions and access guidance
- If a change touches permissions, credentials, or access to external services, keep the scope minimal and explicit.
- Prefer environment-based configuration over hard-coded tokens or broad allow-lists.
- When adding new integrations or automation, default to fail-safe behavior and surface clear configuration errors rather than silently granting access.

## Before changing behavior
- Review [README.md](README.md) for the intended API and worker flow before editing core logic.
- Keep changes compatible with the existing `/api/v1` routes and the Celery polling workflow.
- If a change affects alerts, persistence, or model inference, verify both the ingest path and the polling path.
