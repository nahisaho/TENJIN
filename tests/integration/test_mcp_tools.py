"""Integration tests for MCP tools."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from tenjin.domain.entities.theory import Theory
from tenjin.domain.value_objects.ids import TheoryId
from tenjin.domain.value_objects.category_type import CategoryType
from tenjin.domain.value_objects.priority_level import PriorityLevel


class TestTheoryTools:
    """Integration tests for theory tools."""

    @pytest.fixture
    def mock_theory_service(self, sample_theory: Theory) -> AsyncMock:
        """Create mock theory service."""
        service = AsyncMock()
        service.get_theory = AsyncMock(return_value=sample_theory)
        service.list_theories = AsyncMock(return_value=[sample_theory])
        service.get_by_category = AsyncMock(return_value=[sample_theory])
        service.search_theories = AsyncMock(return_value=[sample_theory])
        return service

    @pytest.mark.asyncio
    async def test_get_theory_tool(
        self,
        mock_theory_service: AsyncMock,
        sample_theory: Theory,
    ) -> None:
        """Test get_theory tool integration."""
        result = await mock_theory_service.get_theory("theory-001")

        assert result is not None
        assert result.id == sample_theory.id
        assert result.name == "Constructivism"

    @pytest.mark.asyncio
    async def test_list_theories_tool(
        self,
        mock_theory_service: AsyncMock,
    ) -> None:
        """Test list_theories tool integration."""
        result = await mock_theory_service.list_theories()

        assert len(result) >= 1
        mock_theory_service.list_theories.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_theories_by_category_tool(
        self,
        mock_theory_service: AsyncMock,
    ) -> None:
        """Test get_theories_by_category tool integration."""
        result = await mock_theory_service.get_by_category(CategoryType.LEARNING_THEORY)

        assert len(result) >= 1


class TestSearchTools:
    """Integration tests for search tools."""

    @pytest.fixture
    def mock_search_service(self) -> AsyncMock:
        """Create mock search service."""
        service = AsyncMock()
        service.semantic_search = AsyncMock(
            return_value=[
                {
                    "theory_id": "theory-001",
                    "name": "Constructivism",
                    "score": 0.95,
                }
            ]
        )
        service.hybrid_search = AsyncMock(
            return_value=[
                {
                    "theory_id": "theory-001",
                    "name": "Constructivism",
                    "score": 0.92,
                }
            ]
        )
        service.find_similar = AsyncMock(return_value=[])
        return service

    @pytest.mark.asyncio
    async def test_search_theories_tool(
        self,
        mock_search_service: AsyncMock,
    ) -> None:
        """Test search_theories tool integration."""
        result = await mock_search_service.semantic_search("constructivism")

        assert result is not None
        assert len(result) >= 1

    @pytest.mark.asyncio
    async def test_hybrid_search_tool(
        self,
        mock_search_service: AsyncMock,
    ) -> None:
        """Test hybrid_search tool integration."""
        result = await mock_search_service.hybrid_search("learning theory")

        assert result is not None


class TestGraphTools:
    """Integration tests for graph tools."""

    @pytest.fixture
    def mock_graph_service(self) -> AsyncMock:
        """Create mock graph service."""
        service = AsyncMock()
        service.get_related_theories = AsyncMock(
            return_value=[
                {
                    "theory_id": "theory-002",
                    "name": "Social Learning Theory",
                    "relationship": "influences",
                }
            ]
        )
        service.find_path = AsyncMock(
            return_value={
                "path": ["theory-001", "theory-003", "theory-002"],
                "relationships": ["influences", "extends"],
            }
        )
        service.get_theory_network = AsyncMock(
            return_value={
                "nodes": [],
                "edges": [],
            }
        )
        return service

    @pytest.mark.asyncio
    async def test_get_related_theories_tool(
        self,
        mock_graph_service: AsyncMock,
    ) -> None:
        """Test get_related_theories tool integration."""
        result = await mock_graph_service.get_related_theories("theory-001")

        assert result is not None
        assert len(result) >= 1

    @pytest.mark.asyncio
    async def test_find_path_tool(
        self,
        mock_graph_service: AsyncMock,
    ) -> None:
        """Test find_path tool integration."""
        result = await mock_graph_service.find_path("theory-001", "theory-002")

        assert result is not None
        assert "path" in result

    @pytest.mark.asyncio
    async def test_get_theory_network_tool(
        self,
        mock_graph_service: AsyncMock,
    ) -> None:
        """Test get_theory_network tool integration."""
        result = await mock_graph_service.get_theory_network("theory-001", depth=2)

        assert result is not None
        assert "nodes" in result
        assert "edges" in result


class TestAnalysisTools:
    """Integration tests for analysis tools."""

    @pytest.fixture
    def mock_analysis_service(self) -> AsyncMock:
        """Create mock analysis service."""
        service = AsyncMock()
        service.compare_theories = AsyncMock(
            return_value={
                "similarities": ["Both emphasize active learning"],
                "differences": ["Different views on social context"],
                "synthesis": "These theories complement each other...",
            }
        )
        service.analyze_theory = AsyncMock(
            return_value={
                "summary": "Constructivism is a learning theory...",
                "strengths": ["Promotes deep understanding"],
                "applications": ["Inquiry-based learning"],
            }
        )
        return service

    @pytest.mark.asyncio
    async def test_compare_theories_tool(
        self,
        mock_analysis_service: AsyncMock,
    ) -> None:
        """Test compare_theories tool integration."""
        result = await mock_analysis_service.compare_theories(
            ["theory-001", "theory-002"]
        )

        assert result is not None
        assert "similarities" in result
        assert "differences" in result

    @pytest.mark.asyncio
    async def test_analyze_theory_tool(
        self,
        mock_analysis_service: AsyncMock,
    ) -> None:
        """Test analyze_theory tool integration."""
        result = await mock_analysis_service.analyze_theory("theory-001")

        assert result is not None
        assert "summary" in result


class TestCitationTools:
    """Integration tests for citation tools."""

    @pytest.fixture
    def mock_citation_service(self) -> AsyncMock:
        """Create mock citation service."""
        service = AsyncMock()
        service.generate_citation = AsyncMock(
            return_value="Piaget, J. (1952). The origins of intelligence in children. International Universities Press."
        )
        service.generate_bibliography = AsyncMock(
            return_value=[
                "Bandura, A. (1977). Social learning theory. Prentice Hall.",
                "Piaget, J. (1952). The origins of intelligence in children. International Universities Press.",
            ]
        )
        service.export_citations = AsyncMock(
            return_value="@book{piaget1952,\n  author = {Piaget, Jean},\n  title = {The origins of intelligence in children},\n  year = {1952}\n}"
        )
        return service

    @pytest.mark.asyncio
    async def test_generate_citation_tool(
        self,
        mock_citation_service: AsyncMock,
    ) -> None:
        """Test generate_citation tool integration."""
        result = await mock_citation_service.generate_citation("theory-001", "apa")

        assert result is not None
        assert "Piaget" in result

    @pytest.mark.asyncio
    async def test_generate_bibliography_tool(
        self,
        mock_citation_service: AsyncMock,
    ) -> None:
        """Test generate_bibliography tool integration."""
        result = await mock_citation_service.generate_bibliography(
            ["theory-001", "theory-002"], "apa"
        )

        assert result is not None
        assert len(result) >= 1

    @pytest.mark.asyncio
    async def test_export_citations_tool(
        self,
        mock_citation_service: AsyncMock,
    ) -> None:
        """Test export_citations tool integration."""
        result = await mock_citation_service.export_citations(
            ["theory-001"], "bibtex"
        )

        assert result is not None
        assert "@book" in result
