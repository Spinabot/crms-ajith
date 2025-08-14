# Merge CRM Integration

This document describes the Merge CRM integration that has been added to your Flask CRMs service.

## Overview

Merge.dev provides a unified API for multiple CRM systems (HubSpot, Salesforce, Pipedrive, etc.). This integration allows your clients to connect their CRM accounts through Merge and then interact with contacts using a single, consistent API.

## Architecture

The integration follows your existing pattern:
- **Models**: `MergeLinkedAccount` stores linked CRM accounts per client
- **Services**: `merge_service.py` handles all Merge API calls
- **Controllers**: `merge_controller.py` provides REST endpoints
- **Routes**: `merge_routes.py` registers the blueprint

## Environment Setup

Add these environment variables:

```bash
# Required: Your Merge Production Access Key
export MERGE_API_KEY="cjtuJl3..."  # Get from https://app.merge.dev/settings/api-keys

# Optional: Base URL (defaults to US)
export MERGE_BASE_URL="https://api.merge.dev"
```

## Database Setup

Run the table creation script:

```bash
python create_merge_tables.py
```

Or use your existing table creator:

```bash
python create_tables.py
```

## API Endpoints

### 1. Create Link Token
**POST** `/api/merge/clients/{client_id}/link-token`

Creates a Merge Link session for CRM integration.

**Request Body:**
```json
{
  "end_user_email": "owner@example.com",
  "end_user_org_name": "Acme Roofing",
  "end_user_origin_id": "client-1",
  "integration_slug": "hubspot"  // optional
}
```

**Response:**
```json
{
  "link_token": "abc123...",
  "magic_link_url": "https://link.merge.dev/...",
  "link_expiry_mins": 10080
}
```

### 2. Save Linked Account
**POST** `/api/merge/clients/{client_id}/linked-accounts`

Saves the account token after user completes Merge Link.

**Request Body:**
```json
{
  "account_token": "token_from_merge_link",
  "integration_slug": "hubspot",
  "end_user_origin_id": "client-1",
  "end_user_email": "owner@example.com",
  "end_user_org_name": "Acme Roofing"
}
```

### 3. List Contacts
**GET** `/api/merge/clients/{client_id}/crm/contacts`

Lists contacts from the linked CRM account.

**Query Parameters:**
- `account_token` (optional): Use specific account token
- `modified_after`: Filter by modification date
- `cursor`: Pagination cursor
- `page_size`: Number of results per page

### 4. Create Contact
**POST** `/api/merge/clients/{client_id}/crm/contacts`

Creates a new contact in the linked CRM.

**Request Body:**
```json
{
  "contact": {
    "name": "Jane Doe",
    "email_addresses": [{"email_address": "jane@example.com"}],
    "phone_numbers": [{"phone_number": "+15551234567"}]
  }
}
```

### 5. Admin: List All Linked Accounts
**GET** `/api/merge/linked-accounts`

Lists all Merge linked accounts (admin/debug endpoint).

## Workflow

### Step 1: Initialize Integration
1. Client calls `/link-token` with their email and org details
2. Your app receives a `magic_link_url`
3. Client opens the magic link in their browser

### Step 2: Complete Link
1. Client authenticates with their CRM (HubSpot, Salesforce, etc.)
2. Merge captures the connection and generates an `account_token`
3. Your app receives the `account_token` (via webhook or manual input)

### Step 3: Save Connection
1. Call `/linked-accounts` to save the `account_token` in your database
2. The client is now connected and ready to use

### Step 4: Use CRM Data
1. Call `/crm/contacts` to list contacts
2. Call `/crm/contacts` POST to create new contacts
3. All requests use the stored `account_token` automatically

## Testing

### Quick Test
```bash
# 1. Set your API key
export MERGE_API_KEY="your_key_here"

# 2. Create a link token
curl -X POST http://localhost:5001/api/merge/clients/1/link-token \
  -H 'Content-Type: application/json' \
  -d '{
    "end_user_email": "owner@example.com",
    "end_user_org_name": "Acme Roofing",
    "end_user_origin_id": "client-1",
    "integration_slug": "hubspot"
  }'

# 3. Open the magic_link_url in a browser
# 4. Complete the CRM connection
# 5. Get the account_token from Merge dashboard
# 6. Save the linked account
# 7. Test listing/creating contacts
```

### Test Script
Run the included test script:
```bash
python test_merge_integration.py
```

## Error Handling

The service includes comprehensive error handling:
- **MergeServiceError**: Custom exception for Merge API errors
- **HTTP 502**: When Merge API calls fail
- **HTTP 400**: When required parameters are missing
- **HTTP 404**: When no linked account is found

## Security Notes

- **Never hardcode** your `MERGE_API_KEY`
- **Store account tokens** securely in your database
- **Validate client_id** to ensure users can only access their own data
- **Use HTTPS** in production for all API calls

## Merge-Specific Details

### Authentication
- **Authorization**: `Bearer <Production Access Key>` (your server)
- **X-Account-Token**: `<account_token>` (specific user's integration)

### API Endpoints
- **Link Token**: `/api/crm/v1/link-token` (category-specific)
- **Contacts**: `/api/crm/v1/contacts` (unified CRM API)
- **Linked Accounts**: `/api/crm/v1/linked-accounts`

### Supported CRMs
- HubSpot
- Salesforce
- Pipedrive
- Zoho CRM
- And many more...

## Troubleshooting

### Common Issues

1. **"MERGE_API_KEY is not set"**
   - Check your environment variables
   - Restart your Flask app after setting env vars

2. **"No Merge linked account found for client"**
   - Client needs to complete the Merge Link process first
   - Save the account_token using `/linked-accounts` endpoint

3. **Merge API errors (502)**
   - Check your API key is valid
   - Verify the account_token is still active
   - Check Merge service status

### Debug Mode
Enable debug logging in your Flask app to see detailed Merge API requests and responses.

## Next Steps

Consider adding:
- **Webhook handlers** for automatic account_token capture
- **Token refresh** logic for expired connections
- **Rate limiting** for Merge API calls
- **Caching** for frequently accessed data
- **Swagger documentation** for the new endpoints

## Support

- [Merge.dev Documentation](https://docs.merge.dev/)
- [Merge API Reference](https://docs.merge.dev/crm/overview/)
- [Merge Support](https://merge.dev/support) 