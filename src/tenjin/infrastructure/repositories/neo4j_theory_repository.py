"""Neo4j implementation of TheoryRepository."""

from datetime import datetime
from typing import Any, Sequence

from ...domain.entities.theory import Theory
from ...domain.entities.theorist import Theorist
from ...domain.entities.concept import Concept
from ...domain.repositories.theory_repository import TheoryRepository
from ...domain.value_objects.theory_id import TheoryId
from ...domain.value_objects.theorist_id import TheoristId
from ...domain.value_objects.concept_id import ConceptId
from ...domain.value_objects.category_type import CategoryType
from ...domain.value_objects.priority_level import PriorityLevel
from ..adapters.neo4j_adapter import Neo4jAdapter
from ..config.logging import get_logger

logger = get_logger(__name__)


class Neo4jTheoryRepository(TheoryRepository):
    """Neo4j implementation of TheoryRepository.

    Provides theory CRUD operations using Neo4j graph database.
    """

    def __init__(self, adapter: Neo4jAdapter) -> None:
        """Initialize repository with Neo4j adapter.

        Args:
            adapter: Neo4j database adapter.
        """
        self._adapter = adapter

    def _record_to_theory(self, record: dict[str, Any]) -> Theory:
        """Convert Neo4j record to Theory entity.

        Args:
            record: Neo4j record dictionary.

        Returns:
            Theory entity.
        """
        theory_data = record.get("t", record)

        # Handle category with fallback
        try:
            category = CategoryType(theory_data.get("category", "learning_theory"))
        except ValueError:
            category = CategoryType.LEARNING_THEORY

        # Handle priority with fallback (default to MEDIUM = 3)
        priority_value = theory_data.get("priority", 3)
        try:
            priority = PriorityLevel(priority_value)
        except ValueError:
            priority = PriorityLevel.MEDIUM

        return Theory(
            id=TheoryId.from_string(theory_data["id"]),
            name=theory_data["name"],
            name_ja=theory_data.get("name_ja", ""),
            description=theory_data["description"],
            description_ja=theory_data.get("description_ja", ""),
            category=category,
            priority=priority,
            year_proposed=theory_data.get("year_proposed"),
            key_principles=theory_data.get("key_principles", theory_data.get("principles", [])),
            applications=theory_data.get("applications", []),
            strengths=theory_data.get("strengths", []),
            limitations=theory_data.get("limitations", []),
            keywords=theory_data.get("keywords", []),
            created_at=datetime.fromisoformat(theory_data.get("created_at", datetime.utcnow().isoformat())),
            updated_at=datetime.fromisoformat(theory_data.get("updated_at", datetime.utcnow().isoformat())),
        )

    async def get_by_id(self, theory_id: TheoryId) -> Theory | None:
        """Get a theory by its ID."""
        query = """
        MATCH (t:Theory {id: $id})
        RETURN t
        """
        records = await self._adapter.execute_read(query, {"id": str(theory_id)})

        if records:
            return self._record_to_theory(records[0])
        return None

    async def get_by_name(self, name: str) -> Theory | None:
        """Get a theory by its name."""
        query = """
        MATCH (t:Theory)
        WHERE t.name = $name OR t.name_ja = $name
        RETURN t
        """
        records = await self._adapter.execute_read(query, {"name": name})

        if records:
            return self._record_to_theory(records[0])
        return None

    async def get_all(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[Theory]:
        """Get all theories with pagination."""
        query = """
        MATCH (t:Theory)
        RETURN t
        ORDER BY t.priority, t.name
        SKIP $offset
        LIMIT $limit
        """
        records = await self._adapter.execute_read(
            query, {"limit": limit, "offset": offset}
        )

        return [self._record_to_theory(r) for r in records]

    async def get_by_category(
        self,
        category: CategoryType,
        limit: int = 50,
    ) -> Sequence[Theory]:
        """Get theories by category."""
        query = """
        MATCH (t:Theory {category: $category})
        RETURN t
        ORDER BY t.priority, t.name
        LIMIT $limit
        """
        records = await self._adapter.execute_read(
            query, {"category": category.value, "limit": limit}
        )

        return [self._record_to_theory(r) for r in records]

    async def get_by_priority(
        self,
        priority: PriorityLevel,
        limit: int = 50,
    ) -> Sequence[Theory]:
        """Get theories by priority level."""
        query = """
        MATCH (t:Theory {priority: $priority})
        RETURN t
        ORDER BY t.name
        LIMIT $limit
        """
        records = await self._adapter.execute_read(
            query, {"priority": priority.value, "limit": limit}
        )

        return [self._record_to_theory(r) for r in records]

    async def get_by_theorist(self, theorist_name: str) -> Sequence[Theory]:
        """Get theories by theorist name."""
        query = """
        MATCH (th:Theorist)-[:FOUNDED|CONTRIBUTED_TO]->(t:Theory)
        WHERE th.name CONTAINS $name OR th.name_ja CONTAINS $name
        RETURN t
        ORDER BY t.priority, t.name
        """
        records = await self._adapter.execute_read(query, {"name": theorist_name})

        return [self._record_to_theory(r) for r in records]

    async def search_by_keyword(
        self,
        keyword: str,
        limit: int = 20,
    ) -> Sequence[Theory]:
        """Search theories by keyword."""
        query = """
        MATCH (t:Theory)
        WHERE t.name CONTAINS $keyword
           OR t.name_ja CONTAINS $keyword
           OR t.description CONTAINS $keyword
           OR t.description_ja CONTAINS $keyword
           OR ANY(k IN t.keywords WHERE k CONTAINS $keyword)
        RETURN t
        ORDER BY t.priority, t.name
        LIMIT $limit
        """
        records = await self._adapter.execute_read(
            query, {"keyword": keyword, "limit": limit}
        )

        return [self._record_to_theory(r) for r in records]

    async def save(self, theory: Theory) -> Theory:
        """Save a theory (create or update)."""
        query = """
        MERGE (t:Theory {id: $id})
        SET t.name = $name,
            t.name_ja = $name_ja,
            t.description = $description,
            t.description_ja = $description_ja,
            t.category = $category,
            t.priority = $priority,
            t.year_proposed = $year_proposed,
            t.key_principles = $key_principles,
            t.applications = $applications,
            t.strengths = $strengths,
            t.limitations = $limitations,
            t.keywords = $keywords,
            t.created_at = $created_at,
            t.updated_at = $updated_at
        RETURN t
        """
        theory.updated_at = datetime.utcnow()

        params = {
            "id": str(theory.id),
            "name": theory.name,
            "name_ja": theory.name_ja,
            "description": theory.description,
            "description_ja": theory.description_ja,
            "category": theory.category.value,
            "priority": theory.priority.value,
            "year_proposed": theory.year_proposed,
            "key_principles": theory.key_principles,
            "applications": theory.applications,
            "strengths": theory.strengths,
            "limitations": theory.limitations,
            "keywords": theory.keywords,
            "created_at": theory.created_at.isoformat(),
            "updated_at": theory.updated_at.isoformat(),
        }

        await self._adapter.execute_write(query, params)
        logger.debug(f"Saved theory: {theory.name}")

        return theory

    async def delete(self, theory_id: TheoryId) -> bool:
        """Delete a theory by ID."""
        query = """
        MATCH (t:Theory {id: $id})
        DETACH DELETE t
        RETURN count(t) as deleted
        """
        result = await self._adapter.execute_write(query, {"id": str(theory_id)})

        return result.get("nodes_deleted", 0) > 0

    async def count(self) -> int:
        """Get total count of theories."""
        query = "MATCH (t:Theory) RETURN count(t) as count"
        records = await self._adapter.execute_read(query)

        return records[0]["count"] if records else 0

    async def count_by_category(self) -> dict[CategoryType, int]:
        """Get theory count by category."""
        query = """
        MATCH (t:Theory)
        RETURN t.category as category, count(*) as count
        """
        records = await self._adapter.execute_read(query)

        return {
            CategoryType(r["category"]): r["count"]
            for r in records
            if r["category"]
        }

    async def get_theorists(self, theory_id: TheoryId) -> Sequence[Theorist]:
        """Get theorists associated with a theory."""
        query = """
        MATCH (th:Theorist)-[:FOUNDED|CONTRIBUTED_TO]->(t:Theory {id: $id})
        RETURN th
        """
        records = await self._adapter.execute_read(query, {"id": str(theory_id)})

        return [
            Theorist(
                id=TheoristId.from_string(r["th"]["id"]),
                name=r["th"]["name"],
                name_ja=r["th"].get("name_ja"),
                birth_year=r["th"].get("birth_year"),
                death_year=r["th"].get("death_year"),
                nationality=r["th"].get("nationality"),
                biography=r["th"].get("biography"),
                contributions=r["th"].get("contributions", []),
            )
            for r in records
        ]

    async def get_concepts(self, theory_id: TheoryId) -> Sequence[Concept]:
        """Get concepts associated with a theory."""
        query = """
        MATCH (c:Concept)-[:BELONGS_TO]->(t:Theory {id: $id})
        RETURN c
        """
        records = await self._adapter.execute_read(query, {"id": str(theory_id)})

        return [
            Concept(
                id=ConceptId.from_string(r["c"]["id"]),
                name=r["c"]["name"],
                name_ja=r["c"].get("name_ja"),
                definition=r["c"].get("definition", ""),
                definition_ja=r["c"].get("definition_ja", ""),
            )
            for r in records
        ]
