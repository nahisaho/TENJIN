"""Pytest configuration and fixtures for TENJIN tests."""

import asyncio
from collections.abc import Generator
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from tenjin.domain.entities.theory import Theory
from tenjin.domain.entities.theorist import Theorist
from tenjin.domain.entities.category import Category
from tenjin.domain.value_objects.theory_id import TheoryId
from tenjin.domain.value_objects.theorist_id import TheoristId
from tenjin.domain.value_objects.category_type import CategoryType
from tenjin.domain.value_objects.priority_level import PriorityLevel


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_theory() -> Theory:
    """Create sample theory for testing."""
    return Theory(
        id=TheoryId.from_string("theory-001"),
        name="Constructivism",
        name_ja="構成主義",
        category=CategoryType.CONSTRUCTIVIST,
        priority=PriorityLevel.CRITICAL,
        description="Learning theory where learners actively construct knowledge.",
        description_ja="学習者が能動的に知識を構築する学習理論",
        key_principles=[
            "Knowledge is actively constructed",
            "Learning builds on prior knowledge",
            "Social interaction facilitates learning",
        ],
        applications=[
            "Inquiry-based learning",
            "Problem-based learning",
            "Collaborative projects",
        ],
        strengths=["Promotes deep understanding", "Develops critical thinking"],
        limitations=["Time-intensive", "Assessment challenges"],
    )


@pytest.fixture
def sample_theory_2() -> Theory:
    """Create second sample theory for testing."""
    return Theory(
        id=TheoryId.from_string("theory-002"),
        name="Social Learning Theory",
        name_ja="社会的学習理論",
        category=CategoryType.SOCIAL_LEARNING,
        priority=PriorityLevel.CRITICAL,
        description="Learning through observation and modeling.",
        description_ja="観察とモデリングによる学習",
        key_principles=[
            "Observational learning",
            "Modeling",
            "Vicarious reinforcement",
        ],
        applications=[
            "Role modeling",
            "Video-based instruction",
            "Peer learning",
        ],
        strengths=["Explains complex social learning"],
        limitations=["Difficult to control modeling influences"],
    )


@pytest.fixture
def sample_theorist() -> Theorist:
    """Create sample theorist for testing."""
    return Theorist(
        id=TheoristId.from_string("theorist-001"),
        name="Jean Piaget",
        name_ja="ジャン・ピアジェ",
        birth_year=1896,
        death_year=1980,
        nationality="Swiss",
        biography="Swiss psychologist known for cognitive development theory.",
        contributions=["Cognitive Development Theory", "Constructivism"],
    )


@pytest.fixture
def sample_category() -> Category:
    """Create sample category for testing."""
    return Category(
        type=CategoryType.COGNITIVE_DEVELOPMENT,
        name="Cognitive Development",
        name_ja="認知発達理論",
        description="Fundamental theories explaining how learning occurs.",
        description_ja="学習がどのように起こるかを説明する基本理論。",
        theory_count=38,
    )


@pytest.fixture
def mock_neo4j_adapter() -> AsyncMock:
    """Create mock Neo4j adapter."""
    adapter = AsyncMock()
    adapter.connect = AsyncMock()
    adapter.close = AsyncMock()
    adapter.execute_read = AsyncMock(return_value=[])
    adapter.execute_write = AsyncMock(return_value=[])
    adapter.health_check = AsyncMock(return_value=True)
    return adapter


@pytest.fixture
def mock_chromadb_adapter() -> MagicMock:
    """Create mock ChromaDB adapter."""
    adapter = MagicMock()
    adapter.get_or_create_collection = MagicMock()
    adapter.add_document = AsyncMock()
    adapter.search = AsyncMock(return_value=[])
    adapter.delete_collection = AsyncMock()
    return adapter


@pytest.fixture
def mock_embedding_adapter() -> AsyncMock:
    """Create mock embedding adapter."""
    adapter = AsyncMock()
    adapter.embed_text = AsyncMock(return_value=[0.1] * 384)
    adapter.embed_texts = AsyncMock(return_value=[[0.1] * 384])
    return adapter


@pytest.fixture
def mock_esperanto_adapter() -> AsyncMock:
    """Create mock Esperanto LLM adapter."""
    adapter = AsyncMock()
    adapter.chat = AsyncMock(return_value="Sample LLM response")
    adapter.chat_stream = AsyncMock()
    adapter.health_check = AsyncMock(return_value=True)
    return adapter


@pytest.fixture
def data_dir() -> Path:
    """Get test data directory."""
    return Path(__file__).parent.parent / "data" / "theories"


@pytest.fixture
def sample_theories_json() -> dict[str, Any]:
    """Sample theories JSON for testing."""
    return {
        "metadata": {
            "version": "1.0.0",
            "total_theories": 2,
        },
        "theories": [
            {
                "id": "theory-001",
                "name": "Constructivism",
                "name_ja": "構成主義",
                "category": "learning_theory",
                "priority": 5,
                "theorists": ["Jean Piaget"],
                "description": "Learning theory where learners actively construct knowledge.",
                "description_ja": "学習者が能動的に知識を構築する学習理論",
                "key_principles": ["Knowledge is actively constructed"],
                "applications": ["Inquiry-based learning"],
                "strengths": ["Promotes deep understanding"],
                "limitations": ["Time-intensive"],
            },
            {
                "id": "theory-002",
                "name": "Social Learning Theory",
                "name_ja": "社会的学習理論",
                "category": "learning_theory",
                "priority": 5,
                "theorists": ["Albert Bandura"],
                "description": "Learning through observation and modeling.",
                "description_ja": "観察とモデリングによる学習",
                "key_principles": ["Observational learning"],
                "applications": ["Role modeling"],
                "strengths": ["Explains complex social learning"],
                "limitations": ["Difficult to control"],
            },
        ],
    }
