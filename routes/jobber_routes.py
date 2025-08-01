from flask import Blueprint
from controllers import jobber_controller

jobber_bp = Blueprint('jobber', __name__, url_prefix='/api/jobber')

jobber_bp.route('/clients', methods=['GET'])(jobber_controller.get_jobber_clients)
jobber_bp.route('/jobs', methods=['GET'])(jobber_controller.get_jobber_jobs)
jobber_bp.route('/clients', methods=['POST'])(jobber_controller.post_jobber_client)
