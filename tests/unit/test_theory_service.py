"""Unit tests for TheoryService."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from tenjin.application.services.theory_service import TheoryService
from tenjin.domain.entities.theory import Theory
from tenjin.domain.value_objects.theory_id import TheoryId
from tenjin.domain.value_objects.category_type import CategoryType
from tenjin.domain.value_objects.priority_level import PriorityLevel


class TestTheoryService:
    """Tests for TheoryService."""

    @pytest.fixture
    def mock_theory_repository(self, sample_theory: Theory) -> AsyncMock:
        """Create mock theory repository."""
        repo = AsyncMock()
        repo.get_by_id = AsyncMock(return_value=sample_theory)
        repo.get_all = AsyncMock(return_value=[sample_theory])
        repo.get_by_category = AsyncMock(return_value=[sample_theory])
        repo.search = AsyncMock(return_value=[sample_theory])
        repo.save = AsyncMock(return_value=sample_theory)
        repo.delete = AsyncMock(return_value=True)
        repo.count = AsyncMock(return_value=1)
        return repo

    @pytest.fixture
    def theory_service(self, mock_theory_repository: AsyncMock) -> TheoryService:
        """Create theory service with mock repository."""
        return TheoryService(theory_repository=mock_theory_repository)

    @pytest.mark.asyncio
    async def test_get_theory_by_id(
        self,
        theory_service: TheoryService,
        mock_theory_repository: AsyncMock,
        sample_theory: Theory,
    ) -> None:
        """Test getting theory by ID."""
        result = await theory_service.get_theory("theory-001")

        assert result is not None
        assert result.id == sample_theory.id
        mock_theory_repository.get_by_id.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_theory_not_found(
        self,
        theory_service: TheoryService,
        mock_theory_repository: AsyncMock,
    ) -> None:
        """Test getting non-existent theory."""
        mock_theory_repository.get_by_id.return_value = None

        result = await theory_service.get_theory("nonexistent")

        assert result is None

    @pytest.mark.asyncio
    async def test_list_theories(
        self,
        theory_service: TheoryService,
        mock_theory_repository: AsyncMock,
        sample_theory: Theory,
    ) -> None:
        """Test listing all theories."""
        result = await theory_service.list_theories()

        assert len(result) == 1
        assert result[0].id == sample_theory.id
        mock_theory_repository.get_all.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_theories_by_category(
        self,
        theory_service: TheoryService,
        mock_theory_repository: AsyncMock,
        sample_theory: Theory,
    ) -> None:
        """Test getting theories by category."""
        result = await theory_service.get_by_category(CategoryType.LEARNING_THEORY)

        assert len(result) == 1
        mock_theory_repository.get_by_category.assert_called_once_with(
            CategoryType.LEARNING_THEORY
        )

    @pytest.mark.asyncio
    async def test_search_theories(
        self,
        theory_service: TheoryService,
        mock_theory_repository: AsyncMock,
    ) -> None:
        """Test searching theories."""
        result = await theory_service.search_theories("constructivism")

        assert len(result) >= 0
        mock_theory_repository.search.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_theory_statistics(
        self,
        theory_service: TheoryService,
        mock_theory_repository: AsyncMock,
    ) -> None:
        """Test getting theory statistics."""
        mock_theory_repository.count.return_value = 200

        stats = await theory_service.get_statistics()

        assert stats["total_theories"] == 200
