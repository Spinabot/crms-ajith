import psycopg2
import psycopg2.extras
from config import Config
import logging

logger = logging.getLogger(__name__)

def get_db_connection():
    """Create and return a database connection."""
    try:
        connection = psycopg2.connect(
            host=Config.POSTGRES_HOST,
            port=Config.POSTGRES_PORT,
            database=Config.POSTGRES_DB,
            user=Config.POSTGRES_USER,
            password=Config.POSTGRES_PASSWORD
        )
        return connection
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        raise

def insert_jobber(user_id, access_token, refresh_token, expiration_time):
    """Insert Jobber authorization data into the database."""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Create table if it doesn't exist
        create_table_query = """
        CREATE TABLE IF NOT EXISTS jobber_auth (
            id SERIAL PRIMARY KEY,
            user_id VARCHAR(255) NOT NULL UNIQUE,
            access_token TEXT NOT NULL,
            refresh_token TEXT NOT NULL,
            expiration_time BIGINT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        cursor.execute(create_table_query)

        # Insert or update the authorization data
        insert_query = """
        INSERT INTO jobber_auth (user_id, access_token, refresh_token, expiration_time)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (user_id)
        DO UPDATE SET
            access_token = EXCLUDED.access_token,
            refresh_token = EXCLUDED.refresh_token,
            expiration_time = EXCLUDED.expiration_time,
            updated_at = CURRENT_TIMESTAMP;
        """

        logger.info(f"Inserting/updating Jobber auth for user {user_id}")
        cursor.execute(insert_query, (user_id, access_token, refresh_token, expiration_time))
        conn.commit()

        logger.info(f"Successfully inserted/updated Jobber auth for user {user_id}")

    except Exception as e:
        logger.error(f"Error inserting Jobber auth data: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()