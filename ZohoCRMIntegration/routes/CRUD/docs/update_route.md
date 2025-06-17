# Update Leads in Zoho CRM API Documentation

## Endpoint
**PUT** `/api/<int:entity_id>/leads`

---

## Description
This endpoint allows users to update one or more leads in Zoho CRM by providing a comma-separated list of lead IDs and the updated data in the request body. The request is authenticated using an OAuth token and rate-limited to prevent abuse.

---

## Rate Limiting
- **Limit**: 5 requests per minute  
- **Purpose**: To prevent abuse and ensure fair usage of the API.

---

## Parameters

| **Parameter** | **Location** | **Type**   | **Required** | **Description**                                                                 |
|---------------|--------------|------------|--------------|---------------------------------------------------------------------------------|
| `entity_id`   | Path         | `integer`  | Yes          | The ID of the entity project.                                                  |
| `client_id`   | Query        | `string`   | Yes          | Comma-separated list of Zoho lead IDs to be updated (e.g., `"id1,id2,id3"`).    |

---

## Headers

| **Header**          | **Value**                          | **Description**                                                                 |
|---------------------|------------------------------------|---------------------------------------------------------------------------------|
| `Authorization`     | `Zoho-oauthtoken <access_token>`  | OAuth token for authenticating the request.                                     |
| `Content-Type`      | `application/json`                | Specifies the format of the request body.                                       |

---

## Request Body

The request body should contain the updated data for the leads. Each lead's data will automatically include its corresponding ID from the `client_id` query parameter.

### Example
```json
{
  "data": [
    {
      "Annual_Revenue": 1600000,
      "City": "Los Angeles Updated",
      "Company": "Innovatech Solutions Updated",
      "Email": "elon.musk.updated@example.com",
      "First_Name": "Elon Dusk",
      "Last_Name": "Musk Updated",
      "Phone": "555-555-9998",
      "Lead_Status": "Contacted"
    }
  ]
}