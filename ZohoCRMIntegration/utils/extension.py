#contains common parts for blueprints like redis conncetion 
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import redis
from config import Config 
redis_client = redis.Redis(
    host=Config.redis_host,
    port=Config.redis_port,
    db=0)

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=f"redis://{Config.redis_host}:{Config.redis_port}"
)
