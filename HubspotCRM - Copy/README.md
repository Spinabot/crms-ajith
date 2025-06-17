# HubSpot CRM Integration API


## Features

- **Contact Management**
  - Create, read, update, and delete HubSpot contacts
  

## Prerequisites

- Python 3.8 or higher
- PostgreSQL 12+
- HubSpot Developer Account
- HubSpot API Token

## Installation

1. **Clone the repository**
   ```bash
   git clone <your-repository-url>
   cd hubspotcrm
   ```

2. **Set up virtual environment**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Linux/Mac
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   Create a `.env` file in the root directory:
   ```
   FLASK_APP=run.py
   FLASK_ENV=development
   FLASK_DEBUG=True
   DB_USER=your_db_user
   DB_PASSWORD=your_db_password
   DB_HOST=localhost
   DB_NAME=db_name
   SECRET_KEY=your-secret-key
   HUBSPOT_API_TOKEN=hubspot_api_key
   ```

5. **Set up database**
   ```bash
   # Create database
   createdb hubspot_db

   # Initialize migrations
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

## API Endpoints

### Contact Management

Operations:
- Create Contact: POST /api/contacts
- List Contacts: GET /api/contacts
- Get Contact: GET /api/contacts/{contact_id}
- Update Contact: PUT /api/contacts/{contact_id}
- Delete Contact: DELETE /api/contacts/{contact_id}
- Search Contacts: POST /api/contacts/search
- Batch Operations: POST /api/contacts/batch


## Running the Application

1. **Activate virtual environment**
   ```bash
   # Windows
   venv\Scripts\activate

   # Linux/Mac
   source venv/bin/activate
   ```
2. **Install Dependancy**
    pip install -r requirements.txt


2. **Start the application**
   ```bash
   flask run
   ```

3. **Access the API**
   - API Base URL: `http://localhost:5000`
   - Swagger Documentation: `http://localhost:5000/swagger`









