from flask import Flask ,jsonify
from flask.cli import AppGroup  # Import AppGroup for CLI commands

from database import db  # Import db from the new database module __init file
from database.insert_data_db import insert_creds
from datetime import datetime, timezone
from database import schemas 
from config import Config 
import requests
from datetime import timedelta
import json
import time 
from flasgger import Swagger  # Import Swagger

#blueprints
from routes.CRUD.clients import clients_blueprint
from routes.CRUD.update import update_blueprint
from routes.CRUD.delete import delete_blueprint
from routes.CRUD.create import create_blueprint
from routes.users.metadata import meta_blueprint
from routes.users.CRM_users import zoho_users_blueprint
from database import create_database
from routes.auth.Oauth_testing import auth_test
from routes.auth.Oauth_login import auth_blueprint
from utils.extension import limiter
 # get limiter and redis client from extension.py file
app = Flask(__name__)
# Load configuration from the Config class
app.config.from_object(Config)

# Initialize Swagger
swagger = Swagger(app)

#register the apps
app.register_blueprint(auth_test, url_prefix="/api/zoho")
app.register_blueprint(clients_blueprint, url_prefix="/api/clients")
app.register_blueprint(update_blueprint, url_prefix="/api/clients")
app.register_blueprint(delete_blueprint,url_prefix ="/api/clients")
app.register_blueprint(create_blueprint,url_prefix = "/api/clients")
app.register_blueprint(meta_blueprint,url_prefix="/api/clients")
app.register_blueprint(zoho_users_blueprint,url_prefix="/api/zoho")
app.register_blueprint(auth_blueprint,url_prefix="/zoho/authorize")


# Initialize db with app
db.init_app(app)

# Define a CLI group for database commands
db_cli = AppGroup("db")
@db_cli.command("init")
def init_db():
    """Initialize the database."""
    create_database.create_database_if_not_exists(
        Config.database_name,
        Config.database_user,
        Config.database_pass,
        Config.database_host
    )
    with app.app_context():
        schemas.create_tables()  # Create tables if needed
        print("Database initialized successfully!")

# Register the CLI group with the app
app.cli.add_command(db_cli)



# Initialize rate limiter
limiter.init_app(app)
@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({
        "error": "Rate limit exceeded",
        "message": "Please try again in a while.",
        "retry_after": "1 minute"
    }), 429



if __name__ == "__main__":
    app.run(port=5000, debug=False)