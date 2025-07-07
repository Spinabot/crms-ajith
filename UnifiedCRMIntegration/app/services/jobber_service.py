import requests
import logging
import time
import psycopg2
from datetime import datetime
from app.models import JobberAuth
from app.config import Config
from app.services.jobber_queries import get_client_data

logger = logging.getLogger(__name__)

def get_db_connection():
    """Create and return a database connection."""
    try:
        connection = psycopg2.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            database=Config.DB_NAME,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD
        )
        return connection
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        raise

class JobberService:
    """Service class for Jobber CRM operations"""

    @staticmethod
    def get_user_tokens(user_id):
        """Get access and refresh tokens for a user using direct database connection"""
        try:
            logger.info(f"Getting tokens for user {user_id} using direct DB connection")

            # Use direct database connection like JobberCRMFlask
            conn = get_db_connection()
            cursor = conn.cursor()

            # Get the most recent token for the user
            query = """
            SELECT access_token, refresh_token, expiration_time, user_id
            FROM jobber_auth
            WHERE user_id = %s
            ORDER BY updated_at DESC
            LIMIT 1
            """

            cursor.execute(query, (str(user_id),))
            result = cursor.fetchone()

            if result:
                access_token, refresh_token, expiration_time, stored_user_id = result
                logger.info(f"Found token in database for user {stored_user_id}")

                # Check if token is expired (same logic as JobberCRMFlask)
                current_time = datetime.now().timestamp()
                if current_time < expiration_time:
                    # Token is still valid
                    logger.info(f"Valid token found in database for user {user_id}")
                    cursor.close()
                    conn.close()

                    return {
                        'access_token': access_token,
                        'refresh_token': refresh_token,
                        'expiration_time': expiration_time
                    }
                else:
                    # Token is expired, try to refresh it
                    logger.warning(f"Token expired for user {user_id}, attempting refresh")
                    cursor.close()
                    conn.close()

                    return JobberService.refresh_user_tokens(user_id)
            else:
                logger.warning(f"No token found for user {user_id}")
                cursor.close()
                conn.close()
                return None

        except Exception as e:
            logger.error(f"Error getting tokens for user {user_id}: {e}")
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()
            return None

    @staticmethod
    def refresh_user_tokens(user_id):
        """Refresh access token for a user using direct database connection"""
        try:
            logger.info(f"Refreshing token for user {user_id}")

            # First get the current refresh token from database
            conn = get_db_connection()
            cursor = conn.cursor()

            # Get current refresh token
            query = """
            SELECT refresh_token
            FROM jobber_auth
            WHERE user_id = %s
            ORDER BY updated_at DESC
            LIMIT 1
            """

            cursor.execute(query, (str(user_id),))
            result = cursor.fetchone()

            if not result:
                logger.error(f"No authentication record found for user {user_id}")
                cursor.close()
                conn.close()
                return None

            refresh_token = result[0]

            # Prepare refresh token request
            refresh_data = {
                "client_id": Config.JOBBER_CLIENT_ID,
                "client_secret": Config.JOBBER_CLIENT_SECRET,
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
            }

            logger.info(f"Requesting token refresh for user {user_id}")

            # Request new access token
            response = requests.post(
                Config.JOBBER_TOKENS_URL,
                data=refresh_data
            )

            if response.status_code == 200:
                response_data = response.json()
                new_access_token = response_data.get("access_token")
                new_refresh_token = response_data.get("refresh_token")

                # Decode JWT to get expiration time
                import jwt
                decoded = jwt.decode(new_access_token, options={"verify_signature": False})
                expiration_time = decoded.get("exp")

                logger.info(f"New token expiration time: {expiration_time} ({datetime.utcfromtimestamp(expiration_time)})")

                # Update database using direct connection
                update_query = """
                UPDATE jobber_auth
                SET access_token = %s, refresh_token = %s, expiration_time = %s, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = %s
                """

                cursor.execute(update_query, (
                    new_access_token,
                    new_refresh_token,
                    expiration_time,
                    str(user_id)
                ))
                conn.commit()

                logger.info(f"Successfully refreshed token for user {user_id}, new expiration: {expiration_time}")

                cursor.close()
                conn.close()

                return {
                    'access_token': new_access_token,
                    'refresh_token': new_refresh_token,
                    'expiration_time': expiration_time
                }
            else:
                logger.error(f"Token refresh failed: {response.status_code}")
                cursor.close()
                conn.close()
                return None

        except Exception as e:
            logger.error(f"Error refreshing token for user {user_id}: {e}")
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()
            return None

    @staticmethod
    def get_client_data(user_id):
        """Get client data from Jobber CRM"""
        try:
            logger.info(f"Starting data retrieval for user {user_id}")

            # Get tokens for the user
            tokens = JobberService.get_user_tokens(user_id)

            if not tokens:
                logger.warning(f"No valid tokens available for user {user_id}")
                return None, "No valid tokens available, please authorize first"

            # Prepare headers for Jobber API request
            headers = {
                "Authorization": f"Bearer {tokens['access_token']}",
                "X-JOBBER-GRAPHQL-VERSION": "2025-01-20",
            }

            # Make request to Jobber API
            jobber_url = Config.JOBBER_API_URL

            logger.info(f"Fetching client data for user {user_id}")

            # Initialize pagination variables
            hasNextPage = True
            end_cursor = None
            variables = {"cursor": end_cursor}
            data = []
            request_count = 0

            # Fetch data with pagination
            while hasNextPage:
                try:
                    # Make GraphQL request
                    payload = {
                        "query": get_client_data,
                        "variables": variables
                    }

                    logger.info(f"Making GraphQL request {request_count + 1} with cursor: {end_cursor}")
                    response = requests.post(jobber_url, json=payload, headers=headers)
                    response_data = response.json()

                    # Check for errors
                    if response.status_code != 200 or "errors" in response_data:
                        logger.error(f"GraphQL query failed: {response_data}")
                        return None, "GraphQL query failed"

                    # Extract data from response
                    data.append(response_data["data"]["clients"]["nodes"])
                    page_info = response_data["data"]["clients"]["pageInfo"]
                    hasNextPage = page_info["hasNextPage"]
                    end_cursor = page_info["endCursor"]
                    variables = {"cursor": end_cursor}
                    request_count += 1

                    logger.info(f"Page {request_count}: {len(response_data['data']['clients']['nodes'])} clients, hasNextPage: {hasNextPage}")

                    # Sleep after every 5 requests to avoid rate limiting
                    if request_count % 5 == 0:
                        logger.info(f"Sleeping for 3 seconds after {request_count} requests")
                        time.sleep(3)

                except Exception as e:
                    logger.error(f"Error during pagination: {e}")
                    return None, f"Error fetching data: {str(e)}"

            logger.info(f"Successfully fetched client data for user {user_id} in {request_count} requests")
            return data, None

        except Exception as e:
            logger.error(f"Unexpected error getting client data: {e}")
            return None, "Internal server error"

    @staticmethod
    def convert_to_unified_lead(jobber_client):
        """Convert Jobber client data to UnifiedLead format"""
        try:
            # Extract basic information
            first_name = jobber_client.get('firstName', '')
            last_name = jobber_client.get('lastName', '')
            company_name = jobber_client.get('companyName', '')

            # Extract email (take first email if available)
            emails = jobber_client.get('emails', [])
            email = emails[0].get('address', '') if emails else ''

            # Extract phone (take first phone if available)
            phones = jobber_client.get('phones', [])
            mobile_phone = ''
            for phone in phones:
                if phone.get('description', '').lower() in ['mobile', 'cell']:
                    mobile_phone = phone.get('number', '')
                    break
            if not mobile_phone and phones:
                mobile_phone = phones[0].get('number', '')

            # Extract address from client properties
            address_line1 = ''
            city = ''
            state = ''
            zip_code = ''
            country = ''

            client_properties = jobber_client.get('clientProperties', {}).get('nodes', [])
            if client_properties:
                address = client_properties[0].get('address', {})
                # Note: Jobber address structure might need adjustment based on actual data
                city = address.get('city', '')
                zip_code = address.get('postalCode', '')
                country = address.get('country', '')

            # Extract lead source
            lead_source = ''
            source_attribution = jobber_client.get('sourceAttribution', {})
            if source_attribution:
                lead_source = source_attribution.get('sourceText', '')

            return {
                'firstName': first_name,
                'lastName': last_name,
                'email': email,
                'mobilePhone': mobile_phone,
                'companyName': company_name,
                'addressLine1': address_line1,
                'city': city,
                'state': state,
                'zip': zip_code,
                'country': country,
                'leadSource': lead_source,
                'crmSystem': 'jobber',
                'crmExternalId': jobber_client.get('id', ''),
                'crmRawData': jobber_client
            }

        except Exception as e:
            logger.error(f"Error converting Jobber client to unified lead: {e}")
            return None