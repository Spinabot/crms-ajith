#!/bin/bash
# Gunicorn configuration
DB_PORT=5432
CACHE_REDIS_PORT=6379
GUNICORN_WORKERS=4
GUNICORN_CLASS="sync"
GUNICORN_HOST="0.0.0.0:5000"
# Wait for PostgreSQL
echo "Waiting for PostgreSQL..."
while ! nc -z postgres "$DB_PORT"; do
  sleep 1
done
echo "PostgreSQL is up!"

# Wait for Redis
echo "Waiting for Redis..."
while ! nc -z redis "$CACHE_REDIS_PORT"; do
  sleep 1
done
echo "Redis is up!" 

echo "Running DB setup..."
python create_db.py

echo "Running migrations..."
mkdir -p migrations/versions

alembic upgrade head

echo "Initializing database..."
# Set the FLASK_APP environment variable
export FLASK_APP=main.py
# Run the Flask CLI command to initialize the database
flask db init




echo "Starting application..."
# Start the application with Gunicorn using env vars
gunicorn -w "$GUNICORN_WORKERS" -k "$GUNICORN_CLASS" -b "$GUNICORN_HOST" main:app