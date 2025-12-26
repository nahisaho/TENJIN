"""MCP Tools registration - Theory tools."""

from typing import Any
from mcp.server import Server
from mcp.types import Tool, TextContent

from ..server import TenjinServer
from ...infrastructure.config.logging import get_logger

logger = get_logger(__name__)


def register_theory_tools(server: Server, tenjin: TenjinServer) -> None:
    """Register theory-related MCP tools.

    Args:
        server: MCP server instance.
        tenjin: TENJIN server instance.
    """

    @server.call_tool()
    async def get_theory(arguments: dict[str, Any]) -> list[TextContent]:
        """Get a theory by ID."""
        theory_id = arguments.get("theory_id", "")
        include_details = arguments.get("include_details", True)

        if include_details:
            result = await tenjin.theory_service.get_theory_details(theory_id)
        else:
            result = await tenjin.theory_service.get_theory(theory_id)

        return [TextContent(type="text", text=str(result))]

    @server.call_tool()
    async def get_theory_by_name(arguments: dict[str, Any]) -> list[TextContent]:
        """Get a theory by name."""
        name = arguments.get("name", "")
        result = await tenjin.theory_service.get_theory_by_name(name)
        return [TextContent(type="text", text=str(result))]

    @server.call_tool()
    async def list_theories(arguments: dict[str, Any]) -> list[TextContent]:
        """List all theories with optional filters."""
        limit = arguments.get("limit", 20)
        offset = arguments.get("offset", 0)
        result = await tenjin.theory_service.list_theories(limit=limit, offset=offset)
        return [TextContent(type="text", text=str(result))]

    @server.call_tool()
    async def get_theories_by_category(arguments: dict[str, Any]) -> list[TextContent]:
        """Get theories by category."""
        category = arguments.get("category", "")
        limit = arguments.get("limit", 20)
        result = await tenjin.theory_service.get_theories_by_category(
            category, limit=limit
        )
        return [TextContent(type="text", text=str(result))]

    @server.call_tool()
    async def get_theories_by_theorist(arguments: dict[str, Any]) -> list[TextContent]:
        """Get theories by theorist."""
        theorist_id = arguments.get("theorist_id", "")
        result = await tenjin.theory_service.get_theories_by_theorist(theorist_id)
        return [TextContent(type="text", text=str(result))]

    @server.call_tool()
    async def get_category_statistics(arguments: dict[str, Any]) -> list[TextContent]:
        """Get statistics by category."""
        result = await tenjin.theory_service.get_category_statistics()
        return [TextContent(type="text", text=str(result))]

    # Register tool definitions
    server.list_tools_handler = lambda: get_theory_tool_definitions()


def get_theory_tool_definitions() -> list[Tool]:
    """Get theory tool definitions."""
    return [
        Tool(
            name="get_theory",
            description="Get detailed information about an educational theory by ID. Returns theory name, description, key principles, applications, strengths, and limitations.",
            inputSchema={
                "type": "object",
                "properties": {
                    "theory_id": {
                        "type": "string",
                        "description": "The unique identifier of the theory",
                    },
                    "include_details": {
                        "type": "boolean",
                        "description": "Include related theories, theorists, and evidence",
                        "default": True,
                    },
                },
                "required": ["theory_id"],
            },
        ),
        Tool(
            name="get_theory_by_name",
            description="Find an educational theory by its name (supports partial matching).",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "The name of the theory to find",
                    },
                },
                "required": ["name"],
            },
        ),
        Tool(
            name="list_theories",
            description="List all educational theories with pagination. Returns theory names, categories, and brief descriptions.",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of theories to return",
                        "default": 20,
                    },
                    "offset": {
                        "type": "integer",
                        "description": "Offset for pagination",
                        "default": 0,
                    },
                },
            },
        ),
        Tool(
            name="get_theories_by_category",
            description="Get all theories in a specific category (e.g., cognitive_development, behavioral, constructivist).",
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "Category name (cognitive_development, behavioral, constructivist, social_learning, humanistic, motivation, instructional_design, adult_learning, technology_enhanced)",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum theories to return",
                        "default": 20,
                    },
                },
                "required": ["category"],
            },
        ),
        Tool(
            name="get_theories_by_theorist",
            description="Get all theories developed by a specific theorist.",
            inputSchema={
                "type": "object",
                "properties": {
                    "theorist_id": {
                        "type": "string",
                        "description": "The theorist's unique identifier",
                    },
                },
                "required": ["theorist_id"],
            },
        ),
        Tool(
            name="get_category_statistics",
            description="Get statistics about theories grouped by category.",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
    ]
