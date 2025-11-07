# Technical Research: Dynamic Literacy Level Assessment System

**Phase**: 0 - Research & Technical Decisions
**Date**: 2025-11-03
**Purpose**: Resolve NEEDS CLARIFICATION items from Technical Context and establish implementation patterns

## Research Topics

### 1. AWS Bedrock Knowledge Base Integration

**Question**: What are the boto3 requirements, configuration patterns, and access methods for AWS Bedrock Knowledge Bases?

**Decision**: Use `boto3>=1.34.0` with bedrock-agent-runtime client

**Rationale**:
- AWS Bedrock Knowledge Base support requires recent boto3 versions (1.34.0+ has bedrock-agent-runtime)
- bedrock-agent-runtime client provides `retrieve` and `retrieve_and_generate` APIs
- Standard AWS credential chain works (IAM roles, environment variables, ~/.aws/credentials)

**Implementation Pattern**:

```python
import boto3
from botocore.exceptions import ClientError

class KnowledgeBaseClient:
    def __init__(self, knowledge_base_id: str, region_name: str = "us-east-1"):
        self.kb_id = knowledge_base_id
        self.client = boto3.client(
            'bedrock-agent-runtime',
            region_name=region_name
        )

    def query(self, query_text: str, max_results: int = 10):
        """Retrieve relevant content from knowledge base"""
        try:
            response = self.client.retrieve(
                knowledgeBaseId=self.kb_id,
                retrievalQuery={'text': query_text},
                retrievalConfiguration={
                    'vectorSearchConfiguration': {
                        'numberOfResults': max_results
                    }
                }
            )
            return response['retrievalResults']
        except ClientError as e:
            # Handle errors (access denied, KB not found, etc.)
            raise
```

**Alternatives Considered**:
- Direct S3 + embedding search: Rejected - Bedrock KB provides managed retrieval with relevance scoring
- OpenSearch direct queries: Rejected - Bedrock KB abstracts this complexity and handles updates
- Manual chunking/indexing: Rejected - Bedrock KB handles document processing automatically

**References**:
- [AWS Bedrock Knowledge Base Documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base.html)
- [boto3 bedrock-agent-runtime Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agent-runtime.html)

---

### 2. Knowledge Base Configuration & IDs

**Question**: How should the 4 level-specific knowledge bases be configured, identified, and accessed?

**Decision**: Environment variable-based configuration with per-level KB IDs

**Rationale**:
- Each literacy level (1-4) has independent curriculum content requiring separate knowledge bases
- Environment variables allow easy configuration across dev/staging/prod
- Configuration class provides type safety and validation

**Implementation Pattern**:

```python
# config.py
import os
from typing import Dict

class LiteracyAssessmentConfig:
    """Configuration for literacy assessment system"""

    # AWS Configuration
    AWS_REGION = os.getenv("AWS_REGION", "eu-central-1")
    AWS_PROFILE = os.getenv("AWS_PROFILE", "mll-dev")

    # Knowledge Base IDs (one per level)
    KB_LEVEL_1_ID = os.getenv("KB_LEVEL_1_ID", "QADZTSAPWX")
    KB_LEVEL_2_ID = os.getenv("KB_LEVEL_2_ID", "KGGD2PTQ2N")
    KB_LEVEL_3_ID = os.getenv("KB_LEVEL_3_ID", "7MGFSODDVI")
    KB_LEVEL_4_ID = os.getenv("KB_LEVEL_4_ID", "7MGFSODDVI")  # Shares KB with Level 3

    @classmethod
    def get_kb_id(cls, level: int) -> str:
        """Get knowledge base ID for specified level"""
        kb_map = {
            1: cls.KB_LEVEL_1_ID,
            2: cls.KB_LEVEL_2_ID,
            3: cls.KB_LEVEL_3_ID,
            4: cls.KB_LEVEL_4_ID,
        }
        kb_id = kb_map.get(level)
        if not kb_id:
            raise ValueError(f"Knowledge base ID not configured for level {level}")
        return kb_id

    @classmethod
    def validate(cls) -> bool:
        """Validate all required configuration is present"""
        required_ids = [
            cls.KB_LEVEL_1_ID,
            cls.KB_LEVEL_2_ID,
            cls.KB_LEVEL_3_ID,
            cls.KB_LEVEL_4_ID,
        ]
        return all(required_ids)
```

