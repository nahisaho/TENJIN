"""MCP Tools registration - Analysis tools."""

from typing import Any
from mcp.server import Server
from mcp.types import Tool, TextContent

from ..server import TenjinServer
from ...infrastructure.config.logging import get_logger

logger = get_logger(__name__)


def register_analysis_tools(server: Server, tenjin: TenjinServer) -> None:
    """Register analysis-related MCP tools.

    Args:
        server: MCP server instance.
        tenjin: TENJIN server instance.
    """

    @server.call_tool()
    async def compare_theories(arguments: dict[str, Any]) -> list[TextContent]:
        """Compare multiple educational theories."""
        theory_ids = arguments.get("theory_ids", [])
        aspects = arguments.get("aspects")

        result = await tenjin.analysis_service.compare_theories(
            theory_ids=theory_ids,
            aspects=aspects,
        )
        return [TextContent(type="text", text=str(result))]

    @server.call_tool()
    async def analyze_theory(arguments: dict[str, Any]) -> list[TextContent]:
        """Perform in-depth analysis of a theory."""
        theory_id = arguments.get("theory_id", "")
        analysis_type = arguments.get("analysis_type", "comprehensive")

        result = await tenjin.analysis_service.analyze_theory(
            theory_id=theory_id,
            analysis_type=analysis_type,
        )
        return [TextContent(type="text", text=str(result))]

    @server.call_tool()
    async def synthesize_theories(arguments: dict[str, Any]) -> list[TextContent]:
        """Synthesize multiple theories for a context."""
        theory_ids = arguments.get("theory_ids", [])
        context = arguments.get("context", "")

        result = await tenjin.analysis_service.synthesize_theories(
            theory_ids=theory_ids,
            context=context,
        )
        return [TextContent(type="text", text=str(result))]

    @server.call_tool()
    async def get_theory_applications(arguments: dict[str, Any]) -> list[TextContent]:
        """Get practical applications for a theory."""
        theory_id = arguments.get("theory_id", "")
        context = arguments.get("context", "")

        result = await tenjin.analysis_service.get_theory_applications(
            theory_id=theory_id,
            context=context,
        )
        return [TextContent(type="text", text=str(result))]


def get_analysis_tool_definitions() -> list[Tool]:
    """Get analysis tool definitions."""
    return [
        Tool(
            name="compare_theories",
            description="Compare multiple educational theories across various aspects using AI analysis. Identifies similarities, differences, and integration opportunities.",
            inputSchema={
                "type": "object",
                "properties": {
                    "theory_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of theory IDs to compare (minimum 2)",
                    },
                    "aspects": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Specific aspects to compare (e.g., core_principles, applications, strengths)",
                    },
                },
                "required": ["theory_ids"],
            },
        ),
        Tool(
            name="analyze_theory",
            description="Perform comprehensive AI-powered analysis of an educational theory, including historical context, theoretical foundation, and modern relevance.",
            inputSchema={
                "type": "object",
                "properties": {
                    "theory_id": {
                        "type": "string",
                        "description": "ID of the theory to analyze",
                    },
                    "analysis_type": {
                        "type": "string",
                        "enum": ["comprehensive", "historical", "practical", "critical"],
                        "description": "Type of analysis to perform",
                        "default": "comprehensive",
                    },
                },
                "required": ["theory_id"],
            },
        ),
        Tool(
            name="synthesize_theories",
            description="Synthesize multiple theories into an integrated approach for a specific educational context.",
            inputSchema={
                "type": "object",
                "properties": {
                    "theory_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Theory IDs to synthesize",
                    },
                    "context": {
                        "type": "string",
                        "description": "Educational context for the synthesis",
                    },
                },
                "required": ["theory_ids"],
            },
        ),
        Tool(
            name="get_theory_applications",
            description="Get detailed practical applications for a theory in a specific context, including classroom activities, assessment methods, and examples.",
            inputSchema={
                "type": "object",
                "properties": {
                    "theory_id": {
                        "type": "string",
                        "description": "ID of the theory",
                    },
                    "context": {
                        "type": "string",
                        "description": "Specific application context (e.g., elementary math, adult ESL)",
                    },
                },
                "required": ["theory_id"],
            },
        ),
    ]
