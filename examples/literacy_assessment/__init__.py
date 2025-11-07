"""
Dynamic Literacy Level Assessment System

A Deep Agents-based system that generates custom literacy assessments by orchestrating
4 specialized subagents (one per level 1-4). Each subagent queries dedicated AWS Bedrock
Knowledge Bases containing curriculum content to generate 10-question assessments with
mixed format (70% multiple choice, 30% open-ended).

Features:
- Single-level and multi-level assessment generation
- Parallel subagent execution for multi-level requests
- Background-calibrated difficulty
- Module diversity (5+ modules per assessment)
- Performance tracking and metadata

Usage:
    from examples.literacy_assessment import create_literacy_assessment_agent

    agent = create_literacy_assessment_agent()
    result = agent.invoke({
        "messages": [{
            "role": "user",
            "content": "Generate a Level 2 assessment for someone with 3 years of software development experience"
        }]
    })
"""

from examples.literacy_assessment.src.agent import create_literacy_assessment_agent

__all__ = ["create_literacy_assessment_agent"]
