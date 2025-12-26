"""SearchService - Hybrid search operations."""

from typing import Any, Sequence

from ...domain.repositories.vector_repository import VectorRepository
from ...domain.repositories.theory_repository import TheoryRepository
from ...domain.value_objects.search_query import SearchQuery
from ...domain.value_objects.search_result import SearchResult, SearchResults
from ...domain.value_objects.category_type import CategoryType
from ...domain.value_objects.priority_level import PriorityLevel
from ...infrastructure.config.logging import get_logger

logger = get_logger(__name__)


class SearchService:
    """Service for search operations.

    Provides hybrid search combining semantic and keyword search,
    with optional LLM-based reranking.
    """

    def __init__(
        self,
        vector_repository: VectorRepository,
        theory_repository: TheoryRepository,
    ) -> None:
        """Initialize search service.

        Args:
            vector_repository: Repository for vector search.
            theory_repository: Repository for keyword search fallback.
        """
        self._vector_repo = vector_repository
        self._theory_repo = theory_repository

    async def search(
        self,
        query: str,
        search_type: str = "hybrid",
        categories: list[str] | None = None,
        priority_min: int = 5,
        priority_max: int = 1,
        limit: int = 10,
        language: str = "both",
    ) -> SearchResults:
        """Perform a search with the specified parameters.

        Args:
            query: Search query text.
            search_type: "semantic", "keyword", or "hybrid".
            categories: Optional list of category filters.
            priority_min: Minimum priority (5=lowest).
            priority_max: Maximum priority (1=highest).
            limit: Maximum results.
            language: "en", "ja", or "both".

        Returns:
            Search results.
        """
        # Build SearchQuery
        category_types = tuple(
            CategoryType.from_string(c) for c in (categories or [])
        )

        search_query = SearchQuery(
            query=query,
            search_type=search_type,  # type: ignore
            categories=category_types,
            priority_min=PriorityLevel.from_int(priority_min),
            priority_max=PriorityLevel.from_int(priority_max),
            limit=limit,
            language=language,  # type: ignore
        )

        if search_type == "semantic":
            return await self._vector_repo.semantic_search(search_query)
        elif search_type == "keyword":
            return await self._keyword_search(search_query)
        else:  # hybrid
            return await self._vector_repo.hybrid_search(search_query)

    async def _keyword_search(self, query: SearchQuery) -> SearchResults:
        """Perform keyword-based search.

        Args:
            query: Search query.

        Returns:
            Search results.
        """
        theories = await self._theory_repo.search_by_keyword(
            query.query, query.limit
        )

        results = [
            SearchResult(
                id=str(t.id),
                entity_type="theory",
                name=t.name,
                score=1.0,  # Keyword match doesn't provide score
                snippet=t.description[:300],
                metadata={
                    "name_ja": t.name_ja,
                    "category": t.category.value,
                    "priority": t.priority.value,
                },
            )
            for t in theories
        ]

        return SearchResults(
            results=tuple(results),
            total_count=len(results),
            query=query.query,
            search_type="keyword",
        )

    async def semantic_search(
        self,
        query: str,
        limit: int = 10,
        categories: list[str] | None = None,
    ) -> SearchResults:
        """Perform semantic search only.

        Args:
            query: Search query.
            limit: Maximum results.
            categories: Optional category filters.

        Returns:
            Semantic search results.
        """
        return await self.search(
            query=query,
            search_type="semantic",
            categories=categories,
            limit=limit,
        )

    async def find_similar(
        self,
        theory_id: str,
        limit: int = 10,
    ) -> Sequence[SearchResult]:
        """Find theories similar to a given theory.

        Args:
            theory_id: Source theory ID.
            limit: Maximum results.

        Returns:
            Similar theories.
        """
        return await self._vector_repo.similar_to(
            entity_id=theory_id,
            entity_type="theory",
            limit=limit,
        )

    async def search_with_reranking(
        self,
        query: str,
        limit: int = 10,
        initial_limit: int = 30,
    ) -> SearchResults:
        """Search with LLM-based reranking.

        Args:
            query: Search query.
            limit: Final number of results.
            initial_limit: Initial results before reranking.

        Returns:
            Reranked search results.
        """
        # Get initial results
        initial_results = await self.search(
            query=query,
            search_type="hybrid",
            limit=initial_limit,
        )

        # Rerank using LLM
        reranked = await self._vector_repo.rerank_results(
            query=query,
            results=initial_results.results,
            top_k=limit,
        )

        return SearchResults(
            results=tuple(reranked),
            total_count=initial_results.total_count,
            query=query,
            search_type="hybrid_reranked",
        )

    async def search_concepts(
        self,
        query: str,
        limit: int = 10,
    ) -> SearchResults:
        """Search for concepts.

        Args:
            query: Search query.
            limit: Maximum results.

        Returns:
            Concept search results.
        """
        search_query = SearchQuery(
            query=query,
            search_type="semantic",
            limit=limit,
        )

        results = await self._vector_repo.semantic_search(search_query)

        # Filter to concepts only
        concept_results = [r for r in results.results if r.entity_type == "concept"]

        return SearchResults(
            results=tuple(concept_results),
            total_count=len(concept_results),
            query=query,
            search_type="semantic",
        )

    async def get_search_suggestions(
        self,
        partial_query: str,
        limit: int = 5,
    ) -> list[str]:
        """Get search suggestions based on partial query.

        Args:
            partial_query: Partial search query.
            limit: Maximum suggestions.

        Returns:
            List of suggested queries.
        """
        # Search for matching theories
        theories = await self._theory_repo.search_by_keyword(partial_query, limit)

        suggestions = []
        for t in theories:
            if partial_query.lower() in t.name.lower():
                suggestions.append(t.name)
            if t.name_ja and partial_query in t.name_ja:
                suggestions.append(t.name_ja)

        return suggestions[:limit]

    async def index_entity(
        self,
        entity_id: str,
        entity_type: str,
        text: str,
        metadata: dict[str, Any] | None = None,
    ) -> bool:
        """Add or update an entity in the search index.

        Args:
            entity_id: Entity identifier.
            entity_type: Type of entity.
            text: Text content to index.
            metadata: Additional metadata.

        Returns:
            True if successful.
        """
        return await self._vector_repo.add_embedding(
            entity_id=entity_id,
            entity_type=entity_type,
            text=text,
            metadata=metadata,
        )

    async def remove_from_index(self, entity_id: str) -> bool:
        """Remove an entity from the search index.

        Args:
            entity_id: Entity identifier.

        Returns:
            True if successful.
        """
        return await self._vector_repo.delete_embedding(entity_id)

    async def get_index_statistics(self) -> dict[str, Any]:
        """Get search index statistics.

        Returns:
            Index statistics.
        """
        return await self._vector_repo.get_collection_stats()
