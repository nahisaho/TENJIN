"""MCP Tools - Action handlers for MCP protocol."""

from mcp.server import Server
from mcp.types import Tool

from ..server import TenjinServer
from .theory_tools import register_theory_tools, get_theory_tool_definitions
from .search_tools import register_search_tools, get_search_tool_definitions
from .graph_tools import register_graph_tools, get_graph_tool_definitions
from .analysis_tools import register_analysis_tools, get_analysis_tool_definitions
from .recommendation_tools import (
    register_recommendation_tools,
    get_recommendation_tool_definitions,
)
from .citation_tools import register_citation_tools, get_citation_tool_definitions
from .methodology_tools import (
    register_methodology_tools,
    get_methodology_tool_definitions,
)
from .inference_tools import (
    register_inference_tools,
    get_inference_tool_definitions,
)
from .cache_tools import register_cache_tools, get_cache_tool_definitions


def register_tools(server: Server, tenjin: TenjinServer) -> None:
    """Register all MCP tools with the server.

    Args:
        server: MCP server instance.
        tenjin: TENJIN server instance.
    """
    # Register tool handlers
    register_theory_tools(server, tenjin)
    register_search_tools(server, tenjin)
    register_graph_tools(server, tenjin)
    register_analysis_tools(server, tenjin)
    register_recommendation_tools(server, tenjin)
    register_citation_tools(server, tenjin)
    register_methodology_tools(server, tenjin)
    register_inference_tools(server, tenjin)
    register_cache_tools(server, tenjin)

    # Register tool listing
    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List all available tools."""
        tools = []
        tools.extend(get_theory_tool_definitions())
        tools.extend(get_search_tool_definitions())
        tools.extend(get_graph_tool_definitions())
        tools.extend(get_analysis_tool_definitions())
        tools.extend(get_recommendation_tool_definitions())
        tools.extend(get_citation_tool_definitions())
        tools.extend(get_methodology_tool_definitions())
        tools.extend(get_inference_tool_definitions())
        tools.extend(get_cache_tool_definitions(tenjin))
        return tools


__all__ = ["register_tools"]
