# 🔑 Jobber CRM OAuth Setup Guide

## 📋 Prerequisites

1. **Jobber Developer Account**: You need access to the Jobber Developer Portal
2. **Flask Application**: Your Flask app should be running on port 5001
3. **Database**: SQLite database with `jobber_tokens` table

## 🚀 Quick Start

### Step 1: Access the OAuth Test Page

Open your browser and go to:
```
http://127.0.0.1:5001/api/jobber/auth/test
```

This page provides:
- ✅ Current authentication status
- 🔐 OAuth authorization button
- 🔄 Status checking
- 🧪 Endpoint testing
- 📚 Complete setup guide

### Step 2: Start OAuth Flow

1. Click **"🔐 Start OAuth Authorization"**
2. You'll be redirected to Jobber's authorization page
3. Log in with your Jobber credentials
4. Authorize the application
5. You'll be redirected back with an access token

### Step 3: Verify Authentication

1. Click **"🔄 Check Status"** to verify your token
2. Click **"🧪 Test Endpoints"** to test the API

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in your project root:

```bash
# Jobber OAuth Credentials
JOBBER_CLIENT_ID=your_actual_client_id
JOBBER_CLIENT_SECRET=your_actual_client_secret

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=1
FLASK_HOST=0.0.0.0
FLASK_PORT=5001

# OAuth Redirect URI
JOBBER_REDIRECT_URI=http://localhost:5001/api/jobber/callback
```

### Jobber App Configuration

In your Jobber Developer Portal:

1. **Redirect URI**: Set to `http://localhost:5001/api/jobber/callback`
2. **Scopes**: Enable `read` and `write` permissions
3. **Client ID & Secret**: Copy these to your `.env` file

## 🔧 Available Endpoints

### OAuth Endpoints
- `GET /api/jobber/auth` - Start OAuth authorization
- `GET /api/jobber/callback` - OAuth callback handler
- `GET /api/jobber/auth/status` - Check authentication status
- `GET /api/jobber/auth/test` - OAuth test page

### Token Management
- `GET /api/jobber/token/debug` - Debug token information
- `POST /api/jobber/token/refresh` - Refresh access token
- `POST /api/jobber/token/insert` - Manually insert token (testing)

### CRM Operations
- `GET /api/jobber/clients` - Get all clients
- `POST /api/jobber/clients` - Create new client
- `GET /api/jobber/clients/<id>` - Get specific client
- `PUT /api/jobber/clients/<id>` - Update client
- `DELETE /api/jobber/clients/<id>` - Delete client

## 🧪 Testing

### Test OAuth Flow
```bash
# 1. Check current status
curl http://127.0.0.1:5001/api/jobber/auth/status

# 2. Start OAuth (will redirect to browser)
curl -L http://127.0.0.1:5001/api/jobber/auth

# 3. Check status again
curl http://127.0.0.1:5001/api/jobber/auth/status

# 4. Test endpoints
curl http://127.0.0.1:5001/api/jobber/clients
```

### Manual Token Insertion (for testing)
```bash
curl -X POST http://127.0.0.1:5001/api/jobber/token/insert \
  -H "Content-Type: application/json" \
  -d '{
    "access_token": "your_access_token_here",
    "refresh_token": "your_refresh_token_here",
    "expires_in": 3600
  }'
```

## 🔍 Troubleshooting

### Common Issues

1. **"No Jobber token found"**
   - Solution: Complete the OAuth flow first
   - Visit: `/api/jobber/auth/test`

2. **"Invalid redirect URI"**
   - Check: Redirect URI in Jobber Developer Portal
   - Must match: `http://localhost:5001/api/jobber/callback`

3. **"Client ID/Secret invalid"**
   - Verify: `.env` file has correct credentials
   - Check: Jobber Developer Portal settings

4. **"Token expired"**
   - Solution: Use refresh token endpoint
   - Or: Re-authenticate via OAuth

### Debug Information

Check the logs:
```bash
tail -f jobber.log
```

Check token status:
```bash
curl http://127.0.0.1:5001/api/jobber/token/debug
```

## 📚 Jobber API Documentation

- **OAuth Guide**: https://developer.getjobber.com/docs/building_your_app/app_authorization/
- **GraphQL API**: https://developer.getjobber.com/docs/api/graphql/
- **Scopes**: `read`, `write`, `admin`

## 🔒 Security Notes

- ✅ State parameter validation prevents CSRF attacks
- ✅ Secure random state generation
- ✅ Automatic token refresh
- ✅ Secure token storage in database
- ⚠️ Development server only - use production WSGI in production
- ⚠️ Store sensitive credentials in environment variables

## 🎯 Next Steps

After successful OAuth setup:

1. **Test all endpoints** using the test page
2. **Implement error handling** for production use
3. **Add rate limiting** for API calls
4. **Set up monitoring** for token expiration
5. **Implement webhook handling** if needed

---

## 🆘 Need Help?

If you encounter issues:

1. Check the **OAuth test page**: `/api/jobber/auth/test`
2. Review the **application logs**: `jobber.log`
3. Verify **Jobber Developer Portal** settings
4. Test with **curl commands** above
5. Check **token debug endpoint**: `/api/jobber/token/debug` 