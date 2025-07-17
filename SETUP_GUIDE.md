# Setup Guide for Unified CRM Integration

## Step 1: Update Your .env File

Your current `.env` file needs to be updated to include the BuilderPrime API key. Update your `.env` file to include:

```env
# Application Settings
FLASK_APP=run.py
FLASK_ENV=development
FLASK_HOST=127.0.0.1
FLASK_PORT=5000
FLASK_DEBUG=1

# Database Settings
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_NAME=leads_db
DB_PORT=5432

# Security Settings
SECRET_KEY=your-secret-key
API_KEY=oHLGPWR.T3SLCKltfQ2VI3ocGJTY

# BuilderPrime CRM Configuration
BUILDER_PRIME_API_KEY=your-builder-prime-api-key
```

## Step 2: Create the Database

The error you're seeing is because the database "leads_db" doesn't exist yet. Run this command to create it:

```bash
python setup_database.py
```

This script will:

- Connect to your PostgreSQL server
- Create the "leads_db" database if it doesn't exist
- Provide feedback on the process

## Step 3: Initialize the Database

After creating the database, run:

```bash
python init_db.py
```

This will:

- Create all the necessary tables
- Set up default CRM connections (inactive)
- Initialize the database schema

## Step 4: Configure BuilderPrime Connection

After the database is initialized, you need to configure the BuilderPrime connection. You can do this by:

1. **Option A: Using the database directly**

   ```sql
   UPDATE crm_connections
   SET api_key = 'your-builder-prime-api-key', is_active = true
   WHERE crm_system = 'builder_prime';
   ```

2. **Option B: Create a configuration script**
   Create a file called `configure_crm.py`:

   ```python
   from app import create_app, db
   from app.models import CRMConnection

   app = create_app()

   with app.app_context():
       connection = CRMConnection.query.filter_by(crm_system='builder_prime').first()
       if connection:
           connection.api_key = 'your-builder-prime-api-key'
           connection.is_active = True
           db.session.commit()
           print("BuilderPrime connection configured successfully!")
   ```

## Step 5: Test the Application

Run the application:

```bash
python run.py
```

Then visit:

- Main application: http://127.0.0.1:5000
- API documentation: http://127.0.0.1:5000/swagger

## Troubleshooting

### PostgreSQL Connection Issues

If you get connection errors:

1. **Make sure PostgreSQL is running**

   ```bash
   # On Windows
   net start postgresql-x64-15

   # On macOS/Linux
   sudo systemctl start postgresql
   ```

2. **Check your credentials**

   - Verify username and password in your `.env` file
   - Make sure the user has permission to create databases

3. **Test connection manually**
   ```bash
   psql -h localhost -U postgres -d postgres
   ```

### Database Already Exists

If you get an error saying the database already exists, that's fine - the setup script will handle it gracefully.

### Permission Issues

If you get permission errors:

1. Make sure your PostgreSQL user has the necessary privileges
2. Try connecting as the postgres superuser first
3. Grant the necessary permissions to your user

## Next Steps

Once the setup is complete:

1. **Test the BuilderPrime integration** using the Swagger documentation
2. **Add more CRM integrations** as needed
3. **Configure additional settings** like Redis for caching
4. **Set up monitoring and logging** for production use

## Support

If you encounter any issues:

1. Check the error messages carefully
2. Verify your PostgreSQL connection
3. Ensure all environment variables are set correctly
4. Check the application logs for more details
