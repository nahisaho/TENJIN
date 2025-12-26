"""GraphService - Graph exploration operations."""

from typing import Any, Sequence

from ...domain.entities.relationship import TheoryRelationship
from ...domain.repositories.graph_repository import GraphRepository
from ...domain.value_objects.relationship_type import RelationshipType
from ...infrastructure.config.logging import get_logger

logger = get_logger(__name__)


class GraphService:
    """Service for graph exploration operations.

    Provides graph traversal, relationship discovery,
    and network visualization data.
    """

    def __init__(self, graph_repository: GraphRepository) -> None:
        """Initialize graph service.

        Args:
            graph_repository: Repository for graph operations.
        """
        self._repository = graph_repository

    async def get_related_theories(
        self,
        theory_id: str,
        relationship_type: str | None = None,
        depth: int = 1,
        limit: int = 20,
    ) -> Sequence[dict[str, Any]]:
        """Get theories related to a given theory.

        Args:
            theory_id: Source theory ID.
            relationship_type: Optional relationship type filter.
            depth: Traversal depth.
            limit: Maximum results.

        Returns:
            Related theories with relationship info.
        """
        rel_type = None
        if relationship_type:
            try:
                rel_type = RelationshipType(relationship_type)
            except ValueError:
                logger.warning(f"Invalid relationship type: {relationship_type}")

        return await self._repository.get_related_theories(
            theory_id=theory_id,
            relationship_type=rel_type,
            depth=depth,
            limit=limit,
        )

    async def get_theory_relationships(
        self,
        theory_id: str,
        direction: str = "both",
    ) -> Sequence[dict[str, Any]]:
        """Get all relationships for a theory.

        Args:
            theory_id: Theory identifier.
            direction: "outgoing", "incoming", or "both".

        Returns:
            List of relationship dictionaries.
        """
        relationships = await self._repository.get_relationships(
            theory_id=theory_id,
            direction=direction,
        )

        return [r.to_dict() for r in relationships]

    async def find_path(
        self,
        source_id: str,
        target_id: str,
        max_depth: int = 5,
    ) -> dict[str, Any] | None:
        """Find shortest path between two theories.

        Args:
            source_id: Start theory ID.
            target_id: End theory ID.
            max_depth: Maximum path length.

        Returns:
            Path information or None if no path exists.
        """
        path = await self._repository.find_path(
            source_id=source_id,
            target_id=target_id,
            max_depth=max_depth,
        )

        if path:
            return {
                "source": source_id,
                "target": target_id,
                "path": path[0] if path else None,
                "exists": True,
            }
        return {
            "source": source_id,
            "target": target_id,
            "path": None,
            "exists": False,
        }

    async def get_theory_network(
        self,
        theory_id: str,
        depth: int = 2,
    ) -> dict[str, Any]:
        """Get network graph centered on a theory.

        Args:
            theory_id: Central theory ID.
            depth: Network depth.

        Returns:
            Network data with nodes and edges.
        """
        return await self._repository.get_theory_network(
            theory_id=theory_id,
            depth=depth,
        )

    async def get_category_network(
        self,
        category: str,
    ) -> dict[str, Any]:
        """Get network graph for a category.

        Args:
            category: Category name.

        Returns:
            Network data for the category.
        """
        return await self._repository.get_category_subgraph(category)

    async def get_influence_chain(
        self,
        theory_id: str,
        direction: str = "both",
        max_depth: int = 3,
    ) -> dict[str, Any]:
        """Get influence chain for a theory.

        Args:
            theory_id: Theory identifier.
            direction: "influencers", "influenced", or "both".
            max_depth: Maximum chain depth.

        Returns:
            Influence chain data.
        """
        chain = await self._repository.get_influence_chain(
            theory_id=theory_id,
            direction=direction,
            max_depth=max_depth,
        )

        return {
            "theory_id": theory_id,
            "direction": direction,
            "chain": list(chain),
            "depth": max_depth,
        }

    async def find_common_connections(
        self,
        theory_ids: list[str],
    ) -> Sequence[dict[str, Any]]:
        """Find theories connected to multiple given theories.

        Args:
            theory_ids: List of theory IDs to find connections for.

        Returns:
            Commonly connected theories.
        """
        return await self._repository.get_common_relationships(theory_ids)

    async def create_relationship(
        self,
        source_id: str,
        target_id: str,
        relationship_type: str,
        description: str = "",
        strength: float = 0.5,
        bidirectional: bool = False,
    ) -> TheoryRelationship:
        """Create a relationship between theories.

        Args:
            source_id: Source theory ID.
            target_id: Target theory ID.
            relationship_type: Type of relationship.
            description: Relationship description.
            strength: Relationship strength (0-1).
            bidirectional: Create reverse relationship too.

        Returns:
            Created relationship.
        """
        rel_type = RelationshipType(relationship_type)

        relationship = TheoryRelationship(
            source_id=source_id,
            target_id=target_id,
            relationship_type=rel_type,
            description=description,
            strength=strength,
            bidirectional=bidirectional,
        )

        return await self._repository.create_relationship(relationship)

    async def delete_relationship(
        self,
        source_id: str,
        target_id: str,
        relationship_type: str,
    ) -> bool:
        """Delete a relationship.

        Args:
            source_id: Source theory ID.
            target_id: Target theory ID.
            relationship_type: Type of relationship.

        Returns:
            True if deleted.
        """
        rel_type = RelationshipType(relationship_type)

        return await self._repository.delete_relationship(
            source_id=source_id,
            target_id=target_id,
            relationship_type=rel_type,
        )

    async def get_relationship_types(self) -> list[dict[str, str]]:
        """Get all available relationship types.

        Returns:
            List of relationship type info.
        """
        return [
            {
                "value": rt.value,
                "name": rt.display_name,
                "description": rt.description,
                "is_symmetric": rt.is_symmetric,
            }
            for rt in RelationshipType
        ]

    async def execute_custom_query(
        self,
        query: str,
        parameters: dict[str, Any] | None = None,
    ) -> Sequence[dict[str, Any]]:
        """Execute a custom Cypher query.

        Args:
            query: Cypher query string.
            parameters: Query parameters.

        Returns:
            Query results.

        Note:
            Use with caution - only for advanced use cases.
        """
        logger.info(f"Executing custom query: {query[:100]}...")
        return await self._repository.execute_cypher(query, parameters)

    async def get_graph_statistics(self) -> dict[str, Any]:
        """Get graph statistics.

        Returns:
            Statistics about the knowledge graph.
        """
        # Get node counts by label
        node_query = """
        MATCH (n)
        RETURN labels(n)[0] as label, count(*) as count
        """
        node_stats = await self._repository.execute_cypher(node_query)

        # Get relationship counts by type
        rel_query = """
        MATCH ()-[r]->()
        RETURN type(r) as type, count(*) as count
        """
        rel_stats = await self._repository.execute_cypher(rel_query)

        return {
            "nodes": {r["label"]: r["count"] for r in node_stats},
            "relationships": {r["type"]: r["count"] for r in rel_stats},
            "total_nodes": sum(r["count"] for r in node_stats),
            "total_relationships": sum(r["count"] for r in rel_stats),
        }
