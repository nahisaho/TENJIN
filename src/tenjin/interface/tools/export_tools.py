"""MCP Tools registration - Export tools."""

import json
from typing import Any

from mcp.server import Server
from mcp.types import Tool, TextContent

from ..server import TenjinServer
from ...infrastructure.config.logging import get_logger

logger = get_logger(__name__)


def register_export_tools(server: Server, tenjin: TenjinServer) -> None:
    """Register export-related MCP tools.

    Args:
        server: MCP server instance.
        tenjin: TENJIN server instance.
    """

    @server.call_tool()
    async def export_theories_json(arguments: dict[str, Any]) -> list[TextContent]:
        """Export theories as JSON."""
        theory_ids = arguments.get("theory_ids")
        categories = arguments.get("categories")
        include_metadata = arguments.get("include_metadata", True)

        result = await tenjin.export_service.export_json(
            theory_ids=theory_ids,
            categories=categories,
            include_metadata=include_metadata,
        )
        return [TextContent(
            type="text",
            text=json.dumps(result, ensure_ascii=False, indent=2),
        )]

    @server.call_tool()
    async def export_theories_markdown(arguments: dict[str, Any]) -> list[TextContent]:
        """Export theories as Markdown document."""
        theory_ids = arguments.get("theory_ids")
        categories = arguments.get("categories")
        language = arguments.get("language", "ja")
        include_toc = arguments.get("include_toc", True)

        result = await tenjin.export_service.export_markdown(
            theory_ids=theory_ids,
            categories=categories,
            language=language,
            include_toc=include_toc,
        )
        return [TextContent(type="text", text=result)]

    @server.call_tool()
    async def export_theories_csv(arguments: dict[str, Any]) -> list[TextContent]:
        """Export theories as CSV."""
        theory_ids = arguments.get("theory_ids")
        categories = arguments.get("categories")

        result = await tenjin.export_service.export_csv(
            theory_ids=theory_ids,
            categories=categories,
        )
        return [TextContent(type="text", text=result)]


def get_export_tool_definitions() -> list[Tool]:
    """Get export tool definitions."""
    return [
        Tool(
            name="export_theories_json",
            description="Export educational theories as JSON format. Returns structured data suitable for backup or import.",
            inputSchema={
                "type": "object",
                "properties": {
                    "theory_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Specific theory IDs to export. If not provided, exports all.",
                    },
                    "categories": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Filter by categories (e.g., ['learning_theory', 'assessment'])",
                    },
                    "include_metadata": {
                        "type": "boolean",
                        "description": "Include export metadata (version, date)",
                        "default": True,
                    },
                },
                "required": [],
            },
        ),
        Tool(
            name="export_theories_markdown",
            description="Export educational theories as a formatted Markdown document. Useful for documentation or sharing.",
            inputSchema={
                "type": "object",
                "properties": {
                    "theory_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Specific theory IDs to export. If not provided, exports all.",
                    },
                    "categories": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Filter by categories",
                    },
                    "language": {
                        "type": "string",
                        "enum": ["ja", "en"],
                        "description": "Output language",
                        "default": "ja",
                    },
                    "include_toc": {
                        "type": "boolean",
                        "description": "Include table of contents",
                        "default": True,
                    },
                },
                "required": [],
            },
        ),
        Tool(
            name="export_theories_csv",
            description="Export educational theories as CSV format. Useful for spreadsheet analysis.",
            inputSchema={
                "type": "object",
                "properties": {
                    "theory_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Specific theory IDs to export. If not provided, exports all.",
                    },
                    "categories": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Filter by categories",
                    },
                },
                "required": [],
            },
        ),
    ]
