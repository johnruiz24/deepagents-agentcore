# Tools and Subagents Reference

Comprehensive reference documentation for all tools and subagents in the Literacy Assessment Agent system.

## Table of Contents

- [Overview](#overview)
- [Subagents](#subagents)
  - [Main Orchestrator Agent](#main-orchestrator-agent)
  - [Level 1 Subagent](#level-1-subagent-foundational)
  - [Level 2 Subagent](#level-2-subagent-intermediate)
  - [Level 3 Subagent](#level-3-subagent-advanced)
  - [Level 4 Subagent](#level-4-subagent-expert)
- [Tools](#tools)
  - [Knowledge Base Query Tools](#knowledge-base-query-tools)
  - [S3 Upload Tool](#s3-upload-tool)
- [Background-Aware Question Generation](#background-aware-question-generation)
- [Assessment Structure](#assessment-structure)

## Overview

The Literacy Assessment Agent uses a multi-agent architecture where a main orchestrator delegates to 4 specialized subagents. Each subagent has access to specific tools for querying knowledge bases and uploading results to S3.

### Agent Hierarchy

```
Main Orchestrator Agent
├── Level 1 Subagent (Foundational)
│   ├── Tool: query_level_1_kb
│   └── Tool: upload_assessment_to_s3
├── Level 2 Subagent (Intermediate)
│   ├── Tool: query_level_2_kb
│   └── Tool: upload_assessment_to_s3
├── Level 3 Subagent (Advanced)
│   ├── Tool: query_level_3_kb
│   └── Tool: upload_assessment_to_s3
└── Level 4 Subagent (Expert)
    ├── Tool: query_level_4_kb
    └── Tool: upload_assessment_to_s3
```

## Subagents

### Main Orchestrator Agent

**File**: `examples/literacy_assessment/src/agent.py` (lines 574-671)
**Model**: Claude Sonnet 4.5 (`eu.anthropic.claude-sonnet-4-5-20250929-v1:0`)

#### Responsibilities

1. **Request Parsing**: Extract target literacy levels and user background
2. **Delegation**: Invoke appropriate level-specific subagents
3. **Parallel Execution**: Handle multi-level requests concurrently
4. **Result Aggregation**: Collect and format subagent responses

#### System Prompt (Excerpt)

```
You are the Literacy Assessment Orchestrator for a multi-level literacy evaluation system.

Your role is to:
1. Parse user requests to identify target level(s) and user background
2. Delegate assessment generation to appropriate level-specific subagents
3. Collect and format results

Available Subagents:
- level-1-assessment-agent: Generates Level 1 (foundational) assessments
- level-2-assessment-agent: Generates Level 2 (intermediate) assessments
- level-3-assessment-agent: Generates Level 3 (advanced) assessments
- level-4-assessment-agent: Generates Level 4 (expert) assessments

REQUEST PATTERNS:

Single-Level Request:
User: "Generate a Level 2 assessment for someone with 3 years of software development experience"

Your response:
1. Parse: level=2, background="3 years of software development experience"
2. Call: task("Generate Level 2 assessment for user with background: ...", "level-2-assessment-agent")
3. Wait for subagent result
4. Return formatted assessment to user

Multi-Level Request (IMPORTANT - USE PARALLEL EXECUTION):
User: "Generate assessments for Levels 1, 2, and 3 for a data analyst with 2 years experience"

Your response:
1. Parse: levels=[1,2,3], background="data analyst with 2 years experience"
2. Call ALL THREE subagents IN PARALLEL (in the SAME response):
   task("Generate Level 1 assessment for data analyst...", "level-1-assessment-agent")
   task("Generate Level 2 assessment for data analyst...", "level-2-assessment-agent")
   task("Generate Level 3 assessment for data analyst...", "level-3-assessment-agent")
3. Wait for all subagent results
4. Aggregate and return all assessments with performance summary
```

#### Key Features

- **Parallel Execution**: Critical for multi-level requests (60%+ speedup vs sequential)
- **Performance Tracking**: Calculates generation time and speedup metrics
- **Validation**: Ensures subagents return complete assessments
- **Flexible Input**: Handles various request formats naturally

---

### Level 1 Subagent (Foundational)

**File**: `examples/literacy_assessment/src/agent.py` (lines 35-161)
**Name**: `level-1-assessment-agent`
**Knowledge Base**: QADZTSAPWX (Level 1 content)
**Difficulty**: Beginner

#### Configuration

```python
{
    "name": "level-1-assessment-agent",
    "description": "Generates Level 1 (foundational) literacy assessments. Use ONLY for Level 1 requests.",
    "system_prompt": "You are a Level 1 literacy assessment specialist focused on FOUNDATIONAL content...",
    "tools": [query_level_1_kb, upload_assessment_to_s3]
}
```

#### Assessment Requirements

- **7 multiple choice questions** (4 options each, A-D, mark correct answer)
- **3 open-ended questions** (with 3-5 key points for rubric)
- **Minimum 5 different modules** covered across all 10 questions
- **Background-calibrated** difficulty (adjust DOMAIN/CONTEXT, not technical depth)

#### Background-Aware Generation

The subagent tailors questions to the user's professional domain:

**For IT/Data Science backgrounds:**
- Use technical scenarios: APIs, system performance, data pipelines, infrastructure
- Examples: "prompt engineering for log analysis", "AI tool selection for development workflows"
- Focus: Practical tool usage in technical contexts

**For Finance/Business backgrounds:**
- Use business scenarios: ROI analysis, budgeting, forecasting, compliance, reporting
- Examples: "AI for financial report generation", "prompt engineering for budget analysis"
- Focus: Business value, decision support, efficiency gains

**For HR/People backgrounds:**
- Use people scenarios: recruitment, training, performance reviews, employee communications
- Examples: "AI for job description creation", "candidate screening automation"
- Focus: People processes, communication, fairness, privacy

**For Marketing/Creative backgrounds:**
- Use content scenarios: copywriting, campaign creation, personalization, brand consistency
- Examples: "AI for email campaign generation", "content personalization at scale"
- Focus: Creativity, brand voice, customer engagement

**For Operations/General backgrounds:**
- Use process scenarios: workflow automation, task management, documentation, customer service
- Examples: "AI for process documentation", "automated response generation"
- Focus: Efficiency, standardization, quality

#### Question Quality Standards (Level 1)

1. **Randomize context** across different modules from the KB
2. **Add realistic constraints**:
   - "...with a 2-hour deadline"
   - "...for a non-technical audience"
   - "...while maintaining data privacy"
3. **All MC options must seem plausible** - avoid obviously wrong answers
4. **Force trade-off decisions** - each option should have pros/cons

#### Execution Process

```
1. Query KB multiple times for diverse content
   → Target 6+ modules to ensure 5+ coverage after selection
   → Consider user's domain when selecting relevant content

2. Generate questions that:
   → Cover diverse topics within Level 1 curriculum
   → Are appropriate for foundational/beginner learners
   → Use scenarios from user's DOMAIN (not technical depth!)
   → Match user's experience level
   → Are unique (no duplicates)
   → Have all plausible options (60-80% find 2+ options reasonable)

3. Format as JSON with complete structure

4. Upload to S3 (both JSON and Markdown formats)

5. Return S3 URIs to orchestrator
```

#### Output Format

```json
{
  "level": 1,
  "multiple_choice_questions": [
    {
      "type": "multiple_choice",
      "question_text": "Question text here?",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_answer_index": 0,
      "explanation": "Why this answer is correct",
      "module_source": "Module name",
      "difficulty": "beginner",
      "kb_document_sources": [
        {"filename": "L1-M1_Module_Name.pdf", "s3_uri": "s3://bucket/path/..."}
      ]
    }
    // ... 6 more MC questions
  ],
  "open_ended_questions": [
    {
      "type": "open_ended",
      "question_text": "Question text here?",
      "expected_key_points": ["Point 1", "Point 2", "Point 3"],
      "evaluation_criteria": "How to evaluate responses",
      "module_source": "Module name",
      "difficulty": "beginner",
      "kb_document_sources": [
        {"filename": "L1-M1_Module_Name.pdf", "s3_uri": "s3://bucket/path/..."}
      ]
    }
    // ... 2 more OE questions
  ],
  "user_background": "<original background text>",
  "modules_covered": ["Module 1", "Module 2", "Module 3", "Module 4", "Module 5", "..."]
}
```

---

### Level 2 Subagent (Intermediate)

**File**: `examples/literacy_assessment/src/agent.py` (lines 162-292)
**Name**: `level-2-assessment-agent`
**Knowledge Base**: KGGD2PTQ2N (Level 2 content)
**Difficulty**: Intermediate

#### Configuration

```python
{
    "name": "level-2-assessment-agent",
    "description": "Generates Level 2 (intermediate) literacy assessments. Use ONLY for Level 2 requests.",
    "system_prompt": "You are a Level 2 literacy assessment specialist focused on INTERMEDIATE content...",
    "tools": [query_level_2_kb, upload_assessment_to_s3]
}
```

#### Assessment Requirements

Same structure as Level 1 (7 MC + 3 OE, 5+ modules), but with **intermediate complexity**:

- Advanced prompting techniques (Chain-of-thought, role assignment, iterative refinement)
- Tool coordination and multi-tool workflows
- API integration basics and error handling
- Process optimization and workflow design

#### Background-Aware Generation (Intermediate Complexity)

**For IT/Data Science backgrounds:**
- Advanced prompting: Chain-of-thought, role assignment, iterative refinement
- Tool coordination: Multi-tool workflows, API integration basics, error handling
- Examples: "Designing a prompt chain for data validation", "Coordinating multiple AI tools for pipeline automation"
- Focus: Practical implementation, workflow optimization, technical troubleshooting

**For Finance/Business backgrounds:**
- Strategic prompting: Complex analysis, scenario modeling, multi-factor decisions
- Process optimization: Automated reporting, predictive analytics, compliance automation
- Examples: "AI-driven financial forecasting workflow", "Automating quarterly reporting with multiple data sources"
- Focus: Business impact, ROI optimization, strategic decision support

**For HR/People backgrounds:**
- Advanced people analytics: Candidate evaluation, performance patterns, sentiment analysis
- Complex workflows: Multi-stage recruitment, personalized training paths, engagement tracking
- Examples: "AI-powered candidate screening with fairness checks", "Personalized learning path generation"
- Focus: Fairness, privacy, personalization, compliance

**For Marketing/Creative backgrounds:**
- Advanced content: Multi-channel campaigns, A/B testing, brand consistency across tools
- Personalization: Segment-specific messaging, dynamic content, iterative refinement
- Examples: "Multi-channel campaign generation with brand guidelines", "Personalized email sequences at scale"
- Focus: Creativity + scale, brand consistency, conversion optimization

**For Operations/General backgrounds:**
- Advanced automation: Complex workflows, exception handling, quality assurance
- Process design: Multi-step automations, human-in-the-loop, error recovery
- Examples: "Multi-stage approval workflow automation", "Automated quality control with escalation"
- Focus: Reliability, scalability, user experience

#### Question Quality Standards (Level 2)

1. **Add realistic constraints**:
   - "...handling 50+ cases per day"
   - "...with 95% accuracy requirement"
   - "...across 5 different departments"
   - "...under regulatory compliance"
2. **All options should be sophisticated approaches** - no obviously wrong answers
3. **Force nuanced trade-offs** - timing vs quality, automation vs control, speed vs accuracy

---

### Level 3 Subagent (Advanced)

**File**: `examples/literacy_assessment/src/agent.py` (lines 294-429)
**Name**: `level-3-assessment-agent`
**Knowledge Base**: 7MGFSODDVI (Level 3 content)
**Difficulty**: Advanced

#### Configuration

```python
{
    "name": "level-3-assessment-agent",
    "description": "Generates Level 3 (advanced) literacy assessments. Use ONLY for Level 3 requests.",
    "system_prompt": "You are a Level 3 literacy assessment specialist focused on ADVANCED content...",
    "tools": [query_level_3_kb, upload_assessment_to_s3]
}
```

#### Assessment Requirements

Same structure (7 MC + 3 OE, 5+ modules), but with **advanced complexity**:

- System design and architecture
- Agent orchestration and multi-agent systems
- Production deployment considerations
- Infrastructure and reliability engineering

#### Background-Aware Generation (Advanced Complexity)

**For IT/Data Science backgrounds:**
- System design: Agent architecture, tool integration, API orchestration
- Infrastructure: Production deployment, monitoring, scaling, error recovery
- Examples: "Designing a multi-agent system for real-time data processing", "Production-ready agent deployment with failover"
- Focus: System architecture, reliability, performance, technical trade-offs

**For Finance/Business backgrounds:**
- Strategic AI implementation: ROI modeling, risk assessment, governance frameworks
- Business transformation: Change management, stakeholder buy-in, success metrics
- Examples: "Building business case for AI-driven forecasting platform", "Governance framework for financial AI agents"
- Focus: Strategic value, risk management, organizational impact, compliance

**For HR/People backgrounds:**
- Strategic workforce planning: AI ethics, bias detection, fairness frameworks
- Organizational design: AI-augmented teams, role evolution, training strategy
- Examples: "Designing fair AI-powered hiring process with audit trails", "Organizational change plan for AI adoption"
- Focus: Ethics, fairness, organizational change, cultural transformation

**For Marketing/Creative backgrounds:**
- Strategic content operations: Multi-agent campaigns, brand governance, quality control
- Market positioning: Competitive differentiation, brand AI strategy, measurement frameworks
- Examples: "Multi-agent content generation with brand consistency controls", "Strategic AI adoption for competitive advantage"
- Focus: Strategic creativity, brand protection, market impact, scale with quality

**For Operations/General backgrounds:**
- Process transformation: Enterprise-wide automation, change management, stakeholder alignment
- Strategic operations: Human-in-the-loop design, escalation frameworks, quality assurance
- Examples: "Designing enterprise-wide process automation with governance", "Change management strategy for AI-driven operations"
- Focus: Organizational transformation, stakeholder management, sustainable change

#### Question Quality Standards (Level 3)

1. **Complex realistic constraints**:
   - "...with 99.9% uptime requirement"
   - "...across 20 countries with different regulations"
   - "...during organizational restructuring"
   - "...with $500K budget and 6-month timeline"
2. **All options are sophisticated architectures/strategies** - require deep understanding
3. **Force strategic trade-offs** - short-term vs long-term, cost vs capability, risk vs innovation

#### Open-Ended Evaluation Criteria

- Must demonstrate understanding of multiple factors
- Should mention trade-offs or risks
- Expect 3-4 specific points covering different dimensions

---

### Level 4 Subagent (Expert)

**File**: `examples/literacy_assessment/src/agent.py` (lines 431-569)
**Name**: `level-4-assessment-agent`
**Knowledge Base**: CHYWO1H6OM (Level 4 content)
**Difficulty**: Expert

#### Configuration

```python
{
    "name": "level-4-assessment-agent",
    "description": "Generates Level 4 (expert) literacy assessments. Use ONLY for Level 4 requests.",
    "system_prompt": "You are a Level 4 literacy assessment specialist focused on EXPERT content...",
    "tools": [query_level_4_kb, upload_assessment_to_s3]
}
```

#### Assessment Requirements

Same structure (7 MC + 3 OE, 5+ modules), but with **expert/leadership complexity**:

- Multi-agent orchestration at enterprise scale
- Executive strategy and board-level decision making
- Organizational transformation and cultural change
- Enterprise risk management and governance

#### Background-Aware Generation (Expert/Leadership Complexity)

**For IT/Data Science backgrounds:**
- Multi-agent orchestration: Complex system coordination, production scalability, incident management
- Enterprise architecture: Platform strategy, technical governance, vendor evaluation
- Examples: "Architecting multi-agent system for 10M daily transactions", "Technical governance framework for AI platform"
- Focus: Enterprise scale, reliability engineering, strategic technical decisions, team leadership

**For Finance/Business backgrounds:**
- Enterprise AI strategy: Board-level business cases, competitive positioning, market transformation
- Organizational transformation: C-level buy-in, cultural change, success measurement, risk governance
- Examples: "Building C-level case for $5M AI investment with 3-year ROI", "Enterprise risk framework for AI-driven finance"
- Focus: Executive strategy, competitive advantage, enterprise risk, board communication

**For HR/People backgrounds:**
- Organizational transformation: Cultural change at scale, workforce planning, AI ethics leadership
- Strategic HR innovation: AI adoption across 1000+ employees, role evolution, future of work
- Examples: "Leading AI transformation for 5000-person organization", "Strategic workforce planning for AI-augmented roles"
- Focus: Cultural transformation, executive stakeholder management, ethical leadership, organizational design

**For Marketing/Creative backgrounds:**
- Brand AI strategy: Market positioning, competitive differentiation, brand governance at scale
- Strategic market transformation: Industry-wide innovation, thought leadership, ecosystem development
- Examples: "Positioning brand as AI innovation leader in competitive market", "Multi-agent content platform serving 50M customers"
- Focus: Market leadership, brand transformation, competitive strategy, innovation at scale

**For Operations/General backgrounds:**
- Enterprise transformation: Organization-wide process redesign, multi-stakeholder alignment, change at scale
- Strategic operations leadership: Platform thinking, ecosystem coordination, long-term sustainability
- Examples: "Leading AI transformation across 20 business units", "Building AI operations platform for enterprise scale"
- Focus: Enterprise change management, platform strategy, stakeholder orchestration, sustainable transformation

#### Question Quality Standards (Level 4)

1. **Enterprise-scale constraints**:
   - "...serving 10M+ customers across 50 countries"
   - "...with $5M budget and C-level accountability"
   - "...during market disruption and competitive pressure"
   - "...with regulatory scrutiny and public visibility"
2. **All options require deep strategic thinking** - board-level decisions, no simple answers
3. **Force complex organizational trade-offs** - innovation vs stability, speed vs governance, centralization vs autonomy

#### Open-Ended Evaluation Criteria (Expert Level)

- Must demonstrate mastery across multiple dimensions (technical, business, organizational, risk)
- Should explicitly mention trade-offs and mitigation strategies
- Expect 4-5 specific points covering strategic, tactical, and risk dimensions
- Should show systems thinking and long-term consequences

---

## Tools

### Knowledge Base Query Tools

**File**: `examples/literacy_assessment/src/kb_tools.py`

#### Overview

Four identical tools (one per level) that query AWS Bedrock Knowledge Bases to retrieve curriculum content.

#### Tool Signature

```python
def query_level_X_kb(query: str, max_results: int = 10) -> dict:
    """
    Query AWS Bedrock Knowledge Base for Level X curriculum content.

    Args:
        query: Natural language query describing desired content
               Example: "advanced prompting techniques", "AI workflow design"
        max_results: Maximum number of results to return (default: 10)

    Returns:
        {
            "status": "success" | "error",
            "results": [
                {
                    "content": "Retrieved text content from KB...",
                    "score": 0.85,  # Relevance score (0-1)
                    "document_source": {
                        "filename": "LX-M1_Module_Name.pdf",
                        "s3_uri": "s3://bucket/path/LX-M1_Module_Name.pdf"
                    }
                },
                ...
            ],
            "result_count": 5,
            "query": "<original query>",
            "kb_id": "KBXXXXXXXXX"
        }

    Error Response:
        {
            "status": "error",
            "error": "Error message describing what went wrong",
            "query": "<original query>",
            "kb_id": "KBXXXXXXXXX"
        }
    """
```

#### Implementation Details

**AWS Integration**:

```python
# Create boto3 client
session = boto3.Session(
    profile_name=AWS_PROFILE,  # or None for IAM role
    region_name=AWS_REGION
)
client = session.client('bedrock-agent-runtime')

# Query knowledge base
response = client.retrieve(
    knowledgeBaseId=KB_ID,
    retrievalQuery={'text': query},
    retrievalConfiguration={
        'vectorSearchConfiguration': {
            'numberOfResults': max_results
        }
    }
)

# Parse results
results = []
for item in response.get('retrievalResults', []):
    results.append({
        'content': item['content']['text'],
        'score': item['score'],
        'document_source': {
            'filename': item['location']['s3Location']['uri'].split('/')[-1],
            's3_uri': item['location']['s3Location']['uri']
        }
    })
```

**IAM Permissions Required**:

- `bedrock:Retrieve` - Query the knowledge base
- `bedrock:RetrieveAndGenerate` - Optional, for RAG operations

**Error Handling**:

```python
try:
    response = client.retrieve(...)
    return {"status": "success", "results": [...]}
except ClientError as e:
    error_code = e.response['Error']['Code']
    if error_code == 'ResourceNotFoundException':
        return {"status": "error", "error": "Knowledge base not found"}
    elif error_code == 'ValidationException':
        return {"status": "error", "error": "Invalid query parameters"}
    elif error_code == 'ThrottlingException':
        return {"status": "error", "error": "Rate limit exceeded"}
    else:
        return {"status": "error", "error": str(e)}
```

#### Usage Example

```python
# Subagent queries KB for content
result = query_level_2_kb("advanced prompting techniques", max_results=10)

if result["status"] == "success":
    for item in result["results"]:
        content = item["content"]
        relevance = item["score"]
        source = item["document_source"]["filename"]

        # Use content to generate questions
        # Track source for traceability
```

#### Best Practices

1. **Multiple Queries**: Query KB multiple times with different search terms to ensure diverse content
   ```python
   # Good: Diverse queries
   query_level_2_kb("advanced prompting techniques")
   query_level_2_kb("AI workflow design patterns")
   query_level_2_kb("tool orchestration strategies")

   # Bad: Single query
   query_level_2_kb("level 2 content")
   ```

2. **Relevance Filtering**: Use score to filter low-quality results
   ```python
   high_quality_results = [
       item for item in result["results"]
       if item["score"] >= 0.7  # Only use highly relevant content
   ]
   ```

3. **Source Tracking**: Always include document sources in questions
   ```python
   question = {
       "question_text": "...",
       "kb_document_sources": [
           item["document_source"] for item in used_results
       ]
   }
   ```

#### Knowledge Base IDs

| Level | KB ID | Content Description |
|-------|-------|---------------------|
| Level 1 | QADZTSAPWX | Foundational literacy curriculum (L1-M1 through L1-M7) |
| Level 2 | KGGD2PTQ2N | Intermediate literacy curriculum (L2-M1 through L2-M7) |
| Level 3 | 7MGFSODDVI | Advanced literacy curriculum (L3-M1 through L3-M7) |
| Level 4 | CHYWO1H6OM | Expert literacy curriculum (L4-M1 through L4-M7) |

---

### S3 Upload Tool

**File**: `examples/literacy_assessment/src/s3_uploader.py`

#### Tool Function

```python
def upload_assessment_to_s3(assessment_json: str, level: int) -> dict:
    """
    Upload assessment to S3 in both JSON and markdown formats.

    Args:
        assessment_json: Complete assessment as JSON string (from json.dumps())
        level: Literacy level (1-4)

    Returns:
        Success Response:
        {
            "status": "success",
            "s3_uri_json": "s3://bucket/path/level_2_20251106_034423.json",
            "s3_uri_markdown": "s3://bucket/path/level_2_20251106_034423.md",
            "level": 2,
            "timestamp": "2025-11-06T03:44:22.918557",
            "bucket": "literacy-framework-development-961105418118-eu-central-1",
            "prefix": "learning_path/assessments"
        }

        Error Response:
        {
            "status": "error",
            "error": "Error message describing what went wrong",
            "level": 2
        }
    """
```

#### Implementation Details

**S3UploaderClient** (Lines 71-331):

```python
class S3UploaderClient:
    def __init__(self, bucket_name=None, prefix=None, region=None, profile=None):
        self.bucket_name = bucket_name or LiteracyAssessmentConfig.S3_BUCKET_NAME
        self.prefix = prefix or LiteracyAssessmentConfig.S3_PREFIX
        self.region = region or LiteracyAssessmentConfig.S3_REGION
        self.profile = profile or LiteracyAssessmentConfig.AWS_PROFILE

        # Create boto3 S3 client
        if self.profile:
            session = boto3.Session(profile_name=self.profile, region_name=self.region)
        else:
            session = boto3.Session(region_name=self.region)
        self.s3_client = session.client('s3')
```

**Filename Generation**:

```python
def _generate_s3_key(self, level: int, timestamp: datetime, file_format: str) -> str:
    """
    Generate S3 key for assessment file.

    Returns: "learning_path/assessments/level_{X}/level_{X}_YYYYMMDD_HHMMSS.{ext}"
    """
    ts_str = timestamp.strftime('%Y%m%d_%H%M%S')
    ext = 'json' if file_format == 'json' else 'md'
    return f"{self.prefix}/level_{level}/level_{level}_{ts_str}.{ext}"
```

**Content Preparation**:

```python
def _prepare_assessment_content(self, assessment: Assessment, file_format: str):
    """
    Prepare assessment content and content type for upload.
    """
    if file_format == 'json':
        # Pydantic model → JSON string
        content = assessment.model_dump_json(indent=2)
        content_type = 'application/json'
    else:  # markdown
        # Pydantic model → Markdown string
        content = format_assessment_as_markdown(assessment)
        content_type = 'text/markdown'

    return content, content_type
```

**Upload with Retry Logic**:

```python
@retry_with_backoff(max_attempts=3, backoff_seconds=[1, 2, 4])
def _upload_with_retry(self, key: str, body: str, content_type: str, metadata: dict):
    """
    Upload to S3 with exponential backoff for transient errors.
    """
    return self.s3_client.put_object(
        Bucket=self.bucket_name,
        Key=key,
        Body=body.encode('utf-8'),
        ContentType=content_type,
        Metadata=metadata
    )
```

**Error Handling**:

- **Permanent Errors** (no retry):
  - `NoSuchBucket` - Bucket doesn't exist
  - `AccessDenied` - IAM permissions insufficient
  - `InvalidBucketName` - Malformed bucket name

- **Transient Errors** (retry with backoff):
  - `Throttling` - Rate limit exceeded
  - `ServiceUnavailable` - AWS service issue
  - `RequestTimeout` - Network timeout
  - `RequestTimeTooSkewed` - Clock sync issue

#### Metadata

Each uploaded file includes metadata:

```python
metadata = {
    'generation-time': '2025-11-06T03:44:22.918557',
    'user-background-hash': '123456789',  # Hash of user background
    'modules-count': '7',
    'literacy-level': '2',
    'question-count': '10',
    'format': 'json' or 'markdown'
}
```

#### IAM Permissions Required

- `s3:PutObject` - Write assessment files
- `s3:PutObjectAcl` - Set object permissions
- `s3:ListBucket` - Verify bucket exists

#### Usage Example

```python
# Subagent generates assessment
assessment_dict = {
    "level": 2,
    "multiple_choice_questions": [...],
    "open_ended_questions": [...],
    "user_background": "...",
    "modules_covered": [...]
}

# Convert to JSON string
assessment_json = json.dumps(assessment_dict)

# Upload to S3 (both formats automatically)
result = upload_assessment_to_s3(assessment_json, level=2)

if result["status"] == "success":
    json_uri = result["s3_uri_json"]
    markdown_uri = result["s3_uri_markdown"]
    # Return URIs to user
```

#### S3 Bucket Structure

```
s3://literacy-framework-development-961105418118-eu-central-1/
└── learning_path/
    └── assessments/
        ├── level_1/
        │   ├── level_1_20251106_034423.json
        │   └── level_1_20251106_034423.md
        ├── level_2/
        │   ├── level_2_20251106_034423.json
        │   └── level_2_20251106_034423.md
        ├── level_3/
        │   ├── level_3_20251106_034423.json
        │   └── level_3_20251106_034423.md
        └── level_4/
            ├── level_4_20251106_034423.json
            └── level_4_20251106_034423.md
```

---

## Background-Aware Question Generation

### Overview

All subagents implement background-aware question generation, which tailors the **domain and context** of questions to match the user's professional background while maintaining the appropriate **technical difficulty** for the literacy level.

### Key Principle

**Adjust DOMAIN/CONTEXT, not TECHNICAL DEPTH**

- ❌ **Wrong**: Change technical complexity based on background
- ✅ **Right**: Change domain scenarios while keeping level-appropriate complexity

### Implementation

#### Step 1: Parse User Background

```python
# Example backgrounds:
"software engineer with 5 years of experience"
"financial analyst at a Fortune 500 company"
"HR manager with 10 years in talent acquisition"
"marketing director for a B2B SaaS startup"
"operations manager in manufacturing"
```

Extract:
- **Domain**: IT, Finance, HR, Marketing, Operations, etc.
- **Experience Level**: Beginner, intermediate, advanced, expert
- **Industry Context**: Specific sector or company type

#### Step 2: Select Domain-Appropriate Scenarios

**Level 2 Example** (Intermediate Complexity):

**IT/Data Science Background**:
```
Question: Your team is implementing an AI-powered code review assistant
that must analyze pull requests across 5 different programming languages.
The system needs to identify bugs, suggest optimizations, and ensure
style consistency. Which orchestration pattern would be most appropriate?

[4 sophisticated technical options requiring understanding of
multi-agent systems, all plausible for experienced engineers]
```

**Finance Background** (Same Level 2 Complexity):
```
Question: Your finance team needs to automate quarterly reporting across
5 business units with different accounting systems. The AI system must
consolidate data, flag anomalies, and generate executive summaries.
Which workflow orchestration approach would be most effective?

[4 sophisticated business options requiring understanding of
multi-agent systems, all plausible for experienced finance professionals]
```

Both questions test the same **literacy concept** (workflow orchestration) at the same **complexity level** (intermediate), but use **different domain contexts**.

### Domain-Specific Vocabulary

Each domain has preferred terminology:

| Concept | IT/Data Science | Finance | HR | Marketing | Operations |
|---------|----------------|---------|-----|-----------|-----------|
| Process | Pipeline, workflow | Process, procedure | Program, initiative | Campaign, funnel | Workflow, system |
| Success | Performance, uptime | ROI, profit | Engagement, retention | Conversion, reach | Efficiency, throughput |
| Error | Bug, exception | Discrepancy, error | Issue, concern | Misalignment, gap | Defect, deviation |
| People | Users, developers | Stakeholders, analysts | Employees, candidates | Customers, audience | Staff, operators |
| Output | Data, results | Reports, insights | Feedback, outcomes | Content, assets | Products, deliverables |

### Complexity Calibration by Level

**Level 1** (Foundational):
- Simple scenarios with clear constraints
- Single-system operations
- Basic tool usage
- Individual contributor focus

**Level 2** (Intermediate):
- Multi-step workflows
- Coordination across 2-3 systems
- Some technical trade-offs
- Team collaboration scenarios

**Level 3** (Advanced):
- Complex architectures
- Enterprise-scale considerations
- Strategic trade-offs
- Cross-functional impact

**Level 4** (Expert):
- Organizational transformation
- C-level decision making
- Market-level impact
- Multi-stakeholder alignment

---

## Assessment Structure

### Complete Assessment Object

```json
{
  "assessment_id": "37cdef8f-b639-4c73-924d-011d60740e44",
  "level": 2,
  "generated_at": "2025-11-06T03:44:22.918557",
  "user_background": "software engineer with 5 years of experience in full-stack development",
  "multiple_choice_questions": [
    {
      "type": "multiple_choice",
      "question_id": "mc_001",
      "question_text": "Your team is implementing...",
      "options": [
        "A) Sequential pipeline approach...",
        "B) Orchestrator-based system... (CORRECT)",
        "C) Single large multi-modal LLM...",
        "D) RAG-based system..."
      ],
      "correct_answer_index": 1,
      "explanation": "The orchestrator pattern (Option B) is optimal because...",
      "module_source": "L2-M7: Using Multiple AI Tools in Tandem",
      "difficulty": "intermediate",
      "kb_document_sources": [
        {
          "filename": "L2-M7_Tool_Orchestration.pdf",
          "s3_uri": "s3://bucket/path/L2-M7_Tool_Orchestration.pdf"
        }
      ]
    }
    // ... 6 more MC questions
  ],
  "open_ended_questions": [
    {
      "type": "open_ended",
      "question_id": "oe_001",
      "question_text": "Describe how you would design...",
      "expected_key_points": [
        "Should mention error handling strategies",
        "Should explain coordination mechanisms",
        "Should discuss trade-offs between approaches"
      ],
      "evaluation_criteria": "Response should demonstrate understanding of multi-agent coordination, mention at least 2 specific challenges, and propose concrete solutions.",
      "module_source": "L2-M7: Using Multiple AI Tools in Tandem",
      "difficulty": "intermediate",
      "kb_document_sources": [
        {
          "filename": "L2-M7_Tool_Orchestration.pdf",
          "s3_uri": "s3://bucket/path/L2-M7_Tool_Orchestration.pdf"
        }
      ]
    }
    // ... 2 more OE questions
  ],
  "modules_covered": [
    "L2-M1: Advanced Prompting - Role, Persona, and Style",
    "L2-M2: Chain-of-Thought & Few-Shot Prompting",
    "L2-M3: Iterative Refinement & Prompt Optimization",
    "L2-M4: Critical Evaluation of AI Outputs",
    "L2-M5: Introduction to AI Workflows",
    "L2-M6: Collaborating with AI - Multi-turn Conversations",
    "L2-M7: Using Multiple AI Tools in Tandem"
  ],
  "metadata": {
    "generation_time_seconds": 42.5,
    "kb_queries_count": 3,
    "total_questions": 10,
    "difficulty_distribution": {
      "beginner": 0,
      "intermediate": 10,
      "advanced": 0
    }
  }
}
```

### Pydantic Models

**File**: `examples/literacy_assessment/src/models.py`

```python
from pydantic import BaseModel, Field
from typing import List, Literal
from datetime import datetime
import uuid

class DocumentSource(BaseModel):
    """Source document from Knowledge Base"""
    filename: str
    s3_uri: str

class MultipleChoiceQuestion(BaseModel):
    """Multiple choice question with 4 options"""
    type: Literal["multiple_choice"] = "multiple_choice"
    question_id: str = Field(default_factory=lambda: f"mc_{uuid.uuid4().hex[:6]}")
    question_text: str
    options: List[str] = Field(..., min_length=4, max_length=4)
    correct_answer_index: int = Field(..., ge=0, le=3)
    explanation: str
    module_source: str
    difficulty: Literal["beginner", "intermediate", "advanced"]
    kb_document_sources: List[DocumentSource]

class OpenEndedQuestion(BaseModel):
    """Open-ended question with evaluation rubric"""
    type: Literal["open_ended"] = "open_ended"
    question_id: str = Field(default_factory=lambda: f"oe_{uuid.uuid4().hex[:6]}")
    question_text: str
    expected_key_points: List[str] = Field(..., min_length=3)
    evaluation_criteria: str
    module_source: str
    difficulty: Literal["beginner", "intermediate", "advanced"]
    kb_document_sources: List[DocumentSource]

class Assessment(BaseModel):
    """Complete literacy assessment"""
    assessment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    level: Literal[1, 2, 3, 4]
    generated_at: datetime = Field(default_factory=datetime.now)
    user_background: str
    multiple_choice_questions: List[MultipleChoiceQuestion] = Field(..., min_length=7, max_length=7)
    open_ended_questions: List[OpenEndedQuestion] = Field(..., min_length=3, max_length=3)
    modules_covered: List[str] = Field(..., min_length=5)
    metadata: dict = Field(default_factory=dict)
```

### Markdown Format

**File**: `examples/literacy_assessment/src/questions.py` (`format_assessment_as_markdown`)

```markdown
# Literacy Level 2 Assessment

**Assessment ID**: 37cdef8f-b639-4c73-924d-011d60740e44
**Generated**: 2025-11-06T03:44:22.918557
**User Background**: software engineer with 5 years of experience in full-stack development
**Modules Covered**: L2-M1: Advanced Prompting, L2-M2: Chain-of-Thought, ... (7 modules)

---

## Multiple Choice Questions (7)

### Question 1 (MC) - Intermediate
**Module**: L2-M7: Using Multiple AI Tools in Tandem

Your team is implementing an AI-powered code review assistant...

A. Sequential pipeline approach...
B. Orchestrator-based system... ✓ CORRECT
C. Single large multi-modal LLM...
D. RAG-based system...

**Explanation**: The orchestrator pattern (Option B) is optimal because...

**Sources**:
- L2-M7_Tool_Orchestration.pdf (s3://bucket/path/...)

---

### Question 2 (MC) - Intermediate
...

---

## Open-Ended Questions (3)

### Question 8 (OE) - Intermediate
**Module**: L2-M7: Using Multiple AI Tools in Tandem

Describe how you would design...

**Expected Key Points**:
- Should mention error handling strategies
- Should explain coordination mechanisms
- Should discuss trade-offs between approaches

**Evaluation Criteria**: Response should demonstrate understanding of...

**Sources**:
- L2-M7_Tool_Orchestration.pdf (s3://bucket/path/...)

---

## Assessment Metrics

- **Total Questions**: 10
- **Multiple Choice**: 7
- **Open-Ended**: 3
- **Modules Covered**: 7
- **Difficulty**: Intermediate
- **Generation Time**: 42.5 seconds
```

---

## Related Documentation

- [Architecture Overview](./ARCHITECTURE.md) - Complete end-to-end system architecture
- [Testing Guide](./TESTING_GUIDE.md) - Testing procedures and best practices
- [Deployment README](../../README.md) - Deployment instructions
- [Historical Documentation](./archive/) - Previous designs and analysis
