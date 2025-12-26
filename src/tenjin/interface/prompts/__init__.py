"""MCP Prompts - Template handlers for MCP protocol."""

from mcp.server import Server
from mcp.types import Prompt, PromptArgument, PromptMessage, TextContent

from ..server import TenjinServer
from ...infrastructure.config.logging import get_logger

logger = get_logger(__name__)


def register_prompts(server: Server, tenjin: TenjinServer) -> None:
    """Register all MCP prompts with the server.

    Args:
        server: MCP server instance.
        tenjin: TENJIN server instance.
    """

    @server.list_prompts()
    async def list_prompts() -> list[Prompt]:
        """List all available prompts."""
        return [
            # Lesson planning prompts
            Prompt(
                name="lesson_plan",
                description="Generate a lesson plan based on educational theories",
                arguments=[
                    PromptArgument(
                        name="topic",
                        description="The topic of the lesson",
                        required=True,
                    ),
                    PromptArgument(
                        name="grade_level",
                        description="Target grade level (e.g., elementary, middle school, high school, university)",
                        required=True,
                    ),
                    PromptArgument(
                        name="duration",
                        description="Lesson duration (e.g., 45 minutes, 1 hour)",
                        required=False,
                    ),
                    PromptArgument(
                        name="theories",
                        description="Comma-separated theory names to incorporate",
                        required=False,
                    ),
                ],
            ),
            # Theory analysis prompts
            Prompt(
                name="theory_analysis",
                description="Analyze and explain an educational theory in depth",
                arguments=[
                    PromptArgument(
                        name="theory_name",
                        description="Name of the theory to analyze",
                        required=True,
                    ),
                    PromptArgument(
                        name="audience",
                        description="Target audience (teacher, student, researcher)",
                        required=False,
                    ),
                    PromptArgument(
                        name="focus",
                        description="Specific focus area (practical, historical, critical)",
                        required=False,
                    ),
                ],
            ),
            # Theory comparison prompts
            Prompt(
                name="theory_comparison",
                description="Compare and contrast educational theories",
                arguments=[
                    PromptArgument(
                        name="theories",
                        description="Comma-separated theory names to compare",
                        required=True,
                    ),
                    PromptArgument(
                        name="aspects",
                        description="Specific aspects to compare (optional)",
                        required=False,
                    ),
                ],
            ),
            # Application guidance prompts
            Prompt(
                name="application_guide",
                description="Get practical guidance for applying a theory",
                arguments=[
                    PromptArgument(
                        name="theory_name",
                        description="Theory to apply",
                        required=True,
                    ),
                    PromptArgument(
                        name="context",
                        description="Teaching context (subject, age group, setting)",
                        required=True,
                    ),
                    PromptArgument(
                        name="challenges",
                        description="Specific challenges to address",
                        required=False,
                    ),
                ],
            ),
            # Assessment design prompts
            Prompt(
                name="assessment_design",
                description="Design assessments aligned with educational theories",
                arguments=[
                    PromptArgument(
                        name="theory_name",
                        description="Theory to align with",
                        required=True,
                    ),
                    PromptArgument(
                        name="learning_objectives",
                        description="Learning objectives to assess",
                        required=True,
                    ),
                    PromptArgument(
                        name="assessment_type",
                        description="Type of assessment (formative, summative, diagnostic)",
                        required=False,
                    ),
                ],
            ),
            # Student engagement prompts
            Prompt(
                name="engagement_strategies",
                description="Get engagement strategies based on learning theories",
                arguments=[
                    PromptArgument(
                        name="challenge",
                        description="The engagement challenge you're facing",
                        required=True,
                    ),
                    PromptArgument(
                        name="age_group",
                        description="Student age group",
                        required=True,
                    ),
                    PromptArgument(
                        name="subject",
                        description="Subject area",
                        required=False,
                    ),
                ],
            ),
            # Differentiation prompts
            Prompt(
                name="differentiation_plan",
                description="Create a differentiation plan using learning theories",
                arguments=[
                    PromptArgument(
                        name="lesson_topic",
                        description="Topic of the lesson",
                        required=True,
                    ),
                    PromptArgument(
                        name="learner_differences",
                        description="Types of learner differences to address",
                        required=True,
                    ),
                    PromptArgument(
                        name="theories",
                        description="Theories to base differentiation on",
                        required=False,
                    ),
                ],
            ),
            # Research summary prompts
            Prompt(
                name="research_summary",
                description="Summarize research evidence for a theory",
                arguments=[
                    PromptArgument(
                        name="theory_name",
                        description="Theory to research",
                        required=True,
                    ),
                    PromptArgument(
                        name="focus_area",
                        description="Specific research focus",
                        required=False,
                    ),
                ],
            ),
            # Professional development prompts
            Prompt(
                name="pd_workshop",
                description="Design a professional development workshop on educational theory",
                arguments=[
                    PromptArgument(
                        name="theory_name",
                        description="Theory to focus on",
                        required=True,
                    ),
                    PromptArgument(
                        name="duration",
                        description="Workshop duration",
                        required=True,
                    ),
                    PromptArgument(
                        name="participant_level",
                        description="Participant experience level",
                        required=False,
                    ),
                ],
            ),
            # Curriculum integration prompts
            Prompt(
                name="curriculum_integration",
                description="Integrate educational theory into curriculum design",
                arguments=[
                    PromptArgument(
                        name="subject",
                        description="Subject area",
                        required=True,
                    ),
                    PromptArgument(
                        name="grade_level",
                        description="Grade level",
                        required=True,
                    ),
                    PromptArgument(
                        name="theories",
                        description="Theories to integrate",
                        required=False,
                    ),
                ],
            ),
            # Parent communication prompts
            Prompt(
                name="parent_communication",
                description="Explain educational approaches to parents",
                arguments=[
                    PromptArgument(
                        name="approach",
                        description="Teaching approach or theory to explain",
                        required=True,
                    ),
                    PromptArgument(
                        name="context",
                        description="What you're doing in class",
                        required=True,
                    ),
                ],
            ),
            # Technology integration prompts
            Prompt(
                name="tech_integration",
                description="Integrate technology using learning theories",
                arguments=[
                    PromptArgument(
                        name="technology",
                        description="Technology tool or platform",
                        required=True,
                    ),
                    PromptArgument(
                        name="learning_goal",
                        description="Learning goal to achieve",
                        required=True,
                    ),
                    PromptArgument(
                        name="theories",
                        description="Theories to align with",
                        required=False,
                    ),
                ],
            ),
            # Classroom management prompts
            Prompt(
                name="classroom_management",
                description="Get theory-based classroom management strategies",
                arguments=[
                    PromptArgument(
                        name="challenge",
                        description="Management challenge",
                        required=True,
                    ),
                    PromptArgument(
                        name="grade_level",
                        description="Grade level",
                        required=True,
                    ),
                ],
            ),
            # Learning environment prompts
            Prompt(
                name="learning_environment",
                description="Design learning environments based on theory",
                arguments=[
                    PromptArgument(
                        name="space_type",
                        description="Type of learning space",
                        required=True,
                    ),
                    PromptArgument(
                        name="goals",
                        description="Learning environment goals",
                        required=True,
                    ),
                    PromptArgument(
                        name="theories",
                        description="Theories to incorporate",
                        required=False,
                    ),
                ],
            ),
            # Japanese education context
            Prompt(
                name="japanese_context",
                description="Apply educational theories in Japanese education context (日本の教育文脈での理論適用)",
                arguments=[
                    PromptArgument(
                        name="theory_name",
                        description="Theory to apply (理論名)",
                        required=True,
                    ),
                    PromptArgument(
                        name="school_type",
                        description="School type: elementary/中学/高校/大学",
                        required=True,
                    ),
                    PromptArgument(
                        name="subject",
                        description="Subject (教科)",
                        required=False,
                    ),
                ],
            ),
        ]

    @server.get_prompt()
    async def get_prompt(name: str, arguments: dict | None = None) -> list[PromptMessage]:
        """Get a specific prompt with arguments."""
        arguments = arguments or {}

        # Build prompt based on name
        if name == "lesson_plan":
            content = _build_lesson_plan_prompt(arguments)
        elif name == "theory_analysis":
            content = _build_theory_analysis_prompt(arguments)
        elif name == "theory_comparison":
            content = _build_theory_comparison_prompt(arguments)
        elif name == "application_guide":
            content = _build_application_guide_prompt(arguments)
        elif name == "assessment_design":
            content = _build_assessment_design_prompt(arguments)
        elif name == "engagement_strategies":
            content = _build_engagement_strategies_prompt(arguments)
        elif name == "differentiation_plan":
            content = _build_differentiation_plan_prompt(arguments)
        elif name == "research_summary":
            content = _build_research_summary_prompt(arguments)
        elif name == "pd_workshop":
            content = _build_pd_workshop_prompt(arguments)
        elif name == "curriculum_integration":
            content = _build_curriculum_integration_prompt(arguments)
        elif name == "parent_communication":
            content = _build_parent_communication_prompt(arguments)
        elif name == "tech_integration":
            content = _build_tech_integration_prompt(arguments)
        elif name == "classroom_management":
            content = _build_classroom_management_prompt(arguments)
        elif name == "learning_environment":
            content = _build_learning_environment_prompt(arguments)
        elif name == "japanese_context":
            content = _build_japanese_context_prompt(arguments)
        else:
            content = f"Unknown prompt: {name}"

        return [
            PromptMessage(
                role="user",
                content=TextContent(type="text", text=content),
            )
        ]


