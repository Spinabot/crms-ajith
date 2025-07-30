from flask import Blueprint
from controllers.builderprime_controller import BuilderPrimeController

# Create blueprint for BuilderPrime routes
builderprime_bp = Blueprint('builderprime', __name__, url_prefix='/api/builderprime')

# Route for creating leads
@builderprime_bp.route('/clients/<int:client_id>/leads', methods=['POST'])
def create_lead(client_id):
    """
    Create a new lead/opportunity in BuilderPrime for a specific client

    Args:
        client_id (int): Client ID from URL parameter

    Returns:
        JSON response with lead creation result
    """
    return BuilderPrimeController.create_lead(client_id)

# Route for getting all BuilderPrime leads
@builderprime_bp.route('/leads', methods=['GET'])
def get_all_leads():
    """
    Get all BuilderPrime leads from the database

    Returns:
        JSON response with list of BuilderPrime leads
    """
    return BuilderPrimeController.get_leads()

# Route for getting BuilderPrime leads for a specific client
@builderprime_bp.route('/clients/<int:client_id>/leads', methods=['GET'])
def get_client_leads(client_id):
    """
    Get BuilderPrime leads for a specific client

    Args:
        client_id (int): Client ID from URL parameter

    Returns:
        JSON response with list of BuilderPrime leads for the client
    """
    return BuilderPrimeController.get_leads(client_id)

# Route for fetching data from BuilderPrime API
@builderprime_bp.route('/clients/<int:client_id>/data', methods=['GET'])
def fetch_builderprime_data(client_id):
    """
    Fetch data from BuilderPrime API for a specific client

    Args:
        client_id (int): Client ID from URL parameter

    Query Parameters:
        last-modified-since (int, optional): Date in milliseconds since epoch (up to 1 year ago)
        lead-status (string, optional): Lead status name to filter by
        lead-source (string, optional): Lead source name to filter by
        dialer-status (string, optional): Dialer status to filter by
        phone (string, optional): Phone number to search for (E.164 format recommended)
        limit (int, optional): Number of records to return (max 500)
        page (int, optional): Page number (starts with 0)

    Returns:
        JSON response with BuilderPrime API data
    """
    return BuilderPrimeController.fetch_builderprime_data(client_id)

# Route for updating BuilderPrime leads
@builderprime_bp.route('/clients/<int:client_id>/leads/<opportunity_id>', methods=['PUT'])
def update_lead(client_id, opportunity_id):
    """
    Update a lead/opportunity in BuilderPrime

    Args:
        client_id (int): Client ID from URL parameter
        opportunity_id (str): BuilderPrime opportunity ID from URL parameter

    Request Body:
        JSON object with fields to update (only non-blank values will be updated)

    Returns:
        JSON response with update result
    """
    return BuilderPrimeController.update_lead(client_id, opportunity_id)