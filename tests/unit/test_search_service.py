"""Unit tests for SearchService."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from tenjin.application.services.search_service import SearchService
from tenjin.domain.entities.theory import Theory
from tenjin.domain.value_objects.theory_id import TheoryId
from tenjin.domain.value_objects.search_query import SearchQuery
from tenjin.domain.value_objects.search_result import SearchResult, SearchResults


class TestSearchService:
    """Tests for SearchService."""

    @pytest.fixture
    def mock_vector_repository(self) -> AsyncMock:
        """Create mock vector repository."""
        repo = AsyncMock()
        # Return SearchResults object as semantic_search does
        mock_results = SearchResults(
            results=(
                SearchResult(
                    id="theory-001",
                    entity_type="theory",
                    name="Constructivism",
                    score=0.95,
                    snippet="Learning as an active process",
                    metadata={"name_ja": "構成主義"},
                ),
            ),
            total_count=1,
            query="constructivism",
            search_type="semantic",
        )
        repo.semantic_search = AsyncMock(return_value=mock_results)
        repo.hybrid_search = AsyncMock(return_value=mock_results)
        repo.similar_to = AsyncMock(return_value=[
            SearchResult(
                id="theory-002",
                entity_type="theory",
                name="Social Constructivism",
                score=0.88,
                snippet="Learning through social interaction",
                metadata={"name_ja": "社会構成主義"},
            )
        ])
        return repo

    @pytest.fixture
    def mock_theory_repository(self, sample_theory: Theory) -> AsyncMock:
        """Create mock theory repository."""
        repo = AsyncMock()
        repo.get_by_id = AsyncMock(return_value=sample_theory)
        repo.get_by_ids = AsyncMock(return_value=[sample_theory])
        repo.search_by_keyword = AsyncMock(return_value=[sample_theory])
        return repo

    @pytest.fixture
    def search_service(
        self,
        mock_vector_repository: AsyncMock,
        mock_theory_repository: AsyncMock,
    ) -> SearchService:
        """Create search service with mocks."""
        return SearchService(
            vector_repository=mock_vector_repository,
            theory_repository=mock_theory_repository,
        )

    @pytest.mark.asyncio
    async def test_semantic_search(
        self,
        search_service: SearchService,
        mock_vector_repository: AsyncMock,
    ) -> None:
        """Test semantic search."""
        results = await search_service.search("constructivism learning", search_type="semantic")

        assert results is not None
        assert results.total_count >= 0
        mock_vector_repository.semantic_search.assert_called_once()

    @pytest.mark.asyncio
    async def test_hybrid_search(
        self,
        search_service: SearchService,
        mock_vector_repository: AsyncMock,
        mock_theory_repository: AsyncMock,
    ) -> None:
        """Test hybrid search combining vector and keyword."""
        results = await search_service.search("constructivism", search_type="hybrid")

        assert results is not None
        mock_vector_repository.hybrid_search.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_with_category_filter(
        self,
        search_service: SearchService,
        mock_vector_repository: AsyncMock,
    ) -> None:
        """Test search with category filter."""
        results = await search_service.search(
            query="learning",
            categories=["learning_theory"],
            limit=10,
        )

        assert results is not None

    @pytest.mark.asyncio
    async def test_find_similar_theories(
        self,
        search_service: SearchService,
        mock_theory_repository: AsyncMock,
        mock_vector_repository: AsyncMock,
        sample_theory: Theory,
    ) -> None:
        """Test finding similar theories."""
        similar = await search_service.find_similar("theory-001", limit=5)

        assert similar is not None
        mock_vector_repository.similar_to.assert_called_once()


class TestSearchQuery:
    """Tests for SearchQuery value object."""

    def test_create_search_query(self) -> None:
        """Test creating search query."""
        query = SearchQuery(
            query="constructivism",
            limit=20,
        )

        assert query.query == "constructivism"
        assert query.limit == 20

    def test_search_query_defaults(self) -> None:
        """Test search query default values."""
        query = SearchQuery(query="test")

        assert query.limit == 10
        assert query.categories == ()


class TestSearchResult:
    """Tests for SearchResult value object."""

    def test_create_search_result(self) -> None:
        """Test creating search result."""
        result = SearchResult(
            id="theory-001",
            entity_type="theory",
            name="Constructivism",
            score=0.95,
            snippet="Learning is active",
            metadata={"name_ja": "構成主義"},
        )

        assert result.id == "theory-001"
        assert result.score == 0.95
        assert result.entity_type == "theory"

    def test_search_result_optional_fields(self) -> None:
        """Test search result with optional fields."""
        result = SearchResult(
            id="theory-001",
            entity_type="theory",
            name="Test Theory",
            score=0.8,
        )

        assert result.snippet == ""
        assert result.metadata == {}
