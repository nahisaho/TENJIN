"""Interface layer - MCP protocol handlers."""

from .server import TenjinServer, get_tenjin_server, run
from .tools import register_tools
from .resources import register_resources
from .prompts import register_prompts

__all__ = [
    "TenjinServer",
    "get_tenjin_server",
    "run",
    "register_tools",
    "register_resources",
    "register_prompts",
]
