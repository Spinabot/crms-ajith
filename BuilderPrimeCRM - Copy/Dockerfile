# Base Stage
FROM python:3.11-slim AS base
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt eventlet
RUN echo "🛠️ Base stage ended..."

# Development Stage
FROM base AS development
ENV FLASK_ENV=development
COPY . .
RUN chmod +x entrypoint.sh
COPY .env .env
ENTRYPOINT ["./entrypoint.sh"]

# Production Stage
FROM base AS production
ENV FLASK_ENV=production
COPY requirements-prod.txt .
RUN pip install --no-cache-dir -r requirements-prod.txt gunicorn eventlet
COPY . .
RUN chmod +x entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"] 