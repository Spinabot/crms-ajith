# Leads Management API

A RESTful API service for managing leads in a CRM system.

The Leads Management API is a RESTful API built with Flask and SQLAlchemy for managing leads in a CRM system. It provides endpoints for creating, retrieving, updating, and deleting leads, along with Swagger documentation for easy testing and integration.

--> Features

- Create Lead: Add new leads to the system.
- List Leads: Retrieve a list of leads with optional filtering.
- Update Lead: Modify existing lead information.
- Delete Lead: Remove leads from the system.
- API Key Authentication: Secure access to the API using an API key.

--> Technologies Used

- Flask: A lightweight WSGI web application framework.
- Flask-SQLAlchemy: An extension for Flask that adds support for SQLAlchemy.
- Flask-Migrate: An extension that handles SQLAlchemy database migrations for Flask applications.
- Flask-RESTx: An extension for building REST APIs in Flask.
- PostgreSQL: A powerful, open-source object-relational database system.
- Python Dotenv: A module to load environment variables from a `.env` file.

--> Getting Started

--> Prerequisites

- Python 3.6 or higher
- PostgreSQL database
- pip (Python package installer)

--> Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/FutureRemodelAI/BuilderPrimeCRM.git

   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   - Copy `.env.example` to `.env`
   - Update the values in `.env` with your configuration:
     ```plaintext
     # Application Settings
     FLASK_APP=run.py
     FLASK_ENV=development
     FLASK_HOST=127.0.0.1
     FLASK_PORT=5000

     # Database Settings
     DB_USER=your_db_user
     DB_PASSWORD=your_db_password
     DB_HOST=localhost
     DB_NAME=leads_db

     # Security Settings
     SECRET_KEY=your-secret-key
     API_KEY=your-api-key
     ```

5. Initialize the database:
   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

--> Running the Application

To start the application, run:

## API Endpoints

### Create Lead
- **URL**: `/api/clients/v1`
- **Method**: POST
- **Headers**: 
  - `Content-Type: application/json`
  - `x-api-key: your-api-key`
- **Body**:
  ```json
  ```

### Get Leads
- **URL**: `/api/clients`
- **Method**: GET
- **Headers**: 
  - `x-api-key: your-api-key`
- **Query Parameters**:
  - `page`: Page number (default: 1)
  - `per_page`: Items per page (default: 10)
  - `lead-status`: Filter by lead status
  - `lead-source`: Filter by lead source
  - `phone`: Filter by phone number

### Update Lead
- **URL**: `/api/clients/v1/{lead_id}`
- **Method**: PUT
- **Headers**: 
  - `Content-Type: application/json`
  - `x-api-key: your-api-key`

### Delete Lead
- **URL**: `/api/clients/v1/{lead_id}`
- **Method**: DELETE
- **Headers**: 
  - `x-api-key: your-api-key`

## Development

1. Start the development server:
   ```bash
   python run.py
   ```

2. Access the Swagger documentation:
   ```
   http://localhost:5000/swagger
   ```

--> API Endpoints

- POST /api/clients/v1: Create a new lead
- GET /api/clients: Retrieve a list of leads
- PUT /api/clients/v1/{lead_id}: Update an existing lead
- DELETE /api/clients/v1/{lead_id}: Delete a lead

--> Authentication
  API access requires authentication using an API key.
  The API key must be included in the request headers for Flask API routes.

  ```
  x-api-key: your-api-key
  ```


