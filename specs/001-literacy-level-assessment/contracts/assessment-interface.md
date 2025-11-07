# Assessment Interface Contract

**Purpose**: Define the programmatic interface for the literacy assessment system
**Type**: Python API (example application, not web service)
**Date**: 2025-11-03

## Overview

This is an example application demonstrating Deep Agents capabilities. The primary interface is through Python code, not HTTP/REST. This document describes the programmatic API.

## Main Entry Point

### `create_literacy_assessment_agent()`

Creates and configures the main Deep Agents orchestrator for literacy assessments.

**Signature**:
```python
def create_literacy_assessment_agent(
    config: LiteracyAssessmentConfig | None = None,
    model: str | BaseChatModel = "claude-sonnet-4-20250514",
) -> CompiledGraph:
    """
    Create literacy assessment agent with 4 level-specific subagents.

    Args:
        config: Configuration object with KB IDs and AWS settings.
                If None, loads from environment variables.
        model: LLM model to use. Accepts LangChain model string or instance.

    Returns:
        CompiledGraph: LangGraph agent ready for invocation

    Raises:
        ValueError: If required KB IDs not configured
        ClientError: If AWS credentials invalid or KBs inaccessible
    """
```

**Example Usage**:
```python
from examples.literacy_assessment import create_literacy_assessment_agent

# Create agent (loads config from environment)
agent = create_literacy_assessment_agent()

# Invoke for single level
result = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "Generate a Level 2 assessment for someone with 3 years of software engineering experience"
    }]
})

# Invoke for multiple levels (parallel execution)
result = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "Generate assessments for Levels 1, 2, and 3 for a beginner with no technical background"
    }]
})
```

---

## Input Contract

### User Message Format

**Structure**:
```
"Generate a Level {N} assessment for {user_background}"
```

or for multiple levels:
```
"Generate assessments for Levels {N1}, {N2}, and {N3} for {user_background}"
```

**Components**:
- **Level specification**: Integer 1-4 or comma-separated list
- **User background**: Free-text description of education, experience, expertise

**Examples**:
```python
# Single level, beginner
"Generate a Level 1 assessment for someone with no prior AI knowledge"

# Single level, advanced
"Generate a Level 3 assessment for a machine learning engineer with 5 years experience"

# Multiple levels, comparison
"Generate assessments for Levels 1, 2, and 3 for an undergraduate computer science student"

# Multiple levels, placement
"Generate all 4 level assessments for someone with a PhD in cognitive science"
```

**Validation**:
- Levels must be 1, 2, 3, or 4
- User background recommended but optional (defaults to "beginner" if missing)
- System extracts level numbers and background from natural language input

---

## Output Contract

### Assessment Response Format

**Structure**: Agent returns assessment(s) in markdown format with structured sections

**Single Level Output**:
```markdown
# Level {N} Literacy Assessment

**Generated**: {timestamp}
**Calibrated for**: {user_background_summary}
**Modules Covered**: {module_list}

## Multiple Choice Questions (7)

### Question 1
**Module**: {module_name}
**Difficulty**: {beginner|intermediate|advanced}

{question_text}

A) {option_1}
B) {option_2}
C) {option_3}
D) {option_4}

**Correct Answer**: {A|B|C|D}
**Explanation**: {why_correct}

[... questions 2-7 ...]

## Open-Ended Questions (3)

### Question 8
**Module**: {module_name}
**Difficulty**: {beginner|intermediate|advanced}

{question_text}

**Key Points to Address**:
- {point_1}
- {point_2}
- {point_3}

[... questions 9-10 ...]

## Generation Metrics
- **Time**: {generation_time}s
- **Modules Covered**: {count} ({module_names})
```

**Multiple Level Output**:
Concatenates individual level assessments with separators:

```markdown
# Multi-Level Assessment Report

**Generated**: {timestamp}
**Levels Requested**: {level_list}
**User Background**: {background}

---

## Level 1 Assessment
[... Level 1 content ...]

---

## Level 2 Assessment
[... Level 2 content ...]

---

## Performance Summary
- **Total Time**: {total_time}s
- **Parallel Execution**: ✅ {speedup_percentage}% faster than sequential
- **Assessments Generated**: {count}
```

