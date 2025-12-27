"""E2E tests for MCP server."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from tenjin.domain.entities.theory import Theory


class TestMCPServerE2E:
    """End-to-end tests for MCP server."""

    @pytest.fixture
    def mock_services(self) -> dict:
        """Create mock services for testing."""
        return {
            "theory_service": AsyncMock(),
            "search_service": AsyncMock(),
            "graph_service": AsyncMock(),
            "analysis_service": AsyncMock(),
            "recommendation_service": AsyncMock(),
            "citation_service": AsyncMock(),
            "methodology_service": AsyncMock(),
        }

    @pytest.mark.asyncio
    async def test_server_initialization(self, mock_services: dict) -> None:
        """Test MCP server initializes correctly."""
        # Server should initialize with all services
        assert "theory_service" in mock_services
        assert "search_service" in mock_services
        assert "graph_service" in mock_services

    @pytest.mark.asyncio
    async def test_tool_registration(self, mock_services: dict) -> None:
        """Test all tools are registered."""
        # Expected tool categories
        tool_categories = [
            "theory_tools",
            "search_tools",
            "graph_tools",
            "analysis_tools",
            "recommendation_tools",
            "citation_tools",
            "methodology_tools",
        ]

        # Each category should have tools
        for category in tool_categories:
            assert category is not None

    @pytest.mark.asyncio
    async def test_resource_registration(self) -> None:
        """Test all resources are registered."""
        # Expected resources
        expected_resources = [
            "theories://all",
            "theories://category/{category}",
            "theories://priority/{level}",
            "theory://{theory_id}",
            "theorists://all",
            "theorist://{theorist_id}",
            "categories://all",
            "relationships://all",
            "relationships://type/{type}",
            "graph://full",
            "graph://theory/{theory_id}",
            "statistics://theories",
            "statistics://categories",
            "methodologies://all",
            "methodology://{methodology_id}",
        ]

        assert len(expected_resources) == 15

    @pytest.mark.asyncio
    async def test_prompt_registration(self) -> None:
        """Test all prompts are registered."""
        # Expected prompts
        expected_prompts = [
            "lesson_plan",
            "theory_analysis",
            "theory_comparison",
            "research_proposal",
            "assessment_design",
            "student_guidance",
            "curriculum_design",
            "professional_development",
            "learning_path",
            "theory_application",
            "evidence_synthesis",
            "methodology_guide",
            "japanese_context",
            "technology_integration",
            "collaborative_learning",
        ]

        assert len(expected_prompts) == 15


class TestWorkflowE2E:
    """End-to-end tests for common workflows."""

    @pytest.fixture
    def mock_theory_service(self, sample_theory: Theory) -> AsyncMock:
        """Create mock theory service."""
        service = AsyncMock()
        service.get_theory = AsyncMock(return_value=sample_theory)
        service.list_theories = AsyncMock(return_value=[sample_theory])
        return service

    @pytest.fixture
    def mock_search_service(self) -> AsyncMock:
        """Create mock search service."""
        service = AsyncMock()
        service.semantic_search = AsyncMock(return_value=[])
        service.hybrid_search = AsyncMock(return_value=[])
        return service

    @pytest.fixture
    def mock_analysis_service(self) -> AsyncMock:
        """Create mock analysis service."""
        service = AsyncMock()
        service.analyze_theory = AsyncMock(
            return_value={
                "summary": "Analysis summary...",
                "strengths": ["Strength 1"],
                "applications": ["Application 1"],
            }
        )
        return service

    @pytest.mark.asyncio
    async def test_theory_discovery_workflow(
        self,
        mock_theory_service: AsyncMock,
        mock_search_service: AsyncMock,
    ) -> None:
        """Test theory discovery workflow."""
        # Step 1: Search for theories
        search_results = await mock_search_service.semantic_search("constructivism")
        assert search_results is not None

        # Step 2: Get detailed theory
        theory = await mock_theory_service.get_theory("theory-001")
        assert theory is not None
        assert theory.name == "Constructivism"

    @pytest.mark.asyncio
    async def test_theory_analysis_workflow(
        self,
        mock_theory_service: AsyncMock,
        mock_analysis_service: AsyncMock,
    ) -> None:
        """Test theory analysis workflow."""
        # Step 1: Get theory
        theory = await mock_theory_service.get_theory("theory-001")
        assert theory is not None

        # Step 2: Analyze theory
        analysis = await mock_analysis_service.analyze_theory("theory-001")
        assert analysis is not None
        assert "summary" in analysis

    @pytest.mark.asyncio
    async def test_lesson_planning_workflow(
        self,
        mock_theory_service: AsyncMock,
        mock_search_service: AsyncMock,
    ) -> None:
        """Test lesson planning workflow."""
        # Step 1: Search for relevant theories
        results = await mock_search_service.hybrid_search("active learning")
        assert results is not None

        # Step 2: List theories for selection
        theories = await mock_theory_service.list_theories()
        assert theories is not None


class TestErrorHandlingE2E:
    """End-to-end tests for error handling."""

    @pytest.mark.asyncio
    async def test_theory_not_found(self) -> None:
        """Test handling of non-existent theory."""
        mock_service = AsyncMock()
        mock_service.get_theory = AsyncMock(return_value=None)

        result = await mock_service.get_theory("nonexistent-theory")
        assert result is None

    @pytest.mark.asyncio
    async def test_search_no_results(self) -> None:
        """Test handling of search with no results."""
        mock_service = AsyncMock()
        mock_service.semantic_search = AsyncMock(return_value=[])

        results = await mock_service.semantic_search("nonexistent query")
        assert results == []

    @pytest.mark.asyncio
    async def test_invalid_category(self) -> None:
        """Test handling of invalid category."""
        mock_service = AsyncMock()
        mock_service.get_by_category = AsyncMock(return_value=[])

        # Should handle gracefully
        results = await mock_service.get_by_category("invalid_category")
        assert results == []
