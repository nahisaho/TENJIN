"""MCP Resources - Data access handlers for MCP protocol."""

from mcp.server import Server
from mcp.types import Resource

from ..server import TenjinServer
from ...infrastructure.config.logging import get_logger

logger = get_logger(__name__)


def register_resources(server: Server, tenjin: TenjinServer) -> None:
    """Register all MCP resources with the server.

    Args:
        server: MCP server instance.
        tenjin: TENJIN server instance.
    """

    @server.list_resources()
    async def list_resources() -> list[Resource]:
        """List all available resources."""
        return [
            # Theory resources
            Resource(
                uri="tenjin://theories",
                name="All Educational Theories",
                description="Complete list of all educational theories in the knowledge base",
                mimeType="application/json",
            ),
            Resource(
                uri="tenjin://theories/by-category/{category}",
                name="Theories by Category",
                description="Theories filtered by category (cognitive_development, behavioral, constructivist, etc.)",
                mimeType="application/json",
            ),
            Resource(
                uri="tenjin://theory/{theory_id}",
                name="Single Theory",
                description="Detailed information about a specific theory",
                mimeType="application/json",
            ),
            # Theorist resources
            Resource(
                uri="tenjin://theorists",
                name="All Theorists",
                description="Complete list of educational theorists",
                mimeType="application/json",
            ),
            Resource(
                uri="tenjin://theorist/{theorist_id}",
                name="Single Theorist",
                description="Detailed information about a specific theorist",
                mimeType="application/json",
            ),
            # Category resources
            Resource(
                uri="tenjin://categories",
                name="Theory Categories",
                description="All available theory categories with descriptions",
                mimeType="application/json",
            ),
            Resource(
                uri="tenjin://categories/statistics",
                name="Category Statistics",
                description="Statistics about theories per category",
                mimeType="application/json",
            ),
            # Relationship resources
            Resource(
                uri="tenjin://relationships/types",
                name="Relationship Types",
                description="All available relationship types between theories",
                mimeType="application/json",
            ),
            Resource(
                uri="tenjin://relationships/{theory_id}",
                name="Theory Relationships",
                description="All relationships for a specific theory",
                mimeType="application/json",
            ),
            # Methodology resources
            Resource(
                uri="tenjin://methodologies",
                name="All Methodologies",
                description="Teaching methodologies associated with theories",
                mimeType="application/json",
            ),
            Resource(
                uri="tenjin://methodology/{methodology_id}",
                name="Single Methodology",
                description="Detailed methodology information",
                mimeType="application/json",
            ),
            # Graph resources
            Resource(
                uri="tenjin://graph/statistics",
                name="Graph Statistics",
                description="Statistics about the knowledge graph",
                mimeType="application/json",
            ),
            Resource(
                uri="tenjin://graph/network",
                name="Full Network",
                description="Complete knowledge graph network data for visualization",
                mimeType="application/json",
            ),
            # Search resources
            Resource(
                uri="tenjin://search/index-stats",
                name="Search Index Statistics",
                description="Statistics about the vector search index",
                mimeType="application/json",
            ),
        ]

    @server.read_resource()
    async def read_resource(uri: str) -> str:
        """Read a specific resource."""
        import json

        # Parse URI
        if uri == "tenjin://theories":
            result = await tenjin.theory_service.list_theories(limit=1000)
            return json.dumps(result, ensure_ascii=False, indent=2)

        elif uri.startswith("tenjin://theories/by-category/"):
            category = uri.split("/")[-1]
            result = await tenjin.theory_service.get_theories_by_category(
                category, limit=100
            )
            return json.dumps(result, ensure_ascii=False, indent=2)

        elif uri.startswith("tenjin://theory/"):
            theory_id = uri.split("/")[-1]
            result = await tenjin.theory_service.get_theory_details(theory_id)
            return json.dumps(result, ensure_ascii=False, indent=2)

        elif uri == "tenjin://theorists":
            return json.dumps({"message": "Theorist listing available"})

        elif uri.startswith("tenjin://theorist/"):
            theorist_id = uri.split("/")[-1]
            return json.dumps({"theorist_id": theorist_id})

        elif uri == "tenjin://categories":
            from ...domain.value_objects.category_type import CategoryType

            categories = [
                {
                    "value": cat.value,
                    "display_name": cat.display_name,
                    "display_name_ja": cat.display_name_ja,
                }
                for cat in CategoryType
            ]
            return json.dumps(categories, ensure_ascii=False, indent=2)

        elif uri == "tenjin://categories/statistics":
            result = await tenjin.theory_service.get_category_statistics()
            return json.dumps(result, ensure_ascii=False, indent=2)

        elif uri == "tenjin://relationships/types":
            from ...domain.value_objects.relationship_type import RelationshipType

            types = [
                {
                    "value": rt.value,
                    "display_name": rt.display_name,
                    "display_name_ja": rt.display_name_ja,
                }
                for rt in RelationshipType
            ]
            return json.dumps(types, ensure_ascii=False, indent=2)

        elif uri.startswith("tenjin://relationships/"):
            theory_id = uri.split("/")[-1]
            result = await tenjin.graph_service.get_theory_relationships(theory_id)
            return json.dumps(result, ensure_ascii=False, indent=2)

        elif uri == "tenjin://methodologies":
            result = await tenjin.methodology_service.list_methodologies(limit=100)
            return json.dumps(result, ensure_ascii=False, indent=2)

        elif uri.startswith("tenjin://methodology/"):
            methodology_id = uri.split("/")[-1]
            result = await tenjin.methodology_service.get_methodology(methodology_id)
            return json.dumps(result, ensure_ascii=False, indent=2)

        elif uri == "tenjin://graph/statistics":
            result = await tenjin.graph_service.get_graph_statistics()
            return json.dumps(result, ensure_ascii=False, indent=2)

        elif uri == "tenjin://graph/network":
            theories = await tenjin.theory_service.list_theories(limit=50)
            theory_ids = [t.get("id", "") for t in theories.get("theories", [])]
            result = await tenjin.graph_service.get_theory_network(
                theory_ids=theory_ids[:20], depth=1
            )
            return json.dumps(result, ensure_ascii=False, indent=2)

        elif uri == "tenjin://search/index-stats":
            result = await tenjin.search_service.get_index_statistics()
            return json.dumps(result, ensure_ascii=False, indent=2)

        else:
            return json.dumps({"error": f"Unknown resource: {uri}"})


__all__ = ["register_resources"]
