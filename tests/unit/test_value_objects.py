"""Unit tests for value objects."""

import pytest

from tenjin.domain.value_objects.ids import TheoryId, TheoristId, CategoryId, MethodologyId, EvidenceId, ConceptId
from tenjin.domain.value_objects.category_type import CategoryType
from tenjin.domain.value_objects.priority_level import PriorityLevel
from tenjin.domain.value_objects.relationship_type import RelationshipType
from tenjin.domain.value_objects.search import SearchQuery, SearchResult, SearchResults


class TestIds:
    """Tests for ID value objects."""

    def test_theory_id(self) -> None:
        """Test TheoryId creation and string conversion."""
        theory_id = TheoryId("theory-001")
        assert str(theory_id) == "theory-001"
        assert theory_id.value == "theory-001"

    def test_theorist_id(self) -> None:
        """Test TheoristId creation."""
        theorist_id = TheoristId("theorist-001")
        assert str(theorist_id) == "theorist-001"

    def test_category_id(self) -> None:
        """Test CategoryId creation."""
        category_id = CategoryId("learning_theory")
        assert str(category_id) == "learning_theory"

    def test_methodology_id(self) -> None:
        """Test MethodologyId creation."""
        methodology_id = MethodologyId("methodology-001")
        assert str(methodology_id) == "methodology-001"

    def test_evidence_id(self) -> None:
        """Test EvidenceId creation."""
        evidence_id = EvidenceId("evidence-001")
        assert str(evidence_id) == "evidence-001"

    def test_concept_id(self) -> None:
        """Test ConceptId creation."""
        concept_id = ConceptId("concept-001")
        assert str(concept_id) == "concept-001"

    def test_id_equality(self) -> None:
        """Test ID equality comparison."""
        id1 = TheoryId("theory-001")
        id2 = TheoryId("theory-001")
        id3 = TheoryId("theory-002")

        assert id1 == id2
        assert id1 != id3

    def test_id_hash(self) -> None:
        """Test ID hashing for use in sets/dicts."""
        id1 = TheoryId("theory-001")
        id2 = TheoryId("theory-001")

        id_set = {id1, id2}
        assert len(id_set) == 1


class TestCategoryType:
    """Tests for CategoryType enum."""

    def test_all_category_types(self) -> None:
        """Test all category type values."""
        expected_categories = [
            "learning_theory",
            "developmental",
            "instructional_design",
            "curriculum",
            "motivation",
            "assessment",
            "social_learning",
            "asian_education",
            "technology_enhanced",
            "modern_education",
            "critical_alternative",
        ]

        for category_value in expected_categories:
            category = CategoryType(category_value)
            assert category.value == category_value

    def test_category_type_from_string(self) -> None:
        """Test creating CategoryType from string."""
        category = CategoryType("learning_theory")
        assert category == CategoryType.LEARNING_THEORY

    def test_category_type_invalid(self) -> None:
        """Test invalid category type raises error."""
        with pytest.raises(ValueError):
            CategoryType("invalid_category")


class TestPriorityLevel:
    """Tests for PriorityLevel enum."""

    def test_priority_levels(self) -> None:
        """Test all priority level values."""
        assert PriorityLevel.CRITICAL.value == 5
        assert PriorityLevel.HIGH.value == 4
        assert PriorityLevel.MEDIUM.value == 3
        assert PriorityLevel.LOW.value == 2
        assert PriorityLevel.MINIMAL.value == 1

    def test_priority_comparison(self) -> None:
        """Test priority level comparison."""
        assert PriorityLevel.CRITICAL.value > PriorityLevel.HIGH.value
        assert PriorityLevel.HIGH.value > PriorityLevel.MEDIUM.value

    def test_priority_from_int(self) -> None:
        """Test creating PriorityLevel from integer."""
        priority = PriorityLevel(5)
        assert priority == PriorityLevel.CRITICAL


class TestRelationshipType:
    """Tests for RelationshipType enum."""

    def test_relationship_types(self) -> None:
        """Test relationship type values."""
        types = [
            ("influences", RelationshipType.INFLUENCES),
            ("extends", RelationshipType.EXTENDS),
            ("contrasts_with", RelationshipType.CONTRASTS_WITH),
            ("complements", RelationshipType.COMPLEMENTS),
            ("derived_from", RelationshipType.DERIVED_FROM),
            ("applied_in", RelationshipType.APPLIED_IN),
            ("evolved_into", RelationshipType.EVOLVED_INTO),
            ("integrates", RelationshipType.INTEGRATES),
            ("critiques", RelationshipType.CRITIQUES),
            ("supports", RelationshipType.SUPPORTS),
        ]

        for value, expected_type in types:
            rel_type = RelationshipType(value)
            assert rel_type == expected_type


class TestSearchValueObjects:
    """Tests for search-related value objects."""

    def test_search_query(self) -> None:
        """Test SearchQuery creation."""
        query = SearchQuery(
            text="constructivism learning",
            category=CategoryType.LEARNING_THEORY,
            limit=10,
            offset=0,
        )

        assert query.text == "constructivism learning"
        assert query.category == CategoryType.LEARNING_THEORY
        assert query.limit == 10
        assert query.offset == 0

    def test_search_query_defaults(self) -> None:
        """Test SearchQuery with default values."""
        query = SearchQuery(text="test query")

        assert query.text == "test query"
        assert query.category is None
        assert query.limit == 10
        assert query.offset == 0

    def test_search_result(self) -> None:
        """Test SearchResult creation."""
        result = SearchResult(
            theory_id=TheoryId("theory-001"),
            name="Constructivism",
            name_ja="構成主義",
            score=0.95,
            highlights=["constructivism", "learning"],
        )

        assert str(result.theory_id) == "theory-001"
        assert result.name == "Constructivism"
        assert result.score == 0.95
        assert len(result.highlights) == 2

    def test_search_results(self) -> None:
        """Test SearchResults container."""
        results = SearchResults(
            items=[
                SearchResult(
                    theory_id=TheoryId("theory-001"),
                    name="Theory 1",
                    name_ja="理論1",
                    score=0.95,
                ),
                SearchResult(
                    theory_id=TheoryId("theory-002"),
                    name="Theory 2",
                    name_ja="理論2",
                    score=0.85,
                ),
            ],
            total=2,
            query="test query",
        )

        assert len(results.items) == 2
        assert results.total == 2
        assert results.query == "test query"
