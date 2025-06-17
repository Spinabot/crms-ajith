# JobNimbus Contacts API

This is a Flask-based REST API for managing contacts using JobNimbus. It supports full CRUD operations and is backed by a PostgreSQL database. The app includes test coverage using `pytest` and is ready for deployment on platforms like Google Cloud Run.

---

## Features

- Create, Read, Update, and Delete JobNimbus contacts
- PostgreSQL database integration with SQLAlchemy
- Modular Flask project structure
- Environment-specific configuration support
- Unit tests with `pytest` and `unittest.mock`
- Blueprint-based route organization

---

## Technologies

- Python 3.12+
- Flask
- SQLAlchemy
- PostgreSQL
- Pytest
- Docker (optional for deployment)
- Google Cloud Run ready (optional)

---

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/jobnimbus-contacts-api.git
   cd jobnimbus-contacts-api
 
2. Create a virtual environment:
    python -m venv venv
    source venv/bin/activate

3. Install dependencies:
    pip install -r requirements.txt

4. Environment Configuration:
    export FLASK_ENV=development
    export DATABASE_URL=postgresql://user:password@localhost/dbname

5. Run the app:
    python run.py

## API Endpoints

| Method | Endpoint             | Description         |
|--------|----------------------|---------------------|
| GET    | /                    | Health check        |
| GET    | /contacts            | List all contacts   |
| POST   | /contacts            | Create new contact  |
| GET    | /contacts/<jnid>     | Get contact by jnid |
| PUT    | /contacts/<jnid>     | Update contact      |
| DELETE | /contacts/<jnid>     | Archive contact     |


6. Testing:
    pytest


