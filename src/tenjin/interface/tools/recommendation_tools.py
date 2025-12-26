"""MCP Tools registration - Recommendation tools."""

from typing import Any
from mcp.server import Server
from mcp.types import Tool, TextContent

from ..server import TenjinServer
from ...infrastructure.config.logging import get_logger

logger = get_logger(__name__)


def register_recommendation_tools(server: Server, tenjin: TenjinServer) -> None:
    """Register recommendation-related MCP tools.

    Args:
        server: MCP server instance.
        tenjin: TENJIN server instance.
    """

    @server.call_tool()
    async def recommend_theories(arguments: dict[str, Any]) -> list[TextContent]:
        """Recommend theories for a context."""
        context = arguments.get("context", "")
        limit = arguments.get("limit", 5)
        filters = arguments.get("filters")

        result = await tenjin.recommendation_service.recommend_for_context(
            context=context,
            limit=limit,
            filters=filters,
        )
        return [TextContent(type="text", text=str(result))]

    @server.call_tool()
    async def recommend_similar_theories(
        arguments: dict[str, Any],
    ) -> list[TextContent]:
        """Recommend theories similar to a given one."""
        theory_id = arguments.get("theory_id", "")
        limit = arguments.get("limit", 5)

        result = await tenjin.recommendation_service.recommend_similar(
            theory_id=theory_id,
            limit=limit,
        )
        return [TextContent(type="text", text=str(result))]

    @server.call_tool()
    async def recommend_for_learner(arguments: dict[str, Any]) -> list[TextContent]:
        """Recommend theories based on learner profile."""
        learner_profile = arguments.get("learner_profile", {})
        limit = arguments.get("limit", 5)

        result = await tenjin.recommendation_service.recommend_for_learner_profile(
            learner_profile=learner_profile,
            limit=limit,
        )
        return [TextContent(type="text", text=str(result))]

    @server.call_tool()
    async def recommend_complementary(arguments: dict[str, Any]) -> list[TextContent]:
        """Recommend complementary theories."""
        theory_ids = arguments.get("theory_ids", [])
        limit = arguments.get("limit", 5)

        result = await tenjin.recommendation_service.recommend_complementary(
            theory_ids=theory_ids,
            limit=limit,
        )
        return [TextContent(type="text", text=str(result))]

    @server.call_tool()
    async def get_learning_path(arguments: dict[str, Any]) -> list[TextContent]:
        """Generate a learning path for a goal."""
        goal = arguments.get("goal", "")
        current_knowledge = arguments.get("current_knowledge", [])

        result = await tenjin.recommendation_service.get_learning_path(
            goal=goal,
            current_knowledge=current_knowledge,
        )
        return [TextContent(type="text", text=str(result))]


def get_recommendation_tool_definitions() -> list[Tool]:
    """Get recommendation tool definitions."""
    return [
        Tool(
            name="recommend_theories",
            description="Recommend educational theories for a specific teaching/learning context. Uses AI to match theories with your needs.",
            inputSchema={
                "type": "object",
                "properties": {
                    "context": {
                        "type": "string",
                        "description": "Description of your educational context or challenge",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum recommendations",
                        "default": 5,
                    },
                    "filters": {
                        "type": "object",
                        "properties": {
                            "category": {"type": "string"},
                            "min_priority": {"type": "integer"},
                            "max_priority": {"type": "integer"},
                        },
                        "description": "Optional filters",
                    },
                },
                "required": ["context"],
            },
        ),
        Tool(
            name="recommend_similar_theories",
            description="Find theories similar to one you already like or use.",
            inputSchema={
                "type": "object",
                "properties": {
                    "theory_id": {
                        "type": "string",
                        "description": "ID of your reference theory",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum recommendations",
                        "default": 5,
                    },
                },
                "required": ["theory_id"],
            },
        ),
        Tool(
            name="recommend_for_learner",
            description="Get personalized theory recommendations based on learner profile (age, learning style, goals, challenges).",
            inputSchema={
                "type": "object",
                "properties": {
                    "learner_profile": {
                        "type": "object",
                        "properties": {
                            "age_group": {
                                "type": "string",
                                "description": "child, adolescent, adult, senior",
                            },
                            "learning_style": {
                                "type": "string",
                                "description": "visual, auditory, kinesthetic, reading/writing",
                            },
                            "subject_area": {"type": "string"},
                            "challenges": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                            "goals": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                        },
                        "description": "Learner characteristics",
                    },
                    "limit": {
                        "type": "integer",
                        "default": 5,
                    },
                },
                "required": ["learner_profile"],
            },
        ),
        Tool(
            name="recommend_complementary",
            description="Find theories that complement your current selection, filling gaps in your approach.",
            inputSchema={
                "type": "object",
                "properties": {
                    "theory_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "IDs of theories you're already using",
                    },
                    "limit": {
                        "type": "integer",
                        "default": 5,
                    },
                },
                "required": ["theory_ids"],
            },
        ),
        Tool(
            name="get_learning_path",
            description="Generate an ordered learning path of theories to achieve a specific educational goal.",
            inputSchema={
                "type": "object",
                "properties": {
                    "goal": {
                        "type": "string",
                        "description": "Your learning or teaching goal",
                    },
                    "current_knowledge": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Theory IDs you already know",
                    },
                },
                "required": ["goal"],
            },
        ),
    ]
