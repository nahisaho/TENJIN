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
        
        # Extended filters
        year_from = arguments.get("year_from")
        year_to = arguments.get("year_to")
        decade = arguments.get("decade")
        evidence_level = arguments.get("evidence_level")

        categories = [category] if category else None

        result = await tenjin.search_service.search(
            query=query,
            search_type=search_type,
            categories=categories,
            limit=limit,
            year_from=year_from,
            year_to=year_to,
            decade=decade,
            evidence_level=evidence_level,
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

    @server.call_tool()
    async def batch_search(arguments: dict[str, Any]) -> list[TextContent]:
        """Perform multiple searches in batch."""
        import json

        queries = arguments.get("queries", [])
        default_search_type = arguments.get("default_search_type", "hybrid")
        default_limit = arguments.get("default_limit", 5)

        result = await tenjin.search_service.batch_search(
            queries=queries,
            default_search_type=default_search_type,
            default_limit=default_limit,
        )
        return [TextContent(
            type="text",
            text=json.dumps(result, ensure_ascii=False, indent=2)
        )]


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
                    "year_from": {
                        "type": "integer",
                        "description": "Filter theories from this year (e.g., 1990)",
                    },
                    "year_to": {
                        "type": "integer",
                        "description": "Filter theories up to this year (e.g., 2020)",
                    },
                    "decade": {
                        "type": "string",
                        "description": "Filter by decade (e.g., '1990s', '2000s')",
                    },
                    "evidence_level": {
                        "type": "string",
                        "enum": ["high", "medium", "low"],
                        "description": "Filter by evidence level",
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
        Tool(
            name="batch_search",
            description="""Execute multiple search queries in a single request.

Useful for:
- Searching multiple related topics at once
- Comparing search results across different queries
- Finding common theories across multiple learning objectives

Returns individual results plus aggregations showing common theories.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "queries": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "Search query text",
                                },
                                "search_type": {
                                    "type": "string",
                                    "enum": ["hybrid", "semantic", "keyword"],
                                    "description": "Search type for this query",
                                },
                                "limit": {
                                    "type": "integer",
                                    "description": "Max results for this query",
                                },
                                "categories": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Category filters",
                                },
                            },
                            "required": ["query"],
                        },
                        "description": "List of search queries to execute",
                    },
                    "default_search_type": {
                        "type": "string",
                        "enum": ["hybrid", "semantic", "keyword"],
                        "description": "Default search type",
                        "default": "hybrid",
                    },
                    "default_limit": {
                        "type": "integer",
                        "description": "Default max results per query",
                        "default": 5,
                    },
                },
                "required": ["queries"],
            },
        ),
    ]
