# Delete Leads in Zoho CRM API Documentation

## Endpoint
**DELETE** `/api/<int:entity_id>/leads`

---

## Description
This endpoint allows users to delete one or more leads in Zoho CRM by providing a comma-separated list of lead IDs. The request is authenticated using an OAuth token and rate-limited to prevent abuse.

---

## Rate Limiting
- **Limit**: 5 requests per minute  
- **Purpose**: To prevent abuse and ensure fair usage of the API.

---

## Parameters

| **Parameter** | **Location** | **Type**   | **Required** | **Description**                                                                 |
|---------------|--------------|------------|--------------|---------------------------------------------------------------------------------|
| `entity_id`   | Path         | `integer`  | Yes          | The ID of the entity project.                                                  |
| `ids`         | Query        | `string`   | Yes          | Comma-separated list of lead IDs to delete (e.g., `"id1,id2,id3"`).            |

---

## Headers

| **Header**          | **Value**                          | **Description**                                                                 |
|---------------------|------------------------------------|---------------------------------------------------------------------------------|
| `Authorization`     | `Zoho-oauthtoken <access_token>`  | OAuth token for authenticating the request.                                     |
| `Content-Type`      | `application/json`                | Specifies the format of the request body.                                       |

---

## Responses

| **Status Code** | **Description**                                                                 |
|------------------|---------------------------------------------------------------------------------|
| `200 OK`         | Leads deleted successfully.                                                    |
| `400 Bad Request`| No lead IDs provided or invalid input.                                         |
| `401 Unauthorized`| Unauthorized access due to missing or invalid access token.                   |
| `500 Internal Server Error`| Internal server error occurred while processing the request.         |

---

## Request Example

### URL
```http
DELETE /api/123/leads?ids=6707647000000665004,6707647000000665005

only example don't real id may be differnt.

##headers
{
  "Authorization": "Zoho-oauthtoken 1000.xxxxxxxx.xxxxxxxxx",
  "Content-Type": "application/json"
}
```

### Response Example
```json
{
  "status": "success",
  "response": {
    "data": [
      {
        "code": "SUCCESS",
        "details": {
          "id": "6707647000000665004"
        },
        "message": "record deleted",
        "status": "success"
      },
      {
        "code": "SUCCESS",
        "details": {
          "id": "6707647000000665005"
        },
        "message": "record deleted",
        "status": "success"
      }
    ]
  }
}
```

### Error Response Example
```json
error 400
{
  "error": "No lead IDs provided"
}
```
error 401
{
  "error": "No access token_data found"
}

Error 500 
{
  "error": "Failed to fetch access token_data",
  "details": "Detailed error message here"
}

Notes for Developers
Maximum IDs:

Ensure that the number of IDs provided in the ids query parameter does not exceed Zoho's API limits.
Testing:

Test the endpoint with valid and invalid inputs to ensure proper error handling and response formatting.
Logging:

Consider adding logging for debugging purposes, especially for token fetching and Zoho API interactions.