# Unified CRM Integration

A unified Flask application that integrates multiple CRM systems into a single API, providing a consistent interface for managing leads across different platforms.

## Supported CRM Systems

- **BuilderPrime CRM** ✅ (Fully implemented)
- **HubSpot CRM** ✅ (Fully implemented)
- **Jobber CRM** ✅ (Authentication implemented)
- **JobNimbus CRM** 🔄 (Coming soon)
- **Zoho CRM** 🔄 (Coming soon)

## Features

- **Unified API**: Single API endpoint for all CRM operations
- **Cross-CRM Synchronization**: Sync leads between different CRM systems
- **Comprehensive Logging**: Track all operations and sync activities
- **Authentication**: API key-based authentication for each CRM system
- **Swagger Documentation**: Interactive API documentation
- **Database Abstraction**: Unified data model for all CRM systems

## Architecture

```
UnifiedCRMIntegration/
├── app/
│   ├── __init__.py          # Flask application factory
│   ├── config.py            # Configuration settings
│   ├── models.py            # Database models
│   ├── swagger.py           # API documentation
│   ├── routes/              # API routes for each CRM
│   │   ├── builder_prime.py
│   │   ├── hubspot.py
│   │   ├── jobber.py
│   │   ├── jobnimbus.py
│   │   └── zoho.py
   │   ├── services/            # Business logic for each CRM
   │   │   ├── builder_prime_service.py
   │   │   └── hubspot_service.py
│   └── utils/               # Utility functions
│       └── auth.py
├── tests/                   # Test files
├── run.py                   # Application entry point
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Database Models

### UnifiedLead

Stores lead information from all CRM systems in a unified format:

- Basic contact information (name, email, phone)
- Address information
- Company information
- Lead status and source
- CRM system tracking
- Raw CRM data storage

### CRMConnection

Manages connections to different CRM systems:

- OAuth tokens and API keys
- Connection status
- Configuration data

### SyncLog

Tracks synchronization activities:

- Operation type (create, update, delete, sync)
- Success/failure status
- Error messages
- Sync data

## API Endpoints

### BuilderPrime CRM

- `POST /api/builder-prime/leads` - Create a new lead
- `GET /api/builder-prime/leads` - Get leads with filtering
- `PUT /api/builder-prime/leads/{id}` - Update a lead
- `DELETE /api/builder-prime/leads/{id}` - Delete a lead
- `POST /api/builder-prime/sync` - Sync leads from BuilderPrime

### HubSpot CRM

- `POST /api/hubspot/leads` - Create a new lead
- `GET /api/hubspot/leads` - Get leads with filtering
- `PUT /api/hubspot/leads/{external_id}` - Update a lead
- `DELETE /api/hubspot/leads/{external_id}` - Delete a lead
- `POST /api/hubspot/leads/sync` - Sync leads from HubSpot

### Jobber CRM Authentication

- `GET /auth/jobber/authorize?userid={user_id}` - Initiate OAuth authorization
- `GET /auth/jobber/callback` - Handle OAuth callback (called by Jobber)
- `GET /auth/jobber/status/{user_id}` - Check authentication status
- `GET /auth/jobber/refresh/{user_id}` - Refresh access token

### Jobber CRM Data

- `GET /api/jobber/clients/{user_id}` - Get client data from Jobber (raw format)
- `GET /api/jobber/leads?user_id={user_id}` - Get leads from Jobber (unified format)

#### Jobber OAuth Flow

1. **Initiate Authorization**: Call `/auth/jobber/authorize?userid=123` to start the OAuth flow
2. **User Authorization**: User is redirected to Jobber to authorize the application
3. **Callback Processing**: Jobber redirects back to `/auth/jobber/callback` with authorization code
4. **Token Storage**: Access and refresh tokens are stored in the database
5. **Status Check**: Use `/auth/jobber/status/{user_id}` to check if user is authenticated
6. **Token Refresh**: Use `/auth/jobber/refresh/{user_id}` to refresh expired tokens

#### Example Usage

````bash
# Start OAuth flow for user 123
curl -X GET "http://localhost:5000/auth/jobber/authorize?userid=123"

# Check authentication status
curl -X GET "http://localhost:5000/auth/jobber/status/123"

# Refresh token if expired
curl -X GET "http://localhost:5000/auth/jobber/refresh/123"

# Get client data (raw Jobber format)
curl -X GET "http://localhost:5000/api/jobber/clients/123"

# Get leads (unified format)
curl -X GET "http://localhost:5000/api/jobber/leads?user_id=123"

### Other CRM Systems

Similar endpoints will be available for each CRM system as they are implemented.

## Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd UnifiedCRMIntegration
````

2. **Create virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file with the following variables:

   ```env
   FLASK_ENV=development
   FLASK_DEBUG=1
   FLASK_HOST=0.0.0.0
   FLASK_PORT=5000

   # Database
   DB_USER=postgres
   DB_PASSWORD=password
   DB_HOST=localhost
   DB_NAME=unified_crm_db
   DB_PORT=5432

   # CRM API Keys
   BUILDER_PRIME_API_KEY=your_builder_prime_api_key
   HUBSPOT_API_TOKEN=your_hubspot_api_token
   HUBSPOT_API_BASE_URL=https://api.hubapi.com

   # Jobber CRM Configuration
   JOBBER_CLIENT_ID=your_jobber_client_id
   JOBBER_CLIENT_SECRET=your_jobber_client_secret
   JOBBER_REDIRECT_URI=http://localhost:5000/auth/jobber/callback
   JOBBER_API_URL=https://api.getjobber.com/api/graphql
   JOBBER_TOKENS_URL=https://api.getjobber.com/api/oauth/token

   JOBNIMBUS_API_KEY=your_jobnimbus_api_key
   ZOHO_CLIENT_ID=your_zoho_client_id

   # Redis (optional)
   REDIS_HOST=localhost
   REDIS_PORT=6379
   ```

5. **Initialize database**

   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

6. **Run the application**
   ```bash
   python run.py
   ```

## Usage

### API Authentication

All API endpoints require authentication using an API key. Include the key in the request header:

```
x-api-key: your_api_key
```

### Creating a Lead in BuilderPrime

```bash
curl -X POST http://localhost:5000/api/builder-prime/leads \
  -H "Content-Type: application/json" \
  -H "x-api-key: your_api_key" \
  -d '{
    "firstName": "John",
    "lastName": "Doe",
    "email": "john.doe@example.com",
    "mobilePhone": "555-123-4567",
    "addressLine1": "123 Main St",
    "city": "Anytown",
    "state": "CA",
    "zip": "12345"
  }'
