from flask import current_app as app
from database.get_creds_db import get_zoho_creds
from database.update_data import update_zoho_creds
from token_handler.refresh_tokens import refresh_token
from utils.extension import redis_client
import time 
#this file handles the tokens fetch from redis or database. 

# 1. First check if tokken in redis , if yes then check if it is expired or not . call the refresh function if expired. 
# 2. if not in redis then check in databae and then check if it is expired or not. call the refresh function if expired. 
# 3. if not in dataase then redirect user the the auth page. 

import datetime
import json
import time
def fetch_tokens(entity_id):
    try:
        tokens = redis_client.hgetall(f"entity_id:{entity_id}#")#check in redis
        if tokens:
            access_token = tokens[b'access_token'].decode('utf-8')
            refresh_token_value = tokens[b'refresh_token'].decode('utf-8')
            expiration_time = int(tokens[b'expiration_time'].decode('utf-8'))

        else:
            tokens = get_zoho_creds(entity_id)
            if not tokens:
                return None
            access_token = tokens.get("access_token")
            refresh_token_value = tokens.get("refresh_token")
            expiration_time = tokens.get("expiration_time")

            # Store in Redis with expiry if valid
            if expiration_time > int(time.time()):  # If not expired
                redis_client.hset(f"entity_id:{entity_id}#", mapping={
                    "access_token": access_token,
                    "refresh_token": refresh_token_value,
                    "expiration_time": expiration_time
                })
                redis_client.expire(f"entity_id:{entity_id}#", 3600) 
            
        if not access_token or not refresh_token_value or not expiration_time:
            raise KeyError("Missing access_token, refresh_token, or expiration_time")

        if expiration_time < int(time.time()):#check if current time bigger than expiration
            new_tokens = refresh_token(entity_id, refresh_token_value)
            if not new_tokens or "access_token" not in new_tokens:
                raise ValueError("Failed to refresh access token")
            tokens["access_token"] = new_tokens["access_token"]
            tokens["expiration_time"] = int(time.time()) + new_tokens["expires_in"]
            #update in redis 
            redis_client.hset(f"entity_id:{entity_id}#", mapping={
                    "access_token": tokens["access_token"],
                    "refresh_token": refresh_token_value,
                "expiration_time": tokens["expiration_time"]
                        })
            redis_client.expire(f"entity_id:{entity_id}#", 3600)
            update_zoho_creds(entity_id, tokens)#update the new tokens in database
            #if refresh happens we are returnign access , refresh , but we so it break when we refresh 
            #these varaibles are not redundant
            access_token = tokens["access_token"]
            expiration_time=tokens['expiration_time']

        return {
            "access_token": access_token,
            "refresh_token": refresh_token_value,
            "expiration_time": expiration_time
        }

    except KeyError as e:
        app.logger.error(f"KeyError in fetch_tokens: {e}")
        return {"error": "Token data is incomplete. Please reauthorize."}
    except Exception as e:
        app.logger.error(f"Unexpected error in fetch_tokens: {e}")
        return {"error": "Internal error while handling token."}

