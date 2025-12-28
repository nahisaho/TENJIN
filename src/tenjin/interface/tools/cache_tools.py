"""MCP Tools registration - Cache management tools."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from mcp.server import Server
from mcp.types import TextContent, Tool

from ...infrastructure.config.logging import get_logger

if TYPE_CHECKING:
    from ..server import TenjinServer

logger = get_logger(__name__)


def register_cache_tools(server: Server, tenjin: TenjinServer) -> None:
    """Register cache management tools.

    Args:
        server: MCP server instance.
        tenjin: TENJIN server instance.
    """

    @server.call_tool()
    async def get_cache_stats(arguments: dict[str, Any]) -> list[TextContent]:
        """Get Redis cache statistics."""
        redis = tenjin.redis_adapter
        if not redis:
            return [
                TextContent(
                    type="text",
                    text="Cache is not enabled or Redis is not available.",
                )
            ]

        try:
            stats = await redis.get_stats()
            result = {
                "status": "connected" if redis._client else "disconnected",
                "statistics": stats,
            }
            return [
                TextContent(
                    type="text",
                    text=json.dumps(result, indent=2, ensure_ascii=False),
                )
            ]
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return [
                TextContent(
                    type="text",
                    text=f"Error getting cache stats: {str(e)}",
                )
            ]

    @server.call_tool()
    async def invalidate_cache(arguments: dict[str, Any]) -> list[TextContent]:
        """Invalidate cached data by pattern."""
        pattern = arguments.get("pattern", "*")

        cache_service = tenjin.cache_service
        redis = tenjin.redis_adapter
        if not cache_service or not redis:
            return [
                TextContent(
                    type="text",
                    text="Cache is not enabled or Redis is not available.",
                )
            ]

        try:
            if pattern == "*":
                await cache_service.invalidate_all()
                deleted = -1  # All keys deleted
            else:
                deleted = await redis.delete_pattern(pattern)
            result = {
                "success": True,
                "pattern": pattern,
                "deleted_keys": deleted,
            }
            return [
                TextContent(
                    type="text",
                    text=json.dumps(result, indent=2, ensure_ascii=False),
                )
            ]
        except Exception as e:
            logger.error(f"Failed to invalidate cache: {e}")
            return [
                TextContent(
                    type="text",
                    text=f"Error invalidating cache: {str(e)}",
                )
            ]


def get_cache_tool_definitions(tenjin: TenjinServer) -> list[Tool]:
    """Get cache tool definitions.

    Args:
        tenjin: TENJIN server instance to check if cache is available.

    Returns:
        List of cache tool definitions (empty if cache not available).
    """
    # Only return cache tools if Redis is available
    if not tenjin.redis_adapter:
        return []

    return [
        Tool(
            name="get_cache_stats",
            description=(
                "Get Redis cache statistics including memory usage, "
                "key counts, and hit/miss information."
            ),
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        Tool(
            name="invalidate_cache",
            description=(
                "Invalidate cached data by pattern. "
                "Use 'search:*' to clear search caches, "
                "'theory:*' for theory caches, or '*' for all."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": (
                            "Key pattern to invalidate (supports wildcards). "
                            "Default: '*' for all keys."
                        ),
                        "default": "*",
                    },
                },
                "required": [],
            },
        ),
    ]
