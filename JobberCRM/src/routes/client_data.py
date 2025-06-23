import asyncio
import json

import aiohttp  # Using aiohttp for async HTTP requests
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request
from fastapi_limiter.depends import RateLimiter

from src.config import Config
from src.queries.get_client_query import get_client_data
from src.utils.token_handler import get_token

router = APIRouter(prefix="/data")


@router.post(
    "/jobber/{userid}", dependencies=[Depends(RateLimiter(times=5, seconds=60))]
)  # Max 5 request in 60 seconds.
async def get_data(userid: int, request: Request):
    redis_client = request.app.state.redis
    try:
        tokens = await get_token(userid, redis_client, request)
        # if tokens in list
        if not isinstance(tokens, list):
            raise HTTPException(500, "Unexpected token format received")
    except Exception as e:
        raise HTTPException(500, f"Error fetching tokens: {str(e)}")

    if not tokens:  # Tokens will be None if no tokens are available
        raise HTTPException(401, "No token available, please authorize first")
    headers = {
        "Authorization": f"Bearer {tokens[0]['access_token']}",
        "X-JOBBER-GRAPHQL-VERSION": "2025-01-20",
    }
    jobber_url = Config.jobber_api_url  # Use the jobber_api_url from the config
    # Use aiohttp to make the request
    async with aiohttp.ClientSession() as session:
        hasNextPage = True
        end_cursor = None
        variables = {"cursor": end_cursor}
        data = []
        request_count = 0  # Initialize request count
        # sleep after every 5 requests to avoid rate limiting
        while hasNextPage:
            async with session.post(
                jobber_url, json={"query": get_client_data, "variables": variables}, headers=headers
            ) as response:
                if response.status != 200 or "errors" in await response.json():
                    raise HTTPException(500, "GraphQL query failed")
            response_data = await response.json()
            data.append(response_data["data"]["clients"]["nodes"])
            page_info = response_data["data"]["clients"]["pageInfo"]
            hasNextPage = page_info["hasNextPage"]
            end_cursor = page_info["endCursor"]
            variables = {"cursor": end_cursor}
            request_count += 1
            if request_count % 5 == 0:
                await asyncio.sleep(
                    3
                )  # Sleep for 3 seconds after every 5 requests to avoid rate limiting
        return data
