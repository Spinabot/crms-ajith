# Jobber CRM Flask Application

A Flask application with PostgreSQL and Redis integration using Docker containers, featuring Jobber OAuth authentication, client management, and data retrieval.

## Project Structure

```
JobberCRMFlask/
├── app.py                 # Main Flask application
├── config.py              # Configuration management
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Docker services orchestration
├── .env                  # Environment variables (create this)
├── .dockerignore         # Docker ignore file
├── auth/                 # Authentication module
│   ├── __init__.py
│   └── routes.py         # OAuth routes and logic
├── client/               # Client management module
│   ├── __init__.py
│   └── routes.py         # Client CRUD operations
├── data/                 # Data retrieval module
│   ├── __init__.py
│   └── routes.py         # Data retrieval operations
├── schemas/              # Data validation schemas
│   ├── __init__.py
│   └── schemas.py        # Marshmallow schemas
├── queries/              # GraphQL queries
│   ├── __init__.py
│   ├── create_client_query.py # GraphQL mutations
│   ├── update_client_query.py # GraphQL mutations for client updates
│   ├── archive_client_query.py # GraphQL mutations for client archiving
│   └── get_client_query.py    # GraphQL queries
├── utils/                # Utility modules
│   ├── __init__.py
│   ├── db_conn.py        # Database connection utilities
│   └── token_handler.py  # Token management utilities
└── test/                 # Test files
    ├── __init__.py
    ├── test_auth.py      # Authentication endpoint tests
    ├── test_database.py  # Database operation tests
    ├── test_client.py    # Client API tests
    ├── test_data.py      # Data retrieval API tests
    └── test_oauth_debug.py # OAuth flow debug tests
```

## Prerequisites

- Docker
- Docker Compose

## Environment Variables

Make sure you have a `.env` file in the root directory with the following variables:

```
POSTGRES_DB=jobberflaskcrm
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
REDIS_HOST=localhost
REDIS_PORT=6379
Remodel_ID=ed00f589-eb57-43ce-a63c-24d7aae75e5d
Remodel_SECRET=d5c3510ae17bd355742765b6412d83dd9409b0aaf5e3e89c753e97da96627d14
JOBBER_API_URL=https://api.getjobber.com/api/graphql
```

## Running the Application

1. **Start all services:**

   ```bash
   docker-compose up --build
   ```

2. **Run in background:**

   ```bash
   docker-compose up -d --build
   ```

3. **Stop all services:**

   ```bash
   docker-compose down
   ```

4. **View logs:**
   ```bash
   docker-compose logs flask_app
   ```

## API Endpoints

### Basic Endpoints

- `GET /` - Returns "Hello World" message
- `GET /health` - Health check endpoint

### Authentication Endpoints

- `GET /auth/jobber?userid=<user_id>` - Initiates Jobber OAuth authorization
- `GET /auth/callback` - Handles OAuth callback from Jobber (called automatically)

### Client Management Endpoints

- `POST /client/create/<userid>` - Create a new client in Jobber
- `POST /client/update/<userid>` - Update an existing client in Jobber
- `POST /client/archive/<userid>` - Archive an existing client in Jobber

### Data Retrieval Endpoints

- `POST /data/jobber/<userid>` - Retrieve all client data from Jobber

## Services

- **Flask App**: Running on port 5000
- **PostgreSQL**: Running on port 5432
- **Redis**: Running on port 6379

## Testing the Application

### Manual Testing

Once the containers are running, you can test the API:

```bash
# Test basic endpoints
curl http://localhost:5000/
# Expected output: {"message": "Hello World"}

curl http://localhost:5000/health
# Expected output: {"status": "healthy", "message": "Flask application is running"}

# Test authorization endpoint
curl -I http://localhost:5000/auth/jobber?userid=123
# Expected: 302 redirect to Jobber authorization URL

# Test client creation (requires authorization first)
curl -X POST http://localhost:5000/client/create/123 \
  -H "Content-Type: application/json" \
  -d '{
    "firstName": "John",
    "lastName": "Doe",
    "companyName": "Test Company",
    "emails": [{"address": "john@example.com", "primary": true}],
    "phones": [{"number": "555-1234", "primary": true}]
  }'
# Expected: 401 if not authorized, 200 if authorized

# Test client update (requires authorization first)
curl -X POST http://localhost:5000/client/update/123 \
  -H "Content-Type: application/json" \
  -d '{
    "clientId": "Z2lkOi8vSm9iYmVyL0NsaWVudC8xMTEyNjk4NzA=",
    "firstName": "John",
    "lastName": "Smith",
    "emailsToAdd": [{"address": "john.smith@example.com", "description": "Primary"}],
    "phonesToAdd": [{"number": "+1234567890", "description": "Mobile"}]
  }'
# Expected: 401 if not authorized, 200 if authorized

# Test client archive (requires authorization first)
curl -X POST http://localhost:5000/client/archive/123 \
  -H "Content-Type: application/json" \
  -d '{
    "clientId": "Z2lkOi8vSm9iYmVyL0NsaWVudC8xMTEyNjk4NzA="
  }'
# Expected: 401 if not authorized, 200 if authorized

# Test data retrieval (requires authorization first)
curl -X POST http://localhost:5000/data/jobber/123
# Expected: 401 if not authorized, 200 with client data if authorized
```

