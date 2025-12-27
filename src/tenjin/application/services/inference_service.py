"""InferenceService - Advanced LLM-powered reasoning operations.

This service provides advanced inference capabilities:
- Theory recommendation based on learner profiles
- Gap analysis for learning design
- Relationship inference between theories
- Evidence-based reasoning
"""

from typing import Any
import json

from ...domain.entities.theory import Theory
from ...domain.repositories.theory_repository import TheoryRepository
from ...domain.repositories.vector_repository import VectorRepository
from ...domain.repositories.graph_repository import GraphRepository
from ...domain.value_objects.theory_id import TheoryId
from ...domain.value_objects.search_query import SearchQuery
from ...infrastructure.adapters.esperanto_adapter import EsperantoAdapter
from ...infrastructure.config.logging import get_logger

logger = get_logger(__name__)


class InferenceService:
    """Service for advanced LLM-powered inference operations.

    Provides intelligent reasoning capabilities that go beyond
    simple search, including theory recommendation, gap analysis,
    and relationship inference.
    """

    def __init__(
        self,
        theory_repository: TheoryRepository,
        vector_repository: VectorRepository,
        graph_repository: GraphRepository,
        llm_adapter: EsperantoAdapter,
    ) -> None:
        """Initialize inference service.

        Args:
            theory_repository: Repository for theory data.
            vector_repository: Repository for vector search.
            graph_repository: Repository for relationship data.
            llm_adapter: LLM adapter for AI inference.
        """
        self._theory_repo = theory_repository
        self._vector_repo = vector_repository
        self._graph_repo = graph_repository
        self._llm = llm_adapter

    # ========================================
    # Theory Recommendation
    # ========================================

    async def recommend_theories_for_learner(
        self,
        learner_profile: dict[str, Any],
        learning_goals: list[str],
        constraints: dict[str, Any] | None = None,
        limit: int = 5,
    ) -> dict[str, Any]:
        """Recommend theories based on learner profile and goals.

        Args:
            learner_profile: Learner characteristics (age, level, style, etc.)
            learning_goals: What the learner wants to achieve
            constraints: Time, resources, or other constraints
            limit: Maximum recommendations

        Returns:
            Personalized theory recommendations with rationale
        """
        logger.info(f"Generating recommendations for goals: {learning_goals}")

        # Build context for semantic search
        context_parts = [
            f"Learning goals: {', '.join(learning_goals)}",
            f"Learner age: {learner_profile.get('age', 'not specified')}",
            f"Learner level: {learner_profile.get('level', 'not specified')}",
            f"Learning style: {learner_profile.get('learning_style', 'not specified')}",
        ]
        search_context = " ".join(context_parts)

        # Find candidate theories via semantic search
        query = SearchQuery(
            query=search_context,
            search_type="semantic",
            limit=limit * 3,
        )
        search_results = await self._vector_repo.search(query)

        if not search_results.results:
            return {
                "learner_profile": learner_profile,
                "learning_goals": learning_goals,
                "recommendations": [],
                "message": "No matching theories found",
            }

        # Get full theory details
        candidate_theories = []
        for result in search_results.results:
            theory = await self._theory_repo.get_by_id(result.entity_id)
            if theory:
                candidate_theories.append({
                    "theory": theory,
                    "semantic_score": result.relevance_score,
                })

        # Use LLM to rank and explain recommendations
        recommendations = await self._rank_theories_for_learner(
            learner_profile,
            learning_goals,
            constraints or {},
            candidate_theories[:limit * 2],
            limit,
        )

        return {
            "learner_profile": learner_profile,
            "learning_goals": learning_goals,
            "constraints": constraints,
            "recommendations": recommendations,
            "total_candidates": len(candidate_theories),
        }

    async def _rank_theories_for_learner(
        self,
        learner_profile: dict[str, Any],
        learning_goals: list[str],
        constraints: dict[str, Any],
        candidates: list[dict],
        limit: int,
    ) -> list[dict[str, Any]]:
        """Use LLM to rank theories for a specific learner.

        Args:
            learner_profile: Learner characteristics
            learning_goals: Learning objectives
            constraints: Constraints
            candidates: Candidate theories
            limit: Max recommendations

        Returns:
            Ranked recommendations with explanations
        """
        # Build theory descriptions for LLM
        theory_descs = []
        for i, c in enumerate(candidates):
            t = c["theory"]
            theory_descs.append(
                f"{i+1}. {t.name} ({t.name_ja})\n"
                f"   Category: {t.category.display_name}\n"
                f"   Description: {t.description[:300]}\n"
                f"   Key Principles: {', '.join(t.key_principles[:3])}"
            )

        prompt = f"""You are an educational theory expert. Recommend the best theories for this learner.

LEARNER PROFILE:
- Age: {learner_profile.get('age', 'not specified')}
- Level: {learner_profile.get('level', 'not specified')}
- Learning Style: {learner_profile.get('learning_style', 'not specified')}
- Prior Knowledge: {learner_profile.get('prior_knowledge', 'not specified')}
- Special Needs: {learner_profile.get('special_needs', 'none')}

LEARNING GOALS:
{chr(10).join(f'- {g}' for g in learning_goals)}

CONSTRAINTS:
- Time: {constraints.get('time', 'flexible')}
- Resources: {constraints.get('resources', 'standard')}
- Setting: {constraints.get('setting', 'classroom')}

CANDIDATE THEORIES:
{chr(10).join(theory_descs)}

Select the top {limit} theories and explain why each is suitable.
Return JSON with this structure:
{{
  "recommendations": [
    {{
      "rank": 1,
      "theory_index": <1-based index>,
      "fit_score": <0.0-1.0>,
      "rationale": "<why this theory fits>",
      "implementation_tips": ["<tip1>", "<tip2>"],
      "potential_challenges": ["<challenge1>"]
    }}
  ],
  "overall_strategy": "<how to combine these theories>"
}}

Return valid JSON only."""

        system_prompt = """You are an expert in educational psychology and instructional design.
Provide evidence-based, practical recommendations tailored to the learner's needs.
Always respond with valid JSON."""

        try:
            response = await self._llm.generate(prompt, system_prompt)
            result = json.loads(response)

            # Enrich with actual theory data
            enriched = []
            for rec in result.get("recommendations", [])[:limit]:
                idx = rec.get("theory_index", 1) - 1
                if 0 <= idx < len(candidates):
                    theory = candidates[idx]["theory"]
                    enriched.append({
                        "rank": rec.get("rank", len(enriched) + 1),
                        "theory": theory.to_dict(),
                        "fit_score": rec.get("fit_score", 0.8),
                        "rationale": rec.get("rationale", ""),
                        "implementation_tips": rec.get("implementation_tips", []),
                        "potential_challenges": rec.get("potential_challenges", []),
                    })

            return enriched

        except Exception as e:
            logger.error(f"LLM ranking failed: {e}")
            # Fallback: return top candidates by semantic score
            return [
                {
                    "rank": i + 1,
                    "theory": c["theory"].to_dict(),
                    "fit_score": c["semantic_score"],
                    "rationale": "Recommended based on semantic relevance",
                    "implementation_tips": [],
                    "potential_challenges": [],
                }
                for i, c in enumerate(candidates[:limit])
            ]

    # ========================================
    # Gap Analysis
    # ========================================

    async def analyze_learning_design_gaps(
        self,
        current_design: dict[str, Any],
        target_outcomes: list[str],
        applied_theories: list[str] | None = None,
    ) -> dict[str, Any]:
        """Analyze gaps in a learning design and suggest improvements.

        Args:
            current_design: Current learning design description
            target_outcomes: Desired learning outcomes
            applied_theories: Theories currently being used (optional)

        Returns:
            Gap analysis with improvement suggestions
        """
        logger.info("Performing learning design gap analysis")

        # Get applied theories details
        applied_theory_details = []
        if applied_theories:
            for tid_str in applied_theories:
                try:
                    tid = TheoryId.from_string(tid_str)
                    theory = await self._theory_repo.get_by_id(tid)
                    if theory:
                        applied_theory_details.append(theory)
                except ValueError:
                    continue

        # Search for potentially useful theories
        outcome_query = " ".join(target_outcomes)
        query = SearchQuery(
            query=outcome_query,
            search_type="semantic",
            limit=15,
        )
        relevant_theories = await self._vector_repo.search(query)

        # Get details for relevant theories
        candidate_theories = []
        for result in relevant_theories.results:
            theory = await self._theory_repo.get_by_id(result.entity_id)
            if theory and theory not in applied_theory_details:
                candidate_theories.append(theory)

        # Perform gap analysis with LLM
        analysis = await self._perform_gap_analysis(
            current_design,
            target_outcomes,
            applied_theory_details,
            candidate_theories[:10],
        )

        return {
            "current_design": current_design,
            "target_outcomes": target_outcomes,
            "applied_theories": [t.to_dict() for t in applied_theory_details],
            "analysis": analysis,
        }

    async def _perform_gap_analysis(
        self,
        current_design: dict[str, Any],
        target_outcomes: list[str],
        applied_theories: list[Theory],
        candidate_theories: list[Theory],
    ) -> dict[str, Any]:
        """Perform LLM-powered gap analysis.

        Args:
            current_design: Current design
            target_outcomes: Target outcomes
            applied_theories: Currently applied theories
            candidate_theories: Potentially useful theories

        Returns:
            Gap analysis results
        """
        applied_desc = "\n".join(
            f"- {t.name}: {t.description[:150]}"
            for t in applied_theories
        ) if applied_theories else "None specified"

        candidate_desc = "\n".join(
            f"- {t.name} ({t.name_ja}): {t.description[:150]}"
            for t in candidate_theories[:8]
        )

        prompt = f"""Analyze the gaps in this learning design and suggest improvements.

CURRENT DESIGN:
- Activities: {current_design.get('activities', 'not specified')}
- Assessment: {current_design.get('assessment', 'not specified')}
- Materials: {current_design.get('materials', 'not specified')}
- Duration: {current_design.get('duration', 'not specified')}
- Setting: {current_design.get('setting', 'not specified')}

TARGET LEARNING OUTCOMES:
{chr(10).join(f'- {o}' for o in target_outcomes)}

CURRENTLY APPLIED THEORIES:
{applied_desc}

POTENTIALLY RELEVANT THEORIES (not yet applied):
{candidate_desc}

Provide a comprehensive gap analysis in JSON format:
{{
  "coverage_assessment": {{
    "cognitive_domain": {{"covered": true/false, "gaps": ["..."]}},
    "affective_domain": {{"covered": true/false, "gaps": ["..."]}},
    "psychomotor_domain": {{"covered": true/false, "gaps": ["..."]}}
  }},
  "theoretical_gaps": [
    {{
      "gap_description": "<what's missing>",
      "impact": "high/medium/low",
      "suggested_theories": ["<theory name>", ...],
      "implementation_suggestion": "<how to address>"
    }}
  ],
  "alignment_issues": [
    {{
      "issue": "<misalignment description>",
      "affected_outcomes": ["<outcome>"],
      "recommendation": "<how to fix>"
    }}
  ],
  "improvement_priorities": [
    {{
      "priority": 1,
      "action": "<specific action>",
      "rationale": "<why important>",
      "expected_impact": "<what will improve>"
    }}
  ],
  "missing_elements": ["<element1>", "<element2>"],
  "overall_score": <0-100>,
  "summary": "<brief summary of findings>"
}}

Return valid JSON only."""

        system_prompt = """You are an expert instructional designer and learning scientist.
Provide thorough, evidence-based gap analysis with actionable recommendations.
Always respond with valid JSON."""

        try:
            response = await self._llm.generate(prompt, system_prompt)
            return json.loads(response)
        except Exception as e:
            logger.error(f"Gap analysis failed: {e}")
            return {
                "coverage_assessment": {},
                "theoretical_gaps": [],
                "alignment_issues": [],
                "improvement_priorities": [],
                "missing_elements": [],
                "overall_score": 0,
                "summary": "Gap analysis unavailable due to processing error",
                "error": str(e),
            }

    # ========================================
    # Relationship Inference
    # ========================================

    async def infer_theory_relationships(
        self,
        theory_id: str,
        inference_depth: int = 2,
    ) -> dict[str, Any]:
        """Infer relationships between theories using LLM reasoning.

        Args:
            theory_id: Base theory to analyze
            inference_depth: How many hops to explore

        Returns:
            Inferred relationships with explanations
        """
        logger.info(f"Inferring relationships for theory: {theory_id}")

        # Get the base theory
        try:
            tid = TheoryId.from_string(theory_id)
            base_theory = await self._theory_repo.get_by_id(tid)
        except ValueError:
            return {"error": "Invalid theory ID"}

        if not base_theory:
            return {"error": "Theory not found"}

        # Get existing relationships from graph
        existing_relations = await self._graph_repo.get_related_theories(
            theory_id=theory_id,
            depth=inference_depth,
            limit=20,
        )

        # Get all theories for potential relationship discovery
        all_theories = await self._theory_repo.get_all()
        
        # Filter to theories not already related
        existing_ids = {r["theory"]["id"] for r in existing_relations}
        existing_ids.add(theory_id)
        unrelated_theories = [
            t for t in all_theories
            if t.id.value not in existing_ids
        ][:15]

        # Use LLM to infer potential relationships
        inferred = await self._infer_relationships(
            base_theory,
            unrelated_theories,
        )

        return {
            "base_theory": base_theory.to_dict(),
            "existing_relationships": existing_relations,
            "inferred_relationships": inferred,
            "relationship_graph": await self._build_relationship_graph(
                base_theory, existing_relations, inferred
            ),
        }

    async def _infer_relationships(
        self,
        base_theory: Theory,
        candidate_theories: list[Theory],
    ) -> list[dict[str, Any]]:
        """Use LLM to infer potential relationships.

        Args:
            base_theory: Base theory
            candidate_theories: Potential related theories

        Returns:
            Inferred relationships
        """
        candidate_desc = "\n".join(
            f"{i+1}. {t.name} ({t.name_ja})\n"
            f"   Category: {t.category.display_name}\n"
            f"   Description: {t.description[:200]}"
            for i, t in enumerate(candidate_theories)
        )

        prompt = f"""Analyze potential theoretical relationships between the base theory and candidates.

BASE THEORY:
- Name: {base_theory.name} ({base_theory.name_ja})
- Category: {base_theory.category.display_name}
- Description: {base_theory.description}
- Key Principles: {', '.join(base_theory.key_principles[:5])}
- Theorists: {', '.join(base_theory.theorists[:3])}

CANDIDATE THEORIES:
{candidate_desc}

For each candidate that has a meaningful relationship with the base theory, identify:
1. The type of relationship
2. The strength of the relationship
3. The evidence/rationale

Relationship types:
- "foundation": Base theory is foundational to candidate
- "extension": Candidate extends base theory
- "complement": Theories complement each other
- "contrast": Theories have contrasting views
- "application": One applies to the other domain
- "synthesis": Candidate synthesizes with base

Return JSON:
{{
  "inferred_relationships": [
    {{
      "candidate_index": <1-based>,
      "relationship_type": "<type>",
      "strength": <0.0-1.0>,
      "direction": "base_to_candidate" | "candidate_to_base" | "bidirectional",
      "evidence": "<reasoning for this relationship>",
      "practical_implications": "<how this relationship is useful>"
    }}
  ]
}}

Only include relationships with strength >= 0.5.
Return valid JSON only."""

        system_prompt = """You are an expert in educational theory and epistemology.
Identify genuine theoretical relationships based on scholarly analysis.
Always respond with valid JSON."""

        try:
            response = await self._llm.generate(prompt, system_prompt)
            result = json.loads(response)

            # Enrich with actual theory data
            enriched = []
            for rel in result.get("inferred_relationships", []):
                idx = rel.get("candidate_index", 1) - 1
                if 0 <= idx < len(candidate_theories):
                    enriched.append({
                        "related_theory": candidate_theories[idx].to_dict(),
                        "relationship_type": rel.get("relationship_type", "unknown"),
                        "strength": rel.get("strength", 0.5),
                        "direction": rel.get("direction", "bidirectional"),
                        "evidence": rel.get("evidence", ""),
                        "practical_implications": rel.get("practical_implications", ""),
                        "inferred": True,
                    })

            return enriched

        except Exception as e:
            logger.error(f"Relationship inference failed: {e}")
            return []

    async def _build_relationship_graph(
        self,
        base_theory: Theory,
        existing: list[dict],
        inferred: list[dict],
    ) -> dict[str, Any]:
        """Build a graph representation of relationships.

        Args:
            base_theory: Base theory
            existing: Existing relationships
            inferred: Inferred relationships

        Returns:
            Graph structure for visualization
        """
        nodes = [
            {
                "id": base_theory.id.value,
                "name": base_theory.name,
                "name_ja": base_theory.name_ja,
                "category": base_theory.category.value,
                "type": "base",
            }
        ]

        edges = []

        # Add existing relationships
        for rel in existing:
            theory_data = rel.get("theory", {})
            nodes.append({
                "id": theory_data.get("id", ""),
                "name": theory_data.get("name", ""),
                "name_ja": theory_data.get("name_ja", ""),
                "category": theory_data.get("category", ""),
                "type": "existing",
            })
            edges.append({
                "source": base_theory.id.value,
                "target": theory_data.get("id", ""),
                "relationship": rel.get("relationship_type", "related"),
                "inferred": False,
            })

        # Add inferred relationships
        for rel in inferred:
            theory_data = rel.get("related_theory", {})
            nodes.append({
                "id": theory_data.get("id", ""),
                "name": theory_data.get("name", ""),
                "name_ja": theory_data.get("name_ja", ""),
                "category": theory_data.get("category", ""),
                "type": "inferred",
            })
            edges.append({
                "source": base_theory.id.value,
                "target": theory_data.get("id", ""),
                "relationship": rel.get("relationship_type", "related"),
                "strength": rel.get("strength", 0.5),
                "inferred": True,
            })

        return {
            "nodes": nodes,
            "edges": edges,
            "node_count": len(nodes),
            "edge_count": len(edges),
            "inferred_count": len(inferred),
        }

    # ========================================
    # Evidence-Based Reasoning
    # ========================================

    async def reason_about_application(
        self,
        scenario: str,
        constraints: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Reason about which theories apply to a specific scenario.

        Args:
            scenario: Educational scenario description
            constraints: Optional constraints

        Returns:
            Reasoned recommendations with evidence
        """
        # Validate input
        if not scenario or not scenario.strip():
            return {
                "scenario": scenario or "",
                "constraints": constraints or {},
                "reasoning": {
                    "error": "Empty scenario provided",
                    "message": "Please provide a scenario description",
                },
                "recommendations": [],
            }

        logger.info(f"Reasoning about scenario: {scenario[:50]}...")

        # Find relevant theories
        query = SearchQuery(
            query=scenario,
            search_type="hybrid",
            limit=15,
        )
        search_results = await self._vector_repo.search(query)

        # Get theory details
        theories = []
        for result in search_results.results:
            theory = await self._theory_repo.get_by_id(result.entity_id)
            if theory:
                theories.append({
                    "theory": theory,
                    "relevance": result.relevance_score,
                })

        # Reason about application
        reasoning = await self._reason_application(
            scenario,
            theories[:10],
            constraints or {},
        )

        return {
            "scenario": scenario,
            "constraints": constraints,
            "reasoning": reasoning,
            "candidate_theories": len(theories),
        }

    async def _reason_application(
        self,
        scenario: str,
        candidates: list[dict],
        constraints: dict[str, Any],
    ) -> dict[str, Any]:
        """Perform evidence-based reasoning about theory application.

        Args:
            scenario: The scenario
            candidates: Candidate theories
            constraints: Constraints

        Returns:
            Reasoning results
        """
        theory_desc = "\n".join(
            f"- {c['theory'].name}: {c['theory'].description[:200]} "
            f"(relevance: {c['relevance']:.2f})"
            for c in candidates
        )

        prompt = f"""As an educational expert, reason about which theories best apply to this scenario.

SCENARIO:
{scenario}

CONSTRAINTS:
- Time available: {constraints.get('time', 'flexible')}
- Resources: {constraints.get('resources', 'standard')}
- Learner count: {constraints.get('learner_count', 'varies')}
- Setting: {constraints.get('setting', 'not specified')}

CANDIDATE THEORIES (ranked by initial relevance):
{theory_desc}

Provide evidence-based reasoning in JSON format:
{{
  "primary_recommendation": {{
    "theory": "<theory name>",
    "confidence": <0.0-1.0>,
    "evidence": ["<evidence1>", "<evidence2>"],
    "application_strategy": "<how to apply>"
  }},
  "secondary_recommendations": [
    {{
      "theory": "<theory name>",
      "role": "<supporting/alternative/for specific aspect>",
      "when_to_use": "<conditions>"
    }}
  ],
  "reasoning_chain": [
    {{
      "step": 1,
      "observation": "<what we observe about the scenario>",
      "inference": "<what this implies>",
      "supporting_theory": "<which theory supports this>"
    }}
  ],
  "potential_pitfalls": ["<pitfall1>", "<pitfall2>"],
  "success_factors": ["<factor1>", "<factor2>"],
  "evaluation_criteria": ["<criterion1>", "<criterion2>"]
}}

Return valid JSON only."""

        system_prompt = """You are an expert in educational theory application.
Provide rigorous, evidence-based reasoning with clear logical chains.
Always respond with valid JSON."""

        try:
            response = await self._llm.generate(prompt, system_prompt)
            return json.loads(response)
        except Exception as e:
            logger.error(f"Reasoning failed: {e}")
            return {
                "primary_recommendation": {
                    "theory": candidates[0]["theory"].name if candidates else "None",
                    "confidence": 0.5,
                    "evidence": ["Based on semantic relevance"],
                    "application_strategy": "Further analysis needed",
                },
                "secondary_recommendations": [],
                "reasoning_chain": [],
                "potential_pitfalls": [],
                "success_factors": [],
                "evaluation_criteria": [],
                "error": str(e),
            }
