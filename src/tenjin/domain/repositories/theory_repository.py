"""TheoryRepository interface - Abstract repository for theory operations."""

from abc import ABC, abstractmethod
from typing import Sequence

from ..entities.theory import Theory
from ..entities.theorist import Theorist
from ..entities.concept import Concept
from ..value_objects.theory_id import TheoryId
from ..value_objects.category_type import CategoryType
from ..value_objects.priority_level import PriorityLevel


class TheoryRepository(ABC):
    """Abstract repository interface for Theory entities.

    This interface defines the contract for theory persistence operations.
    Implementations can use any storage backend (Neo4j, PostgreSQL, etc.).
    """

    @abstractmethod
    async def get_by_id(self, theory_id: TheoryId) -> Theory | None:
        """Get a theory by its ID.

        Args:
            theory_id: The theory identifier.

        Returns:
            Theory if found, None otherwise.
        """
        ...

    @abstractmethod
    async def get_by_name(self, name: str) -> Theory | None:
        """Get a theory by its name.

        Args:
            name: Theory name (English or Japanese).

        Returns:
            Theory if found, None otherwise.
        """
        ...

    @abstractmethod
    async def get_all(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[Theory]:
        """Get all theories with pagination.

        Args:
            limit: Maximum number of results.
            offset: Number of results to skip.

        Returns:
            Sequence of theories.
        """
        ...

    @abstractmethod
    async def get_by_category(
        self,
        category: CategoryType,
        limit: int = 50,
    ) -> Sequence[Theory]:
        """Get theories by category.

        Args:
            category: Category type to filter by.
            limit: Maximum number of results.

        Returns:
            Sequence of theories in the category.
        """
        ...

    @abstractmethod
    async def get_by_priority(
        self,
        priority: PriorityLevel,
        limit: int = 50,
    ) -> Sequence[Theory]:
        """Get theories by priority level.

        Args:
            priority: Priority level to filter by.
            limit: Maximum number of results.

        Returns:
            Sequence of theories with given priority.
        """
        ...

    @abstractmethod
    async def get_by_theorist(self, theorist_name: str) -> Sequence[Theory]:
        """Get theories by theorist name.

        Args:
            theorist_name: Name of the theorist.

        Returns:
            Sequence of theories by the theorist.
        """
        ...

    @abstractmethod
    async def search_by_keyword(
        self,
        keyword: str,
        limit: int = 20,
    ) -> Sequence[Theory]:
        """Search theories by keyword.

        Args:
            keyword: Keyword to search for.
            limit: Maximum number of results.

        Returns:
            Sequence of matching theories.
        """
        ...

    @abstractmethod
    async def save(self, theory: Theory) -> Theory:
        """Save a theory (create or update).

        Args:
            theory: Theory to save.

        Returns:
            Saved theory with updated timestamps.
        """
        ...

    @abstractmethod
    async def delete(self, theory_id: TheoryId) -> bool:
        """Delete a theory by ID.

        Args:
            theory_id: ID of theory to delete.

        Returns:
            True if deleted, False if not found.
        """
        ...

    @abstractmethod
    async def count(self) -> int:
        """Get total count of theories.

        Returns:
            Total number of theories.
        """
        ...

    @abstractmethod
    async def count_by_category(self) -> dict[CategoryType, int]:
        """Get theory count by category.

        Returns:
            Dictionary mapping category to count.
        """
        ...

    @abstractmethod
    async def get_theorists(self, theory_id: TheoryId) -> Sequence[Theorist]:
        """Get theorists associated with a theory.

        Args:
            theory_id: Theory identifier.

        Returns:
            Sequence of associated theorists.
        """
        ...

    @abstractmethod
    async def get_concepts(self, theory_id: TheoryId) -> Sequence[Concept]:
        """Get concepts associated with a theory.

        Args:
            theory_id: Theory identifier.

        Returns:
            Sequence of associated concepts.
        """
        ...
