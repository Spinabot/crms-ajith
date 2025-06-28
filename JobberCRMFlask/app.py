from flask import Flask, jsonify
import os
import logging
from dotenv import load_dotenv
from flasgger import Swagger, swag_from

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Swagger configuration
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec_1',
            "route": '/apispec_1.json',
            "rule_filter": lambda rule: True,  # all in
            "model_filter": lambda tag: True,  # all in
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/"
}

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Jobber CRM Integration API",
        "description": "Flask API for integrating with Jobber CRM system. Provides OAuth authentication, client management, and data retrieval capabilities.",
        "contact": {
            "name": "API Support",
            "email": "support@example.com"
        },
        "version": "1.0.0"
    },
    "host": "localhost:5000",
    "basePath": "/",
    "schemes": [
        "http",
        "https"
    ],
    "consumes": [
        "application/json"
    ],
    "produces": [
        "application/json"
    ],
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT Authorization header using the Bearer scheme. Example: \"Bearer {token}\""
        }
    },
    "security": [
        {
            "Bearer": []
        }
    ]
}

swagger = Swagger(app, config=swagger_config, template=swagger_template)

# Import and register auth blueprint from the new auth folder
from auth.routes import auth_bp
app.register_blueprint(auth_bp)

# Import and register client blueprint
from client.routes import client_bp
app.register_blueprint(client_bp)

# Import and register data blueprint
from data.routes import data_bp
app.register_blueprint(data_bp)

# Import config and validate required settings
from config import Config

# Validate required configuration
if not Config.Remodel_ID or not Config.Remodel_SECRET:
    raise RuntimeError("Remodel_ID and Remodel_SECRET must be set in the environment")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)