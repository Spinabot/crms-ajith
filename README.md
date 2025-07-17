# Unified CRM Integration

A unified Flask application that integrates multiple CRM systems into a single API, providing a consistent interface for managing leads across different platforms with secure secret management using HashiCorp Vault.

## 🎯 Supported CRM Systems

- **BuilderPrime CRM** ✅ (Fully implemented with Vault integration)
- **HubSpot CRM** ✅ (Fully implemented with Vault integration)
- **Jobber CRM** ✅ (Fully implemented with OAuth 2.0 and Vault integration)
- **JobNimbus CRM** ✅ (Fully implemented with Vault integration)
- **Zoho CRM** ✅ (Fully implemented with OAuth 2.0 and Vault integration)

## ✨ Features

- **Unified API**: Single API endpoint for all CRM operations
- **Cross-CRM Synchronization**: Sync leads between different CRM systems
- **Secure Secret Management**: HashiCorp Vault integration for all CRM credentials
- **OAuth 2.0 Support**: Full OAuth flows for Jobber and Zoho CRM
- **Comprehensive Logging**: Track all operations and sync activities
- **Swagger Documentation**: Interactive API documentation with detailed OAuth guides
- **Database Abstraction**: Unified data model for all CRM systems
- **Automatic Token Refresh**: Handles OAuth token expiration automatically
- **Fallback Authentication**: Vault-first with environment variable fallback

## 🏗️ Architecture

```
UnifiedCRMIntegration/
├── app/
│   ├── __init__.py              # Flask application factory
│   ├── config.py                # Configuration settings
│   ├── models.py                # Database models
│   ├── swagger.py               # API documentation
│   ├── routes/                  # API routes for each CRM
│   │   ├── builder_prime.py     # BuilderPrime API endpoints
│   │   ├── hubspot.py          # HubSpot API endpoints
│   │   ├── jobber.py           # Jobber API endpoints
│   │   ├── jobber_auth.py      # Jobber OAuth authentication
│   │   ├── jobnimbus.py        # JobNimbus API endpoints
│   │   └── zoho.py             # Zoho API endpoints
│   ├── services/               # Business logic for each CRM
│   │   ├── builder_prime_service.py
│   │   ├── hubspot_service.py
│   │   ├── jobnimbus_service.py
│   │   ├── zoho_service.py
│   │   └── vault_service.py    # Vault integration service
│   └── utils/                  # Utility functions
│       └── auth.py
├── migrations/                 # Database migrations
├── tests/                     # Test files
├── run.py                     # Application entry point
├── requirements.txt           # Python dependencies

└── README.md                  # This file
```

## 🔐 Authentication & Security

### Vault Integration

All CRM secrets are securely stored in HashiCorp Vault with automatic fallback to environment variables:

- **BuilderPrime**: `BUILDER_PRIME_API_KEY`
- **HubSpot**: `HUBSPOT_API_TOKEN`
- **Jobber**: `JOBBER_CLIENT_ID`, `JOBBER_CLIENT_SECRET`
- **JobNimbus**: `JOBNIMBUS_API_KEY`
- **Zoho**: `ZOHO_CLIENT_ID`, `ZOHO_CLIENT_SECRET`

### OAuth 2.0 Authentication

**Jobber CRM**: User-based OAuth 2.0 flow

- Each user requires separate authorization
- Access tokens expire after 1 hour
- Refresh tokens valid for 30 days

**Zoho CRM**: Entity-based OAuth 2.0 flow

- Each entity requires separate authorization
- Entity ID 1 works without authorization (for testing)
- Access tokens expire after 1 hour
- Refresh tokens valid for 60 days

## 📊 Database Models

### UnifiedLead

Stores lead information from all CRM systems in a unified format:

- Basic contact information (name, email, phone)
- Address information
- Company information
- Lead status and source
- CRM system tracking
- Raw CRM data storage

### JobberAuth

Manages Jobber OAuth authentication:

- User ID mapping
- Access and refresh tokens
- Token expiration tracking

### ZohoCreds

Manages Zoho OAuth authentication:

- Entity ID mapping
- Access and refresh tokens
- Token expiration tracking

### SyncLog

Tracks synchronization activities:

- Operation type (create, update, delete, sync)
- Success/failure status
- Error messages
- Sync data

