"""MethodologyService - Methodology operations."""

from typing import Any

from ...domain.entities.methodology import Methodology
from ...domain.repositories.theory_repository import TheoryRepository
from ...domain.repositories.vector_repository import VectorRepository
from ...domain.value_objects.theory_id import TheoryId
from ...domain.value_objects.methodology_id import MethodologyId
from ...domain.value_objects.search_query import SearchQuery
from ...infrastructure.adapters.esperanto_adapter import EsperantoAdapter
from ...infrastructure.config.logging import get_logger

logger = get_logger(__name__)


class MethodologyService:
    """Service for methodology operations.

    Provides methodology search, recommendations,
    and implementation guidance.
    """

    def __init__(
        self,
        theory_repository: TheoryRepository,
        vector_repository: VectorRepository,
        llm_adapter: EsperantoAdapter,
    ) -> None:
        """Initialize methodology service.

        Args:
            theory_repository: Repository for theory data.
            vector_repository: Repository for vector search.
            llm_adapter: LLM adapter for AI guidance.
        """
        self._theory_repo = theory_repository
        self._vector_repo = vector_repository
        self._llm = llm_adapter
        self._methodologies: dict[str, Methodology] = {}

    async def get_methodology(
        self,
        methodology_id: str,
    ) -> dict[str, Any]:
        """Get methodology by ID.

        Args:
            methodology_id: Methodology identifier.

        Returns:
            Methodology details.
        """
        try:
            mid = MethodologyId.from_string(methodology_id)
        except ValueError:
            return {"error": "Invalid methodology ID"}

        methodology = self._methodologies.get(str(mid))
        if not methodology:
            return {"error": "Methodology not found"}

        return {
            "methodology": methodology.to_dict(),
        }

    async def list_methodologies(
        self,
        theory_id: str | None = None,
        category: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> dict[str, Any]:
        """List methodologies with optional filters.

        Args:
            theory_id: Filter by associated theory.
            category: Filter by methodology category.
            limit: Maximum results.
            offset: Results offset.

        Returns:
            List of methodologies.
        """
        methodologies = list(self._methodologies.values())

        # Apply filters
        if theory_id:
            methodologies = [
                m for m in methodologies
                if theory_id in [str(tid) for tid in m.theory_ids]
            ]

        if category:
            methodologies = [
                m for m in methodologies
                if m.category.lower() == category.lower()
            ]

        # Apply pagination
        total = len(methodologies)
        methodologies = methodologies[offset : offset + limit]

        return {
            "methodologies": [m.to_dict() for m in methodologies],
            "total": total,
            "limit": limit,
            "offset": offset,
        }

    async def search_methodologies(
        self,
        query: str,
        limit: int = 10,
    ) -> dict[str, Any]:
        """Search methodologies by text.

        Args:
            query: Search query.
            limit: Maximum results.

        Returns:
            Matching methodologies.
        """
        search_query = SearchQuery(
            query_text=query,
            entity_type="methodology",
            search_type="semantic",
            limit=limit,
        )

        results = await self._vector_repo.search(search_query)

        methodologies = []
        for result in results.results:
            methodology = self._methodologies.get(str(result.entity_id))
            if methodology:
                methodologies.append({
                    "methodology": methodology.to_dict(),
                    "relevance_score": result.relevance_score,
                })

        return {
            "query": query,
            "results": methodologies,
            "total": len(methodologies),
        }

    async def get_methodologies_for_theory(
        self,
        theory_id: str,
    ) -> dict[str, Any]:
        """Get methodologies associated with a theory.

        Args:
            theory_id: Theory identifier.

        Returns:
            Associated methodologies.
        """
        try:
            tid = TheoryId.from_string(theory_id)
            theory = await self._theory_repo.get_by_id(tid)
        except ValueError:
            return {"error": "Invalid theory ID"}

        if not theory:
            return {"error": "Theory not found"}

        # Get associated methodologies
        associated = [
            m for m in self._methodologies.values()
            if theory_id in [str(tid) for tid in m.theory_ids]
        ]

        return {
            "theory": theory.to_dict(),
            "methodologies": [m.to_dict() for m in associated],
            "count": len(associated),
        }

    async def recommend_methodology(
        self,
        context: str,
        constraints: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Recommend methodology for a context.

        Args:
            context: Educational context description.
            constraints: Optional constraints (time, resources, etc.).

        Returns:
            Recommended methodologies with rationale.
        """
        constraints = constraints or {}

        # Search for relevant methodologies
        search_result = await self.search_methodologies(context, limit=5)

        if not search_result.get("results"):
            # Generate generic recommendations
            prompt = f"""Recommend teaching methodologies for this context:
Context: {context}
Constraints: {constraints}

Provide 3 methodology recommendations in JSON format with:
- name: Methodology name
- description: Brief description
- steps: Implementation steps
- benefits: Expected benefits
- considerations: Things to consider

Return valid JSON array."""

            try:
                response = await self._llm.generate(prompt)
                import json
                recommendations = json.loads(response)
            except Exception:
                recommendations = []

            return {
                "context": context,
                "constraints": constraints,
                "recommendations": recommendations,
                "source": "generated",
            }

        # Enhance with explanations
        recommendations = []
        for item in search_result["results"]:
            methodology = item["methodology"]
            explanation = await self._generate_methodology_explanation(
                methodology, context, constraints
            )
            recommendations.append({
                "methodology": methodology,
                "relevance_score": item["relevance_score"],
                "explanation": explanation,
            })

        return {
            "context": context,
            "constraints": constraints,
            "recommendations": recommendations,
            "source": "database",
        }

    async def _generate_methodology_explanation(
        self,
        methodology: dict,
        context: str,
        constraints: dict,
    ) -> str:
        """Generate explanation for methodology fit.

        Args:
            methodology: Methodology data.
            context: Application context.
            constraints: Constraints.

        Returns:
            Explanation text.
        """
        prompt = f"""Explain why "{methodology.get('name', 'Unknown')}" methodology is suitable:

Context: {context}
Constraints: {constraints}
Methodology: {methodology.get('description', '')[:200]}

Provide a brief 2-3 sentence explanation."""

        try:
            return await self._llm.generate(prompt)
        except Exception:
            return f"This methodology aligns with your context requirements."

    async def get_implementation_guide(
        self,
        methodology_id: str,
        context: str = "",
    ) -> dict[str, Any]:
        """Get implementation guide for a methodology.

        Args:
            methodology_id: Methodology identifier.
            context: Optional implementation context.

        Returns:
            Implementation guide.
        """
        try:
            mid = MethodologyId.from_string(methodology_id)
        except ValueError:
            return {"error": "Invalid methodology ID"}

        methodology = self._methodologies.get(str(mid))
        if not methodology:
            return {"error": "Methodology not found"}

        # Generate implementation guide
        prompt = f"""Create an implementation guide for this methodology:

Methodology: {methodology.name}
Description: {methodology.description}
Steps: {', '.join(methodology.steps)}
Context: {context or 'general educational setting'}

Provide a comprehensive guide in JSON format with:
1. "preparation": Steps to prepare
2. "implementation_phases": Detailed phases
3. "materials_needed": Required materials
4. "time_estimates": Time for each phase
5. "assessment_methods": How to assess effectiveness
6. "common_challenges": Challenges and solutions
7. "success_indicators": How to know it's working

Return valid JSON only."""

        try:
            response = await self._llm.generate(prompt)
            import json
            guide = json.loads(response)
        except Exception as e:
            logger.warning(f"Guide generation failed: {e}")
            guide = {
                "preparation": methodology.steps[:2],
                "implementation_phases": methodology.steps,
                "materials_needed": [],
                "time_estimates": {},
                "assessment_methods": [],
                "common_challenges": [],
                "success_indicators": [],
            }

        return {
            "methodology": methodology.to_dict(),
            "context": context,
            "guide": guide,
        }

    async def create_methodology(
        self,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """Create a new methodology.

        Args:
            data: Methodology data.

        Returns:
            Created methodology.
        """
        try:
            methodology = Methodology(
                id=MethodologyId.generate(),
                name=data["name"],
                name_ja=data.get("name_ja", ""),
                description=data["description"],
                description_ja=data.get("description_ja", ""),
                category=data.get("category", "general"),
                steps=data.get("steps", []),
                theory_ids=[
                    TheoryId.from_string(tid) 
                    for tid in data.get("theory_ids", [])
                ],
                benefits=data.get("benefits", []),
                prerequisites=data.get("prerequisites", []),
                evidence_level=data.get("evidence_level", "moderate"),
            )

            self._methodologies[str(methodology.id)] = methodology

            # Index in vector store
            await self._vector_repo.upsert(
                entity_id=str(methodology.id),
                entity_type="methodology",
                text=f"{methodology.name} {methodology.description}",
                metadata=methodology.to_dict(),
            )

            return {
                "methodology": methodology.to_dict(),
                "status": "created",
            }

        except Exception as e:
            logger.error(f"Failed to create methodology: {e}")
            return {"error": str(e)}

    async def update_methodology(
        self,
        methodology_id: str,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """Update an existing methodology.

        Args:
            methodology_id: Methodology identifier.
            data: Updated data.

        Returns:
            Updated methodology.
        """
        try:
            mid = MethodologyId.from_string(methodology_id)
        except ValueError:
            return {"error": "Invalid methodology ID"}

        methodology = self._methodologies.get(str(mid))
        if not methodology:
            return {"error": "Methodology not found"}

        # Update fields
        if "name" in data:
            methodology.name = data["name"]
        if "name_ja" in data:
            methodology.name_ja = data["name_ja"]
        if "description" in data:
            methodology.description = data["description"]
        if "steps" in data:
            methodology.steps = data["steps"]
        if "benefits" in data:
            methodology.benefits = data["benefits"]

        self._methodologies[str(mid)] = methodology

        # Update vector index
        await self._vector_repo.upsert(
            entity_id=str(mid),
            entity_type="methodology",
            text=f"{methodology.name} {methodology.description}",
            metadata=methodology.to_dict(),
        )

        return {
            "methodology": methodology.to_dict(),
            "status": "updated",
        }

    async def delete_methodology(
        self,
        methodology_id: str,
    ) -> dict[str, Any]:
        """Delete a methodology.

        Args:
            methodology_id: Methodology identifier.

        Returns:
            Deletion status.
        """
        try:
            mid = MethodologyId.from_string(methodology_id)
        except ValueError:
            return {"error": "Invalid methodology ID"}

        if str(mid) not in self._methodologies:
            return {"error": "Methodology not found"}

        del self._methodologies[str(mid)]

        return {
            "methodology_id": methodology_id,
            "status": "deleted",
        }

    async def get_methodology_statistics(self) -> dict[str, Any]:
        """Get methodology statistics.

        Returns:
            Methodology statistics.
        """
        methodologies = list(self._methodologies.values())

        # Count by category
        category_counts: dict[str, int] = {}
        for m in methodologies:
            cat = m.category
            category_counts[cat] = category_counts.get(cat, 0) + 1

        # Count by evidence level
        evidence_counts: dict[str, int] = {}
        for m in methodologies:
            level = getattr(m, "evidence_level", "unknown")
            evidence_counts[level] = evidence_counts.get(level, 0) + 1

        return {
            "total_methodologies": len(methodologies),
            "by_category": category_counts,
            "by_evidence_level": evidence_counts,
        }