### Automated Testing

Run the test scripts to verify all functionality:

```bash
# Test authentication endpoints
python test/test_auth.py

# Test database operations
python test/test_database.py

# Test client creation API
python test/test_client.py

# Test data retrieval API
python test/test_data.py

# Debug OAuth flow
python test/test_oauth_debug.py
```

## OAuth Flow

1. **Authorization Request**: User visits `/auth/jobber?userid=<user_id>`
2. **Redirect to Jobber**: User is redirected to Jobber's authorization page
3. **User Authorization**: User authorizes the application on Jobber
4. **Callback**: Jobber redirects back to `/auth/callback` with authorization code
5. **Token Exchange**: Application exchanges code for access and refresh tokens
6. **Database Storage**: Tokens are stored in PostgreSQL database

## Client Creation Flow

1. **Authorization Required**: User must be authorized first via OAuth
2. **Token Retrieval**: System fetches valid access token from database/Redis
3. **Data Validation**: Client data is validated using Marshmallow schemas
4. **GraphQL Request**: Validated data is sent to Jobber GraphQL API
5. **Response Handling**: Success/error responses are processed and returned

## Client Update Flow

1. **Authorization Required**: User must be authorized first via OAuth
2. **Token Retrieval**: System fetches valid access token from database/Redis
3. **Data Validation**: Update data is validated using Marshmallow schemas
4. **GraphQL Mutation**: Validated data is sent to Jobber GraphQL API via clientEdit mutation
5. **Error Handling**: User errors from Jobber are properly handled and returned
6. **Response Processing**: Success/error responses are processed and returned

## Client Archive Flow

1. **Authorization Required**: User must be authorized first via OAuth
2. **Token Retrieval**: System fetches valid access token from database/Redis
3. **Data Validation**: Archive data is validated using Marshmallow schemas
4. **GraphQL Mutation**: Validated data is sent to Jobber GraphQL API via clientArchive mutation
5. **Error Handling**: User errors from Jobber are properly handled and returned
6. **Response Processing**: Success/error responses are processed and returned

## Data Retrieval Flow

1. **Authorization Required**: User must be authorized first via OAuth
2. **Token Retrieval**: System fetches valid access token from database/Redis
3. **Pagination**: Fetches all client data using GraphQL pagination
4. **Rate Limiting**: Includes 3-second sleep every 5 requests to avoid rate limits
5. **Data Aggregation**: Combines all paginated results into a single response

## Database Schema

The application automatically creates a `jobber_auth` table with the following structure:

```sql
CREATE TABLE jobber_auth (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL UNIQUE,
    access_token TEXT NOT NULL,
    refresh_token TEXT NOT NULL,
    expiration_time BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Rate Limiting

All endpoints include rate limiting:

- Maximum 5 requests per minute per IP address
- Uses Redis for rate limiting storage
- Gracefully handles Redis unavailability
- Data retrieval includes additional rate limiting (3-second sleep every 5 requests)

## Development

For development, the application code is mounted as a volume, so changes to the code will be reflected immediately when running in debug mode.

## Error Handling

The application includes comprehensive error handling for:

- Missing or invalid OAuth parameters
- Database connection issues
- Redis connection issues
- Jobber API errors (400, 401, 403, 500)
- Rate limiting violations
- Data validation errors
- GraphQL errors
- Pagination errors

## Module Organization

### Auth Module (`auth/`)

- **routes.py**: Contains all OAuth-related routes and logic
- Handles Jobber authorization flow
- Implements rate limiting
- Manages token exchange and storage

### Client Module (`client/`)

- **routes.py**: Contains client management routes
- Handles client creation via Jobber GraphQL API
- Implements data validation
- Manages authentication requirements

### Data Module (`data/`)

- **routes.py**: Contains data retrieval routes
- Handles client data fetching via Jobber GraphQL API
- Implements pagination and rate limiting
- Manages authentication requirements

### Schemas Module (`schemas/`)

- **schemas.py**: Marshmallow schemas for data validation
- Validates client creation and update data
- Provides consistent data structure validation

### Queries Module (`queries/`)

- **create_client_query.py**: GraphQL mutations for client creation
- **update_client_query.py**: GraphQL mutations for client updates
- **archive_client_query.py**: GraphQL mutations for client archiving
- **get_client_query.py**: GraphQL queries for data retrieval
- Contains Jobber API GraphQL operations
- Centralized query management

### Utils Module (`utils/`)

- **db_conn.py**: Database connection and operation utilities
- **token_handler.py**: Token management and caching utilities
- Handles PostgreSQL connections and Redis caching
- Manages table creation and data insertion
- Provides error handling and logging

### Test Module (`test/`)

- **test_auth.py**: Tests authentication endpoints
- **test_database.py**: Tests database operations
- **test_client.py**: Tests client creation API
- **test_data.py**: Tests data retrieval API
- **test_oauth_debug.py**: Comprehensive OAuth debugging
- Includes comprehensive test coverage
- Provides detailed test results and error reporting