## 🚀 API Endpoints

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

### Jobber CRM

- `POST /api/jobber/leads` - Create a new client/lead
- `GET /api/jobber/clients` - Get clients with pagination
- `POST /api/jobber/clients/update` - Update a client
- `POST /api/jobber/clients/archive` - Archive a client

#### Jobber OAuth Authentication

- `GET /auth/jobber/authorize?userid={user_id}` - Initiate OAuth authorization
- `GET /auth/jobber/callback` - Handle OAuth callback
- `GET /auth/jobber/status/{user_id}` - Check authentication status
- `POST /auth/jobber/refresh/{user_id}` - Refresh access token

### JobNimbus CRM

- `POST /jobnimbus/contacts` - Create a new contact
- `GET /jobnimbus/contacts` - Get contacts with filtering
- `PUT /jobnimbus/contacts/{jnid}` - Update a contact
- `DELETE /jobnimbus/contacts/{jnid}` - Archive a contact

### Zoho CRM

- `POST /zoho/{entity_id}/leads` - Create a new lead
- `GET /zoho/{entity_id}/leads` - Get leads with filtering
- `PUT /zoho/{entity_id}/leads/{lead_id}` - Update a lead
- `DELETE /zoho/{entity_id}/leads/{lead_id}` - Delete a lead
- `GET /zoho/{entity_id}/users` - Get users
- `GET /zoho/{entity_id}/leads/meta` - Get metadata

#### Zoho OAuth Authentication

- `GET /zoho/{entity_id}/redirect` - Initiate OAuth authorization
- `GET /zoho/authorize/callback` - Handle OAuth callback
- `GET /zoho/{entity_id}/status` - Check authentication status
- `GET /zoho/{entity_id}/refresh` - Refresh access token

### Vault Management

- `GET /vault/status` - Check Vault connection status
- `GET /vault/secrets` - Get all CRM secrets
- `GET /vault/secrets/{path}` - Get specific secret
- `POST /vault/secrets/{path}` - Create/update secret
- `DELETE /vault/secrets/{path}` - Delete secret

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd UnifiedCRMIntegration
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Create a `.env` file with the following variables:

```env
# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=1
FLASK_HOST=0.0.0.0
FLASK_PORT=5000

# Database Configuration
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_NAME=leads_db
DB_PORT=5432

# HubSpot Configuration
HUBSPOT_API_BASE_URL=https://api.hubapi.com

# Jobber Configuration
JOBBER_REDIRECT_URI=http://localhost:5000/auth/jobber/callback
JOBBER_API_URL=https://api.getjobber.com/api/graphql
JOBBER_TOKENS_URL=https://api.getjobber.com/api/oauth/token

# Vault Configuration
VAULT_URL=https://vault.spinabot.com
VAULT_TOKEN=your_vault_token_here
VAULT_SECRET_PATH=spinabot/dev/app-secrets/CRM-Integration
VAULT_MOUNT_POINT=kv/

# Optional: Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
CACHE_DEFAULT_TIMEOUT=300
```

### 5. Vault Configuration

The application is configured to use HashiCorp Vault for secure secret management. All CRM secrets are already stored in Vault at the path specified in `VAULT_SECRET_PATH`.

**Vault Secrets (Already Configured):**

- `BUILDER_PRIME_API_KEY` - BuilderPrime API key
- `HUBSPOT_API_TOKEN` - HubSpot API token
- `JOBBER_CLIENT_ID` - Jobber OAuth client ID
- `JOBBER_CLIENT_SECRET` - Jobber OAuth client secret
- `JOBNIMBUS_API_KEY` - JobNimbus API key
- `ZOHO_CLIENT_ID` - Zoho OAuth client ID
- `ZOHO_CLIENT_SECRET` - Zoho OAuth client secret

**Note:** The application automatically fetches these secrets from Vault. No additional setup is required.

### 6. Initialize Database

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 7. Run the Application

```bash
python run.py
```

## 📖 Usage Examples

### OAuth Authentication (Jobber)

```bash
# 1. Start OAuth flow for user 123
curl -X GET "http://localhost:5000/auth/jobber/authorize?userid=123"

# 2. Check authentication status
curl -X GET "http://localhost:5000/auth/jobber/status/123"

# 3. Use Jobber APIs (after authorization)
curl -X GET "http://localhost:5000/api/jobber/clients" \
  -H "Content-Type: application/json"
```

