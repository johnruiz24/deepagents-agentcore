"""
Question generation and validation utilities.

This module provides helper functions for formatting, validating, and structuring
questions during assessment generation. The actual question content is generated
by LLM agents, but these utilities ensure proper formatting and validation.
"""

from typing import List, Dict, Set
from examples.literacy_assessment.src.models import (
    MultipleChoiceQuestion,
    OpenEndedQuestion,
    Assessment,
    UserBackgroundProfile
)


def validate_question_mix(
    mc_questions: List[MultipleChoiceQuestion],
    oe_questions: List[OpenEndedQuestion]
) -> bool:
    """
    Validate that question mix is correct (7 MC + 3 OE).

    Args:
        mc_questions: List of multiple choice questions
        oe_questions: List of open-ended questions

    Returns:
        True if mix is correct, False otherwise
    """
    return len(mc_questions) == 7 and len(oe_questions) == 3


def validate_module_diversity(
    mc_questions: List[MultipleChoiceQuestion],
    oe_questions: List[OpenEndedQuestion],
    min_modules: int = 5
) -> bool:
    """
    Validate that questions cover at least min_modules different modules.

    Args:
        mc_questions: List of multiple choice questions
        oe_questions: List of open-ended questions
        min_modules: Minimum number of unique modules required

    Returns:
        True if diversity requirement met, False otherwise
    """
    modules: Set[str] = set()

    for q in mc_questions:
        modules.add(q.module_source)

    for q in oe_questions:
        modules.add(q.module_source)

    return len(modules) >= min_modules


def validate_unique_questions(
    mc_questions: List[MultipleChoiceQuestion],
    oe_questions: List[OpenEndedQuestion]
) -> bool:
    """
    Validate that all questions have unique question text (no duplicates).

    Args:
        mc_questions: List of multiple choice questions
        oe_questions: List of open-ended questions

    Returns:
        True if all questions unique, False otherwise
    """
    question_texts: Set[str] = set()

    for q in mc_questions:
        if q.question_text.lower() in question_texts:
            return False
        question_texts.add(q.question_text.lower())

    for q in oe_questions:
        if q.question_text.lower() in question_texts:
            return False
        question_texts.add(q.question_text.lower())

    return True


def get_modules_covered(
    mc_questions: List[MultipleChoiceQuestion],
    oe_questions: List[OpenEndedQuestion]
) -> List[str]:
    """
    Get list of unique modules covered by all questions.

    Args:
        mc_questions: List of multiple choice questions
        oe_questions: List of open-ended questions

    Returns:
        List of unique module names
    """
    modules: Set[str] = set()

    for q in mc_questions:
        modules.add(q.module_source)

    for q in oe_questions:
        modules.add(q.module_source)

    return sorted(list(modules))


def validate_assessment(
    level: int,
    mc_questions: List[MultipleChoiceQuestion],
    oe_questions: List[OpenEndedQuestion],
    user_background: str
) -> Dict[str, any]:
    """
    Validate a complete assessment before creating Assessment object.

    Args:
        level: Literacy level (1-4)
        mc_questions: List of multiple choice questions
        oe_questions: List of open-ended questions
        user_background: User background text

    Returns:
        Dict with validation results and any errors
    """
    errors = []
    warnings = []

    # Check question mix
    if not validate_question_mix(mc_questions, oe_questions):
        errors.append(
            f"Invalid question mix: Expected 7 MC + 3 OE, got {len(mc_questions)} MC + {len(oe_questions)} OE"
        )

    # Check module diversity
    modules = get_modules_covered(mc_questions, oe_questions)
    if len(modules) < 5:
        errors.append(
            f"Insufficient module diversity: Expected 5+, got {len(modules)} ({', '.join(modules)})"
        )

    # Check unique questions
    if not validate_unique_questions(mc_questions, oe_questions):
        warnings.append("Duplicate question text detected")

    # Check level range
    if level not in [1, 2, 3, 4]:
        errors.append(f"Invalid level: {level} (must be 1-4)")

    # Check background not empty
    if not user_background or not user_background.strip():
        warnings.append("Empty user background provided")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "modules_covered": modules,
        "module_count": len(modules),
        "question_count": len(mc_questions) + len(oe_questions)
    }


def create_assessment_from_questions(
    level: int,
    mc_questions: List[MultipleChoiceQuestion],
    oe_questions: List[OpenEndedQuestion],
    user_background: str
) -> Assessment:
    """
    Create an Assessment object from validated questions.

    Args:
        level: Literacy level (1-4)
        mc_questions: List of 7 multiple choice questions
        oe_questions: List of 3 open-ended questions
        user_background: User background text

    Returns:
        Assessment object

    Raises:
        ValueError: If validation fails
    """
    # Validate first
    validation = validate_assessment(level, mc_questions, oe_questions, user_background)

    if not validation["valid"]:
        error_msg = "; ".join(validation["errors"])
        raise ValueError(f"Assessment validation failed: {error_msg}")

    # Create Assessment
    assessment = Assessment(
        level=level,
        multiple_choice_questions=mc_questions,
        open_ended_questions=oe_questions,
        user_background=user_background,
        modules_covered=validation["modules_covered"]
    )

    return assessment


