# utils file for refreshing tokesns and database related functions.
import datetime
import json
import os
import webbrowser

import jwt
import requests
from fastapi import Depends
from fastapi import Request
from fastapi.responses import RedirectResponse

from src.config import Config
from src.utils.db_conn import fetch_tokens_db
from src.utils.db_conn import update_tokens
from src.utils.redis_operation import get_auth_redis
from src.utils.redis_operation import set_auth_redis


# Dependency to provide request globally
def get_request(request: Request):
    return request


# get-tokens
async def get_token(userid, redis_client):
    # Check Redis first
    tokens = await get_auth_redis(userid, redis_client)
    if tokens:
        tokens = [tokens]  # convert to list only if tokens are not None
    if not tokens:  # If Redis returned None or empty
        # Fetch tokens from the database
        tokens = fetch_tokens_db(userid)
        if (
            tokens
            and isinstance(tokens, dict)
            and "message" in tokens
            and tokens["message"] == "User not found"
        ):
            return None  # User not found in DB

        if not tokens:
            return None  # No tokens in DB either
        # Save DB tokens to Redis
        await set_auth_redis(userid, tokens, redis_client)
    # Check if tokens are still valid or need refreshing
    token_status = refresh_token(
        userid,
        tokens[0]["refresh_token"],
        datetime.datetime.fromtimestamp(tokens[0]["expiration_time"]),
    )
    if token_status["status"] == "success":
        tokens = token_status["tokens"]
        await set_auth_redis(userid, tokens, redis_client)  # update redis
        update_tokens(
            userid, tokens["access_token"], tokens["refresh_token"], tokens["expiration_time"]
        )  # update database
        # after updating the redis and database we return the tokens to the user in a list format.
        tokens = [tokens]
    return tokens


def refresh_token(
    userid, refresh_tokens: str, extracted_time, request: Request = Depends(get_request)
):
    if is_token_expired(extracted_time):
        # add log token expired
        refresh_data = {
            "client_id": Config.Remodel_ID,
            "client_secret": Config.Remodel_SECRET,
            "grant_type": "refresh_token",
            "refresh_token": refresh_tokens,
        }

        refresh_response = requests.post(
            "https://api.getjobber.com/api/oauth/token", data=refresh_data
        )

        if refresh_response.status_code == 401:
            # reroute to authorization route if refresh token is not valid for safety
            host = request.url.hostname or "localhost"
            port = request.url.port or 8000
            return RedirectResponse(
                url=f"http://{host}:{port}/auth/jobber/?{userid}", status_code=302
            )
        if refresh_response.status_code == 200:
            new_access_token = refresh_response.json().get("access_token")
            new_refresh_token = refresh_response.json().get("refresh_token")
            decoded = jwt.decode(new_access_token, options={"verify_signature": False})
            new_expiration_time = decoded.get("exp")
            tokens = {
                "access_token": new_access_token,
                "refresh_token": new_refresh_token,
                "expiration_time": new_expiration_time,
            }
            return {"status": "success", "tokens": tokens}

        else:
            # Handling the error response
            try:
                error_response = refresh_response.json()
            except ValueError:
                error_response = {"error": "Unable to parse response"}

            return {"status": "failure", "error": error_response}
    else:
        return {"status": "valid", "message": "Access token is still valid."}


def is_token_expired(extracted_time):
    return datetime.datetime.now() > extracted_time
