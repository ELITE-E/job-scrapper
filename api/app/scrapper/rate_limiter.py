"""
Redis-based per-site rate limiting using sliding window counter.
"""

import os
import time
import logging
from typing import Optional

import redis

logger = logging.getLogger(__name__)


class RedisRateLimiter:
    """
    Sliding window rate limiter backed by Redis.
    Uses sorted sets to track request timestamps and enforce per-site limits.
    """

    def __init__(self, redis_url: Optional[str] = None):
        """
        Initialize rate limiter with Redis connection.

        Args:
            redis_url: Redis URL (defaults to REDIS_URL env var or redis://redis:6379/0)
        """
        url = redis_url or os.getenv("REDIS_URL", "redis://redis:6379/0")
        try:
            self.redis = redis.from_url(url, socket_timeout=5, socket_connect_timeout=5)
            # Test connection
            self.redis.ping()
            logger.info(f"✅ RedisRateLimiter connected to {url}")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Redis: {e}")
            self.redis = None

    def check_rate_limit(self, site_name: str, requests_per_minute: int) -> bool:
        """
        Check if a request for a site is allowed under the rate limit.

        Uses a sliding window: counts requests in the past 60 seconds.
        Returns False if limit exceeded; True if request is allowed.

        Args:
            site_name: Name of the job site (e.g., 'indeed', 'linkedin')
            requests_per_minute: Max requests allowed per minute

        Returns:
            True if request is allowed, False if rate limit exceeded
        """
        if self.redis is None:
            logger.warning("Redis unavailable, skipping rate limit check")
            return True

        try:
            key = f"rate_limit:{site_name}"
            now = time.time()
            window = 60  # seconds

            # Remove old entries outside the 60-second window
            self.redis.zremrangebyscore(key, 0, now - window)

            # Count current requests in the window
            current_count = self.redis.zcard(key)

            if current_count >= requests_per_minute:
                logger.warning(
                    f"Rate limit exceeded for {site_name}: "
                    f"{current_count}/{requests_per_minute} requests in last 60s"
                )
                return False

            # Add current request timestamp to the sorted set
            self.redis.zadd(key, {str(now): now})

            # Set expiration on the key (cleanup after 2 minutes to be safe)
            self.redis.expire(key, 120)

            logger.debug(
                f"Rate limit check passed for {site_name}: "
                f"{current_count + 1}/{requests_per_minute} requests"
            )
            return True

        except Exception as e:
            logger.error(f"Error checking rate limit for {site_name}: {e}")
            # Fail open: allow request if there's a Redis issue
            return True

    def reset_site(self, site_name: str) -> None:
        """Reset rate limit counter for a site (for testing or manual override)."""
        if self.redis is None:
            return

        try:
            key = f"rate_limit:{site_name}"
            self.redis.delete(key)
            logger.info(f"Reset rate limit for {site_name}")
        except Exception as e:
            logger.error(f"Error resetting rate limit for {site_name}: {e}")

    def get_current_count(self, site_name: str) -> int:
        """Get current request count for a site (for debugging)."""
        if self.redis is None:
            return 0

        try:
            key = f"rate_limit:{site_name}"
            now = time.time()
            window = 60
            # Clean old entries
            self.redis.zremrangebyscore(key, 0, now - window)
            return self.redis.zcard(key)
        except Exception as e:
            logger.error(f"Error getting rate limit count for {site_name}: {e}")
            return 0
