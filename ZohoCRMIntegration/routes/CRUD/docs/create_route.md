#### POST `/api/<entity_id>/leads`

Creates leads in Zoho CRM for a given entity.

---

#### **Method**

`POST`

---

#### **Path Parameters**

| Name        | Type    | Required | Description                    |
| ----------- | ------- | -------- | ------------------------------ |
| `entity_id` | Integer | Yes      | ID used to fetch access token. |

---

#### **Request Body**

```json
{
  "layout_id": "optional_layout_id",
  "data": [
    {
      "First_Name": "BILL",
      "Last_Name": "Gates",
      "Company": "Tech Innovators",
      "Email": "Bill.gates@example.com",
      "Phone": "555-555-7777",
      "Website": "http://www.techinnovators.com",
      ...
    }
  ]
}
```

> Required fields per lead: `First_Name`, `Last_Name`, `Company`, `Email`, `Phone`.

---

#### **Rate Limiting**

* 5 requests per minute per client.

---

#### **Authentication**

* Uses Zoho OAuth token fetched via `entity_id`.

---

#### **Responses**

| Status  | Description                            |
| ------- | -------------------------------------- |
| 200/201 | Lead(s) created successfully           |
| 400     | Missing or invalid fields or JSON body |
| 401     | Invalid or missing access token        |
| 502     | Zoho API or response issue             |
| 500     | Internal server error                  |

---

#### **Logic Summary**

1. Validate JSON body.
2. Ensure all required fields in each lead.
3. Fetch access token using `entity_id`.
4. Clean and format data (add layout if present).
5. Send to Zoho API.
6. On success, store audit log and return response.

---

