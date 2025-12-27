"""Inference Tools - MCP tools for advanced LLM-powered inference operations.

Provides tools for:
- Theory recommendation based on learner profiles
- Learning design gap analysis
- Relationship inference between theories
- Evidence-based reasoning
"""

from typing import Any
import json

from mcp.server import Server
from mcp.types import Tool, TextContent

from ..server import TenjinServer
from ...infrastructure.config.logging import get_logger

logger = get_logger(__name__)


def get_inference_tool_definitions() -> list[Tool]:
    """Get inference tool definitions.

    Returns:
        List of inference tool definitions.
    """
    return [
        Tool(
            name="recommend_theories_for_learner",
            description="""Recommend educational theories based on learner profile and learning goals.
            
This tool uses LLM-powered reasoning to provide personalized theory recommendations
considering learner characteristics, goals, and constraints.

Example use cases:
- "What theories work best for visual learners studying math?"
- "Recommend theories for adult learners in corporate training"
- "Which theories support self-directed online learning?"

Returns ranked recommendations with rationale and implementation tips.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "learner_profile": {
                        "type": "object",
                        "description": "Learner characteristics",
                        "properties": {
                            "age": {
                                "type": "string",
                                "description": "Learner age or age range (e.g., 'adult', '10-12', 'university')"
                            },
                            "level": {
                                "type": "string",
                                "description": "Current knowledge level (beginner/intermediate/advanced)"
                            },
                            "learning_style": {
                                "type": "string",
                                "description": "Preferred learning style (visual/auditory/kinesthetic/reading-writing)"
                            },
                            "prior_knowledge": {
                                "type": "string",
                                "description": "Relevant prior knowledge or experience"
                            },
                            "special_needs": {
                                "type": "string",
                                "description": "Any special learning needs or accommodations"
                            }
                        }
                    },
                    "learning_goals": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of learning objectives or goals"
                    },
                    "constraints": {
                        "type": "object",
                        "description": "Optional constraints",
                        "properties": {
                            "time": {
                                "type": "string",
                                "description": "Time available (e.g., '1 hour', '1 semester')"
                            },
                            "resources": {
                                "type": "string",
                                "description": "Available resources (limited/standard/extensive)"
                            },
                            "setting": {
                                "type": "string",
                                "description": "Learning setting (classroom/online/hybrid/self-study)"
                            }
                        }
                    },
                    "limit": {
                        "type": "integer",
                        "default": 5,
                        "description": "Maximum number of recommendations"
                    }
                },
                "required": ["learning_goals"]
            }
        ),
        Tool(
            name="analyze_learning_design_gaps",
            description="""Analyze gaps in a learning design and suggest improvements.
            
This tool performs comprehensive gap analysis on a learning design,
identifying missing elements, misalignments, and areas for improvement.

Example use cases:
- "What's missing in my course design for teaching programming?"
- "Analyze gaps between my lesson plan and learning outcomes"
- "How can I improve my workshop design using educational theory?"

Returns gap analysis with prioritized improvement suggestions.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "current_design": {
                        "type": "object",
                        "description": "Current learning design details",
                        "properties": {
                            "activities": {
                                "type": "string",
                                "description": "Learning activities in the design"
                            },
                            "assessment": {
                                "type": "string",
                                "description": "Assessment methods used"
                            },
                            "materials": {
                                "type": "string",
                                "description": "Learning materials and resources"
                            },
                            "duration": {
                                "type": "string",
                                "description": "Duration of the learning experience"
                            },
                            "setting": {
                                "type": "string",
                                "description": "Learning environment/setting"
                            }
                        }
                    },
                    "target_outcomes": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Desired learning outcomes"
                    },
                    "applied_theories": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Theory IDs currently being applied (optional)"
                    }
                },
                "required": ["current_design", "target_outcomes"]
            }
        ),
        Tool(
            name="infer_theory_relationships",
            description="""Infer relationships between educational theories using LLM reasoning.
            
This tool discovers potential relationships between a theory and others
that may not be explicitly documented, using AI-powered analysis.

Example use cases:
- "What theories are related to Constructivism that I might not know about?"
- "Discover hidden connections between Vygotsky's ZPD and other theories"
- "Find theories that complement or contrast with ARCS model"

Returns both existing and inferred relationships with evidence.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "theory_id": {
                        "type": "string",
                        "description": "Base theory ID to analyze (e.g., 'THEORY-001')"
                    },
                    "inference_depth": {
                        "type": "integer",
                        "default": 2,
                        "maximum": 3,
                        "description": "How many hops to explore in the graph"
                    }
                },
                "required": ["theory_id"]
            }
        ),
        Tool(
            name="reason_about_application",
            description="""Reason about which theories best apply to a specific educational scenario.
            
This tool uses evidence-based reasoning to analyze a scenario and determine
which educational theories are most applicable, with clear reasoning chains.

Example use cases:
- "Which theories apply to teaching critical thinking to high school students?"
- "What's the best theoretical approach for flipped classroom implementation?"
- "Reason about theory selection for a remote team training scenario"

Returns primary and secondary recommendations with reasoning chains.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "scenario": {
                        "type": "string",
                        "description": "Description of the educational scenario"
                    },
                    "constraints": {
                        "type": "object",
                        "description": "Optional constraints",
                        "properties": {
                            "time": {
                                "type": "string",
                                "description": "Time available"
                            },
                            "resources": {
                                "type": "string",
                                "description": "Available resources"
                            },
                            "learner_count": {
                                "type": "string",
                                "description": "Number of learners (individual/small group/large class)"
                            },
                            "setting": {
                                "type": "string",
                                "description": "Educational setting"
                            }
                        }
                    }
                },
                "required": ["scenario"]
            }
        )
    ]