**.env.example**:
```bash
# AWS Configuration
AWS_REGION=eu-central-1
AWS_PROFILE=mll-dev

# Bedrock Knowledge Base IDs (one per literacy level)
KB_LEVEL_1_ID=QADZTSAPWX
KB_LEVEL_2_ID=KGGD2PTQ2N
KB_LEVEL_3_ID=7MGFSODDVI
KB_LEVEL_4_ID=7MGFSODDVI

# Note: Level 3 and 4 share the same knowledge base
# AWS credentials loaded from profile 'mll-dev'
```

**Alternatives Considered**:
- Single KB with metadata filtering: Rejected - Harder to manage independent level content, less clear separation
- Hardcoded IDs in code: Rejected - Not environment-flexible, security risk
- Config file (JSON/YAML): Considered but environment variables simpler for example application

---

### 3. Knowledge Base Query Patterns for Question Generation

**Question**: How should we query knowledge bases to ensure diverse, multi-module coverage for 10-question assessments?

**Decision**: Multi-query strategy with module coverage tracking

**Rationale**:
- Single broad query may concentrate on one topic
- Multiple targeted queries ensure coverage across modules/courses
- Requirement: 5+ modules per assessment (FR-005, SC-005)
- Prevents question duplication through content tracking

**Implementation Pattern**:

```python
def gather_diverse_content(kb_client, level: int, num_modules: int = 6):
    """
    Query KB multiple times with different module-focused prompts
    to ensure content diversity across curriculum
    """
    # Step 1: Get curriculum overview
    overview_query = f"List the main modules and topics in Level {level} curriculum"
    overview_results = kb_client.query(overview_query, max_results=5)

    # Step 2: Extract module names from overview
    # (simplified - actual implementation would parse results)
    modules = extract_modules(overview_results)

    # Step 3: Query each module for detailed content
    module_content = {}
    for module in modules[:num_modules]:
        module_query = f"Detailed content for {module} in Level {level}"
        module_results = kb_client.query(module_query, max_results=3)
        module_content[module] = module_results

    return module_content

def generate_questions_from_content(content, user_background, question_count=10):
    """
    Generate questions from gathered content with:
    - 70% multiple choice (7 questions)
    - 30% open-ended (3 questions)
    - Calibrated to user background
    - Distributed across modules
    """
    # Implementation in question_generator.py
    pass
```

**Query Optimization**:
- Batch queries where possible to reduce latency
- Cache module structure between assessment generations
- Use parallel KB queries for multi-level assessments (via subagents)

**Alternatives Considered**:
- Random sampling from single query: Rejected - May miss important modules
- Pre-generated question bank: Rejected - Not dynamic, doesn't use real-time curriculum updates
- Exhaustive KB scan: Rejected - Too slow, exceeds 60-second target

---

### 4. Subagent Design Pattern for Level-Specific Assessment Generation

**Question**: How should the 4 level-specific subagents be structured to maximize parallelization and maintain clear separation?

**Decision**: Dedicated subagent per level with level-scoped KB access and independent question generation

**Rationale**:
- Matches Deep Agents parallelization pattern (see `examples/parallel/parallel_agent.py`)
- Each subagent queries only its level's KB (no cross-level contamination)
- Main agent spawns 1-4 subagents based on user request
- Subagents return complete assessments, main agent synthesizes

**Implementation Pattern**:

