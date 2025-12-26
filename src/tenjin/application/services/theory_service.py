"""TheoryService - Business logic for theory operations."""

from typing import Sequence

from ...domain.entities.theory import Theory
from ...domain.entities.theorist import Theorist
from ...domain.entities.concept import Concept
from ...domain.repositories.theory_repository import TheoryRepository
from ...domain.value_objects.theory_id import TheoryId
from ...domain.value_objects.category_type import CategoryType
from ...domain.value_objects.priority_level import PriorityLevel
from ...infrastructure.config.logging import get_logger

logger = get_logger(__name__)


class TheoryService:
    """Service for theory-related business operations.

    Provides high-level operations for theory management,
    retrieval, and filtering.
    """

    def __init__(self, theory_repository: TheoryRepository) -> None:
        """Initialize service with repository.

        Args:
            theory_repository: Repository for theory data access.
        """
        self._repository = theory_repository

    async def get_theory(self, theory_id: str) -> Theory | None:
        """Get a theory by ID.

        Args:
            theory_id: Theory identifier string.

        Returns:
            Theory if found, None otherwise.
        """
        try:
            tid = TheoryId.from_string(theory_id)
            return await self._repository.get_by_id(tid)
        except ValueError:
            logger.warning(f"Invalid theory ID format: {theory_id}")
            return None

    async def get_theory_by_name(self, name: str) -> Theory | None:
        """Get a theory by name.

        Args:
            name: Theory name (English or Japanese).

        Returns:
            Theory if found, None otherwise.
        """
        return await self._repository.get_by_name(name)

    async def list_theories(
        self,
        limit: int = 50,
        offset: int = 0,
        category: CategoryType | None = None,
        priority: PriorityLevel | None = None,
    ) -> Sequence[Theory]:
        """List theories with optional filters.

        Args:
            limit: Maximum number of results.
            offset: Number of results to skip.
            category: Optional category filter.
            priority: Optional priority filter.

        Returns:
            Sequence of matching theories.
        """
        if category:
            theories = await self._repository.get_by_category(category, limit)
        elif priority:
            theories = await self._repository.get_by_priority(priority, limit)
        else:
            theories = await self._repository.get_all(limit, offset)

        return theories

    async def get_theories_by_category(
        self,
        category: str | CategoryType,
        limit: int = 50,
    ) -> Sequence[Theory]:
        """Get theories in a specific category.

        Args:
            category: Category name or type.
            limit: Maximum number of results.

        Returns:
            Theories in the category.
        """
        if isinstance(category, str):
            category = CategoryType.from_string(category)

        return await self._repository.get_by_category(category, limit)

    async def get_theories_by_priority(
        self,
        priority: int | PriorityLevel,
        limit: int = 50,
    ) -> Sequence[Theory]:
        """Get theories with a specific priority.

        Args:
            priority: Priority level (1-5) or PriorityLevel.
            limit: Maximum number of results.

        Returns:
            Theories with the priority.
        """
        if isinstance(priority, int):
            priority = PriorityLevel.from_int(priority)

        return await self._repository.get_by_priority(priority, limit)

    async def get_theories_by_theorist(
        self,
        theorist_name: str,
    ) -> Sequence[Theory]:
        """Get theories by a specific theorist.

        Args:
            theorist_name: Name of the theorist.

        Returns:
            Theories by the theorist.
        """
        return await self._repository.get_by_theorist(theorist_name)

    async def search_theories(
        self,
        keyword: str,
        limit: int = 20,
    ) -> Sequence[Theory]:
        """Search theories by keyword.

        Args:
            keyword: Search keyword.
            limit: Maximum number of results.

        Returns:
            Matching theories.
        """
        return await self._repository.search_by_keyword(keyword, limit)

    async def get_theory_details(
        self,
        theory_id: str,
    ) -> dict | None:
        """Get comprehensive theory details including related data.

        Args:
            theory_id: Theory identifier.

        Returns:
            Dictionary with theory and related data.
        """
        theory = await self.get_theory(theory_id)
        if not theory:
            return None

        # Get associated data
        tid = TheoryId.from_string(theory_id)
        theorists = await self._repository.get_theorists(tid)
        concepts = await self._repository.get_concepts(tid)

        return {
            "theory": theory.to_dict(),
            "theorists": [t.to_dict() for t in theorists],
            "concepts": [c.to_dict() for c in concepts],
        }

    async def get_theorists_for_theory(
        self,
        theory_id: str,
    ) -> Sequence[Theorist]:
        """Get theorists associated with a theory.

        Args:
            theory_id: Theory identifier.

        Returns:
            Associated theorists.
        """
        try:
            tid = TheoryId.from_string(theory_id)
            return await self._repository.get_theorists(tid)
        except ValueError:
            return []

    async def get_concepts_for_theory(
        self,
        theory_id: str,
    ) -> Sequence[Concept]:
        """Get concepts associated with a theory.

        Args:
            theory_id: Theory identifier.

        Returns:
            Associated concepts.
        """
        try:
            tid = TheoryId.from_string(theory_id)
            return await self._repository.get_concepts(tid)
        except ValueError:
            return []

    async def get_category_statistics(self) -> dict[str, int]:
        """Get theory count by category.

        Returns:
            Dictionary mapping category names to counts.
        """
        counts = await self._repository.count_by_category()
        return {cat.value: count for cat, count in counts.items()}

    async def get_total_count(self) -> int:
        """Get total number of theories.

        Returns:
            Total theory count.
        """
        return await self._repository.count()

    async def save_theory(self, theory: Theory) -> Theory:
        """Save a theory (create or update).

        Args:
            theory: Theory to save.

        Returns:
            Saved theory.
        """
        return await self._repository.save(theory)

    async def delete_theory(self, theory_id: str) -> bool:
        """Delete a theory.

        Args:
            theory_id: Theory identifier.

        Returns:
            True if deleted.
        """
        try:
            tid = TheoryId.from_string(theory_id)
            return await self._repository.delete(tid)
        except ValueError:
            return False
