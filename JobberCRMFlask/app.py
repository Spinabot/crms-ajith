from flask import Flask, jsonify
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

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

@app.route('/')
def hello_world():
    """Basic hello world endpoint to test if the application is running."""
    return jsonify({"message": "Hello World"})

@app.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "message": "Flask application is running"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)