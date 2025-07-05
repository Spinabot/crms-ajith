-- Initialize HubSpot CRM Database
-- This script runs when the PostgreSQL container starts

-- Create database if it doesn't exist
SELECT 'CREATE DATABASE hubspot_db'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'hubspot_db')\gexec

-- Connect to the database
\c hubspot_db;

-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create any additional tables or setup here
-- (The Flask-Migrate will handle the actual table creation)

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE hubspot_db TO hubspot_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO hubspot_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO hubspot_user;