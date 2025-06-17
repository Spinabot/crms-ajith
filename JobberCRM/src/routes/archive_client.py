import aiohttp  # Using aiohttp for async HTTP requests
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request
from fastapi_limiter.depends import RateLimiter

from src.config import Config
from src.queries.archive_client_query import archive_client_mutation
from src.schemas.schemas import ArchiveClientData
from src.utils.token_handler import get_token

router = APIRouter(prefix="/client")


@router.post("/archive/{userid}", dependencies=[Depends(RateLimiter(times=5, seconds=60))])
async def archive_client(userid: int, data: ArchiveClientData, request: Request):
    redis_client = request.app.state.redis
    try:
        token_data = await get_token(userid, redis_client)

    except Exception as e:
        raise HTTPException(500, f"Error fetching tokens: {str(e)}")

    if not token_data:  # Tokens will be None if no token_data are available
        raise HTTPException(401, "No token available, please authorize first")
    headers = {
        "Authorization": f"Bearer {token_data[0]['access_token']}",
        "Content-Type": "application/json",
        "X-JOBBER-GRAPHQL-VERSION": "2025-01-20",
    }
    jobber_url = Config.jobber_api_url  # Use the jobber_api_url from the config
    async with aiohttp.ClientSession() as session:
        async with session.post(
            jobber_url,
            json={"query": archive_client_mutation, "variables": {"clientId": data.clientId}},
            headers=headers,
        ) as response:
            return await response.json()
