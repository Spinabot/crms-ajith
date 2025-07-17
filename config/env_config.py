import os
from dotenv import load_dotenv

# load .env ONLY if FLASK_ENV=local
if os.getenv("FLASK_ENV") == "local":
    load_dotenv()

class Config:
    """Base config (defaults)"""
    DEBUG = False
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    VAULT_ADDR = os.getenv("VAULT_ADDR")
    VAULT_TOKEN = os.getenv("VAULT_TOKEN")
    VAULT_SECRET_PATH = os.getenv("VAULT_SECRET_PATH")


class LocalConfig(Config):
    """Local dev config"""
    DEBUG = True


class DevConfig(Config):
    """Development (remote dev)"""
    pass


class QAConfig(Config):
    """QA config"""
    pass


class ProdConfig(Config):
    """Production config"""
    pass


config_by_name = {
    'local': LocalConfig,
    'dev': DevConfig,
    'qa': QAConfig,
    'prod': ProdConfig
}