"""Cache service for TENJIN."""

from typing import Any

from ...infrastructure.adapters.redis_adapter import RedisAdapter
from ...infrastructure.config.logging import get_logger

logger = get_logger(__name__)


class CacheService:
    """Service for managing application cache."""

    # Cache key prefixes
    PREFIX_SEARCH = "search"
    PREFIX_THEORY = "theory"
    PREFIX_GRAPH = "graph"
    PREFIX_ANALYSIS = "analysis"
    PREFIX_RECOMMENDATION = "recommendation"

    def __init__(self, redis: RedisAdapter) -> None:
        """Initialize cache service.

        Args:
            redis: Redis adapter instance
        """
        self._redis = redis

    @property
    def is_available(self) -> bool:
        """Check if cache is available."""
        return self._redis.is_connected

    # ===========================================
    # Search Cache
    # ===========================================

    async def get_search_results(
        self,
        query: str,
        search_mode: str = "hybrid",
        limit: int = 10,
    ) -> list[dict[str, Any]] | None:
        """Get cached search results.

        Args:
            query: Search query
            search_mode: Search mode (semantic, keyword, graph, hybrid)
            limit: Result limit

        Returns:
            Cached results or None
        """
        key = f"{self.PREFIX_SEARCH}:{search_mode}:{limit}:{self._hash(query)}"
        return await self._redis.get_json(key)

    async def set_search_results(
        self,
        query: str,
        results: list[dict[str, Any]],
        search_mode: str = "hybrid",
        limit: int = 10,
        ttl: int | None = None,
    ) -> bool:
        """Cache search results.

        Args:
            query: Search query
            results: Search results
            search_mode: Search mode
            limit: Result limit
            ttl: Cache TTL

        Returns:
            True if cached
        """
        key = f"{self.PREFIX_SEARCH}:{search_mode}:{limit}:{self._hash(query)}"
        return await self._redis.set_json(key, results, ttl)

    # ===========================================
    # Theory Cache
    # ===========================================

    async def get_theory(self, theory_id: str) -> dict[str, Any] | None:
        """Get cached theory.

        Args:
            theory_id: Theory ID

        Returns:
            Cached theory or None
        """
        key = f"{self.PREFIX_THEORY}:{theory_id}"
        return await self._redis.get_json(key)

    async def set_theory(
        self,
        theory_id: str,
        theory: dict[str, Any],
        ttl: int | None = None,
    ) -> bool:
        """Cache theory.

        Args:
            theory_id: Theory ID
            theory: Theory data
            ttl: Cache TTL

        Returns:
            True if cached
        """
        key = f"{self.PREFIX_THEORY}:{theory_id}"
        return await self._redis.set_json(key, theory, ttl)

    async def invalidate_theory(self, theory_id: str) -> bool:
        """Invalidate cached theory.

        Args:
            theory_id: Theory ID

        Returns:
            True if invalidated
        """
        key = f"{self.PREFIX_THEORY}:{theory_id}"
        return await self._redis.delete(key)

    # ===========================================
    # Graph Cache
    # ===========================================

    async def get_graph_traversal(
        self,
        start_id: str,
        depth: int,
        relation_types: list[str] | None = None,
    ) -> dict[str, Any] | None:
        """Get cached graph traversal.

        Args:
            start_id: Starting node ID
            depth: Traversal depth
            relation_types: Relation type filter

        Returns:
            Cached traversal or None
        """
        rel_key = "_".join(sorted(relation_types)) if relation_types else "all"
        key = f"{self.PREFIX_GRAPH}:traverse:{start_id}:{depth}:{rel_key}"
        return await self._redis.get_json(key)

    async def set_graph_traversal(
        self,
        start_id: str,
        depth: int,
        result: dict[str, Any],
        relation_types: list[str] | None = None,
        ttl: int | None = None,
    ) -> bool:
        """Cache graph traversal.

        Args:
            start_id: Starting node ID
            depth: Traversal depth
            result: Traversal result
            relation_types: Relation type filter
            ttl: Cache TTL

        Returns:
            True if cached
        """
        rel_key = "_".join(sorted(relation_types)) if relation_types else "all"
        key = f"{self.PREFIX_GRAPH}:traverse:{start_id}:{depth}:{rel_key}"
        return await self._redis.set_json(key, result, ttl)

    # ===========================================
    # Analysis Cache (longer TTL for expensive operations)
    # ===========================================

    async def get_analysis(
        self,
        analysis_type: str,
        params_hash: str,
    ) -> dict[str, Any] | None:
        """Get cached analysis result.

        Args:
            analysis_type: Type of analysis
            params_hash: Hash of analysis parameters

        Returns:
            Cached analysis or None
        """
        key = f"{self.PREFIX_ANALYSIS}:{analysis_type}:{params_hash}"
        return await self._redis.get_json(key)

    async def set_analysis(
        self,
        analysis_type: str,
        params_hash: str,
        result: dict[str, Any],
        ttl: int = 7200,  # 2 hours default for analyses
    ) -> bool:
        """Cache analysis result.

        Args:
            analysis_type: Type of analysis
            params_hash: Hash of analysis parameters
            result: Analysis result
            ttl: Cache TTL (default 2 hours)

        Returns:
            True if cached
        """
        key = f"{self.PREFIX_ANALYSIS}:{analysis_type}:{params_hash}"
        return await self._redis.set_json(key, result, ttl)

    # ===========================================
    # Recommendation Cache
    # ===========================================

    async def get_recommendations(
        self,
        context_hash: str,
    ) -> list[dict[str, Any]] | None:
        """Get cached recommendations.

        Args:
            context_hash: Hash of recommendation context

        Returns:
            Cached recommendations or None
        """
        key = f"{self.PREFIX_RECOMMENDATION}:{context_hash}"
        return await self._redis.get_json(key)

    async def set_recommendations(
        self,
        context_hash: str,
        recommendations: list[dict[str, Any]],
        ttl: int | None = None,
    ) -> bool:
        """Cache recommendations.

        Args:
            context_hash: Hash of recommendation context
            recommendations: Recommendation results
            ttl: Cache TTL

        Returns:
            True if cached
        """
        key = f"{self.PREFIX_RECOMMENDATION}:{context_hash}"
        return await self._redis.set_json(key, recommendations, ttl)

    # ===========================================
    # Cache Management
    # ===========================================

    async def invalidate_all_searches(self) -> int:
        """Invalidate all search caches.

        Returns:
            Number of keys deleted
        """
        return await self._redis.delete_pattern(f"{self.PREFIX_SEARCH}:*")

    async def invalidate_all_theories(self) -> int:
        """Invalidate all theory caches.

        Returns:
            Number of keys deleted
        """
        return await self._redis.delete_pattern(f"{self.PREFIX_THEORY}:*")

    async def invalidate_all(self) -> bool:
        """Invalidate all caches.

        Returns:
            True if successful
        """
        return await self._redis.flush_all()

    async def get_stats(self) -> dict[str, Any]:
        """Get cache statistics.

        Returns:
            Cache statistics
        """
        return await self._redis.get_stats()

    def _hash(self, value: str) -> str:
        """Create hash of value.

        Args:
            value: Value to hash

        Returns:
            Short hash string
        """
        import hashlib
        return hashlib.sha256(value.encode()).hexdigest()[:16]