```python
# Subagent definition (one per level)
level_1_subagent = {
    "name": "level-1-assessment-agent",
    "description": "Generates Level 1 literacy assessments. Only use for Level 1 requests. For multiple levels, call multiple level agents in parallel.",
    "system_prompt": """You are a Level 1 literacy assessment specialist.

Your job is to:
1. Query the Level 1 knowledge base for diverse curriculum content
2. Generate exactly 10 questions:
   - 7 multiple choice questions (4 options each, mark correct answer)
   - 3 open-ended questions
3. Calibrate question difficulty based on user background provided
4. Ensure questions cover at least 5 different modules/courses
5. Return structured assessment in JSON format

User background will be provided in the request. Use it to adjust:
- Question complexity
- Assumed prior knowledge
- Technical depth
- Wording/terminology

Remember: Only your FINAL assessment JSON will be passed to the coordinator. Make it complete and well-formatted!""",
    "tools": [query_level_1_kb, format_assessment],
}

# Similar for levels 2, 3, 4 with different KB access
```

**Parallel Execution**:
```python
# Main agent orchestration for multi-level request
if user_requests_multiple_levels([1, 2, 3]):
    # Call all three subagents in PARALLEL in same response
    task("Generate Level 1 assessment for <background>", "level-1-assessment-agent")
    task("Generate Level 2 assessment for <background>", "level-2-assessment-agent")
    task("Generate Level 3 assessment for <background>", "level-3-assessment-agent")
    # Subagents execute concurrently, return results to main agent
```

**Alternatives Considered**:
- Single subagent with level parameter: Rejected - Harder to ensure clean separation, less clear parallelization
- Main agent does everything: Rejected - Defeats Deep Agents pattern, no context isolation
- Subagents share tools: Considered but separate tools prevent cross-level queries

---

### 5. Question Format & Validation

**Question**: How should questions be structured to support 70% MC / 30% open-ended mix and enable potential auto-scoring?

**Decision**: JSON schema with typed question objects

**Rationale**:
- Structured format enables validation
- Clear distinction between question types
- MC questions include answer key for potential auto-scoring
- Open-ended questions can be manually reviewed or AI-scored later

**Schema**:

```python
from typing import List, Literal
from pydantic import BaseModel, Field

class MultipleChoiceQuestion(BaseModel):
    type: Literal["multiple_choice"] = "multiple_choice"
    question_text: str
    options: List[str] = Field(min_length=4, max_length=4)
    correct_answer_index: int = Field(ge=0, le=3)
    module_source: str  # Which module this came from
    difficulty: Literal["beginner", "intermediate", "advanced"] = "intermediate"

class OpenEndedQuestion(BaseModel):
    type: Literal["open_ended"] = "open_ended"
    question_text: str
    expected_key_points: List[str]  # For guidance/rubric
    module_source: str
    difficulty: Literal["beginner", "intermediate", "advanced"] = "intermediate"

class Assessment(BaseModel):
    level: int = Field(ge=1, le=4)
    multiple_choice_questions: List[MultipleChoiceQuestion] = Field(min_length=7, max_length=7)
    open_ended_questions: List[OpenEndedQuestion] = Field(min_length=3, max_length=3)
    generated_at: str  # ISO timestamp
    user_background: str
    modules_covered: List[str]

    def validate_diversity(self) -> bool:
        """Ensure questions cover at least 5 different modules"""
        unique_modules = set(self.modules_covered)
        return len(unique_modules) >= 5
```

**Alternatives Considered**:
- Plain text format: Rejected - Harder to parse, validate, and process programmatically
- Markdown format: Considered for human readability but JSON better for tooling
- Database storage: Out of scope for example, but JSON enables easy DB integration later

---

## Summary of Technical Decisions

| Topic | Decision | Impact |
|-------|----------|--------|
| **AWS SDK** | boto3>=1.34.0 with bedrock-agent-runtime | Enables KB queries, requires AWS credentials |
| **KB Configuration** | Environment variables, one KB ID per level | Flexible deployment, clear separation |
| **Query Strategy** | Multi-query with module tracking | Ensures diversity, meets 5+ module requirement |
| **Subagent Pattern** | 1 subagent per level, parallel execution | Matches Deep Agents pattern, enables 60% speedup |
| **Question Format** | Pydantic models with JSON schema | Type-safe, validatable, extensible |

