FROM python:3.11-slim-bullseye AS base
WORKDIR /app
RUN apt-get update && apt-get install -y --fix-missing \
    build-essential libpq-dev gcc netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN chmod +x /app/entrypoint.sh
