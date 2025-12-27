"""Unit tests for SearchService."""

import pytest
from unittest.mock import AsyncMock

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
        repo.search = AsyncMock(
            return_value=[
                {
                    "id": "theory-001",
                    "score": 0.95,
                    "metadata": {
                        "name": "Constructivism",
                        "name_ja": "構成主義",
                    },
                }
            ]
        )
        return repo

    @pytest.fixture
    def mock_theory_repository(self, sample_theory: Theory) -> AsyncMock:
        """Create mock theory repository."""
        repo = AsyncMock()
        repo.get_by_id = AsyncMock(return_value=sample_theory)
        repo.get_by_ids = AsyncMock(return_value=[sample_theory])
        return repo

    @pytest.fixture
    def mock_llm_adapter(self) -> AsyncMock:
        """Create mock LLM adapter."""
        adapter = AsyncMock()
        adapter.chat = AsyncMock(return_value="Reranked results analysis")
        return adapter

    @pytest.fixture
    def search_service(
        self,
        mock_vector_repository: AsyncMock,
        mock_theory_repository: AsyncMock,
        mock_llm_adapter: AsyncMock,
    ) -> SearchService:
        """Create search service with mocks."""
        return SearchService(
            vector_repository=mock_vector_repository,
            theory_repository=mock_theory_repository,
            llm_adapter=mock_llm_adapter,
        )

    @pytest.mark.asyncio
    async def test_semantic_search(
        self,
        search_service: SearchService,
        mock_vector_repository: AsyncMock,
    ) -> None:
        """Test semantic search."""
        results = await search_service.semantic_search("constructivism learning")

        assert results is not None
        mock_vector_repository.search.assert_called_once()

    @pytest.mark.asyncio
    async def test_hybrid_search(
        self,
        search_service: SearchService,
        mock_vector_repository: AsyncMock,
        mock_theory_repository: AsyncMock,
    ) -> None:
        """Test hybrid search combining vector and keyword."""
        results = await search_service.hybrid_search("constructivism")

        assert results is not None

    @pytest.mark.asyncio
    async def test_search_with_category_filter(
        self,
        search_service: SearchService,
        mock_vector_repository: AsyncMock,
    ) -> None:
        """Test search with category filter."""
        from tenjin.domain.value_objects.category_type import CategoryType

        query = SearchQuery(
            text="learning",
            category=CategoryType.LEARNING_THEORY,
            limit=10,
        )

        results = await search_service.search(query)

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


class TestSearchQuery:
    """Tests for SearchQuery value object."""

    def test_create_search_query(self) -> None:
        """Test creating search query."""
        query = SearchQuery(
            text="constructivism",
            limit=20,
            offset=10,
        )

        assert query.text == "constructivism"
        assert query.limit == 20
        assert query.offset == 10

    def test_search_query_defaults(self) -> None:
        """Test search query default values."""
        query = SearchQuery(text="test")

        assert query.limit == 10
        assert query.offset == 0
        assert query.category is None


class TestSearchResult:
    """Tests for SearchResult value object."""

    def test_create_search_result(self) -> None:
        """Test creating search result."""
        result = SearchResult(
            theory_id=TheoryId("theory-001"),
            name="Constructivism",
            name_ja="構成主義",
            score=0.95,
            highlights=["constructivism"],
        )

        assert str(result.theory_id) == "theory-001"
        assert result.score == 0.95
        assert len(result.highlights) == 1

    def test_search_result_optional_fields(self) -> None:
        """Test search result with optional fields."""
        result = SearchResult(
            theory_id=TheoryId("theory-001"),
            name="Test Theory",
            name_ja="テスト理論",
            score=0.8,
        )

        assert result.highlights is None or result.highlights == []
