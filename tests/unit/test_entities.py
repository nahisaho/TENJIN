"""Unit tests for domain entities."""

import pytest

from tenjin.domain.entities.theory import Theory
from tenjin.domain.entities.theorist import Theorist
from tenjin.domain.entities.category import Category
from tenjin.domain.entities.relationship import TheoryRelationship
from tenjin.domain.value_objects.ids import TheoryId, TheoristId, CategoryId
from tenjin.domain.value_objects.category_type import CategoryType
from tenjin.domain.value_objects.priority_level import PriorityLevel
from tenjin.domain.value_objects.relationship_type import RelationshipType


class TestTheory:
    """Tests for Theory entity."""

    def test_create_theory(self) -> None:
        """Test creating a theory entity."""
        theory = Theory(
            id=TheoryId("theory-001"),
            name="Constructivism",
            name_ja="構成主義",
            category=CategoryType.LEARNING_THEORY,
            priority=PriorityLevel.HIGH,
            theorist_names=["Jean Piaget"],
            description="Learning theory description",
            description_ja="学習理論の説明",
        )

        assert str(theory.id) == "theory-001"
        assert theory.name == "Constructivism"
        assert theory.name_ja == "構成主義"
        assert theory.category == CategoryType.LEARNING_THEORY
        assert theory.priority == PriorityLevel.HIGH

    def test_theory_with_optional_fields(self, sample_theory: Theory) -> None:
        """Test theory with all optional fields."""
        assert sample_theory.key_principles is not None
        assert len(sample_theory.key_principles) > 0
        assert sample_theory.applications is not None
        assert sample_theory.strengths is not None
        assert sample_theory.limitations is not None

    def test_theory_equality(self) -> None:
        """Test theory equality by ID."""
        theory1 = Theory(
            id=TheoryId("theory-001"),
            name="Constructivism",
            name_ja="構成主義",
            category=CategoryType.LEARNING_THEORY,
            priority=PriorityLevel.HIGH,
        )
        theory2 = Theory(
            id=TheoryId("theory-001"),
            name="Different Name",
            name_ja="異なる名前",
            category=CategoryType.DEVELOPMENTAL,
            priority=PriorityLevel.LOW,
        )

        assert theory1.id == theory2.id


class TestTheorist:
    """Tests for Theorist entity."""

    def test_create_theorist(self) -> None:
        """Test creating a theorist entity."""
        theorist = Theorist(
            id=TheoristId("theorist-001"),
            name="Jean Piaget",
            name_ja="ジャン・ピアジェ",
            birth_year=1896,
            death_year=1980,
            nationality="Swiss",
            primary_field="Developmental Psychology",
        )

        assert str(theorist.id) == "theorist-001"
        assert theorist.name == "Jean Piaget"
        assert theorist.birth_year == 1896
        assert theorist.death_year == 1980

    def test_theorist_with_contributions(self, sample_theorist: Theorist) -> None:
        """Test theorist with contributions."""
        assert sample_theorist.contributions is not None
        assert "Cognitive Development Theory" in sample_theorist.contributions

    def test_theorist_with_related_theories(self, sample_theorist: Theorist) -> None:
        """Test theorist with related theories."""
        assert sample_theorist.related_theory_ids is not None
        assert len(sample_theorist.related_theory_ids) > 0


class TestCategory:
    """Tests for Category entity."""

    def test_create_category(self) -> None:
        """Test creating a category entity."""
        category = Category(
            id=CategoryId("learning_theory"),
            name="Learning Theory",
            name_ja="学習理論",
            description="Theories about learning",
            description_ja="学習に関する理論",
            theory_count=38,
        )

        assert str(category.id) == "learning_theory"
        assert category.name == "Learning Theory"
        assert category.theory_count == 38

    def test_category_with_color(self, sample_category: Category) -> None:
        """Test category with color."""
        assert sample_category.color is not None
        assert sample_category.color.startswith("#")


class TestTheoryRelationship:
    """Tests for TheoryRelationship entity."""

    def test_create_relationship(self) -> None:
        """Test creating a relationship entity."""
        relationship = TheoryRelationship(
            id="rel-001",
            source_id=TheoryId("theory-001"),
            target_id=TheoryId("theory-002"),
            relationship_type=RelationshipType.INFLUENCES,
            strength=0.8,
            description="Theory 1 influences Theory 2",
        )

        assert relationship.id == "rel-001"
        assert str(relationship.source_id) == "theory-001"
        assert str(relationship.target_id) == "theory-002"
        assert relationship.relationship_type == RelationshipType.INFLUENCES
        assert relationship.strength == 0.8

    def test_relationship_types(self) -> None:
        """Test all relationship types."""
        types = [
            RelationshipType.INFLUENCES,
            RelationshipType.EXTENDS,
            RelationshipType.CONTRASTS_WITH,
            RelationshipType.COMPLEMENTS,
            RelationshipType.DERIVED_FROM,
        ]

        for rel_type in types:
            relationship = TheoryRelationship(
                id=f"rel-{rel_type.value}",
                source_id=TheoryId("theory-001"),
                target_id=TheoryId("theory-002"),
                relationship_type=rel_type,
            )
            assert relationship.relationship_type == rel_type
