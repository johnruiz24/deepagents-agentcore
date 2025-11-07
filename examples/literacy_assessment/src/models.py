"""
Pydantic data models for the Literacy Level Assessment System.

This module defines the core data structures for assessments, questions, and user profiles.
All models include validation logic to ensure data integrity.
"""

from datetime import datetime
from typing import List, Literal, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, field_validator


class MultipleChoiceQuestion(BaseModel):
    """
    Multiple choice question with 4 options.

    Attributes:
        type: Question type identifier (always "multiple_choice")
        question_text: The question prompt
        options: List of 4 answer options (labeled A-D)
        correct_answer_index: Index of correct answer (0-3)
        explanation: Explanation of why the answer is correct
        module_source: Curriculum module this question comes from
        difficulty: Question difficulty level
    """
    type: Literal["multiple_choice"] = "multiple_choice"
    question_text: str = Field(..., min_length=10, description="Question prompt")
    options: List[str] = Field(..., min_length=4, max_length=4, description="4 answer options")
    correct_answer_index: int = Field(..., ge=0, le=3, description="Index of correct answer (0-3)")
    explanation: str = Field(..., min_length=10, description="Explanation of correct answer")
    module_source: str = Field(..., description="Source curriculum module")
    difficulty: Literal["beginner", "intermediate", "advanced"] = Field(
        default="intermediate",
        description="Question difficulty level"
    )

    @field_validator("options")
    @classmethod
    def validate_options(cls, v: List[str]) -> List[str]:
        """Ensure exactly 4 non-empty options."""
        if len(v) != 4:
            raise ValueError("Must have exactly 4 options")
        if any(not option.strip() for option in v):
            raise ValueError("All options must be non-empty")
        return v

    @field_validator("question_text", "explanation")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        """Ensure text fields are non-empty."""
        if not v.strip():
            raise ValueError("Text field cannot be empty")
        return v


class OpenEndedQuestion(BaseModel):
    """
    Open-ended question requiring text response.

    Attributes:
        type: Question type identifier (always "open_ended")
        question_text: The question prompt
        expected_key_points: Key points that should be addressed in response
        evaluation_criteria: Criteria for evaluating response quality
        module_source: Curriculum module this question comes from
        difficulty: Question difficulty level
    """
    type: Literal["open_ended"] = "open_ended"
    question_text: str = Field(..., min_length=10, description="Question prompt")
    expected_key_points: List[str] = Field(
        ...,
        min_length=3,
        max_length=7,
        description="Key points for rubric (3-7 points)"
    )
    evaluation_criteria: str = Field(
        ...,
        min_length=20,
        description="Criteria for evaluating responses"
    )
    module_source: str = Field(..., description="Source curriculum module")
    difficulty: Literal["beginner", "intermediate", "advanced"] = Field(
        default="intermediate",
        description="Question difficulty level"
    )

    @field_validator("expected_key_points")
    @classmethod
    def validate_key_points(cls, v: List[str]) -> List[str]:
        """Ensure all key points are non-empty."""
        if any(not point.strip() for point in v):
            raise ValueError("All key points must be non-empty")
        return v

    @field_validator("question_text", "evaluation_criteria")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        """Ensure text fields are non-empty."""
        if not v.strip():
            raise ValueError("Text field cannot be empty")
        return v


class UserBackgroundProfile(BaseModel):
    """
    User background profile for calibrating assessment difficulty.

    Attributes:
        background_text: Original free-form background description
        experience_level: Parsed experience level
        domain: User's domain/field (if mentioned)
        years_experience: Years of experience (if mentioned)
    """
    background_text: str = Field(..., description="Original background description")
    experience_level: Literal["beginner", "intermediate", "advanced", "expert"] = Field(
        default="intermediate",
        description="Parsed experience level"
    )
    domain: Optional[str] = Field(None, description="User's domain/field")
    years_experience: Optional[int] = Field(None, ge=0, description="Years of experience")


class AssessmentMetadata(BaseModel):
    """
    Metadata about assessment generation process.

    Attributes:
        generation_time_seconds: Time taken to generate assessment
        kb_query_count: Number of knowledge base queries made
        modules_queried: List of modules queried from KB
        difficulty_distribution: Count of questions by difficulty
        background_profile_used: User background profile used for calibration
    """
    generation_time_seconds: float = Field(..., ge=0, description="Generation time in seconds")
    kb_query_count: int = Field(..., ge=0, description="Number of KB queries")
    modules_queried: List[str] = Field(default_factory=list, description="Modules queried")
    difficulty_distribution: dict = Field(
        default_factory=dict,
        description="Count of questions by difficulty"
    )
    background_profile_used: Optional[UserBackgroundProfile] = None


