import json 
from fastapi import Request
import redis.asyncio as redis


async def get_auth_redis(userid, redis_client):
    cache_key = f"userid:{userid}#"
    tokens = await redis_client.get(cache_key)
    if tokens and tokens.strip():
        tokens = json.loads(tokens)
        return tokens  # Just return tokens as is
    else:
        return None

    
async def set_auth_redis(userid:int,tokens :list ,redis_client):
    cache_key=f"userid:{userid}#"#ends with hash to make unique to store access tokens only.
    await redis_client.set(cache_key,json.dumps(tokens),ex=3600)#expiry, the tokens stay in redis for one hour.

    
async def delete_auth_redis(userid:int,redis_client):
    cache_key = f"userid:{userid}#"
    await redis_client.delete(cache_key)

