# Data Model: Dynamic Literacy Level Assessment System

**Phase**: 1 - Design
**Date**: 2025-11-03
**Purpose**: Define entities, attributes, relationships, and validation rules for the assessment system

## Core Entities

### 1. User Background Profile

**Purpose**: Captures learner information to calibrate assessment difficulty

**Attributes**:
- `background_text` (string, required): Free-text description of user's education, work experience, and domain knowledge
- `parsed_experience_level` (enum, computed): Extracted experience level - `beginner`, `intermediate`, `advanced`, `expert`
- `domain_expertise` (list[string], computed): Identified areas of expertise from background text (e.g., ["machine learning", "software engineering"])
- `created_at` (datetime): Profile creation timestamp

**Validation Rules**:
- `background_text` must be 10-1000 characters
- If empty or too short, system uses default "beginner" calibration

**Relationships**:
- One-to-many with AssessmentRequest: A user profile can be used for multiple assessment requests

**State Transitions**: Immutable once created for an assessment request

---

### 2. Literacy Level

**Purpose**: Represents one of four progressive curriculum levels

**Attributes**:
- `level_number` (int, required): Level identifier (1, 2, 3, or 4)
- `level_name` (string, required): Display name (e.g., "Level 1: Foundations")
- `knowledge_base_id` (string, required): AWS Bedrock KB ID for this level
- `description` (string): Brief description of level scope

**Validation Rules**:
- `level_number` must be between 1 and 4 (inclusive)
- `knowledge_base_id` must be non-empty string in valid AWS KB ID format

**Relationships**:
- One-to-many with Assessment: Each level can have multiple assessments generated
- One-to-one with KnowledgeBaseContent: Each level has one associated KB

**State Transitions**: Static configuration, no state changes

---

### 3. Assessment Request

**Purpose**: User-initiated request triggering assessment generation

**Attributes**:
- `request_id` (UUID, required): Unique identifier
- `requested_levels` (list[int], required): Target level(s) for assessment (1-4)
- `user_background` (UserBackgroundProfile, required): Learner's background information
- `created_at` (datetime): Request timestamp
- `status` (enum): `pending`, `processing`, `completed`, `failed`
- `processing_start_time` (datetime, optional): When generation began
- `processing_end_time` (datetime, optional): When generation completed
- `error_message` (string, optional): If status is `failed`, describes error

**Validation Rules**:
- `requested_levels` must contain 1-4 unique values from {1, 2, 3, 4}
- Processing time (end - start) should be tracked to verify <60s for single level

**Relationships**:
- One-to-one with UserBackgroundProfile
- One-to-many with Assessment: Generates 1 assessment per requested level

**State Transitions**:
```
pending → processing → completed
pending → processing → failed
```

---

### 4. Assessment

**Purpose**: Generated set of 10 questions for a specific literacy level

**Attributes**:
- `assessment_id` (UUID, required): Unique identifier
- `level` (int, required): Target literacy level (1-4)
- `multiple_choice_questions` (list[MultipleChoiceQuestion], required): Exactly 7 questions
- `open_ended_questions` (list[OpenEndedQuestion], required): Exactly 3 questions
- `generated_at` (datetime): Generation timestamp
- `user_background` (string): Background text used for calibration
- `modules_covered` (list[string], required): Source modules/courses (min 5)
- `generation_time_seconds` (float): Time taken to generate (for performance tracking)

**Validation Rules**:
- Must have exactly 7 multiple choice questions
- Must have exactly 3 open-ended questions
- `modules_covered` must contain at least 5 unique module names
- All questions must have unique question_text (no duplicates)
- `level` must match the level of all contained questions

**Relationships**:
- Many-to-one with AssessmentRequest: Part of a request
- One-to-many with Question: Contains 10 questions total

**State Transitions**: Immutable once generated

---

### 5. Multiple Choice Question

**Purpose**: Structured question with 4 options and single correct answer

**Attributes**:
- `question_id` (UUID, required): Unique identifier
- `type` (literal): Always `"multiple_choice"`
- `question_text` (string, required): The question prompt
- `options` (list[string], required): Exactly 4 answer options
- `correct_answer_index` (int, required): Index (0-3) of correct option
- `module_source` (string, required): Curriculum module this came from
- `difficulty` (enum, required): `beginner`, `intermediate`, `advanced`
- `explanation` (string, optional): Rationale for correct answer
- `distractors_rationale` (string, optional): Why incorrect options are plausible

