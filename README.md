# Spin-a-Bot CRM Integrations

A Flask application for integrating with multiple Customer Relationship Management (CRM) systems.

## Database Schema

The application uses PostgreSQL and includes the following tables:

### Core Tables

- **CRMs**: Stores information about different CRM systems
- **Clients**: Stores client information
- **ClientCRMAuth**: Manages authentication between clients and CRMs

### CRM-Specific Client Data Tables

- **BuilderPrimeClientData**: Client data from BuilderPrime CRM
- **ZohoClientData**: Client data from Zoho CRM
- **HubspotClientData**: Client data from HubSpot CRM
- **JobberClientData**: Client data from Jobber CRM
- **JobNimbusClientData**: Client data from JobNimbus CRM

## Setup Instructions

### Prerequisites

- Python 3.8+
- PostgreSQL database
- pip (Python package manager)

### Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd spin-a-bot-crm-integrations
   ```

2. **Create and activate virtual environment**

   ```bash
   python -m venv .venv
   # On Windows
   .venv\Scripts\activate
   # On macOS/Linux
   source .venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up PostgreSQL database**

   - Create a PostgreSQL database named `spinabot_crm`
   - Or set the `DATABASE_URL` environment variable to point to your database

5. **Run the application**
   ```bash
   python app.py
   ```

The application will automatically create all database tables on first run.

## Environment Variables

- `DATABASE_URL`: PostgreSQL connection string (default: `postgresql://localhost/spinabot_crm`)

## Project Structure

```
spin-a-bot-crm-integrations/
├── app.py                 # Main Flask application entry point
├── models.py              # Database models and schema
├── requirements.txt       # Python dependencies
├── test_swagger.py        # API testing script
├── config/                # Configuration files
│   ├── __init__.py
│   ├── database.py        # Database configuration
│   ├── flask_config.py    # Flask application configuration
│   └── swagger_config.py  # Swagger/OpenAPI documentation
├── controllers/           # API controllers
│   ├── __init__.py
│   └── client_controller.py
├── services/              # Business logic services
│   ├── __init__.py
│   └── client_service.py
├── routes/                # API route definitions
│   ├── __init__.py
│   └── client_routes.py
└── README.md             # This file
```

## API Documentation

The application includes comprehensive Swagger/OpenAPI documentation accessible at:
**http://localhost:5000/swagger**

### Available Endpoints

#### Client Management

