# Merge CRM Integration

This document describes the Merge CRM integration that has been added to your Flask CRMs service.

## Overview

Merge.dev provides a unified API for multiple CRM systems (HubSpot, Salesforce, Pipedrive, etc.) and HRIS systems (BambooHR, Personio, Workday, etc.). This integration allows your clients to connect their CRM and HRIS accounts through Merge and then interact with data using a single, consistent API.

**New Implementation**: We now provide a clean, drop-in set of Flask routes that implement **all CRUD actions Merge actually exposes today**:
- **CRM**: Create/Read/Update on accounts, contacts, engagements, opportunities, tasks, plus Create on leads and notes
- **HRIS**: Create/Read on time-off and timesheet-entries, Read on employees, companies, groups, locations
- **Universal**: Ignore endpoints for soft deletion, passthrough for vendor-specific operations, delete linked account

## Architecture

The integration follows your existing pattern:
- **Models**: `MergeLinkedAccount` stores linked CRM and HRIS accounts per client
- **Services**: 
  - `merge_service.py` handles legacy CRM + HRIS API calls
  - `merge_client.py` provides the new unified API client
- **Controllers**: 
  - `merge_controller.py` provides legacy CRM REST endpoints
  - `merge_hris_controller.py` provides legacy HRIS REST endpoints
- **Routes**: 
  - `merge_routes.py` registers the legacy CRM blueprint
  - `merge_hris_routes.py` registers the legacy HRIS blueprint
  - `merge_crm.py` provides the new unified CRM CRUD routes
  - `merge_hris.py` provides the new unified HRIS CRUD routes

## Environment Setup

Add these environment variables:

