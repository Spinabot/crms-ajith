from flask import Blueprint, request, jsonify
from flask_restx import Resource, Namespace
from app.models import UnifiedLead, CRMConnection, SyncLog, JobberAuth
from app import db
from app.config import Config
from app.utils.auth import require_api_key
from app.swagger import api, jobber_create_client_model, jobber_update_client_model, jobber_archive_client_model, jobber_clients_list_model, error_model
import datetime
import requests
import jwt
import time

jobber_bp = Blueprint('jobber', __name__)
jobber_ns = Namespace('jobber', description='Jobber CRM operations')

# Add namespace to API
api.add_namespace(jobber_ns)

JOBBER_GRAPHQL_URL = "https://api.getjobber.com/api/graphql"

# GraphQL Queries and Mutations
CREATE_CLIENT_MUTATION = '''
mutation CreateClient($input: ClientCreateInput!) {
  clientCreate(input: $input) {
    client {
      id
      firstName
      lastName
      companyName
      billingAddress {
        street1
        street2
        city
        province
        country
        postalCode
      }
      phones {
        number
        primary
      }
      emails {
        address
        primary
      }
    }
    userErrors {
      message
      path
    }
  }
}
'''

GET_CLIENT_DATA_QUERY = '''
query GetBasicClientData($cursor: String) {
  clients(first: 15, after: $cursor, filter: {isLead: true, isArchived: false}) {
    nodes {
      id
      firstName
      lastName
      isLead
      isCompany
      companyName
      jobberWebUri
      phones {
        id
        description
        smsAllowed
        number
      }
      emails {
        id
        address
      }
      balance
      companyName
      defaultEmails
      clientProperties {
        nodes {
          address {
            id
            city
            country
            postalCode
          }
        }
      }
      sourceAttribution {
        sourceText
        metadata
        source {
          __typename
          ... on Application {
            id
            name
          }
        }
      }
    }
    pageInfo {
      endCursor
      hasNextPage
    }
  }
}
'''

UPDATE_CLIENT_MUTATION = '''
mutation UpdateClient(
  $clientId: EncodedId!
  $firstName: String
  $lastName: String
  $companyName: String
  $emailsToEdit: [EmailUpdateAttributes!]
  $emailsToAdd: [EmailCreateAttributes!]
  $phonesToEdit: [PhoneNumberUpdateAttributes!]
  $phonesToAdd: [PhoneNumberCreateAttributes!]
  $phonesToDelete: [EncodedId!]
  $emailsToDelete: [EncodedId!]
  $billingAddress: AddressAttributes
) {
  clientEdit(
    clientId: $clientId
    input: {
      firstName: $firstName
      lastName: $lastName
      companyName: $companyName
      emailsToEdit: $emailsToEdit
      emailsToAdd: $emailsToAdd
      phonesToAdd: $phonesToAdd
      phonesToEdit: $phonesToEdit
      phonesToDelete: $phonesToDelete
      emailsToDelete: $emailsToDelete
      billingAddress: $billingAddress
    }
  ) {
    client {
      id
      firstName
      lastName
      companyName
      jobberWebUri
      emails {
        id
        address
      }
      phones {
        id
        number
      }
      balance
      defaultEmails
      clientProperties {
        nodes {
          address {
            city
            country
            postalCode
          }
        }
      }
      sourceAttribution {
        sourceText
        metadata
        source {
          __typename
          ... on Application {
            id
            name
          }
        }
      }
    }
    userErrors {
      message
      path
    }
  }
}
'''

ARCHIVE_CLIENT_MUTATION = '''
mutation ArchiveClient($clientId: EncodedId!) {
  clientArchive(clientId: $clientId) {
    client {
      id
      firstName
      lastName
      companyName
    }
    userErrors {
      message
      path
    }
  }
}
'''