def _build_lesson_plan_prompt(args: dict) -> str:
    """Build lesson plan prompt."""
    topic = args.get("topic", "")
    grade_level = args.get("grade_level", "")
    duration = args.get("duration", "45 minutes")
    theories = args.get("theories", "")

    prompt = f"""Create a detailed lesson plan for the following:

Topic: {topic}
Grade Level: {grade_level}
Duration: {duration}
"""
    if theories:
        prompt += f"Educational Theories to Incorporate: {theories}\n"

    prompt += """
Please include:
1. Learning objectives (aligned with theory)
2. Materials needed
3. Lesson structure with time allocations
4. Opening activity (hook)
5. Main instructional activities
6. Guided practice
7. Independent practice
8. Assessment strategy
9. Differentiation options
10. Closure/reflection

Explain how the lesson design reflects the educational theory principles."""

    return prompt


def _build_theory_analysis_prompt(args: dict) -> str:
    """Build theory analysis prompt."""
    theory_name = args.get("theory_name", "")
    audience = args.get("audience", "teacher")
    focus = args.get("focus", "comprehensive")

    return f"""Provide a {focus} analysis of {theory_name} for a {audience} audience.

Include:
1. Historical context and development
2. Key theorists and their contributions
3. Core principles and concepts
4. Theoretical foundations
5. Practical applications in education
6. Strengths and benefits
7. Limitations and criticisms
8. Modern relevance and adaptations
9. Related theories
10. Recommended resources for further learning

Tailor the explanation to be accessible for {audience}s while maintaining academic accuracy."""


