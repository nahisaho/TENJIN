"""AnalysisService - Theory analysis and comparison operations."""

from typing import Any

from ...domain.entities.theory import Theory
from ...domain.repositories.theory_repository import TheoryRepository
from ...domain.repositories.graph_repository import GraphRepository
from ...domain.value_objects.theory_id import TheoryId
from ...infrastructure.adapters.esperanto_adapter import EsperantoAdapter
from ...infrastructure.config.logging import get_logger

logger = get_logger(__name__)


class AnalysisService:
    """Service for theory analysis operations.

    Provides theory comparison, synthesis, and
    LLM-powered analysis capabilities.
    """

    def __init__(
        self,
        theory_repository: TheoryRepository,
        graph_repository: GraphRepository,
        llm_adapter: EsperantoAdapter,
    ) -> None:
        """Initialize analysis service.

        Args:
            theory_repository: Repository for theory data.
            graph_repository: Repository for relationship data.
            llm_adapter: LLM adapter for AI analysis.
        """
        self._theory_repo = theory_repository
        self._graph_repo = graph_repository
        self._llm = llm_adapter

    async def compare_theories(
        self,
        theory_ids: list[str],
        aspects: list[str] | None = None,
    ) -> dict[str, Any]:
        """Compare multiple theories.

        Args:
            theory_ids: List of theory IDs to compare.
            aspects: Specific aspects to compare (optional).

        Returns:
            Comparison analysis.
        """
        if len(theory_ids) < 2:
            return {"error": "At least 2 theories required for comparison"}

        # Fetch theories
        theories = []
        for tid_str in theory_ids:
            try:
                tid = TheoryId.from_string(tid_str)
                theory = await self._theory_repo.get_by_id(tid)
                if theory:
                    theories.append(theory)
            except ValueError:
                logger.warning(f"Invalid theory ID: {tid_str}")

        if len(theories) < 2:
            return {"error": "Could not find enough valid theories"}

        # Default aspects
        if not aspects:
            aspects = [
                "core_principles",
                "applications",
                "strengths",
                "limitations",
                "target_learners",
            ]

        # Generate comparison using LLM
        comparison = await self._generate_comparison(theories, aspects)

        return {
            "theories": [t.to_dict() for t in theories],
            "aspects": aspects,
            "comparison": comparison,
        }

    async def _generate_comparison(
        self,
        theories: list[Theory],
        aspects: list[str],
    ) -> dict[str, Any]:
        """Generate AI-powered comparison.

        Args:
            theories: Theories to compare.
            aspects: Aspects to analyze.

        Returns:
            Comparison results.
        """
        # Build theory descriptions
        theory_descs = []
        for t in theories:
            desc = f"""
Theory: {t.name} ({t.name_ja})
Category: {t.category.display_name}
Description: {t.description}
Key Principles: {', '.join(t.key_principles[:5])}
Applications: {', '.join(t.applications[:3])}
"""
            theory_descs.append(desc)

        prompt = f"""Compare the following educational theories across these aspects: {', '.join(aspects)}

{chr(10).join(theory_descs)}

Provide a structured comparison in JSON format with:
1. "similarities": List of key similarities
2. "differences": List of key differences  
3. "aspect_comparison": Object with each aspect as key and comparison as value
4. "synthesis": How these theories might complement each other
5. "recommendation": When to use each theory

Return valid JSON only."""

        system_prompt = """You are an expert in educational theory analysis. 
Provide clear, accurate comparisons based on established educational research.
Always respond with valid JSON."""

        try:
            response = await self._llm.generate(prompt, system_prompt)
            # Parse JSON response
            import json

            return json.loads(response)
        except Exception as e:
            logger.error(f"LLM comparison failed: {e}")
            return {
                "similarities": [],
                "differences": [],
                "aspect_comparison": {},
                "synthesis": "Analysis unavailable",
                "recommendation": "Analysis unavailable",
            }

    async def analyze_theory(
        self,
        theory_id: str,
        analysis_type: str = "comprehensive",
    ) -> dict[str, Any]:
        """Perform in-depth analysis of a theory.

        Args:
            theory_id: Theory identifier.
            analysis_type: Type of analysis to perform.

        Returns:
            Analysis results.
        """
        try:
            tid = TheoryId.from_string(theory_id)
            theory = await self._theory_repo.get_by_id(tid)
        except ValueError:
            return {"error": "Invalid theory ID"}

        if not theory:
            return {"error": "Theory not found"}

        # Get related theories
        related = await self._graph_repo.get_related_theories(
            theory_id=theory_id,
            depth=1,
            limit=5,
        )

        # Generate analysis
        analysis = await self._generate_analysis(theory, analysis_type, related)

        return {
            "theory": theory.to_dict(),
            "analysis_type": analysis_type,
            "analysis": analysis,
            "related_theories": related,
        }

    async def _generate_analysis(
        self,
        theory: Theory,
        analysis_type: str,
        related: list[dict],
    ) -> dict[str, Any]:
        """Generate AI-powered theory analysis.

        Args:
            theory: Theory to analyze.
            analysis_type: Type of analysis.
            related: Related theories.

        Returns:
            Analysis results.
        """
        related_names = [r["theory"].get("name", "") for r in related[:5]]

        prompt = f"""Analyze the following educational theory ({analysis_type} analysis):

Theory: {theory.name} ({theory.name_ja})
Category: {theory.category.display_name}
Description: {theory.description}
Key Principles: {', '.join(theory.key_principles)}
Applications: {', '.join(theory.applications)}
Strengths: {', '.join(theory.strengths)}
Limitations: {', '.join(theory.limitations)}
Related theories: {', '.join(related_names)}

Provide analysis in JSON format with:
1. "summary": Brief summary of the theory
2. "historical_context": Historical development
3. "theoretical_foundation": Underlying assumptions
4. "practical_implications": How to apply in practice
5. "modern_relevance": Relevance in current education
6. "integration_suggestions": How to combine with other approaches
7. "key_takeaways": Main points for practitioners

Return valid JSON only."""

        system_prompt = """You are an educational theory expert.
Provide scholarly, accurate analysis based on educational research.
Always respond with valid JSON."""

        try:
            response = await self._llm.generate(prompt, system_prompt)
            import json

            return json.loads(response)
        except Exception as e:
            logger.error(f"LLM analysis failed: {e}")
            return {
                "summary": theory.description,
                "historical_context": "Analysis unavailable",
                "theoretical_foundation": "Analysis unavailable",
                "practical_implications": theory.applications,
                "modern_relevance": "Analysis unavailable",
                "integration_suggestions": "Analysis unavailable",
                "key_takeaways": theory.key_principles,
            }

    async def synthesize_theories(
        self,
        theory_ids: list[str],
        context: str = "",
    ) -> dict[str, Any]:
        """Synthesize multiple theories for a specific context.

        Args:
            theory_ids: Theories to synthesize.
            context: Application context.

        Returns:
            Synthesis results.
        """
        theories = []
        for tid_str in theory_ids:
            try:
                tid = TheoryId.from_string(tid_str)
                theory = await self._theory_repo.get_by_id(tid)
                if theory:
                    theories.append(theory)
            except ValueError:
                continue

        if not theories:
            return {"error": "No valid theories found"}

        # Generate synthesis
        prompt = f"""Synthesize the following educational theories for this context: {context or 'general educational practice'}

Theories:
{chr(10).join(f'- {t.name}: {t.description[:200]}' for t in theories)}

Provide a synthesis in JSON format with:
1. "integrated_approach": How to combine these theories
2. "key_principles": Combined principles from all theories
3. "implementation_steps": Practical steps to apply
4. "potential_challenges": Challenges in integration
5. "success_indicators": How to measure effectiveness

Return valid JSON only."""

        system_prompt = """You are an expert in educational theory integration.
Create practical, research-based syntheses of educational approaches.
Always respond with valid JSON."""

        try:
            response = await self._llm.generate(prompt, system_prompt)
            import json

            return {
                "theories": [t.to_dict() for t in theories],
                "context": context,
                "synthesis": json.loads(response),
            }
        except Exception as e:
            logger.error(f"Synthesis failed: {e}")
            return {
                "theories": [t.to_dict() for t in theories],
                "context": context,
                "synthesis": {"error": "Synthesis unavailable"},
            }

    async def get_theory_applications(
        self,
        theory_id: str,
        context: str = "",
    ) -> dict[str, Any]:
        """Get practical applications for a theory.

        Args:
            theory_id: Theory identifier.
            context: Specific application context.

        Returns:
            Application suggestions.
        """
        try:
            tid = TheoryId.from_string(theory_id)
            theory = await self._theory_repo.get_by_id(tid)
        except ValueError:
            return {"error": "Invalid theory ID"}

        if not theory:
            return {"error": "Theory not found"}

        prompt = f"""Provide practical applications for {theory.name} in education.
Context: {context or 'general classroom settings'}

Theory applications already known: {', '.join(theory.applications)}

Provide detailed applications in JSON format with:
1. "classroom_activities": Specific activities
2. "assessment_methods": How to assess learning
3. "lesson_planning": How to structure lessons
4. "technology_integration": Technology tools that align
5. "differentiation": How to adapt for different learners
6. "examples": Concrete examples

Return valid JSON only."""

        try:
            response = await self._llm.generate(prompt)
            import json

            return {
                "theory": theory.to_dict(),
                "context": context,
                "applications": json.loads(response),
            }
        except Exception as e:
            logger.error(f"Application generation failed: {e}")
            return {
                "theory": theory.to_dict(),
                "context": context,
                "applications": {"known_applications": theory.applications},
            }
