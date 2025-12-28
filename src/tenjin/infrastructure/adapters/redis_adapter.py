"""Redis cache adapter for TENJIN."""

import json
import hashlib
from typing import Any, TypeVar, Generic
from dataclasses import dataclass

import redis.asyncio as redis
from redis.asyncio.connection import ConnectionPool

from ..config.logging import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


@dataclass
class CacheEntry(Generic[T]):
    """Cache entry with metadata."""

    key: str
    value: T
    ttl: int | None = None


class RedisAdapter:
    """Redis adapter for caching operations."""

    def __init__(
        self,
        url: str = "redis://localhost:6379",
        default_ttl: int = 3600,
        key_prefix: str = "tenjin:",
    ) -> None:
        """Initialize Redis adapter.

        Args:
            url: Redis connection URL
            default_ttl: Default TTL in seconds
            key_prefix: Prefix for all cache keys
        """
        self._url = url
        self._default_ttl = default_ttl
        self._key_prefix = key_prefix
        self._pool: ConnectionPool | None = None
        self._client: redis.Redis | None = None
        self._connected = False

    async def connect(self) -> None:
        """Connect to Redis."""
        if self._connected:
            return

        try:
            self._pool = ConnectionPool.from_url(self._url, decode_responses=True)
            self._client = redis.Redis(connection_pool=self._pool)
            # Test connection
            await self._client.ping()
            self._connected = True
            logger.info(f"Connected to Redis at {self._url}")
        except Exception as e:
            logger.warning(f"Failed to connect to Redis: {e}. Cache will be disabled.")
            self._connected = False

    async def close(self) -> None:
        """Close Redis connection."""
        if self._client:
            await self._client.close()
        if self._pool:
            await self._pool.disconnect()
        self._connected = False
        logger.info("Redis connection closed")

    @property
    def is_connected(self) -> bool:
        """Check if connected to Redis."""
        return self._connected

    def _make_key(self, key: str) -> str:
        """Create prefixed cache key."""
        return f"{self._key_prefix}{key}"

    def _hash_key(self, *args: Any, **kwargs: Any) -> str:
        """Create hash key from arguments."""
        key_data = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True)
        return hashlib.sha256(key_data.encode()).hexdigest()[:16]

    async def get(self, key: str) -> str | None:
        """Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        if not self._connected or not self._client:
            return None

        try:
            full_key = self._make_key(key)
            value = await self._client.get(full_key)
            if value:
                logger.debug(f"Cache hit: {key}")
            return value
        except Exception as e:
            logger.warning(f"Cache get error: {e}")
            return None

    async def get_json(self, key: str) -> Any | None:
        """Get JSON value from cache.

        Args:
            key: Cache key

        Returns:
            Parsed JSON value or None
        """
        value = await self.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return None
        return None

    async def set(
        self,
        key: str,
        value: str,
        ttl: int | None = None,
    ) -> bool:
        """Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: TTL in seconds (uses default if not specified)

        Returns:
            True if successful
        """
        if not self._connected or not self._client:
            return False

        try:
            full_key = self._make_key(key)
            ttl = ttl or self._default_ttl
            await self._client.set(full_key, value, ex=ttl)
            logger.debug(f"Cache set: {key} (TTL: {ttl}s)")
            return True
        except Exception as e:
            logger.warning(f"Cache set error: {e}")
            return False

    async def set_json(
        self,
        key: str,
        value: Any,
        ttl: int | None = None,
    ) -> bool:
        """Set JSON value in cache.

        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized)
            ttl: TTL in seconds

        Returns:
            True if successful
        """
        try:
            json_value = json.dumps(value, ensure_ascii=False, default=str)
            return await self.set(key, json_value, ttl)
        except (TypeError, ValueError) as e:
            logger.warning(f"JSON serialization error: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete key from cache.

        Args:
            key: Cache key

        Returns:
            True if deleted
        """
        if not self._connected or not self._client:
            return False

        try:
            full_key = self._make_key(key)
            result = await self._client.delete(full_key)
            return result > 0
        except Exception as e:
            logger.warning(f"Cache delete error: {e}")
            return False

    async def delete_pattern(self, pattern: str) -> int:
        """Delete keys matching pattern.

        Args:
            pattern: Key pattern (e.g., "search:*")

        Returns:
            Number of keys deleted
        """
        if not self._connected or not self._client:
            return 0

        try:
            full_pattern = self._make_key(pattern)
            keys = []
            async for key in self._client.scan_iter(match=full_pattern):
                keys.append(key)
            if keys:
                return await self._client.delete(*keys)
            return 0
        except Exception as e:
            logger.warning(f"Cache delete pattern error: {e}")
            return 0

    async def exists(self, key: str) -> bool:
        """Check if key exists.

        Args:
            key: Cache key

        Returns:
            True if exists
        """
        if not self._connected or not self._client:
            return False

        try:
            full_key = self._make_key(key)
            return await self._client.exists(full_key) > 0
        except Exception as e:
            logger.warning(f"Cache exists error: {e}")
            return False

    async def ttl(self, key: str) -> int:
        """Get TTL of key.

        Args:
            key: Cache key

        Returns:
            TTL in seconds, -1 if no TTL, -2 if not exists
        """
        if not self._connected or not self._client:
            return -2

        try:
            full_key = self._make_key(key)
            return await self._client.ttl(full_key)
        except Exception as e:
            logger.warning(f"Cache ttl error: {e}")
            return -2

    async def flush_all(self) -> bool:
        """Flush all keys with prefix.

        Returns:
            True if successful
        """
        return await self.delete_pattern("*") >= 0

    async def get_stats(self) -> dict[str, Any]:
        """Get cache statistics.

        Returns:
            Cache statistics dictionary
        """
        if not self._connected or not self._client:
            return {"connected": False}

        try:
            info = await self._client.info("stats")
            memory = await self._client.info("memory")

            # Count keys with our prefix
            key_count = 0
            async for _ in self._client.scan_iter(match=f"{self._key_prefix}*"):
                key_count += 1

            return {
                "connected": True,
                "keys": key_count,
                "hits": info.get("keyspace_hits", 0),
                "misses": info.get("keyspace_misses", 0),
                "memory_used": memory.get("used_memory_human", "unknown"),
            }
        except Exception as e:
            logger.warning(f"Cache stats error: {e}")
            return {"connected": True, "error": str(e)}


class CacheDecorator:
    """Decorator for caching function results."""

    def __init__(self, adapter: RedisAdapter, prefix: str = "", ttl: int | None = None) -> None:
        """Initialize cache decorator.

        Args:
            adapter: Redis adapter instance
            prefix: Key prefix for this decorator
            ttl: TTL override
        """
        self._adapter = adapter
        self._prefix = prefix
        self._ttl = ttl

    def __call__(self, func):
        """Decorate async function with caching."""
        import functools

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            if not self._adapter.is_connected:
                return await func(*args, **kwargs)

            # Generate cache key
            key = f"{self._prefix}:{func.__name__}:{self._adapter._hash_key(*args[1:], **kwargs)}"

            # Try to get from cache
            cached = await self._adapter.get_json(key)
            if cached is not None:
                return cached

            # Execute function
            result = await func(*args, **kwargs)

            # Cache result
            await self._adapter.set_json(key, result, self._ttl)

            return result

        return wrapper