@jobber_ns.route('/leads')
class JobberLeadsResource(Resource):
    @api.doc('create_jobber_lead',
        description='Create a new client/lead in Jobber CRM',
        params={'user_id': 'User ID for the operation'},
        responses={200: 'Success', 404: 'User not found', 400: 'Bad request', 500: 'Internal error'})
    @api.expect(jobber_create_client_model)
    def post(self):
        """Create a lead in Jobber CRM"""
        user_id = request.args.get('user_id')
        if not user_id:
            return {'error': 'user_id parameter is required'}, 400

        try:
            jobber_auth = JobberAuth.query.filter_by(user_id=user_id).first()
            if not jobber_auth:
                return {'error': f'No authentication found for user_id: {user_id}'}, 404
            access_token = jobber_auth.access_token
        except Exception as e:
            return {'error': 'Internal server error'}, 500

        # Parse and validate input JSON
        try:
            data = request.get_json(force=True)
        except Exception as e:
            return {'error': 'Invalid JSON body', 'details': str(e)}, 400

        # Clean up the input data - remove description from emails
        cleaned_data = data.copy()
        if 'emails' in cleaned_data:
            for email in cleaned_data['emails']:
                if 'description' in email:
                    del email['description']

        variables = {"input": cleaned_data}

        # Prepare headers
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "X-JOBBER-GRAPHQL-VERSION": "2025-01-20"
        }

        # Make the request to Jobber's API
        try:
            request_payload = {"query": CREATE_CLIENT_MUTATION, "variables": variables}

            response = requests.post(
                JOBBER_GRAPHQL_URL,
                json=request_payload,
                headers=headers
            )

            # Try to parse JSON response
            try:
                jobber_response = response.json()
                status_code = response.status_code
            except ValueError as json_error:
                # Handle 500 Internal Server Error specifically
                if response.status_code == 500:
                    return {
                        'error': 'Jobber API Internal Server Error',
                        'message': 'The Jobber API encountered an internal error. This might be due to invalid data format or API issues.',
                        'status_code': response.status_code,
                        'raw_response': response.text
                    }, 500
                else:
                    return {
                        'error': 'Invalid response from Jobber API',
                        'status_code': response.status_code,
                        'raw_response': response.text[:500]  # First 500 chars
                    }, 500

        except Exception as e:
            return {'error': 'Failed to contact Jobber API', 'details': str(e)}, 500

        # Return the Jobber API response
        return jobber_response, status_code

@jobber_ns.route('/clients')
class JobberClientsResource(Resource):
    @api.doc('get_jobber_clients',
        description='Get all client data from Jobber CRM with pagination support',
        params={'user_id': 'User ID for the operation'},
        responses={200: ('Success', jobber_clients_list_model), 404: ('User not found', error_model), 401: ('Unauthorized', error_model), 500: ('Internal error', error_model)})
    def get(self):
        """Get all client data from Jobber CRM"""
        user_id = request.args.get('user_id')
        if not user_id:
            return {'error': 'user_id parameter is required'}, 400

        try:
            jobber_auth = JobberAuth.query.filter_by(user_id=user_id).first()
            if not jobber_auth:
                return {'error': f'No authentication found for user_id: {user_id}'}, 404
            access_token = jobber_auth.access_token
        except Exception as e:
            return {'error': 'Internal server error'}, 500

        # Prepare headers
        headers = {
            "Authorization": f"Bearer {access_token}",
            "X-JOBBER-GRAPHQL-VERSION": "2025-01-20"
        }

        # Initialize pagination variables
        hasNextPage = True
        end_cursor = None
        variables = {"cursor": end_cursor}
        all_data = []
        request_count = 0

        # Fetch data with pagination
        while hasNextPage:
            try:
                # Make GraphQL request
                payload = {
                    "query": GET_CLIENT_DATA_QUERY,
                    "variables": variables
                }

                response = requests.post(JOBBER_GRAPHQL_URL, json=payload, headers=headers)
                response_data = response.json()

                # Check for errors
                if response.status_code != 200 or "errors" in response_data:
                    return {'error': 'GraphQL query failed', 'details': response_data}, 500

                # Extract data from response
                all_data.extend(response_data["data"]["clients"]["nodes"])
                page_info = response_data["data"]["clients"]["pageInfo"]
                hasNextPage = page_info["hasNextPage"]
                end_cursor = page_info["endCursor"]
                variables = {"cursor": end_cursor}
                request_count += 1

                # Sleep after every 5 requests to avoid rate limiting
                if request_count % 5 == 0:
                    time.sleep(3)

            except Exception as e:
                return {'error': f'Error fetching data: {str(e)}'}, 500

        return {'data': all_data, 'total_count': len(all_data), 'pages_fetched': request_count}, 200

