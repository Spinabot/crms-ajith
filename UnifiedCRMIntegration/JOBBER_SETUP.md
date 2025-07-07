# Jobber CRM Authentication Setup Guide

This guide explains how to set up and use the Jobber CRM authentication integration in the Unified CRM Integration system.

## Prerequisites

1. **Jobber Developer Account**: You need a Jobber developer account to create OAuth applications
2. **PostgreSQL Database**: The system uses PostgreSQL to store authentication tokens
3. **Redis** (Optional): Used for rate limiting, but the system will work without it

## Setup Steps

### 1. Create Jobber OAuth Application

1. Go to the [Jobber Developer Portal](https://developer.getjobber.com/)
2. Create a new OAuth application
3. Set the redirect URI to: `http://localhost:5000/auth/jobber/callback` (for development)
4. Note down your `Client ID` and `Client Secret`

### 2. Environment Configuration

Add the following environment variables to your `.env` file:

```env
# Jobber CRM Configuration
JOBBER_CLIENT_ID=your_jobber_client_id
JOBBER_CLIENT_SECRET=your_jobber_client_secret
JOBBER_REDIRECT_URI=http://localhost:5000/auth/jobber/callback
JOBBER_API_URL=https://api.getjobber.com/api/graphql
JOBBER_TOKENS_URL=https://api.getjobber.com/api/oauth/token

# Database Configuration
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_NAME=unified_crm_db
DB_PORT=5432

# Redis Configuration (Optional)
REDIS_HOST=localhost
REDIS_PORT=6379
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Initialize Database

Run the migration to create the JobberAuth table:

```bash
python migrations/add_jobber_auth_table.py
```

### 5. Test the Integration

Run the test script to verify everything is working:

```bash
python test_jobber_auth.py
```

## Usage

### OAuth Flow

1. **Start Authorization**: Call the authorize endpoint with a user ID

   ```bash
   curl -X GET "http://localhost:5000/auth/jobber/authorize?userid=123"
   ```

2. **User Authorization**: The user will be redirected to Jobber to authorize the application

3. **Callback Processing**: Jobber will redirect back to your callback URL with an authorization code

4. **Token Storage**: The system automatically exchanges the code for access and refresh tokens and stores them

### Check Authentication Status

```bash
curl -X GET "http://localhost:5000/auth/jobber/status/123"
```

Response:

```json
{
  "status": "authenticated",
  "hasValidToken": true,
  "createdAt": "2024-01-01T12:00:00",
  "updatedAt": "2024-01-01T12:00:00"
}
```

### Refresh Expired Tokens

```bash
curl -X GET "http://localhost:5000/auth/jobber/refresh/123"
```

## API Endpoints

| Endpoint                         | Method | Description           |
| -------------------------------- | ------ | --------------------- |
| `/auth/jobber/authorize`         | GET    | Start OAuth flow      |
| `/auth/jobber/callback`          | GET    | Handle OAuth callback |
| `/auth/jobber/status/{user_id}`  | GET    | Check auth status     |
| `/auth/jobber/refresh/{user_id}` | GET    | Refresh access token  |

## Database Schema

The `jobber_auth` table stores:

- `user_id`: Unique identifier for the user
- `access_token`: OAuth access token
- `refresh_token`: OAuth refresh token
- `expiration_time`: Token expiration timestamp
- `created_at`: Record creation timestamp
- `updated_at`: Record update timestamp

## Error Handling

The system handles various error scenarios:

- **Missing Configuration**: Validates required environment variables
- **Invalid User ID**: Validates user ID format
- **OAuth Errors**: Handles Jobber API errors (400, 401, 403, 500)
- **Database Errors**: Handles database connection and transaction errors
- **Rate Limiting**: Implements rate limiting using Redis (if available)

## Security Considerations

1. **Token Storage**: Access tokens are stored encrypted in the database
2. **Rate Limiting**: API endpoints are rate-limited to prevent abuse
3. **Input Validation**: All user inputs are validated
4. **Error Logging**: Errors are logged for debugging but don't expose sensitive information

## Troubleshooting

### Common Issues

1. **"Missing code or state in callback"**

   - Check that the redirect URI matches exactly what's configured in Jobber
   - Ensure the OAuth flow is completed properly

2. **"Unauthorized – invalid credentials"**

   - Verify your Client ID and Client Secret are correct
   - Check that your Jobber application is properly configured

3. **"Database connection error"**

   - Verify PostgreSQL is running and accessible
   - Check database credentials in environment variables

4. **"Rate limit exceeded"**
   - Wait before making additional requests
   - Check Redis configuration if using rate limiting

### Debug Mode

Enable debug mode by setting:

```env
FLASK_DEBUG=1
```

This will provide more detailed error messages and logging.

## Next Steps

Once authentication is working, you can proceed to implement:

1. **Lead Management**: Create, read, update, delete leads in Jobber
2. **Data Synchronization**: Sync leads between Jobber and other CRM systems
3. **Webhook Integration**: Handle real-time updates from Jobber
4. **Advanced Features**: Custom fields, attachments, etc.

## Support

For issues and questions:

1. Check the logs for error messages
2. Run the test script to verify configuration
3. Review the Jobber API documentation
4. Open an issue in the repository