def format_assessment_as_markdown(assessment: Assessment) -> str:
    """
    Format an assessment as human-readable markdown.

    Args:
        assessment: Assessment object

    Returns:
        Markdown-formatted string
    """
    lines = []

    # Header
    lines.append(f"# Literacy Level {assessment.level} Assessment")
    lines.append(f"\n**Assessment ID**: {assessment.assessment_id}")
    lines.append(f"**Generated**: {assessment.generated_at}")
    lines.append(f"**User Background**: {assessment.user_background}")
    lines.append(f"**Modules Covered**: {', '.join(assessment.modules_covered)} ({len(assessment.modules_covered)} modules)")
    lines.append("\n---\n")

    # Multiple Choice Questions
    lines.append("## Multiple Choice Questions (7)\n")
    for i, q in enumerate(assessment.multiple_choice_questions, 1):
        lines.append(f"### Question {i} (MC) - {q.difficulty.title()}")
        lines.append(f"**Module**: {q.module_source}\n")
        lines.append(f"{q.question_text}\n")

        for j, option in enumerate(q.options):
            letter = chr(65 + j)  # A, B, C, D
            marker = " ✓ CORRECT" if j == q.correct_answer_index else ""
            lines.append(f"{letter}. {option}{marker}")

        lines.append(f"\n**Explanation**: {q.explanation}\n")
        lines.append("---\n")

    # Open-Ended Questions
    lines.append("## Open-Ended Questions (3)\n")
    for i, q in enumerate(assessment.open_ended_questions, 1):
        lines.append(f"### Question {7+i} (OE) - {q.difficulty.title()}")
        lines.append(f"**Module**: {q.module_source}\n")
        lines.append(f"{q.question_text}\n")

        lines.append("**Key Points to Address**:")
        for point in q.expected_key_points:
            lines.append(f"- {point}")

        lines.append(f"\n**Evaluation Criteria**: {q.evaluation_criteria}\n")
        lines.append("---\n")

    # Metadata
    if assessment.metadata:
        lines.append("## Generation Metadata\n")
        lines.append(f"- **Generation Time**: {assessment.metadata.generation_time_seconds:.2f}s")
        lines.append(f"- **KB Queries**: {assessment.metadata.kb_query_count}")
        lines.append(f"- **Modules Queried**: {', '.join(assessment.metadata.modules_queried)}")

        dist = assessment.metadata.difficulty_distribution
        lines.append(f"- **Difficulty Distribution**: Beginner: {dist.get('beginner', 0)}, Intermediate: {dist.get('intermediate', 0)}, Advanced: {dist.get('advanced', 0)}")

    return "\n".join(lines)


def get_difficulty_for_background(background_profile: UserBackgroundProfile) -> str:
    """
    Determine appropriate question difficulty based on user background.

    Args:
        background_profile: Parsed user background profile

    Returns:
        Difficulty level: "beginner", "intermediate", or "advanced"
    """
    experience_map = {
        "beginner": "beginner",
        "intermediate": "intermediate",
        "advanced": "advanced",
        "expert": "advanced"  # Expert users get advanced questions within the level
    }

    return experience_map.get(background_profile.experience_level, "intermediate")


def parse_user_background_simple(background_text: str) -> UserBackgroundProfile:
    """
    Simple heuristic parsing of user background text.

    This is a fallback function for basic parsing. In practice, the LLM agent
    will do more sophisticated parsing.

    Args:
        background_text: Free-form background description

    Returns:
        UserBackgroundProfile with parsed fields
    """
    background_lower = background_text.lower()

    # Detect experience level
    if any(word in background_lower for word in ["beginner", "new", "no experience", "just starting"]):
        experience_level = "beginner"
    elif any(word in background_lower for word in ["expert", "senior", "10+ years", "experienced"]):
        experience_level = "expert"
    elif any(word in background_lower for word in ["advanced", "proficient", "5+ years"]):
        experience_level = "advanced"
    else:
        experience_level = "intermediate"

    # Detect years of experience (basic regex-like search)
    years_experience = None
    for word in background_text.split():
        if word.isdigit():
            years_experience = int(word)
            break

    # Detect domain (basic keyword matching)
    domain = None
    domains = ["software", "data", "engineering", "teaching", "business", "healthcare"]
    for d in domains:
        if d in background_lower:
            domain = d
            break

    return UserBackgroundProfile(
        background_text=background_text,
        experience_level=experience_level,
        domain=domain,
        years_experience=years_experience
    )
