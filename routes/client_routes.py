from flask import Blueprint
from controllers.client_controller import ClientController

# Create blueprint for client routes
client_bp = Blueprint('clients', __name__, url_prefix='/api/clients')

# Define routes
@client_bp.route('/', methods=['POST'])
def create_client():
    """Create a new client"""
    return ClientController.create_client()

@client_bp.route('/', methods=['GET'])
def get_all_clients():
    """Get all clients"""
    return ClientController.get_all_clients()

@client_bp.route('/<int:client_id>', methods=['GET'])
def get_client_by_id(client_id):
    """Get client by ID"""
    return ClientController.get_client_by_id(client_id)

@client_bp.route('/<int:client_id>', methods=['PUT'])
def update_client(client_id):
    """Update client by ID"""
    return ClientController.update_client(client_id)