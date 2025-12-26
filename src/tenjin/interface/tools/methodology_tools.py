"""MCP Tools registration - Methodology tools."""

from typing import Any
from mcp.server import Server
from mcp.types import Tool, TextContent

from ..server import TenjinServer
from ...infrastructure.config.logging import get_logger

logger = get_logger(__name__)


def register_methodology_tools(server: Server, tenjin: TenjinServer) -> None:
    """Register methodology-related MCP tools.

    Args:
        server: MCP server instance.
        tenjin: TENJIN server instance.
    """

    @server.call_tool()
    async def get_methodology(arguments: dict[str, Any]) -> list[TextContent]:
        """Get a methodology by ID."""
        methodology_id = arguments.get("methodology_id", "")

        result = await tenjin.methodology_service.get_methodology(methodology_id)
        return [TextContent(type="text", text=str(result))]

    @server.call_tool()
    async def list_methodologies(arguments: dict[str, Any]) -> list[TextContent]:
        """List methodologies with optional filters."""
        theory_id = arguments.get("theory_id")
        category = arguments.get("category")
        limit = arguments.get("limit", 20)
        offset = arguments.get("offset", 0)

        result = await tenjin.methodology_service.list_methodologies(
            theory_id=theory_id,
            category=category,
            limit=limit,
            offset=offset,
        )
        return [TextContent(type="text", text=str(result))]

    @server.call_tool()
    async def search_methodologies(arguments: dict[str, Any]) -> list[TextContent]:
        """Search for methodologies."""
        query = arguments.get("query", "")
        limit = arguments.get("limit", 10)

        result = await tenjin.methodology_service.search_methodologies(
            query=query,
            limit=limit,
        )
        return [TextContent(type="text", text=str(result))]

    @server.call_tool()
    async def get_methodologies_for_theory(
        arguments: dict[str, Any],
    ) -> list[TextContent]:
        """Get methodologies for a theory."""
        theory_id = arguments.get("theory_id", "")

        result = await tenjin.methodology_service.get_methodologies_for_theory(
            theory_id
        )
        return [TextContent(type="text", text=str(result))]

    @server.call_tool()
    async def recommend_methodology(arguments: dict[str, Any]) -> list[TextContent]:
        """Recommend methodology for a context."""
        context = arguments.get("context", "")
        constraints = arguments.get("constraints")

        result = await tenjin.methodology_service.recommend_methodology(
            context=context,
            constraints=constraints,
        )
        return [TextContent(type="text", text=str(result))]

    @server.call_tool()
    async def get_implementation_guide(arguments: dict[str, Any]) -> list[TextContent]:
        """Get implementation guide for a methodology."""
        methodology_id = arguments.get("methodology_id", "")
        context = arguments.get("context", "")

        result = await tenjin.methodology_service.get_implementation_guide(
            methodology_id=methodology_id,
            context=context,
        )
        return [TextContent(type="text", text=str(result))]


def get_methodology_tool_definitions() -> list[Tool]:
    """Get methodology tool definitions."""
    return [
        Tool(
            name="get_methodology",
            description="Get detailed information about a teaching methodology.",
            inputSchema={
                "type": "object",
                "properties": {
                    "methodology_id": {
                        "type": "string",
                        "description": "ID of the methodology",
                    },
                },
                "required": ["methodology_id"],
            },
        ),
        Tool(
            name="list_methodologies",
            description="List teaching methodologies with optional filters by theory or category.",
            inputSchema={
                "type": "object",
                "properties": {
                    "theory_id": {
                        "type": "string",
                        "description": "Filter by associated theory",
                    },
                    "category": {
                        "type": "string",
                        "description": "Filter by methodology category",
                    },
                    "limit": {
                        "type": "integer",
                        "default": 20,
                    },
                    "offset": {
                        "type": "integer",
                        "default": 0,
                    },
                },
            },
        ),
        Tool(
            name="search_methodologies",
            description="Search for teaching methodologies using natural language.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query",
                    },
                    "limit": {
                        "type": "integer",
                        "default": 10,
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="get_methodologies_for_theory",
            description="Get all methodologies associated with a specific educational theory.",
            inputSchema={
                "type": "object",
                "properties": {
                    "theory_id": {
                        "type": "string",
                        "description": "ID of the theory",
                    },
                },
                "required": ["theory_id"],
            },
        ),
        Tool(
            name="recommend_methodology",
            description="Get AI-powered methodology recommendations for your teaching context and constraints.",
            inputSchema={
                "type": "object",
                "properties": {
                    "context": {
                        "type": "string",
                        "description": "Description of your teaching context",
                    },
                    "constraints": {
                        "type": "object",
                        "properties": {
                            "time_available": {"type": "string"},
                            "class_size": {"type": "integer"},
                            "resources": {"type": "array", "items": {"type": "string"}},
                        },
                        "description": "Constraints to consider",
                    },
                },
                "required": ["context"],
            },
        ),
        Tool(
            name="get_implementation_guide",
            description="Get a comprehensive implementation guide for a methodology, including preparation, phases, materials, and assessment.",
            inputSchema={
                "type": "object",
                "properties": {
                    "methodology_id": {
                        "type": "string",
                        "description": "ID of the methodology",
                    },
                    "context": {
                        "type": "string",
                        "description": "Your specific implementation context",
                    },
                },
                "required": ["methodology_id"],
            },
        ),
    ]
