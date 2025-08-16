# Bitrix24 CRM Integration

This integration provides a clean, production-ready **Bitrix24 CRM** integration for your Flask app that follows the existing `controllers → services → routes` pattern.

## 🚀 Features

- **Full CRUD operations** for Contacts, Deals, and Leads
- **Inbound webhook integration** to call Bitrix24 API methods
- **Outbound webhook receiver** to handle Bitrix24 events
- **Per-client configuration** with database storage
- **Environment variable fallbacks** for global settings
- **Production-ready error handling** and logging

## 📋 Prerequisites

1. **Bitrix24 Portal** with REST API access
2. **Inbound Webhook URL** (for calling Bitrix24 API)
3. **Outbound Webhook Token** (for verifying incoming events)
4. **Flask app** with SQLAlchemy database

## 🔧 Setup

### 1. Environment Variables

Set these environment variables for global defaults:

```bash
# REQUIRED: Your Bitrix24 inbound webhook base URL
export BITRIX_WEBHOOK_BASE="https://b24-k7mbrm.bitrix24.com/rest/1/bn97b3lpvwpp7dxw/"

# REQUIRED: Outbound webhook secret token
export BITRIX_OUTBOUND_TOKEN="mkv9w4dxxvbao7gaemm0y7eay4uctbme"
```

### 2. Database Setup

The integration uses your existing `ClientCRMAuth` table to store per-client Bitrix24 configurations.

**Quick Setup (Recommended):**
```bash
python setup_bitrix24_crm.py
```

This script will:
- Add Bitrix24 to your `CRMs` table
- Update the integration files to use the proper CRM ID
- Ensure proper database relationships

**Manual Setup:**
If you prefer to set up manually, you'll need to:
1. Add a Bitrix24 entry to your `CRMs` table
2. Update the integration files to use the correct `crm_id`

### 3. Flask App Registration

The integration is automatically registered when you import and run your Flask app.

## 📚 API Endpoints

### Configuration

#### Save Client Configuration
```http
POST /api/bitrix/clients/{client_id}/config
```

**Body:**
```json
{
  "webhook_base": "https://b24-...bitrix24.com/rest/1/<token>/",
  "outbound_token": "optional_token_for_this_client"
}
```

#### Debug Client Configuration
```http
GET /api/bitrix/clients/{client_id}/config/debug
```

### Contacts

#### Create Contact
```http
POST /api/bitrix/clients/{client_id}/contacts
```

**Body:**
```json
{
  "fields": {
    "NAME": "Ada",
    "LAST_NAME": "Lovelace",
    "PHONE": [{"VALUE": "+15551234567", "VALUE_TYPE": "WORK"}],
    "EMAIL": [{"VALUE": "ada@example.com", "VALUE_TYPE": "WORK"}]
  }
}
```

#### List Contacts
```http
GET /api/bitrix/clients/{client_id}/contacts?filter[EMAIL]=ada@example.com&select=ID&select=NAME
```

**Query Parameters:**
- `filter[FIELD]` - Filter by specific field values
- `select[]` - Fields to return (can specify multiple)
- `start` - Pagination offset
- `ORDER_BY` - Sort order (ID, NAME, etc.)

#### Get Contact
```http
GET /api/bitrix/clients/{client_id}/contacts/{contact_id}
```

#### Update Contact
```http
PATCH /api/bitrix/clients/{client_id}/contacts/{contact_id}
```

**Body:**
```json
{
  "fields": {
    "NAME": "Updated Name"
  }
}
```

#### Delete Contact
```http
DELETE /api/bitrix/clients/{client_id}/contacts/{contact_id}
```

### Deals

#### Create Deal
```http
POST /api/bitrix/clients/{client_id}/deals
```

**Body:**
```json
{
  "fields": {
    "TITLE": "New Deal",
    "STAGE_ID": "NEW",
    "CURRENCY_ID": "USD",
    "OPPORTUNITY": 5000.00
  }
}
```

#### List Deals
```http
GET /api/bitrix/clients/{client_id}/deals?filter[STAGE_ID]=NEW&select=ID&select=TITLE
```

#### Get Deal
```http
GET /api/bitrix/clients/{client_id}/deals/{deal_id}
```

#### Update Deal
```http
PATCH /api/bitrix/clients/{client_id}/deals/{deal_id}
```

**Body:**
```json
{
  "fields": {
    "STAGE_ID": "IN_PROCESS"
  }
}
```

#### Delete Deal
```http
DELETE /api/bitrix/clients/{client_id}/deals/{deal_id}
```

### Leads

#### Create Lead
```http
POST /api/bitrix/clients/{client_id}/leads
```

**Body:**
```json
{
  "fields": {
    "TITLE": "New Lead",
    "STATUS_ID": "NEW",
    "SOURCE_ID": "WEB"
  }
}
```

#### List Leads
```http
GET /api/bitrix/clients/{client_id}/leads?filter[STATUS_ID]=NEW
```

#### Get Lead
```http
GET /api/bitrix/clients/{client_id}/leads/{lead_id}
```

#### Update Lead
```http
PATCH /api/bitrix/clients/{client_id}/leads/{lead_id}
```