---

## JSON Output Format (Programmatic Access)

For programmatic consumption, assessments can be accessed as structured objects:

```python
# Access structured data from agent filesystem
agent_state = result['messages'][-1]

# Assessments written to filesystem
assessment_files = [
    "/assessments/level_1_assessment.json",
    "/assessments/level_2_assessment.json",
    # etc.
]

# Each JSON follows the Assessment Pydantic model
{
    "assessment_id": "uuid",
    "level": 2,
    "multiple_choice_questions": [
        {
            "question_id": "uuid",
            "type": "multiple_choice",
            "question_text": "...",
            "options": ["A", "B", "C", "D"],
            "correct_answer_index": 2,
            "module_source": "Module 3: Data Structures",
            "difficulty": "intermediate"
        },
        // ... 6 more MC questions
    ],
    "open_ended_questions": [
        {
            "question_id": "uuid",
            "type": "open_ended",
            "question_text": "...",
            "expected_key_points": ["point1", "point2", "point3"],
            "module_source": "Module 5: Algorithms",
            "difficulty": "intermediate"
        },
        // ... 2 more open-ended questions
    ],
    "generated_at": "2025-11-03T10:30:00Z",
    "user_background": "3 years software engineering experience",
    "modules_covered": ["Module 1", "Module 2", "Module 3", "Module 4", "Module 5", "Module 6"],
    "generation_time_seconds": 45.2
}
```

---

## Error Handling

### Error Types

**Configuration Errors**:
```python
ValueError: "Knowledge base ID not configured for level {N}"
```
- **Cause**: Missing KB_LEVEL_{N}_ID in environment
- **Resolution**: Set required environment variables

**AWS Errors**:
```python
ClientError: "An error occurred (ResourceNotFoundException) when calling the Retrieve operation"
```
- **Cause**: KB ID invalid or user lacks access
- **Resolution**: Verify KB IDs and AWS credentials/permissions

**Validation Errors**:
```python
ValueError: "All levels must be between 1 and 4"
```
- **Cause**: Invalid level number in request
- **Resolution**: Use only levels 1-4

**Generation Errors**:
```python
AssessmentGenerationError: "Failed to generate sufficient unique questions for Level {N}"
```
- **Cause**: KB content insufficient or duplicate detection triggered
- **Resolution**: Check KB has adequate diverse content

### Error Response Format

```python
{
    "error": {
        "type": "ConfigurationError",
        "message": "Knowledge base ID not configured for level 2",
        "level": 2,
        "details": "Set KB_LEVEL_2_ID environment variable"
    }
}
```

---

## Performance Contract

### Single Level Assessment

**Target**: <60 seconds
**Typical**: 30-45 seconds

**Breakdown**:
- KB query: 10-15s
- Question generation: 15-20s
- Formatting/validation: 2-5s
- Overhead: 3-5s

### Multi-Level Assessment (Parallel)

**Target**: <60% of sequential time
**Typical**: 40-50% of sequential time

**Example**:
- Sequential (3 levels): ~120s
- Parallel (3 levels): ~50s (58% reduction)

### Concurrency

**Target**: 10+ concurrent users with <20% degradation
**Considerations**:
- AWS Bedrock KB rate limits
- LLM API rate limits
- Local compute for question validation

---

## Future API Considerations

If exposing as a web service in the future:

**Potential REST Endpoints**:
```
POST /api/v1/assessments/generate
GET  /api/v1/assessments/{assessment_id}
GET  /api/v1/levels
GET  /api/v1/health
```

**Potential GraphQL Schema**:
```graphql
type Mutation {
  generateAssessment(input: AssessmentRequest!): AssessmentResponse!
}

type Query {
  assessment(id: ID!): Assessment
  availableLevels: [LiteracyLevel!]!
}
```

**Note**: Not implemented in current example. See data-model.md for entity schemas that would support API implementation.
