import os
from contextlib import asynccontextmanager

import redis.asyncio as redis
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

from src.auth.authorization import router as auth_router
from src.config import Config
from src.routes.archive_client import router as archive_router
from src.routes.client_data import router as get_client_router
from src.routes.create_client import router as client_create_router
from src.routes.update_client import router as update_client_router


# setting up redis and rate limiting
@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_client = redis.from_url(Config.REDIS_URL, encoding="utf-8", decode_responses=True)
    app.state.redis = redis_client
    await FastAPILimiter.init(redis_client)
    yield
    # Optional cleanup can go here


app = FastAPI(lifespan=lifespan)

# CORS setup
ALLOW_ORIGIN = os.getenv("ALLOW_ORIGIN", "*")
# in dev allow all
# in prod allow remodelai.com
app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOW_ORIGIN],  # dynamically set here
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(get_client_router)
app.include_router(archive_router)
app.include_router(client_create_router)
app.include_router(update_client_router)
