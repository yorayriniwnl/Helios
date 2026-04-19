# Deployment helpers

This folder contains guidance for deploying the Helios backend.

1. Generate Alembic migrations (if you modified models):

```bash
# from the backend directory
alembic revision --autogenerate -m "describe the change"
alembic upgrade head
```

2. Build the Docker image and run (example):

```bash
docker build -t helios-backend .
docker run -e ENV=production \
  -e DATABASE_URL="postgresql://user:pass@db:5432/helios" \
  -e JWT_SECRET="<strong-secret>" \
  -e REDIS_URL="redis://redis:6379/0" \
  -p 8000:8000 helios-backend
```

3. Recommended env vars:

- `ENV` or `HELIOS_ENV`: `production`
- `DATABASE_URL`: PostgreSQL or another production DB
- `JWT_SECRET`: cryptographically random secret (>=16 characters)
- `REDIS_URL`: optional Redis connection string
- `CORS_ALLOWED_ORIGINS`: comma-separated allowed origins for the frontend
- `SLOW_QUERY_MS`: optional slow query profiler threshold (ms)
- `LOG_LEVEL`: `INFO` or `WARNING` for production

4. Notes

- The backend will fail-fast on startup if critical production settings are missing or insecure (see `app/core/config.py`).
- Keep `.env` files out of source control; `.gitignore` already excludes them.