```

### Creating a Lead in HubSpot

```bash
curl -X POST http://localhost:5000/api/hubspot/leads \
  -H "Content-Type: application/json" \
  -H "x-api-key: your_api_key" \
  -d '{
    "firstName": "Jane",
    "lastName": "Smith",
    "email": "jane.smith@example.com",
    "mobilePhone": "555-987-6543",
    "addressLine1": "456 Oak Ave",
    "city": "Somewhere",
    "state": "NY",
    "zip": "54321",
    "companyName": "Test Corp",
    "title": "Manager"
  }'
```

### Getting Leads from BuilderPrime

```bash
curl -X GET "http://localhost:5000/api/builder-prime/leads?page=1&per_page=10" \
  -H "x-api-key: your_api_key"
```

### Getting Leads from HubSpot

```bash
curl -X GET "http://localhost:5000/api/hubspot/leads?page=1&per_page=10" \
  -H "x-api-key: your_api_key"
```

### Syncing Leads from BuilderPrime

```bash
curl -X POST http://localhost:5000/api/builder-prime/sync \
  -H "x-api-key: your_api_key"
```

### Syncing Leads from HubSpot

```bash
curl -X POST http://localhost:5000/api/hubspot/leads/sync \
  -H "x-api-key: your_api_key"
```

## API Documentation

Once the application is running, you can access the interactive Swagger documentation at:

```
http://localhost:5000/swagger
```

## Development

### Adding a New CRM Integration

1. **Create service file**: `app/services/new_crm_service.py`
2. **Create routes file**: `app/routes/new_crm.py`
3. **Update configuration**: Add CRM-specific settings to `config.py`
4. **Register blueprint**: Add the new blueprint to `app/__init__.py`
5. **Update documentation**: Add the new namespace to `swagger.py`

### Testing

Run tests using pytest:

```bash
pytest tests/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions, please open an issue in the repository or contact the development team.
