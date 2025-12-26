"""GraphRepository interface - Abstract repository for graph operations."""

from abc import ABC, abstractmethod
from typing import Any, Sequence

from ..entities.relationship import TheoryRelationship
from ..value_objects.relationship_type import RelationshipType


class GraphRepository(ABC):
    """Abstract repository interface for graph-based operations.

    This interface defines operations for graph traversal and relationship
    management in the knowledge graph.
    """

    @abstractmethod
    async def get_related_theories(
        self,
        theory_id: str,
        relationship_type: RelationshipType | None = None,
        depth: int = 1,
        limit: int = 20,
    ) -> Sequence[dict[str, Any]]:
        """Get theories related to a given theory.

        Args:
            theory_id: Source theory ID.
            relationship_type: Optional filter by relationship type.
            depth: Maximum traversal depth.
            limit: Maximum number of results.

        Returns:
            Sequence of related theory data with relationship info.
        """
        ...

    @abstractmethod
    async def get_relationship(
        self,
        source_id: str,
        target_id: str,
    ) -> TheoryRelationship | None:
        """Get relationship between two theories.

        Args:
            source_id: Source theory ID.
            target_id: Target theory ID.

        Returns:
            Relationship if exists, None otherwise.
        """
        ...

    @abstractmethod
    async def get_relationships(
        self,
        theory_id: str,
        direction: str = "both",
    ) -> Sequence[TheoryRelationship]:
        """Get all relationships for a theory.

        Args:
            theory_id: Theory ID.
            direction: "outgoing", "incoming", or "both".

        Returns:
            Sequence of relationships.
        """
        ...

    @abstractmethod
    async def create_relationship(
        self,
        relationship: TheoryRelationship,
    ) -> TheoryRelationship:
        """Create a new relationship between theories.

        Args:
            relationship: Relationship to create.

        Returns:
            Created relationship.
        """
        ...

    @abstractmethod
    async def delete_relationship(
        self,
        source_id: str,
        target_id: str,
        relationship_type: RelationshipType,
    ) -> bool:
        """Delete a relationship.

        Args:
            source_id: Source theory ID.
            target_id: Target theory ID.
            relationship_type: Type of relationship.

        Returns:
            True if deleted, False if not found.
        """
        ...

    @abstractmethod
    async def find_path(
        self,
        source_id: str,
        target_id: str,
        max_depth: int = 5,
    ) -> Sequence[dict[str, Any]] | None:
        """Find shortest path between two theories.

        Args:
            source_id: Source theory ID.
            target_id: Target theory ID.
            max_depth: Maximum path length.

        Returns:
            Path as sequence of nodes/relationships, None if no path.
        """
        ...

    @abstractmethod
    async def get_theory_network(
        self,
        theory_id: str,
        depth: int = 2,
    ) -> dict[str, Any]:
        """Get network graph around a theory.

        Args:
            theory_id: Central theory ID.
            depth: Network depth.

        Returns:
            Dictionary with nodes and edges.
        """
        ...

    @abstractmethod
    async def get_category_subgraph(
        self,
        category: str,
    ) -> dict[str, Any]:
        """Get subgraph for a category.

        Args:
            category: Category name.

        Returns:
            Dictionary with nodes and edges.
        """
        ...

    @abstractmethod
    async def get_influence_chain(
        self,
        theory_id: str,
        direction: str = "both",
        max_depth: int = 3,
    ) -> Sequence[dict[str, Any]]:
        """Get influence chain for a theory.

        Args:
            theory_id: Theory ID.
            direction: "influencers", "influenced", or "both".
            max_depth: Maximum chain depth.

        Returns:
            Sequence of theories in influence chain.
        """
        ...

    @abstractmethod
    async def get_common_relationships(
        self,
        theory_ids: Sequence[str],
    ) -> Sequence[dict[str, Any]]:
        """Find common relationships among theories.

        Args:
            theory_ids: List of theory IDs.

        Returns:
            Theories related to all given theories.
        """
        ...

    @abstractmethod
    async def execute_cypher(
        self,
        query: str,
        parameters: dict[str, Any] | None = None,
    ) -> Sequence[dict[str, Any]]:
        """Execute a Cypher query directly.

        Args:
            query: Cypher query string.
            parameters: Query parameters.

        Returns:
            Query results.
        """
        ...
