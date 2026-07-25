# North Star — API + web client in one container.
# Single process, no database, no secrets, no external calls at runtime.
FROM python:3.11-slim

# Non-root: the app only reads its own data files.
RUN useradd --create-home --uid 10001 northstar
WORKDIR /app

# Dependencies first so code changes don't bust the layer cache.
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY backend/ ./backend/
COPY web/ ./web/

USER northstar
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    NORTH_STAR_WEB_DIR=/app/web \
    PORT=8000
EXPOSE 8000

# Fail the container if the knowledge base won't load or the API is down —
# a North Star serving no programmes is worse than one that is visibly broken.
# Probes $PORT, not a hardcoded 8000 — hosts like Render/Railway/Cloud Run
# inject it, and a healthcheck on the wrong port fails forever and puts the
# container in a restart loop. The timeout keeps a saturated server failing
# fast instead of hanging the check.
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import os,urllib.request,json,sys; \
u='http://127.0.0.1:'+os.environ.get('PORT','8000')+'/health'; \
d=json.load(urllib.request.urlopen(u, timeout=4)); \
sys.exit(0 if d.get('programmes',0) > 0 else 1)"

WORKDIR /app/backend
CMD ["sh", "-c", "uvicorn northstar.api:app --host 0.0.0.0 --port ${PORT:-8000}"]
