"""
Caching Service with Decorators
Provides easy-to-use caching decorators and utilities
"""

import functools
import hashlib
import json
from typing import Optional, Callable, Any
import logging
from ..redis_client import redis_client
from ..config import REDIS_CACHE_TTL

logger = logging.getLogger("mediconnect")


def generate_cache_key(prefix: str, *args, **kwargs) -> str:
    """
    Generate a unique cache key based on function arguments.
    
    Args:
        prefix: Key prefix (usually function name)
        args: Positional arguments
        kwargs: Keyword arguments
        
    Returns:
        Unique cache key
    """
    # Create a string representation of arguments
    key_parts = [prefix]
    
    # Add positional arguments
    for arg in args:
        if hasattr(arg, '__dict__'):
            # For objects, use their dict representation
            key_parts.append(str(sorted(arg.__dict__.items())))
        else:
            key_parts.append(str(arg))
    
    # Add keyword arguments (sorted for consistency)
    for k, v in sorted(kwargs.items()):
        if hasattr(v, '__dict__'):
            key_parts.append(f"{k}:{sorted(v.__dict__.items())}")
        else:
            key_parts.append(f"{k}:{v}")
    
    # Create hash for long keys
    key_str = ":".join(key_parts)
    if len(key_str) > 200:
        # Use hash for very long keys
        key_hash = hashlib.md5(key_str.encode()).hexdigest()
        return f"{prefix}:{key_hash}"
    
    return key_str


def cache(
    ttl: Optional[int] = None,
    key_prefix: Optional[str] = None,
    skip_cache_if: Optional[Callable] = None
):
    """
    Decorator to cache function results in Redis.
    
    Args:
        ttl: Time to live in seconds (default: REDIS_CACHE_TTL)
        key_prefix: Custom key prefix (default: function name)
        skip_cache_if: Function to determine if caching should be skipped
        
    Usage:
        @cache(ttl=300)
        async def get_user(user_id: str):
            return await db.users.find_one({"user_id": user_id})
        
        @cache(ttl=60, key_prefix="doctor_list")
        async def get_doctors(clinic_id: str):
            return await db.doctors.find({"clinic_id": clinic_id}).to_list(100)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Check if caching should be skipped
            if skip_cache_if and skip_cache_if(*args, **kwargs):
                return await func(*args, **kwargs)
            
            # Generate cache key
            prefix = key_prefix or f"{func.__module__}.{func.__name__}"
            cache_key = generate_cache_key(prefix, *args, **kwargs)
            
            # Try to get from cache
            cached_value = await redis_client.get_json(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return cached_value
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Cache result
            cache_ttl = ttl or REDIS_CACHE_TTL
            await redis_client.set_json(cache_key, result, cache_ttl)
            logger.debug(f"Cached result for {cache_key} (TTL: {cache_ttl}s)")
            
            return result
        
        return wrapper
    return decorator


def cache_invalidate(pattern: str):
    """
    Decorator to invalidate cache after function execution.
    
    Args:
        pattern: Cache key pattern to invalidate (e.g., "doctors:*")
        
    Usage:
        @cache_invalidate("doctors:*")
        async def create_doctor(data: DoctorCreate):
            # Create doctor logic
            return doctor
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Execute function
            result = await func(*args, **kwargs)
            
            # Invalidate cache
            deleted = await redis_client.delete_pattern(pattern)
            if deleted > 0:
                logger.info(f"Invalidated {deleted} cache keys matching '{pattern}'")
            
            return result
        
        return wrapper
    return decorator


class CacheManager:
    """
    Cache manager for manual cache operations.
    
    Usage:
        cache_mgr = CacheManager("doctors")
        
        # Get from cache
        doctor = await cache_mgr.get(doctor_id)
        
        # Set cache
        await cache_mgr.set(doctor_id, doctor_data, ttl=300)
        
        # Invalidate cache
        await cache_mgr.invalidate(doctor_id)
        await cache_mgr.invalidate_all()
    """
    
    def __init__(self, namespace: str):
        """
        Initialize cache manager.
        
        Args:
            namespace: Cache namespace (e.g., "doctors", "appointments")
        """
        self.namespace = namespace
    
    def _make_key(self, key: str) -> str:
        """Generate namespaced cache key."""
        return f"{self.namespace}:{key}"
    
    async def get(self, key: str) -> Optional[dict]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None
        """
        cache_key = self._make_key(key)
        return await redis_client.get_json(cache_key)
    
    async def set(
        self,
        key: str,
        value: dict,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
            
        Returns:
            True if successful
        """
        cache_key = self._make_key(key)
        cache_ttl = ttl or REDIS_CACHE_TTL
        return await redis_client.set_json(cache_key, value, cache_ttl)
    
    async def delete(self, key: str) -> int:
        """
        Delete value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Number of keys deleted
        """
        cache_key = self._make_key(key)
        return await redis_client.delete(cache_key)
    
    async def invalidate_all(self) -> int:
        """
        Invalidate all cache entries in this namespace.
        
        Returns:
            Number of keys deleted
        """
        pattern = f"{self.namespace}:*"
        return await redis_client.delete_pattern(pattern)
    
    async def exists(self, key: str) -> bool:
        """
        Check if key exists in cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if exists
        """
        cache_key = self._make_key(key)
        return await redis_client.exists(cache_key) > 0


# Pre-configured cache managers for common entities
doctors_cache = CacheManager("doctors")
appointments_cache = CacheManager("appointments")
clinics_cache = CacheManager("clinics")
locations_cache = CacheManager("locations")
users_cache = CacheManager("users")
services_cache = CacheManager("services")
stats_cache = CacheManager("stats")


async def warm_cache(func: Callable, *args, **kwargs):
    """
    Warm up cache by pre-loading data.
    
    Args:
        func: Function to execute
        args: Positional arguments
        kwargs: Keyword arguments
        
    Usage:
        # Warm up doctors cache on startup
        await warm_cache(get_all_doctors)
    """
    try:
        logger.info(f"Warming cache for {func.__name__}")
        await func(*args, **kwargs)
        logger.info(f"Cache warmed for {func.__name__}")
    except Exception as e:
        logger.error(f"Failed to warm cache for {func.__name__}: {e}")


async def clear_all_cache():
    """
    Clear all application cache.
    Use with caution!
    """
    try:
        client = await redis_client.get_client()
        if client:
            await client.flushdb()
            logger.warning("⚠️ All cache cleared!")
            return True
    except Exception as e:
        logger.error(f"Failed to clear cache: {e}")
    return False
