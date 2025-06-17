# Zoho CRM Integration

This repository contains the codebase for integrating with Zoho CRM to perform CRUD operations on leads data.

---

## Features

- Perform **Create**, **Read**, **Update**, and **Delete** operations on Zoho CRM leads.
- Integrated with **Zoho OAuth** for authentication.
- Rate-limited API endpoints to prevent abuse.
- Swagger API documentation for easy exploration of routes.

---

## Initial Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd ZohoCRMIntegration
```

### 2. Build and Run the Docker Container
```bash
docker-compose -f docker-compose.yml up --build
```

---

## Usage

- Visit `http://127.0.0.1:5000/apidocs` to access the Swagger API documentation and explore the available routes.
- Use the integrated OAuth flow to authenticate with Zoho and obtain the necessary access tokens.
- Perform CRUD operations on leads data using the provided API endpoints.

---



2. Run the Application Using Docker
Ensure Docker and Docker Compose are installed on your system. Then, run:

http://127.0.0.1:5000/apidocs


Available Features
CRUD Operations on Leads
Create: Add new leads to Zoho CRM.
Read: Fetch leads from Zoho CRM.
Update: Modify existing leads in Zoho CRM.
Delete: Remove leads from Zoho CRM.

Before you set spin the docker file first put this data into the .env file for local testing. 
# Environment Variables 
ZOHO_CLIENT_ID="1000.ZFFAMTD7HGQRKRORIPDDOHQ7CKZ1IL"
ZOHO_CLIENT_SECRET="bf49130c11e3b0072d49e74bf27029a8cde5cb4193"
DATABASE_NAME = ZOHO
DB_USER  = postgres
DB_PASSWORD = root
CONNECTION_NAME = postgres
CACHE_REDIS_HOST = redis
CACHE_REDIS_PORT = 6379
CACHE_REDIS_PASSWORD = root
CACHE_REDIS_USERNAME = redis
GUNICORN_WORKERS = 4
GUNICORN_BIND = 0.0.0.0:5000
GUNICORN_WORKER_CLASS = gthread


# Start the Application:

Run the Docker container as described in the setup section.
Initialize the Database:

The database is automatically initialized when the container starts.
Test the API:

Use the Swagger documentation at /apidocs to test the API endpoints.







## `create_db.py`

### Description
The `create_db.py` script is responsible for setting up the database by creating the required tables and inserting initial test data. This script is typically used during development or testing to ensure the database is properly initialized.

---

### Key Features

1. **Table Creation**:
   - Creates all necessary tables in the database using the `create_tables()` function from `database.schemas`.

2. **Test Data Insertion**:
   - Adds a test credential (`entity_id=1`) to the `ZohoCreds` table if it doesn't already exist.
   - Adds a test client (`entity_id=1`) to the `Clients` table if it doesn't already exist.

3. **Access Token Setup**:
   - Inserts a dummy access token and refresh token for testing purposes.
   - Sets the expiration time of the access token to a past timestamp to simulate an expired token.

---

### How It Works

1. **App Context**:
   - The script runs within the Flask app context to access the database models and perform operations.

2. **Table Creation**:
   - Calls the `create_tables()` function to create all tables defined in `database.schemas`.

3. **Credential Check**:
   - Checks if a credential with `entity_id=1` already exists in the `ZohoCreds` table.
   - If not, inserts a test credential with a dummy access token and refresh token.

4. **Client Check**:
   - Checks if a client with `entity_id=1` already exists in the `Clients` table.
   - If not, inserts a test client with dummy data.

---


# Notes for Developers
Rate Limiting:

All endpoints are rate-limited to 5 requests per minute to prevent abuse.
Error Handling:

Proper error messages are returned for invalid requests, missing parameters, or authentication issues.
Database:

The database schema is defined in the database/schemas.py file.
Use create_db.py to set up the database with initial test data.
Logging:

Add logging for debugging and monitoring purposes.#