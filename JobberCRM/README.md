# Jobber API Integration with FastAPI

This repository provides a FastAPI backend that integrates with the Jobber API using OAuth2. It supports client management endpoints and includes both development and production Docker configurations.

## Table of Contents

- Features
- Setup
- Running the Server
  - Development (Docker Compose)
  - Production (Docker Compose)
- API Endpoints
- Notes

## Features

- OAuth 2.0 authentication with Jobber
- Automatic token refresh handling
- Client management: create, update, archive
- Asynchronous FastAPI backend
- Dockerized environment for dev and prod

## Setup

### Prerequisites

- Python 3.7+
- Docker & Docker Compose
- Jobber developer account

### Environment Configuration

Create a `.env` file using the `.env.example` as a reference. Populate it with your credentials:

```ini
Remodel_ID=your_client_id
Remodel_SECRET=your_client_secret
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=jobbercrm
POSTGRES_USER=jobberuser
POSTGRES_PASSWORD=jobberpassword
REDIS_HOST=redis
```

## Running the Server

### Development

Use the development Docker Compose file:

```bash
docker-compose -f docker-compose.dev.yml up --build
```

The dev server uses:

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

### Production

Use the production Docker Compose file:

```bash
docker-compose -f docker-compose.prod.yml up --build -d
```

Production uses a more stable setup with:

```bash
  uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4 
```

## API Endpoints

1. /auth/jobber/?userid (GET)

Initiates the OAuth 2.0 authentication flow with Jobber for a specific user.

2. /data/jobber/userid (POST)

Fetches client-related data from the Jobber API using the user's access token.

3. /clients/create/userid (POST)

Creates a new client under the authenticated user's Jobber account. The request body should include client details such as name, email, phone, and address.

4. /clients/update/userid (POST)

Updates the details of an existing client. You can modify fields like name, contact info, and custom fields.

5. /clients/archive/userid (POST)

Archives a client in the user's Jobber account, effectively soft deleting them.

## Notes

- Ensure `.env` is properly configured before starting the app.
- The authentication flow must be completed to access secure endpoints.
- Use `docker-compose.dev.yml` for development and `docker-compose.prod.yml` for deployment.

