"""MCP Tools registration - Search tools."""

from typing import Any
from mcp.server import Server
from mcp.types import Tool, TextContent

from ..server import TenjinServer
from ...infrastructure.config.logging import get_logger

logger = get_logger(__name__)


def register_search_tools(server: Server, tenjin: TenjinServer) -> None:
    """Register search-related MCP tools.

    Args:
        server: MCP server instance.
        tenjin: TENJIN server instance.
    """

    @server.call_tool()
    async def search_theories(arguments: dict[str, Any]) -> list[TextContent]:
        """Search theories using hybrid search (graph + vector)."""
        query = arguments.get("query", "")
        search_type = arguments.get("search_type", "hybrid")
        limit = arguments.get("limit", 10)
        category = arguments.get("category")

        filters = {"category": category} if category else None

        result = await tenjin.search_service.search(
            query=query,
            search_type=search_type,
            limit=limit,
            filters=filters,
        )
        return [TextContent(type="text", text=str(result))]

    @server.call_tool()
    async def semantic_search(arguments: dict[str, Any]) -> list[TextContent]:
        """Perform semantic search across theories."""
        query = arguments.get("query", "")
        limit = arguments.get("limit", 10)

        result = await tenjin.search_service.semantic_search(
            query=query,
            limit=limit,
        )
        return [TextContent(type="text", text=str(result))]

    @server.call_tool()
    async def find_similar_theories(arguments: dict[str, Any]) -> list[TextContent]:
        """Find theories similar to a given theory."""
        theory_id = arguments.get("theory_id", "")
        limit = arguments.get("limit", 5)

        result = await tenjin.search_service.find_similar(
            theory_id=theory_id,
            limit=limit,
        )
        return [TextContent(type="text", text=str(result))]

    @server.call_tool()
    async def search_with_reranking(arguments: dict[str, Any]) -> list[TextContent]:
        """Search with LLM reranking for improved relevance."""
        query = arguments.get("query", "")
        limit = arguments.get("limit", 10)

        result = await tenjin.search_service.search_with_reranking(
            query=query,
            limit=limit,
        )
        return [TextContent(type="text", text=str(result))]

    @server.call_tool()
    async def search_concepts(arguments: dict[str, Any]) -> list[TextContent]:
        """Search for concepts across theories."""
        query = arguments.get("query", "")
        limit = arguments.get("limit", 10)

        result = await tenjin.search_service.search_concepts(
            query=query,
            limit=limit,
        )
        return [TextContent(type="text", text=str(result))]


def get_search_tool_definitions() -> list[Tool]:
    """Get search tool definitions."""
    return [
        Tool(
            name="search_theories",
            description="Search educational theories using hybrid search combining graph relationships and semantic similarity. Best for finding relevant theories for a teaching context.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (natural language)",
                    },
                    "search_type": {
                        "type": "string",
                        "enum": ["hybrid", "semantic", "keyword"],
                        "description": "Type of search to perform",
                        "default": "hybrid",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum results to return",
                        "default": 10,
                    },
                    "category": {
                        "type": "string",
                        "description": "Filter by category (optional)",
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="semantic_search",
            description="Perform pure semantic search to find theories based on meaning similarity. Best for conceptual queries.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Natural language query",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum results",
                        "default": 10,
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="find_similar_theories",
            description="Find theories similar to a specific theory based on content and relationships.",
            inputSchema={
                "type": "object",
                "properties": {
                    "theory_id": {
                        "type": "string",
                        "description": "ID of the reference theory",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum similar theories",
                        "default": 5,
                    },
                },
                "required": ["theory_id"],
            },
        ),
        Tool(
            name="search_with_reranking",
            description="Advanced search with LLM-based reranking for highest relevance. Use for complex queries where precision matters.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Complex search query",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum results",
                        "default": 10,
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="search_concepts",
            description="Search for specific educational concepts across all theories.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Concept to search for",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum results",
                        "default": 10,
                    },
                },
                "required": ["query"],
            },
        ),
    ]