## Dependencies

**New Dependencies**:
```txt
boto3>=1.34.0
pydantic>=2.0.0
python-dotenv>=1.0.0  # For .env file loading
```

**Existing Dependencies** (from deepagents):
- langchain>=1.0.0
- langchain-anthropic>=1.0.0
- langchain-core>=1.0.0

---

### 6. S3 Upload Patterns for Assessment Storage

**Question**: How should generated assessments be uploaded to S3 for durable storage and cross-system accessibility?

**Decision**: Use boto3 S3 client with `put_object()` and retry logic with exponential backoff

**Rationale**:
- S3 provides durable, scalable storage for generated assessments
- Same bucket as knowledge base content simplifies IAM permissions
- Hierarchical key structure enables level-based organization
- Metadata tags support audit trails and filtering
- Retry logic handles transient AWS errors gracefully

**Implementation Pattern**:

```python
import boto3
from botocore.exceptions import ClientError
import time
from functools import wraps
from datetime import datetime

class S3UploaderClient:
    """Client for uploading assessment files to S3."""

    def __init__(self, bucket_name: str, prefix: str, region: str, profile: str):
        """Initialize S3 uploader with boto3 session."""
        self.bucket_name = bucket_name
        self.prefix = prefix
        self.region = region
        self.profile = profile

        # Create boto3 session with profile (same pattern as KB tools)
        session = boto3.Session(
            profile_name=self.profile,
            region_name=self.region
        )

        # Initialize S3 client
        self.s3_client = session.client('s3')

    def _generate_s3_key(self, level: int, timestamp: datetime, file_format: str) -> str:
        """
        Generate S3 key for assessment file.

        Returns: 'learning_path/assessments/level_1/level_1_20251105_120000.json'
        """
        ts_str = timestamp.strftime('%Y%m%d_%H%M%S')
        ext = 'json' if file_format == 'json' else 'md'
        key = f"{self.prefix}/level_{level}/level_{level}_{ts_str}.{ext}"
        return key

    def _retry_with_backoff(self, max_attempts=3, backoff_seconds=[1, 2, 4]):
        """Decorator for retry logic with exponential backoff."""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                for attempt in range(max_attempts):
                    try:
                        return func(*args, **kwargs)
                    except ClientError as e:
                        error_code = e.response['Error']['Code']

                        # Permanent errors - don't retry
                        if error_code in ['NoSuchBucket', 'AccessDenied']:
                            raise

                        # Transient errors - retry with backoff
                        if error_code in ['Throttling', 'ServiceUnavailable', 'RequestTimeout']:
                            if attempt < max_attempts - 1:
                                sleep_time = backoff_seconds[attempt]
                                print(f"Retry {attempt + 1}/{max_attempts} after {sleep_time}s")
                                time.sleep(sleep_time)
                                continue

                        raise
                raise RuntimeError(f"Max retries ({max_attempts}) exceeded")
            return wrapper
        return decorator

    @_retry_with_backoff(max_attempts=3, backoff_seconds=[1, 2, 4])
    def upload_assessment(self, assessment: Assessment, file_format: str) -> str:
        """
        Upload assessment file to S3 with retry logic.

        Returns:
            S3 URI (s3://bucket/key)
        """
        # Generate S3 key
        key = self._generate_s3_key(assessment.level, datetime.now(), file_format)

        # Prepare content and metadata
        if file_format == 'json':
            body = assessment.model_dump_json(indent=2)
            content_type = 'application/json'
        else:  # markdown
            body = assessment.to_markdown()
            content_type = 'text/markdown'

        metadata = {
            'generation-time': datetime.now().isoformat(),
            'user-background-hash': hash(assessment.user_background),
            'modules-count': str(len(assessment.modules_covered)),
            'literacy-level': str(assessment.level),
            'question-count': '10',
            'format': file_format
        }

        # Upload to S3
        self.s3_client.put_object(
            Bucket=self.bucket_name,
            Key=key,
            Body=body,
            ContentType=content_type,
            Metadata=metadata
        )

        # Return S3 URI
        return f"s3://{self.bucket_name}/{key}"
```

