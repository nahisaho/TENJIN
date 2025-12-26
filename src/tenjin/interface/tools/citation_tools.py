"""MCP Tools registration - Citation tools."""

from typing import Any
from mcp.server import Server
from mcp.types import Tool, TextContent

from ..server import TenjinServer
from ...infrastructure.config.logging import get_logger

logger = get_logger(__name__)


def register_citation_tools(server: Server, tenjin: TenjinServer) -> None:
    """Register citation-related MCP tools.

    Args:
        server: MCP server instance.
        tenjin: TENJIN server instance.
    """

    @server.call_tool()
    async def generate_citation(arguments: dict[str, Any]) -> list[TextContent]:
        """Generate citation for a theory."""
        theory_id = arguments.get("theory_id", "")
        style = arguments.get("style", "apa")
        include_url = arguments.get("include_url", True)

        result = await tenjin.citation_service.generate_citation(
            theory_id=theory_id,
            style=style,
            include_url=include_url,
        )
        return [TextContent(type="text", text=str(result))]

    @server.call_tool()
    async def generate_bibliography(arguments: dict[str, Any]) -> list[TextContent]:
        """Generate bibliography for multiple theories."""
        theory_ids = arguments.get("theory_ids", [])
        style = arguments.get("style", "apa")
        sort_by = arguments.get("sort_by", "author")

        result = await tenjin.citation_service.generate_bibliography(
            theory_ids=theory_ids,
            style=style,
            sort_by=sort_by,
        )
        return [TextContent(type="text", text=str(result))]

    @server.call_tool()
    async def export_citations(arguments: dict[str, Any]) -> list[TextContent]:
        """Export citations in various formats."""
        theory_ids = arguments.get("theory_ids", [])
        format = arguments.get("format", "bibtex")

        result = await tenjin.citation_service.export_citations(
            theory_ids=theory_ids,
            format=format,
        )
        return [TextContent(type="text", text=str(result))]

    @server.call_tool()
    async def get_citation_preview(arguments: dict[str, Any]) -> list[TextContent]:
        """Preview citation in all styles."""
        theory_id = arguments.get("theory_id", "")

        result = await tenjin.citation_service.get_citation_preview(theory_id)
        return [TextContent(type="text", text=str(result))]


def get_citation_tool_definitions() -> list[Tool]:
    """Get citation tool definitions."""
    return [
        Tool(
            name="generate_citation",
            description="Generate a properly formatted citation for an educational theory in your preferred style.",
            inputSchema={
                "type": "object",
                "properties": {
                    "theory_id": {
                        "type": "string",
                        "description": "ID of the theory to cite",
                    },
                    "style": {
                        "type": "string",
                        "enum": ["apa", "mla", "chicago", "harvard"],
                        "description": "Citation style",
                        "default": "apa",
                    },
                    "include_url": {
                        "type": "boolean",
                        "description": "Include URL if available",
                        "default": True,
                    },
                },
                "required": ["theory_id"],
            },
        ),
        Tool(
            name="generate_bibliography",
            description="Generate a formatted bibliography for multiple theories, sorted and formatted in your preferred style.",
            inputSchema={
                "type": "object",
                "properties": {
                    "theory_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of theory IDs to include",
                    },
                    "style": {
                        "type": "string",
                        "enum": ["apa", "mla", "chicago", "harvard"],
                        "default": "apa",
                    },
                    "sort_by": {
                        "type": "string",
                        "enum": ["author", "year", "title"],
                        "default": "author",
                    },
                },
                "required": ["theory_ids"],
            },
        ),
        Tool(
            name="export_citations",
            description="Export citations in formats compatible with reference managers (BibTeX, RIS, EndNote).",
            inputSchema={
                "type": "object",
                "properties": {
                    "theory_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Theory IDs to export",
                    },
                    "format": {
                        "type": "string",
                        "enum": ["bibtex", "ris", "endnote"],
                        "default": "bibtex",
                    },
                },
                "required": ["theory_ids"],
            },
        ),
        Tool(
            name="get_citation_preview",
            description="Preview how a theory's citation looks in all supported styles.",
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
    ]
