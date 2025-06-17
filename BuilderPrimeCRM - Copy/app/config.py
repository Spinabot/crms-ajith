import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    PORT = os.getenv('FLASK_PORT', '5050')
    FLASK_ENV = os.getenv("FLASK_ENV", "development")

    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_NAME = os.getenv('DB_NAME', 'leads_db')
    DB_PORT = os.getenv('DB_PORT', '5432')
    
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI') or \
        f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')
    API_KEY = os.getenv('API_KEY')
    
    WTF_CSRF_ENABLED = True

    CACHE_TYPE = "RedisCache"
    CACHE_REDIS_HOST = os.getenv("REDIS_HOST", "redis")
    CACHE_REDIS_PORT = os.getenv("REDIS_PORT", 6379)
    CACHE_DEFAULT_TIMEOUT = os.getenv("CACHE_DEFAULT_TIMEOUT", 300)
    
    RATELIMIT_HEADERS_ENABLED = True
    DEFAULT_RATELIMIT = "5 per minute"

    DEBUG = os.getenv('FLASK_DEBUG', '0') == '1'
    TESTING = False