#### Delete Lead
```http
DELETE /api/bitrix/clients/{client_id}/leads/{lead_id}
```

### Webhook Receiver

#### Outbound Webhook
```http
POST /api/bitrix/webhook
```

This endpoint receives events from Bitrix24 when configured as an outbound webhook. It verifies the `application_token` against your configured secret.

## 🧪 Testing

### Quick Test Script

Run the included test script:

```bash
python test_bitrix24_integration.py
```

### Manual Testing with cURL

#### 1. Save Configuration
```bash
curl -X POST http://localhost:5001/api/bitrix/clients/1/config \
  -H 'Content-Type: application/json' \
  -d '{
    "webhook_base": "https://b24-k7mbrm.bitrix24.com/rest/1/bn97b3lpvwpp7dxw/",
    "outbound_token": "mkv9w4dxxvbao7gaemm0y7eay4uctbme"
  }'
```

#### 2. Create Contact
```bash
curl -X POST http://localhost:5001/api/bitrix/clients/1/contacts \
  -H 'Content-Type: application/json' \
  -d '{
    "fields": {
      "NAME": "Ada",
      "LAST_NAME": "Lovelace",
      "PHONE": [{"VALUE": "+15551234567", "VALUE_TYPE": "WORK"}],
      "EMAIL": [{"VALUE": "ada@example.com", "VALUE_TYPE": "WORK"}]
    }
  }'
```

#### 3. List Contacts
```bash
curl "http://localhost:5001/api/bitrix/clients/1/contacts?select=ID&select=NAME&select=EMAIL"
```

#### 4. Update Deal Stage
```bash
curl -X PATCH http://localhost:5001/api/bitrix/clients/1/deals/123 \
  -H 'Content-Type: application/json' \
  -d '{ "STAGE_ID": "WON" }'
```

## 🔍 How It Works

### 1. Service Layer (`services/bitrix24_service.py`)
- **`bx_call()`** - Generic method to call any Bitrix24 REST API method
- **Form flattening** - Converts nested JSON to form-encoded data that Bitrix24 expects
- **Error handling** - Parses Bitrix24 error responses and raises appropriate exceptions
- **Client-specific config** - Reads webhook base URLs from database or falls back to environment

### 2. Controller Layer (`controllers/bitrix24_controller.py`)
- **RESTful endpoints** - Full CRUD operations for contacts, deals, and leads
- **Configuration management** - Save and retrieve client-specific Bitrix24 settings
- **Webhook receiver** - Handles incoming Bitrix24 events with token verification

### 3. Routes Layer (`routes/bitrix24_routes.py`)
- **Blueprint registration** - Integrates with your existing Flask app structure

## 🚨 Error Handling

The integration handles common Bitrix24 errors:

- **HTTP errors** - Network and server issues
- **API errors** - Bitrix24-specific error codes and descriptions
- **Configuration errors** - Missing webhook URLs or tokens
- **Validation errors** - Invalid request data

## 🔐 Security

- **Token verification** - Outbound webhooks verify `application_token`
- **Client isolation** - Each client has separate webhook configurations
- **Environment fallbacks** - Sensitive data can be stored in environment variables

## 📖 Bitrix24 API Reference

For detailed information about available fields and methods:

- [Contacts API](https://apidocs.bitrix24.com/api-reference/crm/contacts/)
- [Deals API](https://apidocs.bitrix24.com/api-reference/crm/deals/)
- [Leads API](https://apidocs.bitrix24.com/api-reference/crm/leads/)
- [Webhook Events](https://apidocs.bitrix24.com/api-reference/events/)

## 🚀 Next Steps

### Extend with Additional Entities
You can easily add support for:
- **Companies** (`crm.company.*`)
- **Tasks** (`tasks.task.*`)
- **Activities** (`crm.activity.*`)
- **Custom fields** and **user fields**

### Add Swagger Documentation
Integrate with your existing Swagger setup to document the Bitrix24 endpoints.

### Implement Retry Logic
Add exponential backoff and retry mechanisms for network failures.

### Event Processing
Enhance the webhook receiver to process specific Bitrix24 events and trigger actions.

## 🆘 Troubleshooting

### Common Issues

1. **"No Bitrix24 webhook base configured"**
   - Set `BITRIX_WEBHOOK_BASE` environment variable
   - Or save configuration via `/api/bitrix/clients/{id}/config`

2. **"Bitrix24 error: QUERY_LIMIT_EXCEEDED"**
   - Bitrix24 has rate limits; implement delays between calls

3. **"invalid application_token"**
   - Verify your outbound webhook token matches Bitrix24 configuration

4. **"fields[FIELD] is required"**
   - Check Bitrix24 API documentation for required fields

### Debug Mode

Use the debug endpoint to check your configuration:

```bash
curl "http://localhost:5001/api/bitrix/clients/1/config/debug"
```

## 📞 Support

For issues with this integration:
1. Check the logs for detailed error messages
2. Verify your Bitrix24 webhook configuration
3. Test with the provided test script
4. Check Bitrix24 API documentation for field requirements 