# Jobber Client Data API Testing Guide

This guide explains how to test the Jobber client data API that we've integrated into the Unified CRM Integration system.

## 🎯 **What We've Implemented**

### **Authentication (Already Working)**

- ✅ OAuth 2.0 flow with Jobber
- ✅ Token storage and management
- ✅ Token refresh functionality
- ✅ Authentication status checking

### **Client Data Retrieval (New)**

- ✅ Raw client data from Jobber GraphQL API
- ✅ Pagination support for large datasets
- ✅ Unified lead format conversion
- ✅ Error handling and validation

## 📋 **API Endpoints**

### **1. Get Client Data (Raw Format)**

```
GET /api/jobber/clients/{user_id}
```

**Description:** Retrieves client data directly from Jobber in its original format.

**Parameters:**

- `user_id` (path): The user ID for authentication

**Response:**

```json
{
  "message": "Client data retrieved successfully",
  "count": 25,
  "data": [
    {
      "id": "client_123",
      "firstName": "John",
      "lastName": "Doe",
      "companyName": "ABC Company",
      "isLead": true,
      "emails": [{"id": "email_1", "address": "john@example.com"}],
      "phones": [{"id": "phone_1", "number": "555-123-4567"}],
      "clientProperties": {...},
      "sourceAttribution": {...}
    }
  ]
}
```

### **2. Get Leads (Unified Format)**

```
GET /api/jobber/leads?user_id={user_id}
```

**Description:** Retrieves leads from Jobber and converts them to the unified format used across all CRM systems.

**Parameters:**

- `user_id` (query): The user ID for authentication

**Response:**

```json
{
  "message": "Leads retrieved successfully",
  "count": 15,
  "leads": [
    {
      "firstName": "John",
      "lastName": "Doe",
      "email": "john@example.com",
      "mobilePhone": "555-123-4567",
      "companyName": "ABC Company",
      "city": "Anytown",
      "state": "CA",
      "zip": "12345",
      "leadSource": "Website",
      "crmSystem": "jobber",
      "crmExternalId": "client_123",
      "crmRawData": {...}
    }
  ]
}
```

## 🧪 **Testing the API**

### **Prerequisites**

1. ✅ Jobber authentication completed for user 123
2. ✅ Application running on `http://localhost:5000`
3. ✅ Database connection working

### **Step 1: Verify Authentication**

```bash
curl -X GET "http://localhost:5000/auth/jobber/status/123"
```

**Expected Response:**

```json
{
  "status": "authenticated",
  "hasValidToken": true,
  "createdAt": "2024-01-01T12:00:00",
  "updatedAt": "2024-01-01T12:00:00"
}
```

### **Step 2: Test Client Data Retrieval**

```bash
curl -X GET "http://localhost:5000/api/jobber/clients/123"
```

**Expected Response:**

```json
{
  "message": "Client data retrieved successfully",
  "count": 25,
  "data": [...]
}
```

### **Step 3: Test Leads Retrieval**

```bash
curl -X GET "http://localhost:5000/api/jobber/leads?user_id=123"
```

**Expected Response:**

```json
{
  "message": "Leads retrieved successfully",
  "count": 15,
  "leads": [...]
}
```

## 🔧 **Using the Test Script**

We've created a comprehensive test script that automates all the testing:

```bash
cd UnifiedCRMIntegration
python test_jobber_client_api.py
```

This script will:

1. ✅ Check authentication status
2. ✅ Test client data retrieval
3. ✅ Test leads retrieval (unified format)
4. ✅ Test error scenarios

## 📊 **Postman Collection**

### **Collection Setup**

1. Create a new collection: "Jobber Client API"
2. Set environment variables:
   - `base_url`: `http://localhost:5000`
   - `user_id`: `123`

### **Request 1: Get Client Data**

- **Method:** `GET`
- **URL:** `{{base_url}}/api/jobber/clients/{{user_id}}`
- **Headers:** `Accept: application/json`

### **Request 2: Get Leads**

- **Method:** `GET`
- **URL:** `{{base_url}}/api/jobber/leads?user_id={{user_id}}`
- **Headers:** `Accept: application/json`

## 🚨 **Error Scenarios**

### **1. Unauthenticated User**

```bash
curl -X GET "http://localhost:5000/api/jobber/clients/999"
```

**Expected Response:**

```json
{
  "error": "User not authenticated with Jobber. Please authorize first."
}
```

**Status:** `401 Unauthorized`

### **2. Missing User ID Parameter**

```bash
curl -X GET "http://localhost:5000/api/jobber/leads"
```

**Expected Response:**

```json
{
  "error": "user_id parameter is required"
}
```

**Status:** `400 Bad Request`

### **3. Expired Token**

If the token is expired, the API will automatically attempt to refresh it. If refresh fails:

**Expected Response:**

```json
{
  "error": "Authentication expired. Please refresh your token."
}
```

**Status:** `401 Unauthorized`

## 📈 **Performance Considerations**

### **Pagination**

- The API automatically handles pagination for large datasets
- Fetches 15 clients per page
- Includes rate limiting (3-second delay every 5 requests)

### **Rate Limiting**

- Jobber API has rate limits
- The service includes automatic delays to avoid hitting limits
- Redis-based rate limiting (optional, falls back gracefully)

### **Token Management**

- Automatic token refresh when expired
- Token validation before each request
- Secure token storage in database

## 🔍 **Debugging**

### **Check Logs**

Look for these log messages:

- `"Starting data retrieval for user {user_id}"`
- `"Making GraphQL request {count} with cursor: {cursor}"`
- `"Successfully fetched client data for user {user_id} in {count} requests"`

### **Common Issues**

1. **"No valid tokens available"**

   - Solution: Complete OAuth flow again
   - Check: `GET /auth/jobber/status/{user_id}`

2. **"GraphQL query failed"**

   - Solution: Check Jobber API status
   - Verify: API credentials are correct

3. **"Authentication expired"**
   - Solution: Refresh token manually
   - Check: `GET /auth/jobber/refresh/{user_id}`

## 🎉 **Success Indicators**

When everything is working correctly, you should see:

1. ✅ Authentication status shows `"hasValidToken": true`
2. ✅ Client data retrieval returns data with count > 0
3. ✅ Leads retrieval returns unified format data
4. ✅ No error messages in the response
5. ✅ Logs show successful GraphQL requests

## 🚀 **Next Steps**

Once the client data API is working, you can:

1. **Integrate with other CRM systems** - Compare data across platforms
2. **Build lead synchronization** - Sync leads between Jobber and other CRMs
3. **Add lead creation** - Create new leads in Jobber
4. **Implement webhooks** - Handle real-time updates from Jobber
5. **Add advanced filtering** - Filter leads by various criteria

The foundation is now complete for a full Jobber CRM integration!
