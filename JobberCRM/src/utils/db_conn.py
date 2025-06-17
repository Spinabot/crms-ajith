import os

import psycopg2
from psycopg2 import pool

from src.config import Config

# Set up connection pool
db_pool = psycopg2.pool.SimpleConnectionPool(
    1,
    20,
    dbname=Config.POSTGRES_DB,
    user=Config.POSTGRES_USER,
    password=Config.POSTGRES_PASSWORD,
    host=Config.POSTGRES_HOST,
    port=Config.POSTGRES_PORT,
)  # pooling allow multiple users to access database using same connection


def get_connection():
    """Get a connection from the pool"""
    # add database connection requeted log
    return db_pool.getconn()


def release_connection(conn):
    # connection release log
    """Release a connection back to the pool"""
    db_pool.putconn(conn)


# CREATE operation
def insert_jobber(user_id, access_token, refresh_token, expiration_time):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO tokens (userid, access_token, refresh_token, expiration_time)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (userid) 
            DO UPDATE SET 
                access_token = EXCLUDED.access_token, 
                refresh_token = EXCLUDED.refresh_token, 
                expiration_time = EXCLUDED.expiration_time;
        """,
            (user_id, access_token, refresh_token, expiration_time),
        )  # if user token aldready exits then update it.
        conn.commit()
    except Exception as e:
        return {"error": str(e)}
    finally:
        cur.close()
        release_connection(conn)


# READ operation
def fetch_tokens_db(user_id):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM tokens WHERE userid = %s", (user_id,))
        rows = cur.fetchall()
        if not rows:
            return {"message": "User not found"}
        result = []
        for row in rows:
            result.append(
                {
                    "userid": row[0],
                    "access_token": row[1],
                    "refresh_token": row[2],
                    "expiration_time": row[3],
                }
            )
        return result
    except Exception as e:
        return {"error": str(e)}
    finally:
        cur.close()
        release_connection(conn)


# UPDATE operation
def update_tokens(user_id, new_access_token, new_refresh_token, new_expiration_time):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            UPDATE tokens
            SET access_token = %s, refresh_token = %s, expiration_time = %s
            WHERE userid = %s
        """,
            (new_access_token, new_refresh_token, new_expiration_time, user_id),
        )
        conn.commit()
    except Exception as e:
        return {"error": str(e)}
    finally:
        cur.close()
        release_connection(conn)


# DELETE operation
def delete_jobber(user_id):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM tokens WHERE userid = %s", (user_id,))
        conn.commit()
    except Exception as e:
        return {"error": str(e)}
    finally:
        cur.close()
        release_connection(conn)


# Close the connection pool
def close_connection_pool():
    db_pool.closeall()
