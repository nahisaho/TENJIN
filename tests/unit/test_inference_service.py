"""Tests for InferenceService - Advanced LLM-powered reasoning operations."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from tenjin.application.services.inference_service import InferenceService
from tenjin.domain.entities.theory import Theory
from tenjin.domain.value_objects.theory_id import TheoryId
from tenjin.domain.value_objects.category_type import CategoryType
from tenjin.domain.value_objects.priority_level import PriorityLevel


@pytest.fixture
def mock_theory_repository():
    """Create a mock theory repository."""
    repo = AsyncMock()
    return repo


@pytest.fixture
def mock_vector_repository():
    """Create a mock vector repository."""
    repo = AsyncMock()
    return repo


@pytest.fixture
def mock_graph_repository():
    """Create a mock graph repository."""
    repo = AsyncMock()
    return repo


@pytest.fixture
def mock_llm_adapter():
    """Create a mock LLM adapter."""
    adapter = AsyncMock()
    return adapter


@pytest.fixture
def sample_theory():
    """Create a sample theory for testing."""
    return Theory(
        id=TheoryId.from_string("THEORY-001"),
        name="Constructivism",
        name_ja="構成主義",
        category=CategoryType.CONSTRUCTIVIST,
        description="Learning as an active, constructive process",
        description_ja="学習は能動的・構成的プロセスである",
        priority=PriorityLevel.HIGH,
        key_principles=["Active learning", "Prior knowledge", "Social interaction"],
        applications=["Project-based learning", "Collaborative activities"],
        strengths=["Promotes deep understanding"],
        limitations=["Time-intensive"],
    )


@pytest.fixture
def inference_service(
    mock_theory_repository,
    mock_vector_repository,
    mock_graph_repository,
    mock_llm_adapter
):
    """Create an InferenceService instance with mocked dependencies."""
    return InferenceService(
        theory_repository=mock_theory_repository,
        vector_repository=mock_vector_repository,
        graph_repository=mock_graph_repository,
        llm_adapter=mock_llm_adapter,
    )


class TestRecommendTheoriesForLearner:
    """Tests for recommend_theories_for_learner method."""

    @pytest.mark.asyncio
    async def test_recommend_with_valid_profile(
        self, inference_service, mock_vector_repository, mock_theory_repository, sample_theory
    ):
        """Test recommendation with valid learner profile."""
        # Setup mocks
        mock_search_result = MagicMock()
        mock_search_result.results = [
            MagicMock(entity_id=TheoryId.from_string("THEORY-001"), relevance_score=0.9)
        ]
        mock_vector_repository.search.return_value = mock_search_result
        mock_theory_repository.get_by_id.return_value = sample_theory

        # Execute
        result = await inference_service.recommend_theories_for_learner(
            learner_profile={"age": "adult", "level": "beginner"},
            learning_goals=["Understand constructivism"],
            limit=5,
        )

        # Verify
        assert "learning_goals" in result
        assert "recommendations" in result or "message" in result
        mock_vector_repository.search.assert_called_once()

    @pytest.mark.asyncio
    async def test_recommend_with_no_matches(
        self, inference_service, mock_vector_repository
    ):
        """Test recommendation when no matching theories found."""
        # Setup mock with empty results
        mock_search_result = MagicMock()
        mock_search_result.results = []
        mock_vector_repository.search.return_value = mock_search_result

        # Execute
        result = await inference_service.recommend_theories_for_learner(
            learner_profile={},
            learning_goals=["Unknown topic"],
            limit=5,
        )

        # Verify
        assert result["recommendations"] == []
        assert "No matching theories found" in result["message"]


class TestAnalyzeLearningDesignGaps:
    """Tests for analyze_learning_design_gaps method."""

    @pytest.mark.asyncio
    async def test_gap_analysis_with_applied_theories(
        self, inference_service, mock_theory_repository, mock_vector_repository,
        mock_llm_adapter, sample_theory
    ):
        """Test gap analysis with specified applied theories."""
        # Setup mocks
        mock_theory_repository.get_by_id.return_value = sample_theory
        mock_search_result = MagicMock()
        mock_search_result.results = []
        mock_vector_repository.search.return_value = mock_search_result
        mock_llm_adapter.generate.return_value = '{"theoretical_gaps": [], "overall_score": 75}'

        # Execute
        result = await inference_service.analyze_learning_design_gaps(
            current_design={"activities": "lectures", "assessment": "tests"},
            target_outcomes=["Critical thinking", "Problem solving"],
            applied_theories=["THEORY-001"],
        )

        # Verify
        assert "current_design" in result
        assert "target_outcomes" in result
        assert "analysis" in result

    @pytest.mark.asyncio
    async def test_gap_analysis_without_applied_theories(
        self, inference_service, mock_vector_repository, mock_llm_adapter
    ):
        """Test gap analysis without any applied theories."""
        # Setup mocks
        mock_search_result = MagicMock()
        mock_search_result.results = []
        mock_vector_repository.search.return_value = mock_search_result
        mock_llm_adapter.generate.return_value = '{"theoretical_gaps": [], "overall_score": 50}'

        # Execute
        result = await inference_service.analyze_learning_design_gaps(
            current_design={"activities": "self-study"},
            target_outcomes=["Basic understanding"],
        )

        # Verify
        assert result["applied_theories"] == []


class TestInferTheoryRelationships:
    """Tests for infer_theory_relationships method."""

    @pytest.mark.asyncio
    async def test_infer_relationships_valid_theory(
        self, inference_service, mock_theory_repository, mock_graph_repository,
        mock_llm_adapter, sample_theory
    ):
        """Test relationship inference for a valid theory."""
        # Setup mocks
        mock_theory_repository.get_by_id.return_value = sample_theory
        mock_theory_repository.get_all.return_value = [sample_theory]
        mock_graph_repository.get_related_theories.return_value = []
        mock_llm_adapter.generate.return_value = '{"inferred_relationships": []}'

        # Execute
        result = await inference_service.infer_theory_relationships(
            theory_id="THEORY-001",
            inference_depth=2,
        )

        # Verify
        assert "base_theory" in result
        assert "existing_relationships" in result
        assert "inferred_relationships" in result
        assert "relationship_graph" in result

    @pytest.mark.asyncio
    async def test_infer_relationships_invalid_theory_id(
        self, inference_service, mock_theory_repository
    ):
        """Test relationship inference with non-existent theory ID."""
        # Theory not found in repository
        mock_theory_repository.get_by_id.return_value = None

        result = await inference_service.infer_theory_relationships(
            theory_id="NON-EXISTENT-001",
            inference_depth=2,
        )

        assert "error" in result
        assert "Theory not found" in result["error"]

    @pytest.mark.asyncio
    async def test_infer_relationships_theory_not_found(
        self, inference_service, mock_theory_repository
    ):
        """Test relationship inference when theory not found."""
        mock_theory_repository.get_by_id.return_value = None

        result = await inference_service.infer_theory_relationships(
            theory_id="THEORY-999",
            inference_depth=2,
        )

        assert "error" in result
        assert "Theory not found" in result["error"]


class TestReasonAboutApplication:
    """Tests for reason_about_application method."""

    @pytest.mark.asyncio
    async def test_reason_with_valid_scenario(
        self, inference_service, mock_vector_repository, mock_theory_repository,
        mock_llm_adapter, sample_theory
    ):
        """Test reasoning about a valid educational scenario."""
        # Setup mocks
        mock_search_result = MagicMock()
        mock_search_result.results = [
            MagicMock(entity_id=TheoryId.from_string("THEORY-001"), relevance_score=0.85)
        ]
        mock_vector_repository.search.return_value = mock_search_result
        mock_theory_repository.get_by_id.return_value = sample_theory
        mock_llm_adapter.generate.return_value = '''
        {
            "primary_recommendation": {
                "theory": "Constructivism",
                "confidence": 0.9,
                "evidence": ["Active learning scenario"],
                "application_strategy": "Use project-based learning"
            },
            "secondary_recommendations": [],
            "reasoning_chain": [],
            "potential_pitfalls": [],
            "success_factors": [],
            "evaluation_criteria": []
        }
        '''

        # Execute
        result = await inference_service.reason_about_application(
            scenario="Teaching programming to high school students",
            constraints={"time": "1 semester", "setting": "classroom"},
        )

        # Verify
        assert "scenario" in result
        assert "reasoning" in result
        mock_vector_repository.search.assert_called_once()

    @pytest.mark.asyncio
    async def test_reason_with_empty_scenario(
        self, inference_service, mock_vector_repository
    ):
        """Test reasoning with empty scenario returns error."""
        result = await inference_service.reason_about_application(
            scenario="",
            constraints=None,
        )

        assert "scenario" in result
        assert result["scenario"] == ""
        assert "reasoning" in result
        assert "error" in result["reasoning"]


class TestBuildRelationshipGraph:
    """Tests for _build_relationship_graph method."""

    @pytest.mark.asyncio
    async def test_build_graph_structure(self, inference_service, sample_theory):
        """Test that graph structure is correctly built."""
        existing = [
            {"theory": {"id": "THEORY-002", "name": "Behaviorism", "name_ja": "行動主義", "category": "learning_theory"}}
        ]
        inferred = [
            {"related_theory": {"id": "THEORY-003", "name": "Cognitivism", "name_ja": "認知主義", "category": "learning_theory"}, "relationship_type": "complement", "strength": 0.8}
        ]

        result = await inference_service._build_relationship_graph(
            sample_theory, existing, inferred
        )

        assert "nodes" in result
        assert "edges" in result
        assert result["node_count"] == 3  # base + 1 existing + 1 inferred
        assert result["edge_count"] == 2
        assert result["inferred_count"] == 1
