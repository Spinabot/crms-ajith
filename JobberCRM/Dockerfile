FROM python:3.11-slim AS base

WORKDIR /app

RUN apt-get update && apt-get install -y \
        build-essential libpq-dev gcc netcat-openbsd dos2unix \
        && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN dos2unix /app/entrypoint.sh && chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