def _build_theory_comparison_prompt(args: dict) -> str:
    """Build theory comparison prompt."""
    theories = args.get("theories", "")
    aspects = args.get("aspects", "all major aspects")

    return f"""Compare and contrast the following educational theories: {theories}

Analyze across these aspects: {aspects}

Provide:
1. Summary of each theory
2. Key similarities
3. Key differences
4. Complementary elements
5. Contradictory elements
6. Best use cases for each
7. Integrated approach suggestions
8. Practical comparison table"""


def _build_application_guide_prompt(args: dict) -> str:
    """Build application guide prompt."""
    theory_name = args.get("theory_name", "")
    context = args.get("context", "")
    challenges = args.get("challenges", "")

    prompt = f"""Provide practical guidance for applying {theory_name} in this context:

Context: {context}
"""
    if challenges:
        prompt += f"Specific Challenges: {challenges}\n"

    prompt += """
Include:
1. Key principles to apply
2. Step-by-step implementation guide
3. Specific strategies and techniques
4. Example activities
5. Common pitfalls to avoid
6. Success indicators
7. Adaptation suggestions"""

    return prompt


def _build_assessment_design_prompt(args: dict) -> str:
    """Build assessment design prompt."""
    theory_name = args.get("theory_name", "")
    objectives = args.get("learning_objectives", "")
    assessment_type = args.get("assessment_type", "formative and summative")

    return f"""Design assessments aligned with {theory_name} theory.

Learning Objectives: {objectives}
Assessment Type: {assessment_type}

Include:
1. Assessment rationale (theory alignment)
2. Assessment methods
3. Rubrics or scoring guides
4. Sample questions/tasks
5. Feedback strategies
6. Student self-assessment options"""


def _build_engagement_strategies_prompt(args: dict) -> str:
    """Build engagement strategies prompt."""
    challenge = args.get("challenge", "")
    age_group = args.get("age_group", "")
    subject = args.get("subject", "")

    return f"""Suggest engagement strategies based on learning theories for:

Challenge: {challenge}
Age Group: {age_group}
Subject: {subject if subject else "General"}

Provide:
1. Analysis of the engagement challenge
2. Relevant theories that address this
3. Specific strategies with theory connections
4. Implementation tips
5. Success indicators"""


def _build_differentiation_plan_prompt(args: dict) -> str:
    """Build differentiation plan prompt."""
    topic = args.get("lesson_topic", "")
    differences = args.get("learner_differences", "")
    theories = args.get("theories", "")

    return f"""Create a differentiation plan for:

Lesson Topic: {topic}
Learner Differences to Address: {differences}
Theories to Apply: {theories if theories else "Appropriate learning theories"}

Include:
1. Content differentiation strategies
2. Process differentiation strategies
3. Product differentiation strategies
4. Environment modifications
5. Assessment adaptations
6. Theory-based rationale for each strategy"""


