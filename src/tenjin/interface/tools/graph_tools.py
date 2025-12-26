"""MCP Tools registration - Graph tools."""

from typing import Any
from mcp.server import Server
from mcp.types import Tool, TextContent

from ..server import TenjinServer
from ...infrastructure.config.logging import get_logger

logger = get_logger(__name__)


def register_graph_tools(server: Server, tenjin: TenjinServer) -> None:
    """Register graph-related MCP tools.

    Args:
        server: MCP server instance.
        tenjin: TENJIN server instance.
    """

    @server.call_tool()
    async def get_related_theories(arguments: dict[str, Any]) -> list[TextContent]:
        """Get theories related to a given theory."""
        theory_id = arguments.get("theory_id", "")
        relationship_type = arguments.get("relationship_type")
        depth = arguments.get("depth", 1)
        limit = arguments.get("limit", 10)

        result = await tenjin.graph_service.get_related_theories(
            theory_id=theory_id,
            relationship_type=relationship_type,
            depth=depth,
            limit=limit,
        )
        return [TextContent(type="text", text=str(result))]

    @server.call_tool()
    async def get_theory_relationships(arguments: dict[str, Any]) -> list[TextContent]:
        """Get all relationships for a theory."""
        theory_id = arguments.get("theory_id", "")

        result = await tenjin.graph_service.get_theory_relationships(theory_id)
        return [TextContent(type="text", text=str(result))]

    @server.call_tool()
    async def find_theory_path(arguments: dict[str, Any]) -> list[TextContent]:
        """Find path between two theories."""
        source_id = arguments.get("source_id", "")
        target_id = arguments.get("target_id", "")
        max_depth = arguments.get("max_depth", 5)

        result = await tenjin.graph_service.find_path(
            source_id=source_id,
            target_id=target_id,
            max_depth=max_depth,
        )
        return [TextContent(type="text", text=str(result))]

    @server.call_tool()
    async def get_theory_network(arguments: dict[str, Any]) -> list[TextContent]:
        """Get network visualization data for theories."""
        theory_ids = arguments.get("theory_ids", [])
        depth = arguments.get("depth", 1)

        result = await tenjin.graph_service.get_theory_network(
            theory_ids=theory_ids,
            depth=depth,
        )
        return [TextContent(type="text", text=str(result))]

    @server.call_tool()
    async def get_influence_chain(arguments: dict[str, Any]) -> list[TextContent]:
        """Get chain of influence from a theory."""
        theory_id = arguments.get("theory_id", "")
        max_depth = arguments.get("max_depth", 3)

        result = await tenjin.graph_service.get_influence_chain(
            theory_id=theory_id,
            max_depth=max_depth,
        )
        return [TextContent(type="text", text=str(result))]

    @server.call_tool()
    async def find_common_connections(arguments: dict[str, Any]) -> list[TextContent]:
        """Find common connections between theories."""
        theory_ids = arguments.get("theory_ids", [])

        result = await tenjin.graph_service.find_common_connections(theory_ids)
        return [TextContent(type="text", text=str(result))]

    @server.call_tool()
    async def get_graph_statistics(arguments: dict[str, Any]) -> list[TextContent]:
        """Get statistics about the knowledge graph."""
        result = await tenjin.graph_service.get_graph_statistics()
        return [TextContent(type="text", text=str(result))]


def get_graph_tool_definitions() -> list[Tool]:
    """Get graph tool definitions."""
    return [
        Tool(
            name="get_related_theories",
            description="Get theories related to a given theory through the knowledge graph. Can filter by relationship type and traversal depth.",
            inputSchema={
                "type": "object",
                "properties": {
                    "theory_id": {
                        "type": "string",
                        "description": "ID of the source theory",
                    },
                    "relationship_type": {
                        "type": "string",
                        "description": "Filter by relationship type (influences, extends, contradicts, etc.)",
                    },
                    "depth": {
                        "type": "integer",
                        "description": "Traversal depth (1-3)",
                        "default": 1,
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum results",
                        "default": 10,
                    },
                },
                "required": ["theory_id"],
            },
        ),
        Tool(
            name="get_theory_relationships",
            description="Get all relationships (incoming and outgoing) for a theory.",
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
            name="find_theory_path",
            description="Find the shortest path between two theories in the knowledge graph.",
            inputSchema={
                "type": "object",
                "properties": {
                    "source_id": {
                        "type": "string",
                        "description": "Starting theory ID",
                    },
                    "target_id": {
                        "type": "string",
                        "description": "Target theory ID",
                    },
                    "max_depth": {
                        "type": "integer",
                        "description": "Maximum path length",
                        "default": 5,
                    },
                },
                "required": ["source_id", "target_id"],
            },
        ),
        Tool(
            name="get_theory_network",
            description="Get network data for visualization of theories and their relationships.",
            inputSchema={
                "type": "object",
                "properties": {
                    "theory_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of theory IDs to include",
                    },
                    "depth": {
                        "type": "integer",
                        "description": "How many hops to include",
                        "default": 1,
                    },
                },
                "required": ["theory_ids"],
            },
        ),
        Tool(
            name="get_influence_chain",
            description="Get the chain of theoretical influence from a given theory.",
            inputSchema={
                "type": "object",
                "properties": {
                    "theory_id": {
                        "type": "string",
                        "description": "Starting theory ID",
                    },
                    "max_depth": {
                        "type": "integer",
                        "description": "Maximum depth to trace",
                        "default": 3,
                    },
                },
                "required": ["theory_id"],
            },
        ),
        Tool(
            name="find_common_connections",
            description="Find theories that connect multiple given theories.",
            inputSchema={
                "type": "object",
                "properties": {
                    "theory_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of theory IDs to find connections for",
                    },
                },
                "required": ["theory_ids"],
            },
        ),
        Tool(
            name="get_graph_statistics",
            description="Get overall statistics about the knowledge graph (node counts, relationship types, etc.).",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
    ]
