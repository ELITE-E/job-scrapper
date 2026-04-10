from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.extension import _rate_limit_exceeded_handler

from slowapi.storage import RedisStorage


# 🔹 Redis-backed (recommended for production)
storage = RedisStorage("redis://localhost:6379")

limiter = Limiter(
    key_func=get_remote_address,
    storage=storage
)