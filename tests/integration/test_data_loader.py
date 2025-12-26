"""Integration tests for data loader."""

import json
import pytest
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

from tenjin.infrastructure.data.data_loader import DataLoader


class TestDataLoader:
    """Integration tests for DataLoader."""

    @pytest.fixture
    def mock_neo4j_adapter(self) -> AsyncMock:
        """Create mock Neo4j adapter."""
        adapter = AsyncMock()
        adapter.execute_write = AsyncMock(return_value=[])
        adapter.execute_read = AsyncMock(return_value=[])
        return adapter

    @pytest.fixture
    def mock_chromadb_adapter(self) -> AsyncMock:
        """Create mock ChromaDB adapter."""
        adapter = AsyncMock()
        adapter.get_or_create_collection = AsyncMock()
        adapter.add_document = AsyncMock()
        adapter.delete_collection = AsyncMock()
        return adapter

    @pytest.fixture
    def mock_embedding_adapter(self) -> AsyncMock:
        """Create mock embedding adapter."""
        adapter = AsyncMock()
        adapter.embed_text = AsyncMock(return_value=[0.1] * 384)
        return adapter

    @pytest.fixture
    def temp_data_dir(self, tmp_path: Path, sample_theories_json: dict[str, Any]) -> Path:
        """Create temporary data directory with test files."""
        data_dir = tmp_path / "theories"
        data_dir.mkdir()

        # Write test theories.json
        with open(data_dir / "theories.json", "w", encoding="utf-8") as f:
            json.dump(sample_theories_json, f)

        # Write test categories.json
        categories = {
            "metadata": {"version": "1.0.0"},
            "categories": [
                {
                    "id": "learning_theory",
                    "name": "Learning Theory",
                    "name_ja": "学習理論",
                    "description": "Theories about learning",
                    "description_ja": "学習に関する理論",
                    "theory_count": 2,
                }
            ],
        }
        with open(data_dir / "categories.json", "w", encoding="utf-8") as f:
            json.dump(categories, f)

        # Write test theorists.json
        theorists = {
            "metadata": {"version": "1.0.0"},
            "theorists": [
                {
                    "id": "theorist-001",
                    "name": "Jean Piaget",
                    "name_ja": "ジャン・ピアジェ",
                    "birth_year": 1896,
                    "death_year": 1980,
                    "nationality": "Swiss",
                    "primary_field": "Developmental Psychology",
                    "contributions": ["Cognitive Development Theory"],
                    "key_works": [],
                    "related_theories": ["theory-001"],
                }
            ],
        }
        with open(data_dir / "theorists.json", "w", encoding="utf-8") as f:
            json.dump(theorists, f)

        # Write test relationships.json
        relationships = {
            "metadata": {"version": "1.0.0"},
            "relationships": [
                {
                    "id": "rel-001",
                    "source_id": "theory-001",
                    "target_id": "theory-002",
                    "relationship_type": "influences",
                    "strength": 0.8,
                    "description": "Theory 1 influences Theory 2",
                }
            ],
        }
        with open(data_dir / "relationships.json", "w", encoding="utf-8") as f:
            json.dump(relationships, f)

        return data_dir

    @pytest.fixture
    def data_loader(
        self,
        mock_neo4j_adapter: AsyncMock,
        mock_chromadb_adapter: AsyncMock,
        mock_embedding_adapter: AsyncMock,
        temp_data_dir: Path,
    ) -> DataLoader:
        """Create DataLoader with mocks."""
        return DataLoader(
            neo4j_adapter=mock_neo4j_adapter,
            chromadb_adapter=mock_chromadb_adapter,
            embedding_adapter=mock_embedding_adapter,
            data_dir=temp_data_dir,
        )

    @pytest.mark.asyncio
    async def test_load_categories(
        self,
        data_loader: DataLoader,
        mock_neo4j_adapter: AsyncMock,
    ) -> None:
        """Test loading categories."""
        categories = await data_loader.load_categories()

        assert len(categories) == 1
        assert categories[0].name == "Learning Theory"
        mock_neo4j_adapter.execute_write.assert_called()

    @pytest.mark.asyncio
    async def test_load_theorists(
        self,
        data_loader: DataLoader,
        mock_neo4j_adapter: AsyncMock,
    ) -> None:
        """Test loading theorists."""
        theorists = await data_loader.load_theorists()

        assert len(theorists) == 1
        assert theorists[0].name == "Jean Piaget"
        mock_neo4j_adapter.execute_write.assert_called()

    @pytest.mark.asyncio
    async def test_load_theories(
        self,
        data_loader: DataLoader,
        mock_neo4j_adapter: AsyncMock,
        mock_chromadb_adapter: AsyncMock,
        mock_embedding_adapter: AsyncMock,
    ) -> None:
        """Test loading theories."""
        theories = await data_loader.load_theories()

        assert len(theories) == 2
        assert theories[0].name == "Constructivism"
        mock_neo4j_adapter.execute_write.assert_called()
        mock_chromadb_adapter.add_document.assert_called()
        mock_embedding_adapter.embed_text.assert_called()

    @pytest.mark.asyncio
    async def test_load_relationships(
        self,
        data_loader: DataLoader,
        mock_neo4j_adapter: AsyncMock,
    ) -> None:
        """Test loading relationships."""
        relationships = await data_loader.load_relationships()

        assert len(relationships) == 1
        mock_neo4j_adapter.execute_write.assert_called()

    @pytest.mark.asyncio
    async def test_load_all(
        self,
        data_loader: DataLoader,
        mock_chromadb_adapter: AsyncMock,
    ) -> None:
        """Test loading all data."""
        counts = await data_loader.load_all()

        assert counts["categories"] == 1
        assert counts["theorists"] == 1
        assert counts["theories"] == 2
        assert counts["relationships"] == 1
        mock_chromadb_adapter.get_or_create_collection.assert_called_once()

    def test_map_category_type(self, data_loader: DataLoader) -> None:
        """Test category type mapping."""
        from tenjin.domain.value_objects.category_type import CategoryType

        assert data_loader._map_category_type("learning_theory") == CategoryType.LEARNING_THEORY
        assert data_loader._map_category_type("developmental") == CategoryType.DEVELOPMENTAL
        assert data_loader._map_category_type("unknown") == CategoryType.LEARNING_THEORY

    def test_map_relationship_type(self, data_loader: DataLoader) -> None:
        """Test relationship type mapping."""
        from tenjin.domain.value_objects.relationship_type import RelationshipType

        assert data_loader._map_relationship_type("influences") == RelationshipType.INFLUENCES
        assert data_loader._map_relationship_type("extends") == RelationshipType.EXTENDS
        assert data_loader._map_relationship_type("unknown") == RelationshipType.INFLUENCES

    def test_create_embedding_text(
        self,
        data_loader: DataLoader,
        sample_theory: Any,
    ) -> None:
        """Test embedding text creation."""
        text = data_loader._create_embedding_text(sample_theory)

        assert "Constructivism" in text
        assert "構成主義" in text
        assert "learning_theory" in text
