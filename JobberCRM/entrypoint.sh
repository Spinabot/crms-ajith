#!/bin/bash

echo "Waiting for PostgreSQL..."
while ! nc -z postgres $DATABASE_PORT; do
  sleep 1
done
echo "PostgreSQL is up!"


echo "Waiting for Redis..."
while ! nc -z redis $CACHE_REDIS_PORT; do
  sleep 1
done
echo "Redis is up!"

# Run DB setup (creates tables if not there)
echo "Running DB setup..."
python src/database.py

echo "Starting application..."

uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload --workers "$GUNICORN_WORKERS"