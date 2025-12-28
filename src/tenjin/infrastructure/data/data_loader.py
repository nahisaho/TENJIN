"""Data Loader for TENJIN Education Theory GraphRAG System.

This module provides utilities for loading educational theory data
from JSON files into Neo4j and ChromaDB databases.
"""

import json
import logging
from pathlib import Path
from typing import Any

from tenjin.domain.entities.theory import Theory
from tenjin.domain.entities.theorist import Theorist
from tenjin.domain.entities.category import Category
from tenjin.domain.entities.relationship import TheoryRelationship
from tenjin.domain.value_objects.theory_id import TheoryId
from tenjin.domain.value_objects.theorist_id import TheoristId
from tenjin.domain.value_objects.category_type import CategoryType
from tenjin.domain.value_objects.priority_level import PriorityLevel
from tenjin.domain.value_objects.relationship_type import RelationshipType
from tenjin.infrastructure.adapters.neo4j_adapter import Neo4jAdapter
from tenjin.infrastructure.adapters.chromadb_adapter import ChromaDBAdapter
from tenjin.infrastructure.adapters.esperanto_adapter import EmbeddingAdapter

logger = logging.getLogger(__name__)


class DataLoader:
    """Loads educational theory data into databases."""

    def __init__(
        self,
        neo4j_adapter: Neo4jAdapter,
        chromadb_adapter: ChromaDBAdapter,
        embedding_adapter: EmbeddingAdapter,
        data_dir: Path | None = None,
    ) -> None:
        """Initialize data loader.

        Args:
            neo4j_adapter: Neo4j database adapter.
            chromadb_adapter: ChromaDB vector store adapter.
            embedding_adapter: Text embedding adapter.
            data_dir: Directory containing JSON data files.
        """
        self.neo4j = neo4j_adapter
        self.chromadb = chromadb_adapter
        self.embedding = embedding_adapter
        self.data_dir = data_dir or Path(__file__).parent.parent.parent.parent.parent / "data" / "theories"

    def _load_json(self, filename: str) -> dict[str, Any]:
        """Load JSON file from data directory.

        Args:
            filename: Name of JSON file.

        Returns:
            Parsed JSON data.
        """
        filepath = self.data_dir / filename
        logger.info(f"Loading {filepath}")
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    async def load_categories(self) -> list[Category]:
        """Load categories into Neo4j.

        Returns:
            List of loaded categories.
        """
        data = self._load_json("categories.json")
        categories = []

        for item in data["categories"]:
            # Map category id to CategoryType enum
            try:
                category_type = CategoryType(item["id"])
            except ValueError:
                logger.warning(f"Unknown category type: {item['id']}, skipping")
                continue

            category = Category(
                type=category_type,
                name=item["name"],
                name_ja=item["name_ja"],
                description=item["description"],
                description_ja=item["description_ja"],
                theory_count=item["theory_count"],
            )
            categories.append(category)

            # Create Neo4j node
            query = """
            MERGE (c:Category {id: $id})
            SET c.name = $name,
                c.name_ja = $name_ja,
                c.description = $description,
                c.description_ja = $description_ja,
                c.theory_count = $theory_count
            RETURN c
            """
            await self.neo4j.execute_write(
                query,
                {
                    "id": category_type.value,
                    "name": category.name,
                    "name_ja": category.name_ja,
                    "description": category.description,
                    "description_ja": category.description_ja,
                    "theory_count": category.theory_count,
                },
            )

        logger.info(f"Loaded {len(categories)} categories")
        return categories

    async def load_theorists(self) -> list[Theorist]:
        """Load theorists into Neo4j.

        Returns:
            List of loaded theorists.
        """
        data = self._load_json("theorists.json")
        theorists = []

        for item in data["theorists"]:
            theorist = Theorist(
                id=TheoristId(item["id"]),
                name=item["name"],
                name_ja=item["name_ja"],
                birth_year=item.get("birth_year"),
                death_year=item.get("death_year"),
                nationality=item.get("nationality"),
                primary_field=item.get("primary_field"),
                contributions=item.get("contributions", []),
                key_works=item.get("key_works", []),
                related_theory_ids=[TheoryId(tid) for tid in item.get("related_theories", [])],
            )
            theorists.append(theorist)

            # Create Neo4j node
            query = """
            MERGE (t:Theorist {id: $id})
            SET t.name = $name,
                t.name_ja = $name_ja,
                t.birth_year = $birth_year,
                t.death_year = $death_year,
                t.nationality = $nationality,
                t.primary_field = $primary_field,
                t.contributions = $contributions,
                t.key_works = $key_works
            RETURN t
            """
            await self.neo4j.execute_write(
                query,
                {
                    "id": str(theorist.id),
                    "name": theorist.name,
                    "name_ja": theorist.name_ja,
                    "birth_year": theorist.birth_year,
                    "death_year": theorist.death_year,
                    "nationality": theorist.nationality,
                    "primary_field": theorist.primary_field,
                    "contributions": theorist.contributions,
                    "key_works": theorist.key_works,
                },
            )

        logger.info(f"Loaded {len(theorists)} theorists")
        return theorists

    async def load_theories(self) -> list[Theory]:
        """Load theories into Neo4j and ChromaDB.

        Returns:
            List of loaded theories.
        """
        data = self._load_json("theories.json")
        theories = []
        theorist_names_map = {}  # Store theorist names for Neo4j

        for item in data["theories"]:
            # Map category string to CategoryType enum
            category_type = self._map_category_type(item["category"])

            theory = Theory(
                id=TheoryId(item["id"]),
                name=item["name"],
                name_ja=item["name_ja"],
                category=category_type,
                priority=PriorityLevel(item["priority"]),
                description=item["description"],
                description_ja=item["description_ja"],
                key_principles=item.get("key_principles", []),
                applications=item.get("applications", []),
                strengths=item.get("strengths", []),
                limitations=item.get("limitations", []),
            )
            theories.append(theory)
            theorist_names_map[str(theory.id)] = item.get("theorists", [])

            # Create Neo4j node
            query = """
            MERGE (t:Theory {id: $id})
            SET t.name = $name,
                t.name_ja = $name_ja,
                t.category = $category,
                t.priority = $priority,
                t.theorist_names = $theorist_names,
                t.description = $description,
                t.description_ja = $description_ja,
                t.key_principles = $key_principles,
                t.applications = $applications,
                t.strengths = $strengths,
                t.limitations = $limitations
            RETURN t
            """
            await self.neo4j.execute_write(
                query,
                {
                    "id": str(theory.id),
                    "name": theory.name,
                    "name_ja": theory.name_ja,
                    "category": theory.category.value,
                    "priority": theory.priority.value,
                    "theorist_names": theorist_names_map[str(theory.id)],
                    "description": theory.description,
                    "description_ja": theory.description_ja,
                    "key_principles": theory.key_principles,
                    "applications": theory.applications,
                    "strengths": theory.strengths,
                    "limitations": theory.limitations,
                },
            )

            # Link to category
            category_query = """
            MATCH (t:Theory {id: $theory_id})
            MATCH (c:Category {id: $category_id})
            MERGE (t)-[:BELONGS_TO]->(c)
            """
            await self.neo4j.execute_write(
                category_query,
                {
                    "theory_id": str(theory.id),
                    "category_id": theory.category.value,
                },
            )

            # Generate embedding and add to ChromaDB
            embedding_text = self._create_embedding_text(theory)
            embedding = await self.embedding.embed(embedding_text)
            
            self.chromadb.add(
                ids=[str(theory.id)],
                embeddings=[embedding],
                documents=[embedding_text],
                metadatas=[{
                    "name": theory.name,
                    "name_ja": theory.name_ja,
                    "category": theory.category.value,
                    "priority": theory.priority.value,
                }],
            )

        logger.info(f"Loaded {len(theories)} theories")
        return theories

    async def load_relationships(self) -> list[TheoryRelationship]:
        """Load theory relationships into Neo4j.

        Returns:
            List of loaded relationships.
        """
        data = self._load_json("relationships.json")
        relationships = []

        for item in data["relationships"]:
            # Map relationship type string to enum
            rel_type = self._map_relationship_type(item["relationship_type"])

            relationship = TheoryRelationship(
                source_id=str(item["source_id"]),
                target_id=str(item["target_id"]),
                relationship_type=rel_type,
                strength=item.get("strength", 0.5),
                description=item.get("description", ""),
            )
            relationships.append(relationship)

            # Create Neo4j relationship
            query = f"""
            MATCH (source:Theory {{id: $source_id}})
            MATCH (target:Theory {{id: $target_id}})
            MERGE (source)-[r:{rel_type.value.upper()}]->(target)
            SET r.id = $id,
                r.strength = $strength,
                r.description = $description
            RETURN r
            """
            await self.neo4j.execute_write(
                query,
                {
                    "source_id": str(relationship.source_id),
                    "target_id": str(relationship.target_id),
                    "id": item.get("id", f"{relationship.source_id}-{rel_type.value}-{relationship.target_id}"),
                    "strength": relationship.strength,
                    "description": relationship.description,
                },
            )

        logger.info(f"Loaded {len(relationships)} relationships")
        return relationships

    async def link_theorists_to_theories(self) -> None:
        """Create relationships between theorists and their theories."""
        data = self._load_json("theorists.json")

        for item in data["theorists"]:
            theorist_id = item["id"]
            for theory_id in item.get("related_theories", []):
                query = """
                MATCH (theorist:Theorist {id: $theorist_id})
                MATCH (theory:Theory {id: $theory_id})
                MERGE (theorist)-[:DEVELOPED]->(theory)
                """
                await self.neo4j.execute_write(
                    query,
                    {"theorist_id": theorist_id, "theory_id": theory_id},
                )

        logger.info("Linked theorists to theories")

    async def load_all(self) -> dict[str, int]:
        """Load all data into databases.

        Returns:
            Dictionary with counts of loaded items.
        """
        logger.info("Starting full data load...")

        # Ensure ChromaDB collection exists
        self.chromadb.connect()

        categories = await self.load_categories()
        theorists = await self.load_theorists()
        theories = await self.load_theories()
        relationships = await self.load_relationships()
        await self.link_theorists_to_theories()

        counts = {
            "categories": len(categories),
            "theorists": len(theorists),
            "theories": len(theories),
            "relationships": len(relationships),
        }

        logger.info(f"Data load complete: {counts}")
        return counts

    def _map_category_type(self, category_str: str) -> CategoryType:
        """Map category string to CategoryType enum.

        Args:
            category_str: Category string from JSON.

        Returns:
            CategoryType enum value.
        """
        mapping = {
            "learning_theory": CategoryType.LEARNING_THEORY,
            "developmental": CategoryType.DEVELOPMENTAL,
            "instructional_design": CategoryType.INSTRUCTIONAL_DESIGN,
            "curriculum": CategoryType.CURRICULUM,
            "motivation": CategoryType.MOTIVATION,
            "assessment": CategoryType.ASSESSMENT,
            "social_learning": CategoryType.SOCIAL_LEARNING,
            "asian_education": CategoryType.ASIAN_EDUCATION,
            "technology_enhanced": CategoryType.TECHNOLOGY_ENHANCED,
            "modern_education": CategoryType.MODERN_EDUCATION,
            "critical_alternative": CategoryType.CRITICAL_ALTERNATIVE,
        }
        return mapping.get(category_str, CategoryType.LEARNING_THEORY)

    def _map_relationship_type(self, rel_str: str) -> RelationshipType:
        """Map relationship string to RelationshipType enum.

        Args:
            rel_str: Relationship type string from JSON.

        Returns:
            RelationshipType enum value.
        """
        mapping = {
            "influences": RelationshipType.INFLUENCES,
            "influenced_by": RelationshipType.INFLUENCED_BY,
            "extends": RelationshipType.EXTENDS,
            "contrasts_with": RelationshipType.CONTRASTS_WITH,
            "complements": RelationshipType.COMPLEMENTS,
            "derived_from": RelationshipType.DERIVED_FROM,
            "applies": RelationshipType.APPLIES_TO,
            "applies_to": RelationshipType.APPLIES_TO,
            "evolved_into": RelationshipType.BUILDS_UPON,  # Map to BUILDS_UPON
            "supports": RelationshipType.COMPLEMENTS,  # Map to COMPLEMENTS
            "same_as": RelationshipType.SIMILAR_TO,  # Map to SIMILAR_TO
        }
        return mapping.get(rel_str, RelationshipType.INFLUENCES)

    def _create_embedding_text(self, theory: Theory) -> str:
        """Create text for embedding from theory.

        Args:
            theory: Theory entity.

        Returns:
            Combined text for embedding.
        """
        parts = [
            f"Theory: {theory.name}",
            f"Japanese Name: {theory.name_ja}",
            f"Category: {theory.category.value}",
            f"Description: {theory.description}",
            f"Description (Japanese): {theory.description_ja}",
        ]

        if theory.key_principles:
            parts.append(f"Key Principles: {', '.join(theory.key_principles)}")

        if theory.applications:
            parts.append(f"Applications: {', '.join(theory.applications)}")

        if theory.theorists:
            theorist_names = [t.name if hasattr(t, 'name') else str(t) for t in theory.theorists]
            parts.append(f"Theorists: {', '.join(theorist_names)}")

        return "\n".join(parts)


async def main() -> None:
    """Main entry point for data loading."""
    import asyncio
    from tenjin.infrastructure.config.settings import get_settings

    logging.basicConfig(level=logging.INFO)
    settings = get_settings()

    # Initialize adapters
    neo4j_adapter = Neo4jAdapter(
        uri=settings.neo4j_uri,
        username=settings.neo4j_username,
        password=settings.neo4j_password,
    )
    chromadb_adapter = ChromaDBAdapter(persist_directory=settings.chromadb_path)
    embedding_adapter = EmbeddingAdapter(
        provider=settings.embedding_provider,
        model=settings.embedding_model,
    )

    try:
        await neo4j_adapter.connect()
        loader = DataLoader(neo4j_adapter, chromadb_adapter, embedding_adapter)
        counts = await loader.load_all()
        print(f"Loaded: {counts}")
    finally:
        await neo4j_adapter.close()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
