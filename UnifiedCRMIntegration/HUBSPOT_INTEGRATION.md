# HubSpot CRM Integration

This document describes the HubSpot CRM integration for the Unified CRM Integration system.

## Overview

The HubSpot integration allows you to:

- Create leads in HubSpot CRM
- Retrieve and list leads from HubSpot
- Update existing leads
- Delete leads (archived in HubSpot)
- Sync all leads from HubSpot to the unified database

## Configuration

### Environment Variables

Add the following environment variables to your `.env` file:

```env
# HubSpot CRM Configuration
HUBSPOT_API_TOKEN=your_hubspot_api_token
HUBSPOT_API_BASE_URL=https://api.hubapi.com
```

### Getting HubSpot API Token

1. Log in to your HubSpot account
2. Go to Settings → Account Setup → Integrations → API Keys
3. Create a new API key or use an existing one
4. Copy the API key to your environment variables

## API Endpoints

### Base URL

All HubSpot endpoints are prefixed with `/api/hubspot`

### 1. Create Lead

**POST** `/api/hubspot/leads`

Creates a new lead in HubSpot CRM and stores it in the unified database.

**Request Body:**

```json
{
  "firstName": "John",
  "lastName": "Doe",
  "email": "john.doe@example.com",
  "mobilePhone": "+18005554444",
  "homePhone": "+18005554445",
  "officePhone": "+18005554446",
  "addressLine1": "123 Main Street",
  "addressLine2": "Suite 100",
  "city": "Los Angeles",
  "state": "CA",
  "zip": "90210",
  "country": "USA",
  "companyName": "Acme Corp",
  "title": "Manager",
  "leadStatus": "Lead Received",
  "leadSource": "Website"
}
```

**Valid Lead Status Values:**

- `Lead Received` → maps to `lead`
- `Qualified` → maps to `marketingqualifiedlead`
- `Sales Qualified` → maps to `salesqualifiedlead`
- `Opportunity` → maps to `opportunity`
- `Customer` → maps to `customer`
- `Subscriber` → maps to `subscriber`
- `Evangelist` → maps to `evangelist`
- `Other` → maps to `other`

**Note:** The `notes` field is not supported in HubSpot by default. You can create a custom property in HubSpot for notes if needed.

**Response (201):**

```json
{
  "id": "12345",
  "firstName": "John",
  "lastName": "Doe",
  "email": "john.doe@example.com",
  "mobilePhone": "+18005554444",
  "homePhone": "+18005554445",
  "officePhone": "+18005554446",
  "addressLine1": "123 Main Street",
  "addressLine2": "Suite 100",
  "city": "Los Angeles",
  "state": "CA",
  "zip": "90210",
  "country": "USA",
  "companyName": "Acme Corp",
  "title": "Manager",
  "leadStatus": "Lead Received",
  "leadSource": "Website",
  "createdAt": "2024-01-15T10:30:00Z",
  "updatedAt": "2024-01-15T10:30:00Z",
  "archived": false
}
```

### 2. List Leads

**GET** `/api/hubspot/leads`

Retrieves leads from HubSpot with pagination and filtering.

**Query Parameters:**

- `page` (int, default: 1): Page number
- `per_page` (int, default: 10, max: 100): Items per page
- `last_modified_since` (string): Filter by last modified date
- `lead_status` (string): Filter by lead status
- `lead_source` (string): Filter by lead source

**Response (200):**

```json
{
  "leads": [
    {
      "id": "12345",
      "firstName": "John",
      "lastName": "Doe",
      "email": "john.doe@example.com"
      // ... other lead fields
    }
  ],
  "total": 150,
  "pages": 15,
  "current_page": 1,
  "per_page": 10
}
```

### 3. Get Lead

**GET** `/api/hubspot/leads/{external_id}`

Retrieves a specific lead by its HubSpot external ID.

**Response (200):**

```json
{
  "id": 1,
  "firstName": "John",
  "lastName": "Doe",
  "email": "john.doe@example.com",
  // ... other lead fields
  "crmSystem": "hubspot",
  "crmExternalId": "12345",
  "createdAt": "2024-01-15T10:30:00Z",
  "updatedAt": "2024-01-15T10:30:00Z"
}
```

### 4. Update Lead

**PUT** `/api/hubspot/leads/{external_id}`

Updates an existing lead in HubSpot CRM.

**Request Body:**

```json
{
  "title": "Senior Manager",
  "leadStatus": "Qualified"
}
```

**Response (200):**

```json
{
  "id": "12345",
  "firstName": "John",
  "lastName": "Doe",
  "email": "john.doe@example.com",
  "title": "Senior Manager",
  "leadStatus": "Qualified",
  // ... other lead fields
  "updatedAt": "2024-01-15T11:30:00Z"
}
```

### 5. Delete Lead

**DELETE** `/api/hubspot/leads/{external_id}`

