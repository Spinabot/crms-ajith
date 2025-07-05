#!/bin/bash
set -e

echo "Starting HubSpot CRM Application..."

# Wait for database to be ready
echo "Waiting for database to be ready..."
while ! pg_isready -h $DB_HOST -p 5432 -U $DB_USER; do
    echo "Database is not ready yet. Waiting..."
    sleep 2
done

echo "Database is ready!"

# Initialize database
echo "Initializing database..."
python init_db.py

# Start the application
echo "Starting Flask application..."
exec python run.py