**Validation Rules**:
- `options` must have exactly 4 distinct strings
- `correct_answer_index` must be 0, 1, 2, or 3
- `question_text` must be 20-500 characters
- Each option must be 5-200 characters
- `difficulty` must align with user background and level

**Relationships**:
- Many-to-one with Assessment
- Many-to-one with Module (via module_source)

**State Transitions**: Immutable once created

---

### 6. Open Ended Question

**Purpose**: Question requiring text response for deeper understanding assessment

**Attributes**:
- `question_id` (UUID, required): Unique identifier
- `type` (literal): Always `"open_ended"`
- `question_text` (string, required): The question prompt
- `expected_key_points` (list[string], required): Key concepts expected in answer (for rubric)
- `module_source` (string, required): Curriculum module this came from
- `difficulty` (enum, required): `beginner`, `intermediate`, `advanced`
- `sample_answer` (string, optional): Example strong answer
- `evaluation_criteria` (string, optional): How to assess answer quality

**Validation Rules**:
- `question_text` must be 30-500 characters
- `expected_key_points` must have 2-5 items
- `difficulty` must align with user background and level

**Relationships**:
- Many-to-one with Assessment
- Many-to-one with Module (via module_source)

**State Transitions**: Immutable once created

---

### 7. Knowledge Base Content

**Purpose**: Reference to curriculum content stored in AWS Bedrock KB

**Attributes**:
- `knowledge_base_id` (string, required): AWS KB identifier
- `level` (int, required): Associated literacy level (1-4)
- `modules` (list[ModuleMetadata], optional): Cached list of available modules
- `last_synced` (datetime, optional): When KB content was last updated
- `total_documents` (int, optional): Document count in KB

**Validation Rules**:
- `knowledge_base_id` must be valid AWS KB ID format
- `level` must be 1-4

**Relationships**:
- One-to-one with LiteracyLevel
- One-to-many with Module: KB contains multiple modules

**State Transitions**: Read-only from application perspective (KB maintained externally)

---

### 8. Module Metadata

**Purpose**: Represents a curriculum module within a level's KB

**Attributes**:
- `module_name` (string, required): Module identifier
- `module_title` (string, required): Human-readable title
- `topics` (list[string], optional): List of topics covered
- `document_count` (int, optional): Number of documents in this module

**Validation Rules**:
- `module_name` must be unique within a level

**Relationships**:
- Many-to-one with KnowledgeBaseContent
- One-to-many with Question: Questions sourced from module

**State Transitions**: Read-only

---

## Entity Relationships Diagram

```
User Background Profile (1) ----< (1) Assessment Request (1) ----< (*) Assessment

Assessment (1) ----< (7) Multiple Choice Question
Assessment (1) ----< (3) Open Ended Question

Literacy Level (1) ----< (*) Assessment
Literacy Level (1) ---- (1) Knowledge Base Content

Knowledge Base Content (1) ----< (*) Module Metadata

Module Metadata (1) ----< (*) Multiple Choice Question (via module_source)
Module Metadata (1) ----< (*) Open Ended Question (via module_source)
```

## Pydantic Implementation Models