**S3 Bucket Configuration**:
- **Bucket**: `literacy-framework-development-961105418118-eu-central-1` (existing bucket)
- **Path Structure**:
  - Knowledge base content: `s3://bucket/learning_path/levels/level_{level}/`
  - Assessment files: `s3://bucket/learning_path/assessments/level_{level}/`
- **Key Format**: `learning_path/assessments/level_{level}/level_{level}_YYYYMMDD_HHMMSS.{ext}`

**Retry Strategy**:
- **Transient errors** (retry with exponential backoff):
  - `Throttling`: Rate limit exceeded
  - `ServiceUnavailable`: S3 temporarily unavailable
  - `RequestTimeout`: Request timed out
- **Permanent errors** (fail immediately):
  - `NoSuchBucket`: Bucket doesn't exist
  - `AccessDenied`: Insufficient IAM permissions
- **Backoff timing**: 1s → 2s → 4s (max 3 attempts)

**Batch Upload for Multiple Assessments**:
```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def upload_multiple_assessments(
    assessments: List[Assessment],
    formats: List[str] = ["json", "markdown"]
) -> Dict[str, List[str]]:
    """Upload multiple assessments concurrently with ThreadPoolExecutor."""
    results = {}

    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_assessment = {}
        for assessment in assessments:
            for fmt in formats:
                future = executor.submit(upload_assessment, assessment, fmt)
                future_to_assessment[future] = (assessment.level, fmt)

        for future in as_completed(future_to_assessment):
            level, fmt = future_to_assessment[future]
            try:
                s3_uri = future.result()
                key = f"level_{level}"
                if key not in results:
                    results[key] = []
                results[key].append(s3_uri)
            except Exception as e:
                print(f"Upload failed for level {level} ({fmt}): {e}")

    return results
```

**Alternatives Considered**:
- `upload_file()`: Rejected - Designed for large files from disk, less efficient for in-memory content
- boto3 built-in retries: Available via `Config(retries={'max_attempts': 3})` but less control
- asyncio with aioboto3: Rejected - Adds complexity and dependency
- More workers (10-20): Rejected - Risk of S3 throttling

**IAM Permissions Required**:
```json
{
  "Effect": "Allow",
  "Action": [
    "s3:PutObject",
    "s3:GetObject",
    "s3:ListBucket",
    "s3:HeadBucket"
  ],
  "Resource": [
    "arn:aws:s3:::literacy-framework-development-961105418118-eu-central-1",
    "arn:aws:s3:::literacy-framework-development-961105418118-eu-central-1/*"
  ]
}
```

**Testing**:
- Unit tests with `moto` for S3 mocking
- Integration tests with real S3 bucket
- Validation script for S3 bucket access

**References**:
- [boto3 S3 put_object](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.put_object)
- [S3 Error Codes](https://docs.aws.amazon.com/AmazonS3/latest/API/ErrorResponses.html)
- [boto3 Thread Safety](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/resources.html#multithreading-and-multiprocessing)

---

## Next Steps

Phase 1 artifacts:
1. **data-model.md**: Define Assessment, Question, UserProfile entities based on Pydantic models above + S3 URI fields
2. **contracts/**: Document assessment generation API (if exposing as service)
3. **quickstart.md**: Setup instructions including AWS credentials, KB creation, S3 bucket configuration, environment configuration
4. **Update agent context**: Add boto3, Bedrock KB patterns, S3 upload patterns to Claude context
