"""
Redis Client Configuration and Connection Pool
Provides centralized Redis connection management with best practices
"""

import redis.asyncio as redis
from redis.asyncio.connection import ConnectionPool
from typing import Optional
import logging
import json
from .config import REDIS_URL, REDIS_ENABLED, REDIS_MAX_CONNECTIONS

logger = logging.getLogger("mediconnect")


class RedisClient:
    """
    Singleton Redis client with connection pooling and error handling.
    
    Best Practices Implemented:
    - Connection pooling for efficient resource usage
    - Async/await support for non-blocking operations
    - Automatic reconnection on connection failures
    - Graceful degradation when Redis is unavailable
    - JSON serialization for complex data types
    """
    
    _instance: Optional['RedisClient'] = None
    _pool: Optional[ConnectionPool] = None
    _client: Optional[redis.Redis] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    async def initialize(self):
        """
        Initialize Redis connection pool.
        Should be called during application startup.
        """
        if not REDIS_ENABLED:
            logger.warning("⚠️ Redis is disabled. Caching will not be available.")
            return
        
        try:
            # Create connection pool
            self._pool = ConnectionPool.from_url(
                REDIS_URL,
                max_connections=REDIS_MAX_CONNECTIONS,
                decode_responses=True,
                encoding="utf-8",
                socket_connect_timeout=5,
                socket_keepalive=True,
                health_check_interval=30
            )
            
            # Create Redis client
            self._client = redis.Redis(connection_pool=self._pool)
            
            # Test connection
            await self._client.ping()
            logger.info(f"✅ Redis connected successfully at {REDIS_URL}")
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to Redis: {e}")
            logger.warning("⚠️ Application will continue without caching")
            self._client = None
            self._pool = None
    
    async def close(self):
        """
        Close Redis connection pool.
        Should be called during application shutdown.
        """
        if self._client:
            await self._client.close()
            logger.info("✅ Redis connection closed")
        
        if self._pool:
            await self._pool.disconnect()
            logger.info("✅ Redis connection pool closed")
    
    def is_available(self) -> bool:
        """Check if Redis is available."""
        return REDIS_ENABLED and self._client is not None
    
    async def get(self, key: str) -> Optional[str]:
        """
        Get value from Redis.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found or Redis unavailable
        """
        if not self.is_available():
            return None
        
        try:
            value = await self._client.get(key)
            if value:
                logger.debug(f"Cache HIT: {key}")
            else:
                logger.debug(f"Cache MISS: {key}")
            return value
        except Exception as e:
            logger.error(f"Redis GET error for key '{key}': {e}")
            return None
    
    async def set(
        self,
        key: str,
        value: str,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Set value in Redis with optional TTL.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (None for no expiration)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_available():
            return False
        
        try:
            if ttl:
                await self._client.setex(key, ttl, value)
            else:
                await self._client.set(key, value)
            logger.debug(f"Cache SET: {key} (TTL: {ttl}s)")
            return True
        except Exception as e:
            logger.error(f"Redis SET error for key '{key}': {e}")
            return False
    
    async def delete(self, *keys: str) -> int:
        """
        Delete one or more keys from Redis.
        
        Args:
            keys: Keys to delete
            
        Returns:
            Number of keys deleted
        """
        if not self.is_available() or not keys:
            return 0
        
        try:
            deleted = await self._client.delete(*keys)
            logger.debug(f"Cache DELETE: {keys} ({deleted} deleted)")
            return deleted
        except Exception as e:
            logger.error(f"Redis DELETE error for keys {keys}: {e}")
            return 0
    
    async def exists(self, *keys: str) -> int:
        """
        Check if keys exist in Redis.
        
        Args:
            keys: Keys to check
            
        Returns:
            Number of existing keys
        """
        if not self.is_available() or not keys:
            return 0
        
        try:
            return await self._client.exists(*keys)
        except Exception as e:
            logger.error(f"Redis EXISTS error for keys {keys}: {e}")
            return 0
    
    async def expire(self, key: str, ttl: int) -> bool:
        """
        Set expiration time for a key.
        
        Args:
            key: Cache key
            ttl: Time to live in seconds
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_available():
            return False
        
        try:
            return await self._client.expire(key, ttl)
        except Exception as e:
            logger.error(f"Redis EXPIRE error for key '{key}': {e}")
            return False
    
    async def incr(self, key: str, amount: int = 1) -> Optional[int]:
        """
        Increment a counter in Redis.
        
        Args:
            key: Counter key
            amount: Amount to increment by
            
        Returns:
            New value or None if error
        """
        if not self.is_available():
            return None
        
        try:
            return await self._client.incrby(key, amount)
        except Exception as e:
            logger.error(f"Redis INCR error for key '{key}': {e}")
            return None
    
    async def get_json(self, key: str) -> Optional[dict]:
        """
        Get JSON value from Redis.
        
        Args:
            key: Cache key
            
        Returns:
            Deserialized JSON or None
        """
        value = await self.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error for key '{key}': {e}")
        return None
    
    async def set_json(
        self,
        key: str,
        value: dict,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Set JSON value in Redis.
        
        Args:
            key: Cache key
            value: Dictionary to cache
            ttl: Time to live in seconds
            
        Returns:
            True if successful, False otherwise
        """
        try:
            json_str = json.dumps(value)
            return await self.set(key, json_str, ttl)
        except (TypeError, ValueError) as e:
            logger.error(f"JSON encode error for key '{key}': {e}")
            return False
    
    async def delete_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching a pattern.
        
        Args:
            pattern: Pattern to match (e.g., "user:*")
            
        Returns:
            Number of keys deleted
        """
        if not self.is_available():
            return 0
        
        try:
            keys = []
            async for key in self._client.scan_iter(match=pattern, count=100):
                keys.append(key)
            
            if keys:
                deleted = await self.delete(*keys)
                logger.info(f"Cache PATTERN DELETE: {pattern} ({deleted} keys)")
                return deleted
            return 0
        except Exception as e:
            logger.error(f"Redis PATTERN DELETE error for pattern '{pattern}': {e}")
            return 0
    
    async def get_client(self) -> Optional[redis.Redis]:
        """
        Get raw Redis client for advanced operations.
        
        Returns:
            Redis client or None if unavailable
        """
        return self._client if self.is_available() else None


# Global Redis client instance
redis_client = RedisClient()


async def get_redis() -> RedisClient:
    """
    Dependency injection function for FastAPI.
    
    Usage:
        @app.get("/endpoint")
        async def endpoint(redis: RedisClient = Depends(get_redis)):
            await redis.set("key", "value")
    """
    return redis_client
