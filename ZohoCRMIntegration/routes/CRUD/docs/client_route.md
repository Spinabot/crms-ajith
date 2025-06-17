#this file has docs on what each route does. 
Perfect — keeping it clean and professional is best for dev teams. Here's a solid structure for your documentation files.

---

#### GET `/api/<entity_id>/leads`

Fetches leads from Zoho CRM for a given entity.

---

#### **Method**

`GET`

---

#### **Path Parameters**

| Name        | Type    | Required | Description                           |
| ----------- | ------- | -------- | ------------------------------------- |
| `entity_id` | Integer | Yes      | The ID used to fetch token and leads. |

---

#### **Query Parameters**

| Name        | Type   | Required | Description                           |
| ----------- | ------ | -------- | ------------------------------------- |
| `client_id` | String | No       | If provided, fetches a specific lead. |

---

#### **Rate Limiting**

* 5 requests per minute per client (IP or user).
* Implemented using `@limiter.limit("5 per minute")`.

---

#### **Authentication**

* Uses Zoho OAuth access token.
* Retrieved via `fetch_tokens(entity_id)`.

---

#### **Responses**

| Status | Description                          |
| ------ | ------------------------------------ |
| 200    | Successfully fetched leads.          |
| 401    | Unauthorized or token missing.       |
| 500    | Internal error fetching token or API |
| 502    | Invalid JSON response from Zoho.     |

---

#### **Headers Sent to Zoho**

```http
Authorization: Zoho-oauthtoken <access_token>
```

---

#### **Logic Summary**

1. Fetch access token using `entity_id`.
2. Form URL to Zoho endpoint.
3. If `client_id` present, target specific record.
4. Perform GET request to Zoho.
5. Parse and return result or error.


