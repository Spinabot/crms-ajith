import os
from dotenv import load_dotenv

load_dotenv()  # Loads variables from .env into os.environ

class Config:
    # Authentication and Third-party Services
    client_id = os.getenv("ZOHO_CLIENT_ID", "default_client_id")
    client_secret = os.getenv("ZOHO_CLIENT_SECRET", "default_client_secret")
    redirect_uri = os.getenv("ZOHO_REDIRECT_URI", "default_redirect_uri")
    
    # Database Configuration
    database_name = os.getenv("DATABASE_NAME", "postgres")
    database_user = os.getenv("DB_USER", "postgres")
    database_pass = os.getenv("DB_PASSWORD", "")
    database_host = os.getenv("CONNECTION_NAME", "localhost")
    SQLALCHEMY_DATABASE_URI = f"postgresql://{database_user}:{database_pass}@{database_host}/{database_name}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Application Secret
    SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")
    
    # Redis Configuration
    redis_host = os.getenv("CACHE_REDIS_HOST", "localhost")
    redis_port = os.getenv("CACHE_REDIS_PORT", "6379")
    redis_username = os.getenv("CACHE_REDIS_USERNAME", "redis")
    redis_password = os.getenv("CACHE_REDIS_PASSWORD", "redis")
    
    # Gunicorn Configuration
    gunicorn_workers = os.getenv("GUNICORN_WORKERS", "2")
    gunicorn_bind = os.getenv("GUNICORN_BIND", "0.0.0.0:8080")
    gunicorn_worker_class = os.getenv("GUNICORN_WORKER_CLASS", "gevent")

    # Rate Limiting
    ratelimit_headers_enabled = os.getenv("RATELIMIT_HEADERS_ENABLED", "True")
    default_ratelimit = os.getenv("DEFAULT_RATELIMIT", "200 per day, 50 per hour")