@jobber_ns.route('/clients/update')
class JobberUpdateClientResource(Resource):
    @api.doc('update_jobber_client',
        description='Update an existing client in Jobber CRM',
        params={'user_id': 'User ID for the operation'},
        responses={200: 'Success', 404: ('User not found', error_model), 400: ('Bad request', error_model), 500: ('Internal error', error_model)})
    @api.expect(jobber_update_client_model)
    def post(self):
        """Update an existing client in Jobber CRM"""
        user_id = request.args.get('user_id')
        if not user_id:
            return {'error': 'user_id parameter is required'}, 400

        try:
            jobber_auth = JobberAuth.query.filter_by(user_id=user_id).first()
            if not jobber_auth:
                return {'error': f'No authentication found for user_id: {user_id}'}, 404
            access_token = jobber_auth.access_token
        except Exception as e:
            return {'error': 'Internal server error'}, 500

        # Parse and validate input JSON
        try:
            data = request.get_json(force=True)
            if not data.get('clientId'):
                return {'error': 'clientId is required'}, 400
        except Exception as e:
            return {'error': 'Invalid JSON body', 'details': str(e)}, 400

        # Prepare variables for GraphQL mutation
        variables = {"clientId": data["clientId"]}
        for field, value in data.items():
            if field != "clientId" and value is not None:
                variables[field] = value

        # Prepare headers
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "X-JOBBER-GRAPHQL-VERSION": "2025-01-20"
        }

        # Make the request to Jobber's API
        try:
            request_payload = {"query": UPDATE_CLIENT_MUTATION, "variables": variables}

            response = requests.post(
                JOBBER_GRAPHQL_URL,
                json=request_payload,
                headers=headers
            )

            jobber_response = response.json()
            status_code = response.status_code

            # Check for GraphQL errors
            if "errors" in jobber_response:
                return {'error': 'GraphQL errors', 'details': jobber_response["errors"]}, 500

            # Check for user errors in the response
            if "data" in jobber_response and "clientEdit" in jobber_response["data"]:
                user_errors = jobber_response["data"]["clientEdit"].get("userErrors", [])
                if user_errors:
                    return {'error': 'Client update failed', 'userErrors': user_errors}, 400

        except Exception as e:
            return {'error': 'Failed to contact Jobber API', 'details': str(e)}, 500

        return jobber_response, status_code

@jobber_ns.route('/clients/archive')
class JobberArchiveClientResource(Resource):
    @api.doc('archive_jobber_client',
        description='Archive (soft delete) a client in Jobber CRM',
        params={'user_id': 'User ID for the operation'},
        responses={200: 'Success', 404: ('User not found', error_model), 400: ('Bad request', error_model), 500: ('Internal error', error_model)})
    @api.expect(jobber_archive_client_model)
    def post(self):
        """Archive (soft delete) a client in Jobber CRM"""
        user_id = request.args.get('user_id')
        if not user_id:
            return {'error': 'user_id parameter is required'}, 400

        try:
            jobber_auth = JobberAuth.query.filter_by(user_id=user_id).first()
            if not jobber_auth:
                return {'error': f'No authentication found for user_id: {user_id}'}, 404
            access_token = jobber_auth.access_token
        except Exception as e:
            return {'error': 'Internal server error'}, 500

        # Parse and validate input JSON
        try:
            data = request.get_json(force=True)
            if not data.get('clientId'):
                return {'error': 'clientId is required'}, 400
        except Exception as e:
            return {'error': 'Invalid JSON body', 'details': str(e)}, 400

        # Prepare variables for GraphQL mutation
        variables = {"clientId": data["clientId"]}

        # Prepare headers
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "X-JOBBER-GRAPHQL-VERSION": "2025-01-20"
        }

        # Make the request to Jobber's API
        try:
            request_payload = {"query": ARCHIVE_CLIENT_MUTATION, "variables": variables}

            response = requests.post(
                JOBBER_GRAPHQL_URL,
                json=request_payload,
                headers=headers
            )

            jobber_response = response.json()
            status_code = response.status_code

            # Check for GraphQL errors
            if "errors" in jobber_response:
                return {'error': 'GraphQL errors', 'details': jobber_response["errors"]}, 500

            # Check for user errors in the response
            if "data" in jobber_response and "clientArchive" in jobber_response["data"]:
                user_errors = jobber_response["data"]["clientArchive"].get("userErrors", [])
                if user_errors:
                    return {'error': 'Client archive failed', 'userErrors': user_errors}, 400

        except Exception as e:
            return {'error': 'Failed to contact Jobber API', 'details': str(e)}, 500

        return jobber_response, status_code