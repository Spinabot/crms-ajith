#!/bin/sh

echo "Running database migrations..."

flask db upgrade || {
    echo "❌ Migration failed!"
    exit 1
}

if [ "$FLASK_ENV" = "production" ]; then
    echo "Starting Gunicorn server..."
    exec gunicorn -k eventlet -w 1 -b 0.0.0.0:5050 run:app
else
    echo "Starting Flask in development mode..."
    exec flask run --host=0.0.0.0 --port=5050
fi 