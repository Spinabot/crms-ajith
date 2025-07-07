import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    PORT = os.getenv('FLASK_PORT', '5000')
    FLASK_ENV = os.getenv("FLASK_ENV", "development")

    # Database Configuration
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_NAME = os.getenv('DB_NAME', 'leads_db')
    DB_PORT = os.getenv('DB_PORT', '5432')

    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI') or \
        f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')
    API_KEY = os.getenv('API_KEY')

    # BuilderPrime CRM Configuration
    BUILDER_PRIME_API_KEY = os.getenv('BUILDER_PRIME_API_KEY')

    # HubSpot CRM Configuration
    HUBSPOT_API_TOKEN = os.getenv('HUBSPOT_API_TOKEN')
    HUBSPOT_API_BASE_URL = os.getenv('HUBSPOT_API_BASE_URL', 'https://api.hubapi.com')
    HUBSPOT_CLIENT_ID = os.getenv('HUBSPOT_CLIENT_ID')
    HUBSPOT_CLIENT_SECRET = os.getenv('HUBSPOT_CLIENT_SECRET')

    # Jobber CRM Configuration
    JOBBER_CLIENT_ID = os.getenv('JOBBER_CLIENT_ID')
    JOBBER_CLIENT_SECRET = os.getenv('JOBBER_CLIENT_SECRET')
    JOBBER_REDIRECT_URI = os.getenv('JOBBER_REDIRECT_URI')
    JOBBER_API_URL = os.getenv('JOBBER_API_URL', 'https://api.getjobber.com/api/graphql')
    JOBBER_TOKENS_URL = os.getenv('JOBBER_TOKENS_URL', 'https://api.getjobber.com/api/oauth/token')

    # JobNimbus CRM Configuration
    JOBNIMBUS_API_KEY = os.getenv('JOBNIMBUS_API_KEY')

    # Zoho CRM Configuration
    ZOHO_CLIENT_ID = os.getenv('ZOHO_CLIENT_ID')
    ZOHO_CLIENT_SECRET = os.getenv('ZOHO_CLIENT_SECRET')
    ZOHO_REDIRECT_URI = os.getenv('ZOHO_REDIRECT_URI')

    # Redis Configuration
    CACHE_TYPE = "RedisCache"
    CACHE_REDIS_HOST = os.getenv("REDIS_HOST", "redis")
    CACHE_REDIS_PORT = os.getenv("REDIS_PORT", 6379)
    CACHE_DEFAULT_TIMEOUT = os.getenv("CACHE_DEFAULT_TIMEOUT", 300)

    # Rate Limiting
    RATELIMIT_HEADERS_ENABLED = True
    DEFAULT_RATELIMIT = "5 per minute"

    DEBUG = os.getenv('FLASK_DEBUG', '0') == '1'
    TESTING = False