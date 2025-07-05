import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    # Load environment variables from .env file
    Remodel_ID = os.getenv("Remodel_ID", default="default_client_id")
    Remodel_SECRET = os.getenv("Remodel_SECRET", default="default_client_secret")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", default="localhost")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT", default="5432")
    POSTGRES_DB = os.getenv("POSTGRES_DB", default="mydatabase")
    POSTGRES_USER = os.getenv("POSTGRES_USER", default="user")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", default="password")
    REDIS_HOST = os.getenv("REDIS_HOST", default="jobber_redis")
    REDIS_PORT = os.getenv("REDIS_PORT", default="6379")
    REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}"

    # HARDCODED JOBBER URLS IN CONFIG
    jobber_api_url = "https://api.getjobber.com/api/graphql"
    jobber_tokens_url = "https://api.getjobber.com/api/oauth/token"