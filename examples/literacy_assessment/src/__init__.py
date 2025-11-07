"""
Literacy Assessment System - Core Module

This module contains the core components for the literacy assessment system:
- agent: Main assessment agent with level-specific subagents
- config: AWS Bedrock configuration
- models: Pydantic data models
- kb_tools: AWS Bedrock Knowledge Base tools
- questions: Question validation utilities
"""

from examples.literacy_assessment.src.agent import create_literacy_assessment_agent
from examples.literacy_assessment.src.config import LiteracyAssessmentConfig
from examples.literacy_assessment.src.models import (
    MultipleChoiceQuestion,
    OpenEndedQuestion,
    Assessment,
    UserBackgroundProfile,
)
from examples.literacy_assessment.src.kb_tools import (
    query_level_1_kb,
    query_level_2_kb,
    query_level_3_kb,
    query_level_4_kb,
)

__all__ = [
    "create_literacy_assessment_agent",
    "LiteracyAssessmentConfig",
    "MultipleChoiceQuestion",
    "OpenEndedQuestion",
    "Assessment",
    "UserBackgroundProfile",
    "query_level_1_kb",
    "query_level_2_kb",
    "query_level_3_kb",
    "query_level_4_kb",
]