def _build_research_summary_prompt(args: dict) -> str:
    """Build research summary prompt."""
    theory_name = args.get("theory_name", "")
    focus_area = args.get("focus_area", "effectiveness and applications")

    return f"""Summarize research evidence for {theory_name} with focus on {focus_area}.

Include:
1. Key research studies
2. Evidence quality assessment
3. Main findings
4. Practical implications
5. Research gaps
6. Recommendations for practitioners"""


def _build_pd_workshop_prompt(args: dict) -> str:
    """Build PD workshop prompt."""
    theory_name = args.get("theory_name", "")
    duration = args.get("duration", "2 hours")
    level = args.get("participant_level", "mixed")

    return f"""Design a professional development workshop on {theory_name}.

Duration: {duration}
Participant Level: {level}

Include:
1. Learning objectives
2. Pre-workshop preparation
3. Workshop agenda
4. Interactive activities
5. Discussion questions
6. Practice applications
7. Resources and handouts
8. Follow-up activities"""


def _build_curriculum_integration_prompt(args: dict) -> str:
    """Build curriculum integration prompt."""
    subject = args.get("subject", "")
    grade_level = args.get("grade_level", "")
    theories = args.get("theories", "")

    return f"""Guide for integrating educational theories into curriculum design:

Subject: {subject}
Grade Level: {grade_level}
Theories: {theories if theories else "Appropriate theories"}

Include:
1. Curriculum framework alignment
2. Unit design templates
3. Learning progression
4. Cross-curricular connections
5. Assessment integration
6. Implementation timeline"""


def _build_parent_communication_prompt(args: dict) -> str:
    """Build parent communication prompt."""
    approach = args.get("approach", "")
    context = args.get("context", "")

    return f"""Help me explain {approach} to parents.

What I'm doing in class: {context}

Provide:
1. Simple explanation of the approach
2. Benefits for their child
3. How they can support at home
4. Common questions and answers
5. Resources for parents
6. Sample communication (letter/newsletter)"""


def _build_tech_integration_prompt(args: dict) -> str:
    """Build tech integration prompt."""
    technology = args.get("technology", "")
    learning_goal = args.get("learning_goal", "")
    theories = args.get("theories", "")

    return f"""Guide for integrating technology with learning theory:

Technology: {technology}
Learning Goal: {learning_goal}
Theories to Align: {theories if theories else "Appropriate theories"}

Include:
1. Theory-technology alignment
2. Implementation strategies
3. Student activities
4. Assessment approaches
5. Potential challenges
6. Best practices"""


def _build_classroom_management_prompt(args: dict) -> str:
    """Build classroom management prompt."""
    challenge = args.get("challenge", "")
    grade_level = args.get("grade_level", "")

    return f"""Provide theory-based classroom management strategies:

Challenge: {challenge}
Grade Level: {grade_level}

Include:
1. Analysis from behavioral theories
2. Constructivist approaches
3. Humanistic strategies
4. Specific techniques
5. Prevention strategies
6. Intervention strategies
7. Creating positive environment"""


def _build_learning_environment_prompt(args: dict) -> str:
    """Build learning environment prompt."""
    space_type = args.get("space_type", "classroom")
    goals = args.get("goals", "")
    theories = args.get("theories", "")

    return f"""Design a learning environment based on theory:

Space Type: {space_type}
Goals: {goals}
Theories: {theories if theories else "Appropriate theories"}

Include:
1. Physical layout recommendations
2. Materials and resources
3. Visual environment
4. Flexible spaces
5. Technology integration
6. Social interaction areas
7. Quiet/focus areas"""


def _build_japanese_context_prompt(args: dict) -> str:
    """Build Japanese context prompt."""
    theory_name = args.get("theory_name", "")
    school_type = args.get("school_type", "")
    subject = args.get("subject", "")

    return f"""日本の教育文脈で{theory_name}を適用する方法を説明してください。

学校種別: {school_type}
教科: {subject if subject else "一般"}

以下を含めてください:
1. 日本の教育制度との関連
2. 学習指導要領との整合性
3. 日本の教室環境への適応
4. 具体的な実践例
5. 評価方法
6. 保護者への説明方法
7. 課題と対策

Apply {theory_name} in Japanese educational context:

School Type: {school_type}
Subject: {subject if subject else "General"}

Include both Japanese and international perspectives."""


__all__ = ["register_prompts"]