```python
from datetime import datetime
from enum import Enum
from typing import List, Literal
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, field_validator

class ExperienceLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class QuestionDifficulty(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class RequestStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class UserBackgroundProfile(BaseModel):
    background_text: str = Field(min_length=10, max_length=1000)
    parsed_experience_level: ExperienceLevel = ExperienceLevel.BEGINNER
    domain_expertise: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class LiteracyLevel(BaseModel):
    level_number: int = Field(ge=1, le=4)
    level_name: str
    knowledge_base_id: str = Field(min_length=1)
    description: str = ""

class AssessmentRequest(BaseModel):
    request_id: UUID = Field(default_factory=uuid4)
    requested_levels: List[int] = Field(min_length=1, max_length=4)
    user_background: UserBackgroundProfile
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: RequestStatus = RequestStatus.PENDING
    processing_start_time: datetime | None = None
    processing_end_time: datetime | None = None
    error_message: str | None = None

    @field_validator('requested_levels')
    @classmethod
    def validate_levels(cls, v):
        if not all(1 <= level <= 4 for level in v):
            raise ValueError("All levels must be between 1 and 4")
        if len(v) != len(set(v)):
            raise ValueError("Levels must be unique")
        return v

class MultipleChoiceQuestion(BaseModel):
    question_id: UUID = Field(default_factory=uuid4)
    type: Literal["multiple_choice"] = "multiple_choice"
    question_text: str = Field(min_length=20, max_length=500)
    options: List[str] = Field(min_length=4, max_length=4)
    correct_answer_index: int = Field(ge=0, le=3)
    module_source: str
    difficulty: QuestionDifficulty
    explanation: str | None = None
    distractors_rationale: str | None = None

    @field_validator('options')
    @classmethod
    def validate_options(cls, v):
        if len(v) != 4:
            raise ValueError("Must have exactly 4 options")
        if len(set(v)) != 4:
            raise ValueError("Options must be unique")
        return v

class OpenEndedQuestion(BaseModel):
    question_id: UUID = Field(default_factory=uuid4)
    type: Literal["open_ended"] = "open_ended"
    question_text: str = Field(min_length=30, max_length=500)
    expected_key_points: List[str] = Field(min_length=2, max_length=5)
    module_source: str
    difficulty: QuestionDifficulty
    sample_answer: str | None = None
    evaluation_criteria: str | None = None

class Assessment(BaseModel):
    assessment_id: UUID = Field(default_factory=uuid4)
    level: int = Field(ge=1, le=4)
    multiple_choice_questions: List[MultipleChoiceQuestion] = Field(min_length=7, max_length=7)
    open_ended_questions: List[OpenEndedQuestion] = Field(min_length=3, max_length=3)
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    user_background: str
    modules_covered: List[str] = Field(min_length=5)
    generation_time_seconds: float

    def validate_diversity(self) -> bool:
        """Ensure questions cover at least 5 different modules"""
        all_modules = [q.module_source for q in self.multiple_choice_questions]
        all_modules.extend([q.module_source for q in self.open_ended_questions])
        return len(set(all_modules)) >= 5

    @field_validator('modules_covered')
    @classmethod
    def validate_module_count(cls, v):
        if len(set(v)) < 5:
            raise ValueError("Must cover at least 5 unique modules")
        return v

class ModuleMetadata(BaseModel):
    module_name: str
    module_title: str
    topics: List[str] = Field(default_factory=list)
    document_count: int | None = None

class KnowledgeBaseContent(BaseModel):
    knowledge_base_id: str
    level: int = Field(ge=1, le=4)
    modules: List[ModuleMetadata] = Field(default_factory=list)
    last_synced: datetime | None = None
    total_documents: int | None = None
```

## Agent State Model (Deep Agents)

Deep Agents uses LangGraph StateGraph with message-based state. Our assessment system adds:

```python
from typing import TypedDict, List
from langchain_core.messages import BaseMessage

class LiteracyAssessmentState(TypedDict):
    """State for literacy assessment agent"""
    messages: List[BaseMessage]  # Standard LangGraph message history
    assessment_request: AssessmentRequest | None  # Current request being processed
    generated_assessments: List[Assessment]  # Results from subagents
    filesystem: dict  # FilesystemMiddleware state (managed by middleware)
```

**State Flow**:
1. User input → `assessment_request` created
2. Main agent spawns subagents → each generates `Assessment`
3. Subagent results → `generated_assessments` list
4. Main agent synthesizes → final response in `messages`

## Validation Summary

| Entity | Key Constraints |
|--------|-----------------|
| User Background | 10-1000 characters |
| Assessment Request | 1-4 unique levels |
| Assessment | 7 MC + 3 open-ended, 5+ modules |
| MC Question | 4 unique options, valid index |
| Open Ended | 2-5 key points |
| Level | 1-4 range |

## Next Steps

- **contracts/**: Define REST/GraphQL API if exposing as service (optional for example)
- **quickstart.md**: Setup guide using these models
- **Implementation**: Create Pydantic models in `examples/literacy-assessment/models.py`