```bash
# Required: Your Merge Production Access Key
export MERGE_API_KEY="cjtuJl3..."  # Get from https://app.merge.dev/settings/api-keys

# Required: Your Merge Webhook Secret
export MERGE_WEBHOOK_SECRET="your_webhook_secret"  # Get from Merge Dashboard → Webhooks → Security

# Optional: Base URL (defaults to US)
export MERGE_BASE_URL="https://api.merge.dev"

# New Unified API (Recommended)
export MERGE_PROD_KEY="cjtuJl3..."  # Same as MERGE_API_KEY
export MERGE_ACCOUNT_TOKEN="your_linked_account_token"  # Per-end-customer token
export MERGE_CRM_BASE="https://api.merge.dev/api/crm/v1"  # Optional region override
export MERGE_HRIS_BASE="https://api.merge.dev/api/hris/v1"  # Optional region override
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

### CRM Integration

#### 1. Create Link Token
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

### 6. Webhook Endpoint
**POST** `/api/merge/webhook`

Receives webhooks from Merge for linked account events, sync status updates, and data changes.
Verifies webhook signature for security and updates local records accordingly.

**Headers:**
- `X-Merge-Webhook-Signature`: HMAC-SHA256 signature for webhook verification

### 7. Webhook Debug
**GET** `/api/merge/webhook/debug`

Provides debug information about webhook configuration and latest webhook data.
Useful for troubleshooting webhook setup and verification.

## New Unified API Endpoints

The new implementation provides clean, standardized CRUD operations that match exactly what Merge exposes today, plus **capabilities discovery** and **meta-driven writes** for all supported CRMs.

### CRM Unified API

#### Accounts
- **GET** `/api/merge/crm/accounts` - List all accounts
- **POST** `/api/merge/crm/accounts` - Create new account
- **GET** `/api/merge/crm/accounts/{id}` - Get account by ID
- **PATCH** `/api/merge/crm/accounts/{id}` - Update account

#### Contacts
- **GET** `/api/merge/crm/contacts` - List all contacts
- **POST** `/api/merge/crm/contacts` - Create new contact
- **GET** `/api/merge/crm/contacts/{id}` - Get contact by ID
- **PATCH** `/api/merge/crm/contacts/{id}` - Update contact
- **POST** `/api/merge/crm/contacts/ignore/{id}` - Ignore contact (soft delete)

#### Leads
- **GET** `/api/merge/crm/leads` - List all leads
- **POST** `/api/merge/crm/leads` - Create new lead
- **GET** `/api/merge/crm/leads/{id}` - Get lead by ID

#### Opportunities
- **GET** `/api/merge/crm/opportunities` - List all opportunities
- **POST** `/api/merge/crm/opportunities` - Create new opportunity
- **GET** `/api/merge/crm/opportunities/{id}` - Get opportunity by ID
- **PATCH** `/api/merge/crm/opportunities/{id}` - Update opportunity

#### Tasks
- **GET** `/api/merge/crm/tasks` - List all tasks
- **POST** `/api/merge/crm/tasks` - Create new task
- **GET** `/api/merge/crm/tasks/{id}` - Get task by ID
- **PATCH** `/api/merge/crm/tasks/{id}` - Update task

#### Notes
- **GET** `/api/merge/crm/notes` - List all notes
- **POST** `/api/merge/crm/notes` - Create new note
- **GET** `/api/merge/crm/notes/{id}` - Get note by ID

#### Engagements
- **GET** `/api/merge/crm/engagements` - List all engagements
- **POST** `/api/merge/crm/engagements` - Create new engagement
- **GET** `/api/merge/crm/engagements/{id}` - Get engagement by ID
- **PATCH** `/api/merge/crm/engagements/{id}` - Update engagement

#### Users
- **GET** `/api/merge/crm/users` - List all users
- **GET** `/api/merge/crm/users/{id}` - Get user by ID
- **POST** `/api/merge/crm/users/ignore/{id}` - Ignore user

#### Universal Operations
- **POST** `/api/merge/crm/delete-account` - Delete linked account
- **POST** `/api/merge/crm/passthrough` - Vendor-specific operations

#### Capabilities Discovery & Meta-Driven Writes
- **GET** `/api/merge/crm/capabilities` - List linked accounts & their capabilities
- **GET** `/api/merge/crm/integrations` - All available integrations (names, slugs, logos)
- **GET** `/api/merge/crm/meta/{model}/post` - Get writable fields for creating objects
- **GET** `/api/merge/crm/meta/{model}/{id}/patch` - Get writable fields for updating objects

#### Allowlist Management
- **GET** `/api/merge/crm/allowlist/status` - Check allowlist validation & resolved slugs

### HRIS Unified API

#### Employees
- **GET** `/api/merge/hris/employees` - List all employees
- **GET** `/api/merge/hris/employees/{id}` - Get employee by ID
- **POST** `/api/merge/hris/employees/ignore/{id}` - Ignore employee

#### Time Off
- **GET** `/api/merge/hris/time-off` - List all time off requests
- **POST** `/api/merge/hris/time-off` - Create new time off request
- **GET** `/api/merge/hris/time-off/{id}` - Get time off by ID

#### Timesheet Entries
- **GET** `/api/merge/hris/timesheet-entries` - List all timesheet entries
- **POST** `/api/merge/hris/timesheet-entries` - Create new timesheet entry
- **GET** `/api/merge/hris/timesheet-entries/{id}` - Get timesheet by ID

#### Read-Only Resources
- **GET** `/api/merge/hris/companies` - List companies
- **GET** `/api/merge/hris/groups` - List groups
- **GET** `/api/merge/hris/locations` - List locations

#### Universal Operations
- **POST** `/api/merge/hris/delete-account` - Delete linked account
- **POST** `/api/merge/hris/passthrough` - Vendor-specific operations

## CRM Capabilities Discovery & Meta-Driven Writes

### Why This Covers ALL CRMs

Your **one** set of endpoints now works across *all* the CRMs on Merge's Supported Fields page:

- **Unified API**: Merge exposes **one** CRM API for accounts, contacts, leads, opportunities, tasks, users, notes, engagements, etc.
- **Meta-Driven**: Every write first calls `/meta` to learn **which fields are writable** for the specific linked account
- **Smart Validation**: POST/PATCH only includes fields that a given CRM actually supports
- **Allowlist Control**: Restrict to specific integrations via `MERGE_CRM_ALLOWED_SLUGS`
- **Passthrough Escape**: For anything not unified (esp. **DELETE**), call vendor APIs directly

### How It Works

1. **Discover Capabilities**: Call `/api/merge/crm/capabilities` to see what's linked
2. **Check Integrations**: Call `/api/merge/crm/integrations` to see available vendors
3. **Validate Allowlist**: Call `/api/merge/crm/allowlist/status` to check vendor resolution
4. **Get Meta**: Before writing, call `/api/merge/crm/meta/{model}/post` or `/meta/{model}/{id}/patch`
5. **Validate & Write**: Send only supported fields, get helpful errors for invalid values
6. **Passthrough**: For deletes or vendor-specific actions, use `/api/merge/crm/passthrough`

### Allowlist Management

The system automatically resolves vendor names to Merge slugs and enforces the allowlist:

#### Setting Your Allowlist

```bash
# Use the comprehensive list from your CSV
export MERGE_CRM_ALLOWED_SLUGS="accelo,activecampaign,affinity,capsule,close,teamwork_crm,vtiger,zendesk_sell,zoho_crm"
```

#### Checking Allowlist Status

```bash
# See validation results and resolved slugs
curl "http://localhost:5001/api/merge/crm/allowlist/status"

