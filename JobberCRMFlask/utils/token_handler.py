import logging
import redis
import requests
import jwt
from datetime import datetime
from config import Config
from utils.db_conn import get_db_connection

logger = logging.getLogger(__name__)

def refresh_access_token(userid, refresh_token):
    """
    Refresh the access token using the refresh token.
    """
    try:
        logger.info(f"Refreshing access token for user {userid}")

        # Prepare refresh token request
        refresh_data = {
            "client_id": Config.Remodel_ID,
            "client_secret": Config.Remodel_SECRET,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }

        # Make request to Jobber token endpoint
        response = requests.post(
            "https://api.getjobber.com/api/oauth/token",
            data=refresh_data
        )

        if response.status_code == 200:
            # Extract new tokens from response
            response_data = response.json()
            new_access_token = response_data.get("access_token")
            new_refresh_token = response_data.get("refresh_token")

            # Decode JWT to get new expiration time
            decoded = jwt.decode(new_access_token, options={"verify_signature": False})
            new_expiration_time = decoded.get("exp")

            # Update tokens in database
            conn = get_db_connection()
            cursor = conn.cursor()

            update_query = """
            UPDATE jobber_auth
            SET access_token = %s, refresh_token = %s, expiration_time = %s, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = %s
            """

            cursor.execute(update_query, (
                new_access_token,
                new_refresh_token,
                new_expiration_time,
                str(userid)
            ))
            conn.commit()

            logger.info(f"Successfully refreshed tokens for user {userid}")

            cursor.close()
            conn.close()

            return [{"access_token": new_access_token}]

        elif response.status_code == 400:
            logger.error("Bad Request during token refresh")
            return None
        elif response.status_code == 401:
            logger.error("Unauthorized during token refresh - refresh token may be invalid")
            return None
        else:
            logger.error(f"Token refresh failed with status {response.status_code}")
            return None

    except Exception as e:
        logger.error(f"Error refreshing token for user {userid}: {e}")
        return None

def get_token(userid, redis_client=None):
    """
    Get access token for a user from database.
    This is a synchronous version of the async function from FastAPI.
    """
    try:
        logger.info(f"Fetching token for user {userid}")

        # First try to get from Redis cache
        if redis_client:
            try:
                cache_key = f"userid:{userid}#"
                cached_token = redis_client.get(cache_key)
                if cached_token:
                    logger.info(f"Token found in Redis cache for user {userid}")
                    return [{"access_token": cached_token}]
            except Exception as e:
                logger.warning(f"Redis cache error: {e}")

        # If not in cache, get from database
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

        cursor.execute(query, (str(userid),))
        result = cursor.fetchone()

        if result:
            access_token, refresh_token, expiration_time, stored_user_id = result
            logger.info(f"Found token in database for user {stored_user_id}")

            # Check if token is expired
            current_time = datetime.now().timestamp()
            if current_time < expiration_time:
                # Token is still valid
                logger.info(f"Valid token found in database for user {userid}")

                # Cache in Redis if available
                if redis_client:
                    try:
                        cache_key = f"userid:{userid}#"
                        redis_client.setex(cache_key, 3600, access_token)  # Cache for 1 hour
                    except Exception as e:
                        logger.warning(f"Failed to cache token in Redis: {e}")

                # Return in the expected format
                token_data = [{"access_token": access_token}]
                logger.info(f"Returning token data: {token_data}")
                return token_data
            else:
                # Token is expired, try to refresh it
                logger.warning(f"Token expired for user {userid}, attempting refresh")

                # Clear expired token from Redis cache
                if redis_client:
                    try:
                        cache_key = f"userid:{userid}#"
                        redis_client.delete(cache_key)
                    except Exception as e:
                        logger.warning(f"Failed to clear expired token from Redis: {e}")

                # Try to refresh the token
                refreshed_tokens = refresh_access_token(userid, refresh_token)
                if refreshed_tokens:
                    logger.info(f"Successfully refreshed tokens for user {userid}")

                    # Cache new token in Redis
                    if redis_client:
                        try:
                            cache_key = f"userid:{userid}#"
                            redis_client.setex(cache_key, 3600, refreshed_tokens[0]['access_token'])
                        except Exception as e:
                            logger.warning(f"Failed to cache refreshed token in Redis: {e}")

                    return refreshed_tokens
                else:
                    logger.error(f"Failed to refresh token for user {userid}")
                    return None
        else:
            logger.warning(f"No token found for user {userid}")

            # Let's check what users exist in the database
            cursor.execute("SELECT user_id FROM jobber_auth")
            all_users = cursor.fetchall()
            if all_users:
                logger.info(f"Available users in database: {[user[0] for user in all_users]}")
            else:
                logger.info("No users found in database")

            return None

    except Exception as e:
        logger.error(f"Error fetching token for user {userid}: {e}")
        raise
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

def refresh_token_if_needed(userid, refresh_token):
    """
    Refresh the access token using the refresh token.
    This would be called when the access token is expired.
    """
    try:
        # This is a placeholder for token refresh logic
        # You would implement the actual token refresh here
        logger.info(f"Refreshing token for user {userid}")

        # For now, return None to indicate refresh is needed
        return None

    except Exception as e:
        logger.error(f"Error refreshing token for user {userid}: {e}")
        raise