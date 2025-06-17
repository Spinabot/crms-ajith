import datetime
import os

import jwt
import requests
from dotenv import load_dotenv

# load secrets file from .env file
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request
from fastapi.responses import RedirectResponse  # to redirect the user to the Jobber login page
from fastapi_limiter.depends import RateLimiter

from src.config import Config
from src.schemas.schemas import Client
from src.utils.db_conn import insert_jobber

# --- Config ---

if not Config.Remodel_ID or not Config.Remodel_SECRET:
    raise RuntimeError("Remodel_ID and Remodel_SECRET must be set in the environment")

router = APIRouter(prefix="/auth")


# --- Routes ---
@router.get("/jobber", dependencies=[Depends(RateLimiter(times=5, seconds=60))])
async def authorize(request: Request, userid: int):
    global REDIRECT_URI
    redis_client = request.app.state.redis
    key = f"userid:{userid}#"
    await redis_client.delete(key)  # remove outdated redis data
    host = request.url.hostname or "localhost"
    port = request.url.port or 8000
    REDIRECT_URI = f"http://{host}:{port}/auth/callback"
    auth_url = (
        f"https://api.getjobber.com/api/oauth/authorize"
        f"?response_type=code&client_id={Config.Remodel_ID}&redirect_uri={REDIRECT_URI}&state={int(userid)}"
    )
    return RedirectResponse(url=auth_url, status_code=302)


@router.get("/callback")
def get_callback(code: str, state: str):
    if not code or not state:
        raise HTTPException(
            status_code=400, detail="Missing code or state in callback"
        )  # user didn't come via proper OAuth redirect

    user_id = state  # passing userid in state params

    token_data = {
        "client_id": Config.Remodel_ID,
        "client_secret": Config.Remodel_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
    }

    response = requests.post("https://api.getjobber.com/api/oauth/token", data=token_data)

    if response.status_code == 200:
        access_token = response.json().get("access_token")
        refresh_token = response.json().get("refresh_token")
        decoded = jwt.decode(access_token, options={"verify_signature": False})
        expiration_time = decoded.get("exp")
        insert_jobber(user_id, access_token, refresh_token, expiration_time)
        return {"status": "success", "message": "Authorization successful"}

    elif response.status_code == 400:
        raise HTTPException(
            status_code=400, detail="Bad Request – check input fields"
        )  # likely missing or malformed token request params

    elif response.status_code == 401:
        raise HTTPException(
            status_code=401, detail="Unauthorized – invalid credentials"
        )  # client_id or secret might be wrong

    elif response.status_code == 403:
        raise HTTPException(
            status_code=403, detail="Forbidden – access denied"
        )  # credentials valid, but app doesn't have permission

    else:
        raise HTTPException(
            status_code=500, detail="Unexpected error during OAuth flow"
        )  # something unexpected like server down, timeout, etc.