# Response includes:
# - total_vendors: count of vendors in your allowlist
# - resolved_slugs: count of successfully resolved slugs
# - unresolved_names: list of vendors that couldn't be resolved
# - valid_slugs: list of resolved slugs for enforcement
# - name_to_slug_mapping: complete mapping of names to slugs
```

#### Automatic Slug Resolution

The system automatically:
- Normalizes vendor names (removes spaces, special chars, lowercase)
- Matches against Merge's Integration Metadata API
- Provides detailed feedback on resolved vs. unresolved vendors
- Enforces the resolved slugs at linked account creation

#### Troubleshooting Unresolved Vendors

If you get unresolved vendors:

1. **Check the status**: `/api/merge/crm/allowlist/status`
2. **Compare with available**: `/api/merge/crm/integrations`
3. **Manual correction**: Update your allowlist with exact slugs
4. **Auto-resolution**: The system will re-validate on next check

### Environment Setup

```bash
# Required for all operations
export MERGE_PROD_KEY="your_production_access_key"
export MERGE_ACCOUNT_TOKEN="your_linked_account_token"

# CRM Allowlist - restrict to specific integrations
export MERGE_CRM_ALLOWED_SLUGS="accelo,activecampaign,affinity,capsule,close,teamwork_crm,vtiger,zendesk_sell,zoho_crm"
```

**💡 Pro Tip**: The system automatically resolves vendor names to Merge slugs. If you get unresolved vendors, check `/api/merge/crm/allowlist/status` for details.

### Example Workflow

```bash
# 1. See what integrations are available
curl "http://localhost:5001/api/merge/crm/integrations"

# 2. Check what's currently linked
curl "http://localhost:5001/api/merge/crm/capabilities"

# 3. Get writable fields for contacts
curl "http://localhost:5001/api/merge/crm/meta/contacts/post?account_token=YOUR_TOKEN"

# 4. Create contact using only supported fields
curl -X POST "http://localhost:5001/api/merge/clients/1/crm/contacts" \
  -H "Content-Type: application/json" \
  -d '{
    "account_token": "YOUR_TOKEN",
    "contact": {
      "first_name": "Ada",
      "last_name": "Lovelace",
      "email_addresses": [{"email_address": "ada@example.com"}]
    }
  }'
```

### Supported CRM Models

- **Accounts**: `GET`, `POST`, `GET{id}`, `PATCH{id}`
- **Contacts**: `GET`, `POST`, `GET{id}`, `PATCH{id}`, `IGNORE`
- **Leads**: `GET`, `POST`, `GET{id}`
- **Opportunities**: `GET`, `POST`, `GET{id}`, `PATCH{id}`
- **Tasks**: `GET`, `POST`, `GET{id}`, `PATCH{id}`
- **Notes**: `GET`, `POST`, `GET{id}`
- **Engagements**: `GET`, `POST`, `GET{id}`, `PATCH{id}`
- **Users**: `GET`, `GET{id}`, `IGNORE`

### Handling "Delete" Operations

Since unified delete isn't exposed for most models:

1. **Ignore**: Use `POST /{model}/ignore/{id}` to stop syncing that record
2. **Passthrough**: Use `POST /passthrough` with `DELETE` to the provider's native endpoint

```bash
# Example: delete a contact via passthrough
curl -X POST "http://localhost:5001/api/merge/crm/passthrough" \
  -H "Content-Type: application/json" \
  -d '{
    "method": "DELETE",
    "path": "/crm/v3/objects/contacts/12345",
    "request_format": "JSON"
  }'
