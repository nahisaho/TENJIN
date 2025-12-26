"""VectorRepository interface - Abstract repository for vector operations."""

from abc import ABC, abstractmethod
from typing import Any, Sequence

from ..value_objects.search_query import SearchQuery
from ..value_objects.search_result import SearchResult, SearchResults


class VectorRepository(ABC):
    """Abstract repository interface for vector-based operations.

    This interface defines operations for semantic search and embedding
    management in the vector database.
    """

    @abstractmethod
    async def semantic_search(
        self,
        query: SearchQuery,
    ) -> SearchResults:
        """Perform semantic search using embeddings.

        Args:
            query: Search query parameters.

        Returns:
            Search results with relevance scores.
        """
        ...

    @abstractmethod
    async def similar_to(
        self,
        entity_id: str,
        entity_type: str,
        limit: int = 10,
    ) -> Sequence[SearchResult]:
        """Find entities similar to a given entity.

        Args:
            entity_id: Source entity ID.
            entity_type: Type of entity.
            limit: Maximum results.

        Returns:
            Similar entities with similarity scores.
        """
        ...

    @abstractmethod
    async def add_embedding(
        self,
        entity_id: str,
        entity_type: str,
        text: str,
        metadata: dict[str, Any] | None = None,
    ) -> bool:
        """Add or update embedding for an entity.

        Args:
            entity_id: Entity ID.
            entity_type: Type of entity.
            text: Text to embed.
            metadata: Additional metadata.

        Returns:
            True if successful.
        """
        ...

    @abstractmethod
    async def delete_embedding(self, entity_id: str) -> bool:
        """Delete embedding for an entity.

        Args:
            entity_id: Entity ID.

        Returns:
            True if deleted, False if not found.
        """
        ...

    @abstractmethod
    async def get_embedding(self, entity_id: str) -> list[float] | None:
        """Get raw embedding vector for an entity.

        Args:
            entity_id: Entity ID.

        Returns:
            Embedding vector or None.
        """
        ...

    @abstractmethod
    async def batch_add_embeddings(
        self,
        items: Sequence[dict[str, Any]],
    ) -> int:
        """Add multiple embeddings in batch.

        Args:
            items: List of dicts with id, type, text, metadata.

        Returns:
            Number of embeddings added.
        """
        ...

    @abstractmethod
    async def hybrid_search(
        self,
        query: SearchQuery,
        keyword_weight: float = 0.3,
        semantic_weight: float = 0.7,
    ) -> SearchResults:
        """Perform hybrid search combining keyword and semantic.

        Args:
            query: Search query parameters.
            keyword_weight: Weight for keyword matches.
            semantic_weight: Weight for semantic similarity.

        Returns:
            Combined search results.
        """
        ...

    @abstractmethod
    async def rerank_results(
        self,
        query: str,
        results: Sequence[SearchResult],
        top_k: int = 10,
    ) -> Sequence[SearchResult]:
        """Rerank search results using LLM.

        Args:
            query: Original query.
            results: Initial search results.
            top_k: Number of results to return.

        Returns:
            Reranked results.
        """
        ...

    @abstractmethod
    async def get_collection_stats(self) -> dict[str, Any]:
        """Get statistics about the vector collection.

        Returns:
            Dictionary with collection statistics.
        """
        ...

    @abstractmethod
    async def clear_collection(self) -> bool:
        """Clear all embeddings from the collection.

        Returns:
            True if successful.
        """
        ...