### OAuth Authentication (Zoho)

```bash
# 1. Start OAuth flow for entity 123
curl -X GET "http://localhost:5000/zoho/123/redirect"

# 2. Check authentication status
curl -X GET "http://localhost:5000/zoho/123/status"

# 3. Use Zoho APIs (after authorization)
curl -X GET "http://localhost:5000/zoho/123/leads" \
  -H "Content-Type: application/json"
```

### Creating Leads

```bash
# BuilderPrime
curl -X POST http://localhost:5000/api/builder-prime/leads \
  -H "Content-Type: application/json" \
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

# HubSpot
curl -X POST http://localhost:5000/api/hubspot/leads \
  -H "Content-Type: application/json" \
  -d '{
    "firstName": "Jane",
    "lastName": "Smith",
    "email": "jane.smith@example.com",
    "mobilePhone": "555-987-6543",
    "addressLine1": "456 Oak Ave",
    "city": "Somewhere",
    "state": "NY",
    "zip": "54321"
  }'

# JobNimbus
curl -X POST http://localhost:5000/jobnimbus/contacts \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Alice",
    "last_name": "Johnson",
    "email": "alice.johnson@example.com",
    "mobile_phone": "555-555-5555"
  }'

# Zoho (entity_id 1 works without auth)
curl -X POST http://localhost:5000/zoho/1/leads \
  -H "Content-Type: application/json" \
  -d '{
    "First_Name": "Bob",
    "Last_Name": "Wilson",
    "Email": "bob.wilson@example.com",
    "Phone": "555-111-2222"
  }'
```

### Vault Management

```bash
# Check Vault status
curl -X GET "http://localhost:5000/vault/status"

# Get all CRM secrets
curl -X GET "http://localhost:5000/vault/secrets"

# Get specific secret
curl -X GET "http://localhost:5000/vault/secrets/BUILDER_PRIME_API_KEY"
```

## 📚 API Documentation

Once the application is running, access the interactive Swagger documentation:

```
http://localhost:5000/swagger
```

The documentation includes:

- Complete OAuth 2.0 flow guides for Jobber and Zoho
- Detailed endpoint descriptions and examples
- Request/response models for all CRMs
- Vault integration information

## 🔧 Development

### Adding a New CRM Integration

1. **Create service file**: `app/services/new_crm_service.py`
2. **Create routes file**: `app/routes/new_crm.py`
3. **Update configuration**: Add CRM-specific settings to `config.py`
4. **Register blueprint**: Add the new blueprint to `app/__init__.py`
5. **Update documentation**: Add the new namespace to `swagger.py`
6. **Add Vault integration**: Update `vault_service.py` and store secrets in Vault

### Testing

Run tests using pytest:

```bash
pytest tests/
```

### Database Migrations

```bash
# Create a new migration
flask db migrate -m "Description of changes"

# Apply migrations
flask db upgrade
```

## 🚨 Important Notes

### OAuth Authentication

- **Jobber**: Each user_id requires separate authorization
- **Zoho**: Entity ID 1 works without authorization (for testing)
- **Token Refresh**: Both systems automatically refresh expired tokens
- **Browser Required**: OAuth flows require browser interaction

### Vault Integration

- **Vault-First**: All secrets are fetched from Vault first
- **Fallback**: Environment variables are used if Vault is unavailable
- **No Hardcoded Secrets**: Never commit secrets to version control
- **Secret Rotation**: Easy to rotate secrets without code changes

### Environment Variables

- **Required**: Database and Vault configuration
- **Optional**: CRM secrets (if using Vault)
- **Development**: Use `.env` file for local development
- **Production**: Use environment variables or Vault

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Update documentation
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:

- Open an issue in the repository
- Check the Swagger documentation at `/swagger`
- Review the Vault integration guide
- Contact the development team

## 🔄 Version History

- **v1.0.0**: Initial release with BuilderPrime and HubSpot
- **v2.0.0**: Added Jobber OAuth integration
- **v3.0.0**: Added JobNimbus and Zoho integrations
- **v4.0.0**: Added HashiCorp Vault integration for all CRM secrets
