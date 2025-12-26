"""RecommendationService - Theory recommendation operations."""

from typing import Any

from ...domain.entities.theory import Theory
from ...domain.repositories.theory_repository import TheoryRepository
from ...domain.repositories.vector_repository import VectorRepository
from ...domain.repositories.graph_repository import GraphRepository
from ...domain.value_objects.category_type import CategoryType
from ...domain.value_objects.search_query import SearchQuery
from ...infrastructure.adapters.esperanto_adapter import EsperantoAdapter
from ...infrastructure.config.logging import get_logger

logger = get_logger(__name__)


class RecommendationService:
    """Service for theory recommendation operations.

    Provides personalized and contextual theory
    recommendations using graph, vector, and LLM analysis.
    """

    def __init__(
        self,
        theory_repository: TheoryRepository,
        vector_repository: VectorRepository,
        graph_repository: GraphRepository,
        llm_adapter: EsperantoAdapter,
    ) -> None:
        """Initialize recommendation service.

        Args:
            theory_repository: Repository for theory data.
            vector_repository: Repository for vector search.
            graph_repository: Repository for relationship data.
            llm_adapter: LLM adapter for AI recommendations.
        """
        self._theory_repo = theory_repository
        self._vector_repo = vector_repository
        self._graph_repo = graph_repository
        self._llm = llm_adapter

    async def recommend_for_context(
        self,
        context: str,
        limit: int = 5,
        filters: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Recommend theories for a specific educational context.

        Args:
            context: Description of the educational context.
            limit: Maximum number of recommendations.
            filters: Optional filters (category, priority, etc.).

        Returns:
            Recommended theories with explanations.
        """
        # Perform semantic search to find relevant theories
        query = SearchQuery(
            query_text=context,
            search_type="semantic",
            limit=limit * 2,  # Get more candidates for ranking
        )
        search_results = await self._vector_repo.search(query)

        if not search_results.results:
            return {
                "context": context,
                "recommendations": [],
                "message": "No matching theories found",
            }

        # Get full theory details
        theories = []
        for result in search_results.results:
            theory = await self._theory_repo.get_by_id(result.entity_id)
            if theory:
                theories.append((theory, result.relevance_score))

        # Apply filters if provided
        if filters:
            theories = self._apply_filters(theories, filters)

        # Generate recommendations with explanations
        recommendations = await self._generate_recommendations(
            context, theories[:limit]
        )

        return {
            "context": context,
            "recommendations": recommendations,
            "total_candidates": len(theories),
        }

    def _apply_filters(
        self,
        theories: list[tuple[Theory, float]],
        filters: dict[str, Any],
    ) -> list[tuple[Theory, float]]:
        """Apply filters to theory list.

        Args:
            theories: List of (theory, score) tuples.
            filters: Filter criteria.

        Returns:
            Filtered theories.
        """
        filtered = theories

        if "category" in filters:
            try:
                cat = CategoryType(filters["category"])
                filtered = [(t, s) for t, s in filtered if t.category == cat]
            except ValueError:
                pass

        if "min_priority" in filters:
            min_p = filters["min_priority"]
            filtered = [(t, s) for t, s in filtered if t.priority.value >= min_p]

        if "max_priority" in filters:
            max_p = filters["max_priority"]
            filtered = [(t, s) for t, s in filtered if t.priority.value <= max_p]

        return filtered

    async def _generate_recommendations(
        self,
        context: str,
        theories: list[tuple[Theory, float]],
    ) -> list[dict[str, Any]]:
        """Generate recommendations with explanations.

        Args:
            context: Educational context.
            theories: Candidate theories with scores.

        Returns:
            Recommendations with explanations.
        """
        recommendations = []

        for theory, score in theories:
            # Generate personalized explanation
            explanation = await self._generate_explanation(context, theory)

            recommendations.append({
                "theory": theory.to_dict(),
                "relevance_score": score,
                "explanation": explanation,
                "key_benefits": theory.strengths[:3],
                "considerations": theory.limitations[:2],
            })

        return recommendations

    async def _generate_explanation(
        self,
        context: str,
        theory: Theory,
    ) -> str:
        """Generate explanation for why theory fits context.

        Args:
            context: Educational context.
            theory: Recommended theory.

        Returns:
            Explanation text.
        """
        prompt = f"""Explain in 2-3 sentences why "{theory.name}" is suitable for this context:
Context: {context}

Theory: {theory.name}
Description: {theory.description}
Key principles: {', '.join(theory.key_principles[:3])}
Applications: {', '.join(theory.applications[:3])}

Provide a brief, practical explanation of the fit."""

        try:
            response = await self._llm.generate(prompt)
            return response.strip()
        except Exception as e:
            logger.warning(f"Explanation generation failed: {e}")
            return f"{theory.name} aligns with your context through its focus on {theory.key_principles[0] if theory.key_principles else 'learning'}."

    async def recommend_similar(
        self,
        theory_id: str,
        limit: int = 5,
    ) -> dict[str, Any]:
        """Recommend theories similar to a given theory.

        Args:
            theory_id: Reference theory ID.
            limit: Maximum recommendations.

        Returns:
            Similar theory recommendations.
        """
        # Get related from graph
        graph_related = await self._graph_repo.get_related_theories(
            theory_id=theory_id,
            depth=1,
            limit=limit,
        )

        # Get semantically similar from vector store
        source_theory = await self._theory_repo.get_by_id(theory_id)
        if not source_theory:
            return {"error": "Theory not found"}

        query = SearchQuery(
            query_text=f"{source_theory.name} {source_theory.description}",
            search_type="semantic",
            limit=limit,
        )
        vector_similar = await self._vector_repo.search(query)

        # Combine and deduplicate
        seen_ids = {theory_id}
        recommendations = []

        # Add graph-related first
        for item in graph_related:
            tid = item.get("theory", {}).get("id", "")
            if tid and tid not in seen_ids:
                seen_ids.add(tid)
                theory = await self._theory_repo.get_by_id(tid)
                if theory:
                    recommendations.append({
                        "theory": theory.to_dict(),
                        "source": "graph_relationship",
                        "relationship": item.get("relationship_type", "related"),
                    })

        # Add vector-similar
        for result in vector_similar.results:
            tid = str(result.entity_id)
            if tid not in seen_ids:
                seen_ids.add(tid)
                theory = await self._theory_repo.get_by_id(result.entity_id)
                if theory:
                    recommendations.append({
                        "theory": theory.to_dict(),
                        "source": "semantic_similarity",
                        "similarity_score": result.relevance_score,
                    })

        return {
            "source_theory": source_theory.to_dict(),
            "recommendations": recommendations[:limit],
        }

    async def recommend_for_learner_profile(
        self,
        learner_profile: dict[str, Any],
        limit: int = 5,
    ) -> dict[str, Any]:
        """Recommend theories based on learner profile.

        Args:
            learner_profile: Learner characteristics.
            limit: Maximum recommendations.

        Returns:
            Personalized recommendations.
        """
        # Extract profile characteristics
        age_group = learner_profile.get("age_group", "adult")
        learning_style = learner_profile.get("learning_style", "")
        subject_area = learner_profile.get("subject_area", "")
        challenges = learner_profile.get("challenges", [])
        goals = learner_profile.get("goals", [])

        # Build context from profile
        context_parts = [f"Learner age group: {age_group}"]
        if learning_style:
            context_parts.append(f"Preferred learning style: {learning_style}")
        if subject_area:
            context_parts.append(f"Subject area: {subject_area}")
        if challenges:
            context_parts.append(f"Challenges: {', '.join(challenges)}")
        if goals:
            context_parts.append(f"Learning goals: {', '.join(goals)}")

        context = ". ".join(context_parts)

        # Use LLM to determine best categories
        category_prompt = f"""Based on this learner profile, which educational theory categories would be most beneficial?
Profile: {context}

Categories available:
- cognitive_development: Cognitive development theories
- behavioral: Behavioral learning theories
- constructivist: Constructivist theories
- social_learning: Social learning theories
- humanistic: Humanistic theories
- motivation: Motivation theories
- instructional_design: Instructional design theories
- adult_learning: Adult learning theories
- technology_enhanced: Technology-enhanced learning

Return the top 3 category codes as a comma-separated list."""

        try:
            cat_response = await self._llm.generate(category_prompt)
            suggested_cats = [c.strip().lower() for c in cat_response.split(",")]
        except Exception:
            suggested_cats = []

        # Perform recommendation with context
        recommendations = await self.recommend_for_context(
            context=context,
            limit=limit,
            filters={"category": suggested_cats[0]} if suggested_cats else None,
        )

        return {
            "learner_profile": learner_profile,
            "suggested_categories": suggested_cats,
            "recommendations": recommendations.get("recommendations", []),
        }

    async def recommend_complementary(
        self,
        theory_ids: list[str],
        limit: int = 5,
    ) -> dict[str, Any]:
        """Recommend theories that complement existing selections.

        Args:
            theory_ids: Currently selected theories.
            limit: Maximum recommendations.

        Returns:
            Complementary theory recommendations.
        """
        # Get current theories
        current_theories = []
        current_categories = set()

        for tid in theory_ids:
            theory = await self._theory_repo.get_by_id(tid)
            if theory:
                current_theories.append(theory)
                current_categories.add(theory.category.value)

        if not current_theories:
            return {"error": "No valid theories provided"}

        # Find theories from different categories
        all_categories = set(c.value for c in CategoryType)
        complement_categories = all_categories - current_categories

        recommendations = []

        for cat_value in complement_categories:
            try:
                cat = CategoryType(cat_value)
                theories = await self._theory_repo.get_by_category(cat, limit=2)
                for theory in theories:
                    if str(theory.id) not in theory_ids:
                        recommendations.append({
                            "theory": theory.to_dict(),
                            "reason": f"Adds {cat.display_name} perspective",
                        })
            except Exception:
                continue

            if len(recommendations) >= limit:
                break

        # Generate synthesis suggestion
        if recommendations and current_theories:
            synthesis_prompt = f"""Suggest how these new theories could complement the existing selection:

Current theories: {', '.join(t.name for t in current_theories)}
Suggested additions: {', '.join(r['theory']['name'] for r in recommendations[:3])}

Provide a brief explanation of how they work together."""

            try:
                synthesis = await self._llm.generate(synthesis_prompt)
            except Exception:
                synthesis = "These theories offer complementary perspectives."

        else:
            synthesis = ""

        return {
            "current_theories": [t.to_dict() for t in current_theories],
            "recommendations": recommendations[:limit],
            "synthesis_suggestion": synthesis,
        }

    async def get_learning_path(
        self,
        goal: str,
        current_knowledge: list[str] | None = None,
    ) -> dict[str, Any]:
        """Generate a learning path of theories for a goal.

        Args:
            goal: Learning or teaching goal.
            current_knowledge: Already known theories.

        Returns:
            Ordered learning path.
        """
        current_knowledge = current_knowledge or []

        # Get relevant theories
        query = SearchQuery(
            query_text=goal,
            search_type="semantic",
            limit=10,
        )
        results = await self._vector_repo.search(query)

        candidates = []
        for result in results.results:
            if str(result.entity_id) not in current_knowledge:
                theory = await self._theory_repo.get_by_id(result.entity_id)
                if theory:
                    candidates.append(theory)

        # Use LLM to order into learning path
        if candidates:
            path_prompt = f"""Create a learning path for this goal: {goal}

Available theories (order these from foundational to advanced):
{chr(10).join(f'- {t.name}: {t.description[:100]}' for t in candidates)}

Already known: {', '.join(current_knowledge) if current_knowledge else 'None'}

Return as JSON array with objects containing:
- name: theory name
- order: sequence number (1-based)
- reason: why at this position
- prerequisites: what should be learned first

Return valid JSON only."""

            try:
                response = await self._llm.generate(path_prompt)
                import json

                path = json.loads(response)
            except Exception:
                path = [{"name": t.name, "order": i + 1, "reason": "Relevance"} 
                       for i, t in enumerate(candidates)]

        else:
            path = []

        return {
            "goal": goal,
            "current_knowledge": current_knowledge,
            "learning_path": path,
            "estimated_theories": len(path),
        }