Archives a lead in HubSpot (HubSpot doesn't allow permanent deletion) and removes it from the unified database.

**Response (204):** No content

### 6. Sync Leads

**POST** `/api/hubspot/leads/sync`

Synchronizes all leads from HubSpot to the unified database.

**Response (200):**

```json
{
  "message": "Successfully synced 150 leads from HubSpot",
  "synced_count": 150,
  "total_count": 150
}
```

## Data Mapping

### HubSpot to Unified Lead Mapping

| HubSpot Property | Unified Lead Field | Notes                                            |
| ---------------- | ------------------ | ------------------------------------------------ |
| `firstname`      | `firstName`        | First name                                       |
| `lastname`       | `lastName`         | Last name                                        |
| `email`          | `email`            | Email address                                    |
| `phone`          | `mobilePhone`      | Phone number (HubSpot doesn't distinguish types) |
| `address`        | `addressLine1`     | Full address string                              |
| `city`           | `city`             | City                                             |
| `state`          | `state`            | State                                            |
| `zip`            | `zip`              | ZIP code                                         |
| `country`        | `country`          | Country                                          |
| `company`        | `companyName`      | Company name                                     |
| `jobtitle`       | `title`            | Job title                                        |
| `lifecyclestage` | `leadStatus`       | Lifecycle stage                                  |
| `hs_lead_status` | `leadSource`       | Lead status                                      |

### Unified Lead to HubSpot Mapping

| Unified Lead Field              | HubSpot Property | Notes            |
| ------------------------------- | ---------------- | ---------------- |
| `firstName`                     | `firstname`      | First name       |
| `lastName`                      | `lastname`       | Last name        |
| `email`                         | `email`          | Email address    |
| `mobilePhone`                   | `phone`          | Phone number     |
| `companyName`                   | `company`        | Company name     |
| `title`                         | `jobtitle`       | Job title        |
| `leadStatus`                    | `lifecyclestage` | Lifecycle stage  |
| `addressLine1` + `addressLine2` | `address`        | Combined address |
| `city`                          | `city`           | City             |
| `state`                         | `state`          | State            |
| `zip`                           | `zip`            | ZIP code         |
| `country`                       | `country`        | Country          |

### Lead Status Mapping

| Unified Lead Status | HubSpot Lifecycle Stage  |
| ------------------- | ------------------------ |
| `Lead Received`     | `lead`                   |
| `Qualified`         | `marketingqualifiedlead` |
| `Sales Qualified`   | `salesqualifiedlead`     |
| `Opportunity`       | `opportunity`            |
| `Customer`          | `customer`               |
| `Subscriber`        | `subscriber`             |
| `Evangelist`        | `evangelist`             |
| `Other`             | `other`                  |

## Error Handling

The integration handles various error scenarios:

### Common Error Responses

**400 Bad Request:**

```json
{
  "error": "Validation error",
  "message": "Email is required"
}
```

**404 Not Found:**

```json
{
  "error": "Lead not found",
  "message": "Lead with external ID 12345 not found"
}
```

**409 Conflict:**

```json
{
  "error": "Contact already exists",
  "message": "Contact with this email already exists"
}
```

**500 Internal Server Error:**

```json
{
  "error": "HubSpot API error",
  "message": "Failed to create lead: API rate limit exceeded"
}
```

## Testing

Use the provided test script to verify the integration:

```bash
python test_hubspot_integration.py
```

The test script will:

1. Create a test lead
2. Retrieve the created lead
3. Update the lead
4. List leads
5. Sync leads
6. Delete the test lead

## Limitations

1. **Phone Number Types**: HubSpot doesn't distinguish between mobile, home, and office phone numbers. All phone numbers are stored in a single field.

2. **Address Format**: HubSpot stores the full address as a single string, while the unified system separates address components.

3. **Deletion**: HubSpot doesn't allow permanent deletion of contacts. The integration archives contacts instead.

4. **Rate Limiting**: HubSpot has API rate limits that may affect bulk operations.

5. **Notes Field**: HubSpot doesn't have a default `notes` property. You can create a custom property in HubSpot for notes if needed.

6. **Lead Status**: Only specific lifecycle stage values are valid in HubSpot. The integration maps common status values to valid HubSpot lifecycle stages.

## Troubleshooting

### Common Issues

1. **Authentication Error**: Ensure your `HUBSPOT_API_TOKEN` is valid and has the necessary permissions.

2. **Rate Limiting**: If you encounter rate limit errors, implement delays between API calls.

3. **Missing Fields**: Some HubSpot properties might not be available depending on your HubSpot plan.

4. **Sync Issues**: Check the sync logs in the database for detailed error information.

5. **Invalid Lead Status**: Use only the supported lead status values listed above.

### Debug Mode

Enable debug logging by setting:

```env
FLASK_DEBUG=1
```

This will provide detailed error messages and API request/response logs.

## Support

For issues related to the HubSpot integration:

1. Check the sync logs in the database
2. Review the application logs
3. Verify your HubSpot API token and permissions
4. Test with the provided test script