class Assessment(BaseModel):
    """
    Complete literacy level assessment with mixed question format.

    An assessment contains exactly 10 questions:
    - 7 multiple choice questions (70%)
    - 3 open-ended questions (30%)

    Questions must cover at least 5 different curriculum modules for diversity.

    Attributes:
        assessment_id: Unique identifier
        level: Literacy level (1-4)
        multiple_choice_questions: List of 7 MC questions
        open_ended_questions: List of 3 open-ended questions
        generated_at: ISO timestamp of generation
        user_background: Original user background text
        modules_covered: List of unique modules covered
        metadata: Generation metadata (optional)
        s3_uri_json: S3 URI for JSON file (if uploaded)
        s3_uri_markdown: S3 URI for Markdown file (if uploaded)
        s3_upload_time: ISO timestamp of S3 upload (if uploaded)
    """
    assessment_id: UUID = Field(default_factory=uuid4, description="Unique assessment ID")
    level: int = Field(..., ge=1, le=4, description="Literacy level (1-4)")
    multiple_choice_questions: List[MultipleChoiceQuestion] = Field(
        ...,
        min_length=7,
        max_length=7,
        description="Exactly 7 multiple choice questions"
    )
    open_ended_questions: List[OpenEndedQuestion] = Field(
        ...,
        min_length=3,
        max_length=3,
        description="Exactly 3 open-ended questions"
    )
    generated_at: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="ISO timestamp of generation"
    )
    user_background: str = Field(..., description="User background text used for calibration")
    modules_covered: List[str] = Field(..., min_length=5, description="Unique modules covered (5+ required)")
    metadata: Optional[AssessmentMetadata] = None

    def validate_diversity(self) -> bool:
        """
        Validate that questions cover at least 5 different modules.

        Returns:
            True if diversity requirement met, False otherwise
        """
        unique_modules = set(self.modules_covered)
        return len(unique_modules) >= 5

    def validate_mix(self) -> bool:
        """
        Validate that assessment has correct question mix (7 MC + 3 OE).

        Returns:
            True if mix is correct, False otherwise
        """
        return (
            len(self.multiple_choice_questions) == 7 and
            len(self.open_ended_questions) == 3
        )

    def get_all_modules(self) -> List[str]:
        """
        Get list of all modules from all questions.

        Returns:
            List of module sources from all questions
        """
        mc_modules = [q.module_source for q in self.multiple_choice_questions]
        oe_modules = [q.module_source for q in self.open_ended_questions]
        return mc_modules + oe_modules

    def get_difficulty_distribution(self) -> dict:
        """
        Get distribution of questions by difficulty level.

        Returns:
            Dict mapping difficulty to count
        """
        distribution = {"beginner": 0, "intermediate": 0, "advanced": 0}

        for q in self.multiple_choice_questions:
            distribution[q.difficulty] += 1

        for q in self.open_ended_questions:
            distribution[q.difficulty] += 1

        return distribution

    @field_validator("modules_covered")
    @classmethod
    def validate_module_diversity(cls, v: List[str]) -> List[str]:
        """Ensure at least 5 unique modules covered."""
        unique_modules = set(v)
        if len(unique_modules) < 5:
            raise ValueError(f"Must cover at least 5 unique modules, got {len(unique_modules)}")
        return v


class MultiLevelAssessmentResult(BaseModel):
    """
    Result of multi-level parallel assessment generation.

    Attributes:
        assessments: List of generated assessments (one per level)
        total_time_seconds: Total time for parallel generation
        parallel_speedup_percent: Speedup percentage vs sequential
        levels_generated: List of levels generated
    """
    assessments: List[Assessment] = Field(..., min_length=1, description="Generated assessments")
    total_time_seconds: float = Field(..., ge=0, description="Total generation time")
    parallel_speedup_percent: Optional[float] = Field(
        None,
        description="Speedup percentage vs sequential (only for multi-level)"
    )
    levels_generated: List[int] = Field(..., description="Levels generated")

    @field_validator("levels_generated")
    @classmethod
    def validate_levels(cls, v: List[int]) -> List[int]:
        """Ensure all levels are 1-4."""
        if any(level not in [1, 2, 3, 4] for level in v):
            raise ValueError("All levels must be 1-4")
        return v