```

## Legacy API Endpoints

### CRM Integration

**Query Parameters:**
- `account_token` (optional): Use specific account token
- `employment_status`: Filter by employment status
- `department`: Filter by department
- `page_size`: Number of results per page

#### 9. Get Employee Details
**GET** `/api/merge/hris/clients/{client_id}/employees/{employee_id}`

Gets detailed information about a specific employee.

#### 10. List Employments
**GET** `/api/merge/hris/clients/{client_id}/employments`

Lists employment records from the linked HRIS account.

#### 11. List Locations
**GET** `/api/merge/hris/clients/{client_id}/locations`

Lists location records from the linked HRIS account.

#### 12. List Groups
**GET** `/api/merge/hris/clients/{client_id}/groups`

Lists group records from the linked HRIS account.

#### 13. Time Off Operations
**GET** `/api/merge/hris/clients/{client_id}/time-off`

Lists time off records from the linked HRIS account.

**POST** `/api/merge/hris/clients/{client_id}/time-off`

Creates a new time off request.

**Request Body:**
```json
{
  "model": {
    "employee": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "request_type": "VACATION",
    "units": "DAYS",
    "amount": 1,
    "start_time": "2025-08-20T09:00:00Z",
    "end_time": "2025-08-20T17:00:00Z"
  }
}
```

#### 14. Timesheet Entries
**GET** `/api/merge/hris/clients/{client_id}/timesheet-entries`

Lists timesheet entries from the linked HRIS account.

**POST** `/api/merge/hris/clients/{client_id}/timesheet-entries`

Creates a new timesheet entry.

**Request Body:**
```json
{
  "model": {
    "employee": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "hours_worked": 8,
    "start_time": "2025-08-13T09:00:00Z",
    "end_time": "2025-08-13T17:00:00Z"
  }
}
```

#### 15. Passthrough Operations
**POST** `/api/merge/hris/clients/{client_id}/passthrough`

Uses Merge's passthrough functionality for vendor-specific operations not covered by unified endpoints.

**Request Body:**
```json
{
  "method": "PATCH",
  "path": "/employees/123",
  "data": {"first_name": "Jane"},
  "request_format": "JSON",
  "run_async": false
}
```

**Use cases:**
- Update employee information (PATCH)
- Delete records (DELETE)
- Vendor-specific endpoints
- Custom operations

## Workflow

### Step 1: Initialize Integration
1. Client calls `/link-token` with their email and org details
2. Your app receives a `magic_link_url`
3. Client opens the magic link in their browser

### Step 2: Complete Link
1. Client authenticates with their CRM (HubSpot, Salesforce, etc.)
2. Merge captures the connection and generates an `account_token`
3. Your app receives the `account_token` (via webhook or manual input)

**Webhook Integration (Recommended):**
- Configure webhook URL in Merge Dashboard: `https://yourapp.com/api/merge/webhook`
- Merge automatically sends webhooks for linked account events
- Your app verifies webhook signature and updates records automatically
- No manual intervention required for account token capture

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
# 5. Get the account_token from Merge dashboard (or via webhook)
# 6. Save the linked account (or let webhook handle it automatically)
# 7. Test listing/creating contacts

# Webhook Testing (Optional):
# 8. Test webhook signature verification
curl -X POST http://localhost:5001/api/merge/webhook \
  -H 'X-Merge-Webhook-Signature: test_signature' \
  -d '{"test": "data"}'

# 9. Check webhook debug info
curl http://localhost:5001/api/merge/webhook/debug

# HRIS Testing Examples:
# 10. List employees
curl "http://localhost:5001/api/merge/hris/clients/1/employees?page_size=25"

# 11. Create time off request
curl -X POST "http://localhost:5001/api/merge/hris/clients/1/time-off" \
  -H 'Content-Type: application/json' \
  -d '{
    "model": {
      "employee": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
      "request_type": "VACATION",
      "units": "DAYS",
      "amount": 1,
      "start_time": "2025-08-20T09:00:00Z",
      "end_time": "2025-08-20T17:00:00Z"
    }
  }'

# 12. Create timesheet entry
curl -X POST "http://localhost:5001/api/merge/hris/clients/1/timesheet-entries" \
  -H 'Content-Type: application/json' \
  -d '{
    "model": {
      "employee": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
      "hours_worked": 8,
      "start_time": "2025-08-13T09:00:00Z",
      "end_time": "2025-08-13T17:00:00Z"
    }
  }'

# 13. Passthrough example (PATCH employee)
curl -X POST "http://localhost:5001/api/merge/hris/clients/1/passthrough" \
  -H 'Content-Type: application/json' \
  -d '{
    "method": "PATCH",
    "path": "/employees/123",
    "data": {"first_name": "Jane"},
    "request_format": "JSON"
  }'

### Test Scripts
Run the included test scripts:
```bash
# Test legacy CRM integration
python test_merge_integration.py

# Test legacy HRIS integration
python test_merge_hris_integration.py

# Test new unified API (Recommended)
python test_merge_unified_api.py
```

## How to Handle "Delete" Operations

Since Merge's unified API doesn't expose DELETE operations for most models, use these alternatives:

### 1. **Ignore Endpoints** (Soft Delete)
```bash
# Ignore a contact (stops syncing)
POST /api/merge/crm/contacts/ignore/{model_id}

# Ignore an employee
POST /api/merge/hris/employees/ignore/{model_id}
```

### 2. **Passthrough** (Hard Delete)
```bash
# Delete a contact via vendor API
POST /api/merge/crm/passthrough
{
  "method": "DELETE",
  "path": "/crm/v3/objects/contacts/12345",
  "request_format": "JSON"
}

# Delete an employee via vendor API
POST /api/merge/hris/passthrough
{
  "method": "DELETE",
  "path": "/employees/12345",
  "request_format": "JSON"
}
```

### 3. **Delete Linked Account**
```bash
# Unlink an integration completely
POST /api/merge/crm/delete-account
POST /api/merge/hris/delete-account
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