- **POST /api/clients/** - Create a new client
- **GET /api/clients/** - Get all clients
- **GET /api/clients/{id}** - Get client by ID
- **PUT /api/clients/{id}** - Update client by ID

#### BuilderPrime CRM Integration

- **POST /api/builderprime/clients/{client_id}/leads** - Create a new lead/opportunity in BuilderPrime
- **GET /api/builderprime/leads** - Get all BuilderPrime leads from database
- **GET /api/builderprime/clients/{client_id}/leads** - Get BuilderPrime leads for a specific client
- **GET /api/builderprime/clients/{client_id}/data** - Fetch data directly from BuilderPrime API
- **PUT /api/builderprime/clients/{client_id}/leads/{opportunity_id}** - Update a lead/opportunity in BuilderPrime

### Sample Request Body (Create Client)

```json
{
  "company_name": "Spinabot",
  "email": "contact@spinabot.com",
  "other_contact_info": "Phone: 555-123-4567",
  "builderprime": {
    "api_key": "bp_api_key_abc123",
    "domain": "spinbot"
  },
  "hubspot_api_key": "hs_api_key_def456"
}
```

**Note:** The `builderprime` object contains both `api_key` and `domain` for BuilderPrime credentials, stored in a flexible JSON credentials field for future expansion.

### Response Format

```json
{
  "success": true,
  "message": "Client created successfully",
  "data": {
    "id": 1,
    "company_name": "Spinabot",
    "email": "contact@spinabot.com",
    "other_contact_info": "Phone: 123-456-7890",
    "created_at": "2024-01-15T10:30:00",
    "updated_at": "2024-01-15T10:30:00",
    "crm_integrations": [
      {
        "crm_name": "BuilderPrime",
        "crm_id": 1,
        "domain": "spinbot",
        "has_api_key": true,
        "credentials": {
          "api_key": "bp_api_key_abc123",
          "domain": "spinbot"
        },
        "created_at": "2024-01-15T10:30:00",
        "updated_at": "2024-01-15T10:30:00"
      },
      {
        "crm_name": "HubSpot",
        "crm_id": 2,
        "domain": null,
        "has_api_key": true,
        "credentials": {
          "api_key": "hs_api_key_def456"
        },
        "created_at": "2024-01-15T10:30:00",
        "updated_at": "2024-01-15T10:30:00"
      }
    ],
    "total_crm_integrations": 2
  }
}
```

### Update Client

#### Sample Request Body (Update Client)

```json
{
  "company_name": "Updated Spinabot",
  "email": "updated@spinabot.com",
  "other_contact_info": "Updated phone: 555-123-4567",
  "builderprime": {
    "api_key": "new_bp_api_key_abc123",
    "domain": "updated-spinbot"
  },
  "hubspot_api_key": "new_hs_api_key_def456"
}
```

#### Update Client Response Format

```json
{
  "success": true,
  "message": "Client updated successfully",
  "data": {
    "id": 1,
    "company_name": "Updated Spinabot",
    "email": "updated@spinabot.com",
    "other_contact_info": "Updated phone: 555-123-4567",
    "domain": "updated-spinabot",
    "crm_integrations": [
      {
        "crm_name": "BuilderPrime",
        "domain": "updated-spinabot",
        "has_api_key": true
      },
      {
        "crm_name": "HubSpot",
        "domain": "updated-spinabot",
        "has_api_key": true
      }
    ],
    "updated_fields": {
      "client": ["company_name", "email", "other_contact_info"],
      "crm_auth": ["BuilderPrime", "HubSpot"]
    }
  }
}
```

### BuilderPrime Lead Creation

#### Sample Request Body (Create BuilderPrime Lead)

```json
{
  "first_name": "John",
  "last_name": "Smith",
  "email": "johnsmith3@gmail.com",
  "mobile_phone": "+18005554444",
  "mobile_phone_extension": "1",
  "home_phone": "+18005554444",
  "home_phone_extension": "2",
  "office_phone": "+18005554444",
  "office_phone_extension": "3",
  "fax": "+18005554444",
  "address_line1": "123 Main Street",
  "address_line2": "Suite 2",
  "city": "Los Angeles",
  "state": "CA",
  "zip": "12345",
  "company_name": "Widgets Galore",
  "title": "President",
  "notes": "Some notes about this lead",
  "lead_status_name": "Lead Received",
  "lead_source_name": "Facebook",
  "sales_person_first_name": "Alice",
  "sales_person_last_name": "Thompson",
  "lead_setter_first_name": "Bob",
  "lead_setter_last_name": "Roberts",
  "class_name": "Residential",
  "project_type_name": "Kitchen Renovation",
  "external_id": "AB-4617",
  "dialer_status": "1st Attempt",
  "custom_fields": [
    {
      "name": "Budget",
      "value": "5000"
    },
    {
      "name": "Referred By",
      "value": "Axl Rose"
    }
  ]
}
```

#### BuilderPrime Response Format

```json
{
  "success": true,
  "message": "Lead created successfully in BuilderPrime",
  "data": {
    "builderprime_response": {
      "message": "Client Successfully Created. Opportunity: 3793445",
      "opportunity_id": "3793445",
      "content_type": "text/plain;charset=UTF-8"
    },
    "client_id": 1,
    "domain": "spinbot",
    "external_id": "AB-4617",
    "stored_data_id": 1
  }
}
```

#### BuilderPrime Leads Response Format

```json
{
  "success": true,
  "message": "Found 2 BuilderPrime leads",
  "data": [
    {
      "id": 1,
      "source_client_id": "1",
      "crm_client_id": "3793445",
      "name": "John Smith",
      "email": "johnsmith3@gmail.com",
      "phone_number": "+18005554444",
      "opportunity_id": "3793445",
      "created_at": "2024-01-15T10:30:00",
      "updated_at": "2024-01-15T10:30:00"
    }
  ]
}
```

#### BuilderPrime API Data Fetching

**Endpoint:** `GET /api/builderprime/clients/{client_id}/data`

**Query Parameters:**

- `last-modified-since` (int, optional): Date in milliseconds since epoch (up to 1 year ago)
- `lead-status` (string, optional): Lead status name to filter by
- `lead-source` (string, optional): Lead source name to filter by
- `dialer-status` (string, optional): Dialer status to filter by
- `phone` (string, optional): Phone number to search for (E.164 format recommended)
- `limit` (int, optional): Number of records to return (max 500)
- `page` (int, optional): Page number (starts with 0)

**Sample Request:**

```
GET /api/builderprime/clients/1/data?limit=10&lead-status=Lead Received&page=0
```

**Sample Response:**

```json
{
  "success": true,
  "message": "Data fetched successfully from BuilderPrime",
  "data": {
    "builderprime_data": [
      {
        "id": 1035,
        "firstName": "Eli",
        "lastName": "Manning",
        "phoneNumber": "+12125551234",
        "homePhoneNumber": "+12125551234",
        "officePhoneNumber": "+12125551234",
        "emailAddress": "eli@giants.com",
        "type": "NEW",
        "addressLine1": "1 MetLife Stadium Dr",
        "addressLine2": null,
        "city": "East Rutherford",
        "state": "NJ",
        "zip": "07073",
        "companyName": "New York Giants",
        "doNotContact": false,
        "dialerStatus": "At Dialer",
        "clientId": 21596,
        "leadStatusName": "Job Paid",
        "leadSourceDescription": "Direct Mail",
        "salesPersonFirstName": "Alice",
        "salesPersonLastName": "Thompson",
        "leadSetterFirstName": "Bob",
        "leadSetterLastName": "Roberts",
        "projectTypeDescription": "Window replacement",
        "locationName": "Residential",
        "buildingTypeDescription": "Single Family",
        "bestContactTime": "Evening",
        "bestContactMethod": "Mobile Phone",
        "estimatedValue": 10000,
        "closeProbability": 50,
        "createdDate": 1503670680313,
        "lastModifiedDate": 1560687583714
      }
    ],
    "client_id": 1,
    "domain": "spinbot",
    "parameters": {
      "limit": 10,
      "lead-status": "Lead Received",
      "page": 0
    },
    "total_records": 1
  }
}
```

#### BuilderPrime Lead Update

**Endpoint:** `PUT /api/builderprime/clients/{client_id}/leads/{opportunity_id}`

**Sample Request Body (Update BuilderPrime Lead):**

```json
{
  "first_name": "Marcus",
  "last_name": "Rodriguez",
  "email": "marcus.rodriguez@techcorp.com",
  "mobile_phone": "+15551234567",
  "home_phone": "+15559876543",
  "office_phone": "+15555555555",
  "fax": "+15554443333",
  "do_not_contact": false,
  "dialer_status": "At Dialer",
  "address_line1": "456 Innovation Drive",
  "address_line2": "Floor 3",
  "city": "Austin",
  "state": "TX",
  "zip": "78701",
  "company_name": "TechCorp Solutions",
  "title": "Senior Developer",
  "notes": "Updated notes about this lead",
  "lead_status_name": "Qualified Lead",
  "lead_source_name": "LinkedIn",
  "sales_person_first_name": "Sarah",
  "sales_person_last_name": "Johnson",
  "lead_setter_first_name": "Mike",
  "lead_setter_last_name": "Chen",
  "class_name": "Commercial",
  "project_type_name": "Custom Software Development",
  "custom_fields": [
    {
      "name": "Budget",
      "value": "15000"
    },
    {
      "name": "Timeline",
      "value": "3 months"
    }
  ]
}
```

**Sample Response:**

```json
{
  "success": true,
  "message": "Lead updated successfully in BuilderPrime",
  "data": {
    "builderprime_response": {
      "message": "Client Successfully Updated. Opportunity: 3793445",
      "opportunity_id": "3793445",
      "content_type": "text/plain;charset=UTF-8"
    },
    "client_id": 1,
    "domain": "spinbot",
    "opportunity_id": "3793445",
    "stored_data_id": 1
  }
}
```

**Note:** Only non-blank values will be updated. Omit fields that don't need to be modified.

**Important:** BuilderPrime requires exact field value matches. If you get validation errors, the API will provide helpful tips in the error message.

**Error Handling for Updates:**

If you encounter validation errors when updating leads, the API will provide helpful tips:

- **Lead Status Error**: Use values like "Lead Received", "Qualified", "Proposal Sent", etc.
- **Lead Source Error**: Use values like "Website", "Phone", "Referral", etc.
- **Dialer Status Error**: Use values like "Not Started", "In Progress", "Completed", etc.
- **Project Type Error**: Use values like "Kitchen Renovation", "Bathroom Remodel", etc.
- **Class Error**: Use values like "Residential", "Commercial", etc.

**Example Error Response:**

```json
{
  "success": false,
  "message": "BuilderPrime API error: 400 - Unable to update client with name: Marcus Rodriguez in Builder Prime from API using API key with description: Spinabot. Please contact support for help in resolving this issue.Detail: The specified lead status could not be found. (Tip: The lead status name must match exactly with what's configured in BuilderPrime. Common values include: 'Lead Received', 'Qualified', 'Proposal Sent', 'Closed Won', 'Closed Lost')",
  "data": {
    "status_code": 400,
    "response_text": "{\"message\":\"Unable to update client with name: Marcus Rodriguez in Builder Prime from API using API key with description: Spinabot. Please contact support for help in resolving this issue.Detail: The specified lead status could not be found.\"}",
    "content_type": "application/json",
    "api_url": "https://spinbot.builderprime.com/api/clients/v1/3797455"
  }
}
```

### Testing the API

1. Start the Flask application: `python app.py`
2. Open your browser and go to: http://localhost:5000/swagger
3. Use the interactive Swagger UI to test all endpoints
4. Or run the test script: `python test_swagger.py`

## Database Relationships

- **CRMs** ↔ **ClientCRMAuth** (One-to-Many)
- **Clients** ↔ **ClientCRMAuth** (One-to-Many)
- **CRMs** ↔ **CRM Client Data Tables** (One-to-Many)

Each CRM client data table stores client information specific to that CRM system while maintaining relationships with the core CRM and client tables.

## OAuth Fix (Jobber)

Update `services/jobber_service.py` constants:

```python
# === Jobber OAuth configuration ===
CLIENT_ID     = os.getenv("JOBBER_CLIENT_ID", "6c6a5fb3-9c6b-4887-80cb-c65f1cc2825a")
CLIENT_SECRET = os.getenv("JOBBER_CLIENT_SECRET", "dddff56b393da10a8519f36e4d7b13e273c83a80c1044f6d41e4d16aa92645b4")
REDIRECT_URI  = os.getenv("JOBBER_REDIRECT_URI", "http://localhost:5001/api/jobber/callback")
AUTH_URL      = "https://api.getjobber.com/api/oauth/authorize"
TOKEN_URL     = "https://api.getjobber.com/api/oauth/token"
GRAPHQL_URL   = "https://api.getjobber.com/api/graphql"
```

Ensure `.env` contains:

```
JOBBER_CLIENT_ID=6c6a5fb3-9c6b-4887-80cb-c65f1cc2825a
JOBBER_CLIENT_SECRET=dddff56b393da10a8519f36e4d7b13e273c83a80c1044f6d41e4d16aa92645b4
JOBBER_REDIRECT_URI=http://localhost:5001/api/jobber/callback
```