def register_inference_tools(server: Server, tenjin: TenjinServer) -> None:
    """Register inference tool handlers.

    Args:
        server: MCP server instance.
        tenjin: TENJIN server instance.
    """

    @server.call_tool()
    async def call_inference_tool(name: str, arguments: dict) -> list[TextContent]:
        """Handle inference tool calls."""
        
        # Get inference service
        inference_service = tenjin.get_inference_service()
        
        if name == "recommend_theories_for_learner":
            result = await inference_service.recommend_theories_for_learner(
                learner_profile=arguments.get("learner_profile", {}),
                learning_goals=arguments.get("learning_goals", []),
                constraints=arguments.get("constraints"),
                limit=arguments.get("limit", 5),
            )
            return [TextContent(
                type="text",
                text=json.dumps(result, ensure_ascii=False, indent=2)
            )]

        elif name == "analyze_learning_design_gaps":
            result = await inference_service.analyze_learning_design_gaps(
                current_design=arguments.get("current_design", {}),
                target_outcomes=arguments.get("target_outcomes", []),
                applied_theories=arguments.get("applied_theories"),
            )
            return [TextContent(
                type="text",
                text=json.dumps(result, ensure_ascii=False, indent=2)
            )]

        elif name == "infer_theory_relationships":
            result = await inference_service.infer_theory_relationships(
                theory_id=arguments.get("theory_id", ""),
                inference_depth=arguments.get("inference_depth", 2),
            )
            return [TextContent(
                type="text",
                text=json.dumps(result, ensure_ascii=False, indent=2)
            )]

        elif name == "reason_about_application":
            result = await inference_service.reason_about_application(
                scenario=arguments.get("scenario", ""),
                constraints=arguments.get("constraints"),
            )
            return [TextContent(
                type="text",
                text=json.dumps(result, ensure_ascii=False, indent=2)
            )]

        # If tool name doesn't match, return None to let other handlers try
        return None


__all__ = ["register_inference_tools", "get_inference_tool_definitions"]
