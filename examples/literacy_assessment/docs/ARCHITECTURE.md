# Literacy Assessment Agent - Architecture

Complete end-to-end architecture documentation for the Literacy Assessment Agent deployed on AWS Bedrock AgentCore.

## Table of Contents

- [Overview](#overview)
- [End-to-End Request Flow](#end-to-end-request-flow)
- [Component Architecture](#component-architecture)
- [Data Flow](#data-flow)
- [AWS Infrastructure](#aws-infrastructure)
- [Deployment Architecture](#deployment-architecture)

## Overview

The Literacy Assessment Agent is a multi-agent system that generates personalized literacy assessments by orchestrating specialized subagents. The system is deployed as a serverless application on AWS Bedrock AgentCore and integrates with AWS Bedrock Knowledge Bases for content retrieval.

### Key Components

1. **Main Orchestrator Agent** - Routes requests to appropriate level-specific subagents
2. **4 Level-Specific Subagents** - Generate assessments for Levels 1-4
3. **Knowledge Base Tools** - Query AWS Bedrock Knowledge Bases for curriculum content
4. **S3 Upload Tools** - Persist assessments to S3 in JSON and Markdown formats
5. **AWS Bedrock AgentCore** - Serverless runtime environment

## End-to-End Request Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          USER REQUEST                                         │
│  "Generate a Level 2 assessment for a software engineer with 5 years exp"   │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    AWS BEDROCK AGENTCORE ENDPOINT                             │
│  ARN: arn:aws:bedrock-agentcore:eu-central-1:YOUR_AWS_ACCOUNT_ID:runtime/...       │
│  Protocol: HTTP | Network: PUBLIC | Region: eu-central-1                     │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          DOCKER CONTAINER                                     │
│  Image: YOUR_AWS_ACCOUNT_ID.dkr.ecr.eu-central-1.amazonaws.com/                     │
│         bedrock-agentcore-literacy_assessment                                 │
│  Runtime: Python 3.12 | Platform: linux/arm64                                │
│                                                                               │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                      serve_bedrock.py                                   │ │
│  │  ┌──────────────────────────────────────────────────────────────────┐  │ │
│  │  │           FastAPI Application (Port 8080)                         │  │ │
│  │  │  - POST /invoke → LangGraph agent invocation                     │  │ │
│  │  │  - GET /health → Health check endpoint                           │  │ │
│  │  └──────────────────────────────────────────────────────────────────┘  │ │
│  └────────────────────────────────┬───────────────────────────────────────┘ │
└───────────────────────────────────┼─────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    MAIN ORCHESTRATOR AGENT                                    │
│  File: examples/literacy_assessment/src/agent.py                             │
│  Model: Claude Sonnet 4.5 (eu.anthropic.claude-sonnet-4-5-20250929-v1:0)    │
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  REQUEST PARSING                                                     │   │
│  │  1. Extract target level(s): [1, 2, 3, or 4]                       │   │
│  │  2. Extract user background: "software engineer with 5 years exp"   │   │
│  │  3. Determine execution strategy: Single or Parallel                │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  SUBAGENT DELEGATION (Parallel if multiple levels)                  │   │
│  │  → task("Generate Level 2 assessment...", "level-2-assessment-agent")│  │
│  └─────────────────────────────────────────────────────────────────────┘   │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    LEVEL 2 SUBAGENT                                           │
│  Name: level-2-assessment-agent                                              │
│  File: examples/literacy_assessment/src/agent.py (lines 162-292)             │
│  Model: Claude Sonnet 4.5 (inherited from main agent)                        │
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  TOOLS AVAILABLE                                                     │   │
│  │  - query_level_2_kb: Query Level 2 Knowledge Base                   │   │
│  │  - upload_assessment_to_s3: Upload to S3 (JSON + Markdown)          │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  EXECUTION STEPS                                                     │   │
│  │  1. Parse user background (domain, experience level)                │   │
│  │  2. Query Knowledge Base for Level 2 content (multiple queries)     │   │
│  │  3. Generate 7 multiple choice questions                            │   │
│  │  4. Generate 3 open-ended questions                                 │   │
│  │  5. Validate 5+ modules covered                                     │   │
│  │  6. Format as JSON assessment object                                │   │
│  │  7. Upload to S3 (both JSON and Markdown)                           │   │
│  │  8. Return S3 URIs to orchestrator                                  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└───────┬──────────────────────────────────────────────────────┬──────────────┘
        │                                                       │
        ▼                                                       ▼
┌──────────────────────────────────────┐   ┌──────────────────────────────────┐
│  KNOWLEDGE BASE QUERY                │   │  S3 UPLOAD                        │
│  Tool: query_level_2_kb              │   │  Tool: upload_assessment_to_s3   │
│  File: src/kb_tools.py (lines 82-165)│   │  File: src/s3_uploader.py        │
└───────┬──────────────────────────────┘   └───────┬──────────────────────────┘
        │                                           │
        ▼                                           ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          AWS SERVICES                                         │
│                                                                               │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  AWS BEDROCK KNOWLEDGE BASE (Level 2)                                 │ │
│  │  ID: YOUR_LEVEL_2_KB_ID                                                       │ │
│  │  Region: eu-central-1                                                 │ │
│  │  Content: Intermediate literacy curriculum (L2-M1 through L2-M7)     │ │
│  │                                                                        │ │
│  │  IAM Permission: bedrock:Retrieve                                     │ │
│  │  API: bedrock-agent-runtime:Retrieve                                  │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                               │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  AMAZON S3 BUCKET                                                     │ │
│  │  Name: literacy-framework-development-YOUR_AWS_ACCOUNT_ID-eu-central-1       │ │
│  │  Region: eu-central-1                                                 │ │
│  │  Path: learning_path/assessments/level_2/                            │ │
│  │                                                                        │ │
│  │  Uploads:                                                             │ │
│  │  - level_2_20251106_034423.json  (21KB - Machine readable)           │ │
│  │  - level_2_20251106_034423.md    (19KB - Human readable)             │ │
│  │                                                                        │ │
│  │  IAM Permissions: s3:PutObject, s3:PutObjectAcl, s3:ListBucket       │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                               │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  AWS CLOUDWATCH LOGS                                                  │ │
│  │  Log Group: /aws/bedrock-agentcore/runtimes/literacy_assessment-*    │ │
│  │  - Agent invocation logs                                              │ │
│  │  - Tool execution traces                                              │ │
│  │  - Performance metrics                                                │ │
│  │  - Error details with context                                         │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          RESPONSE TO USER                                     │
│  {                                                                            │
│    "status": "success",                                                       │
│    "s3_uri_json": "s3://.../level_2_20251106_034423.json",                  │
│    "s3_uri_markdown": "s3://.../level_2_20251106_034423.md",                │
│    "level": 2,                                                                │
│    "timestamp": "2025-11-06T03:44:22.918557",                                │
│    "assessment_preview": {                                                    │
│      "multiple_choice_questions": 7,                                          │
│      "open_ended_questions": 3,                                               │
│      "modules_covered": 7                                                     │
│    }                                                                          │
│  }                                                                            │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Component Architecture

### 1. Main Orchestrator Agent

**Location**: `examples/literacy_assessment/src/agent.py` (lines 574-671)

**Responsibilities**:
- Parse user requests to identify target literacy levels
- Parse user background for context
- Delegate to appropriate level-specific subagents
- Handle parallel execution for multi-level requests
- Aggregate and return results

**System Prompt** (MAIN_AGENT_PROMPT):
```
You are the Literacy Assessment Orchestrator for a multi-level literacy evaluation system.

Your role is to:
1. Parse user requests to identify target level(s) and user background
2. Delegate assessment generation to appropriate level-specific subagents
3. Collect and format results
```

**Tools**: None (delegates to subagents)

**Subagents**: 4 level-specific assessment agents

### 2. Level-Specific Subagents

Each subagent is specialized for one literacy level:

| Level | Name | KB ID | Difficulty | Lines |
|-------|------|-------|------------|-------|
| Level 1 | level-1-assessment-agent | YOUR_LEVEL_1_KB_ID | Foundational | 35-161 |
| Level 2 | level-2-assessment-agent | YOUR_LEVEL_2_KB_ID | Intermediate | 162-292 |
| Level 3 | level-3-assessment-agent | YOUR_LEVEL_3_KB_ID | Advanced | 294-429 |
| Level 4 | level-4-assessment-agent | YOUR_LEVEL_4_KB_ID | Expert | 431-569 |

**Common Structure**:
```python
{
    "name": "level-X-assessment-agent",
    "description": "Generates Level X assessments...",
    "system_prompt": "You are a Level X literacy assessment specialist...",
    "tools": [
        query_level_X_kb,      # KB query tool
        upload_assessment_to_s3 # S3 upload tool
    ]
}
```

**Assessment Generation Process** (all levels):
1. Query Knowledge Base multiple times for diverse content
2. Parse user background to identify domain (IT, Finance, HR, Marketing, Operations)
3. Generate 7 multiple choice questions (4 options each, mark correct answer)
4. Generate 3 open-ended questions (with 3-5 key points for rubric)
5. Ensure 5+ different modules covered
6. Calibrate difficulty to user's domain and experience
7. Format as JSON assessment object
8. Upload to S3 (both JSON and Markdown formats)
9. Return S3 URIs

### 3. Knowledge Base Query Tools

**Location**: `examples/literacy_assessment/src/kb_tools.py`

**Tools**:
- `query_level_1_kb(query, max_results=10)` - Lines 19-81
- `query_level_2_kb(query, max_results=10)` - Lines 82-144
- `query_level_3_kb(query, max_results=10)` - Lines 145-207
- `query_level_4_kb(query, max_results=10)` - Lines 208-270

**Implementation**:
```python
def query_level_X_kb(query: str, max_results: int = 10) -> dict:
    """
    Query AWS Bedrock Knowledge Base for Level X content.

    Returns:
        {
            "status": "success",
            "results": [
                {
                    "content": "Retrieved text content...",
                    "score": 0.85,
                    "document_source": {
                        "filename": "LX-M1_Module_Name.pdf",
                        "s3_uri": "s3://bucket/path/..."
                    }
                },
                ...
            ],
            "result_count": 5
        }
    """
```

**AWS Integration**:
- Uses `boto3.client('bedrock-agent-runtime')`
- API: `retrieve()` method
- Requires IAM permission: `bedrock:Retrieve`
- Returns ranked results with relevance scores
- Includes source document metadata for traceability

### 4. S3 Upload Tool

**Location**: `examples/literacy_assessment/src/s3_uploader.py`

**Tool Function**:
```python
def upload_assessment_to_s3(assessment_json: str, level: int) -> dict:
    """
    Upload assessment to S3 in both JSON and markdown formats.

    Args:
        assessment_json: Complete assessment as JSON string
        level: Literacy level (1-4)

    Returns:
        {
            "status": "success",
            "s3_uri_json": "s3://.../level_2_20251106_034423.json",
            "s3_uri_markdown": "s3://.../level_2_20251106_034423.md",
            "level": 2,
            "timestamp": "2025-11-06T03:44:22.918557",
            "bucket": "literacy-framework-development-YOUR_AWS_ACCOUNT_ID-eu-central-1",
            "prefix": "learning_path/assessments"
        }
    """
```

**S3UploaderClient** (lines 71-331):
- Boto3 S3 client with retry logic (exponential backoff)
- Generates timestamped filenames: `level_{X}_YYYYMMDD_HHMMSS.{ext}`
- Uploads both formats with synchronized timestamps
- Sets appropriate Content-Type headers
- Includes metadata: generation time, user background hash, module count
- Handles transient errors (throttling, timeouts) with automatic retry
- Fails fast on permanent errors (access denied, bucket not found)

**Markdown Formatting** (`format_assessment_as_markdown`):
- Located in `src/questions.py`
- Converts Assessment Pydantic model to human-readable markdown
- Includes metadata header, question numbering, answer indicators
- Properly formatted for printing or sharing

## Data Flow

### Request Processing Timeline

```
Time    Component                   Action
────────────────────────────────────────────────────────────────────────
0ms     User                        → Send request to AgentCore endpoint

100ms   AgentCore                   → Route to Docker container
                                      (HTTP POST /invoke)

150ms   serve_bedrock.py            → Deserialize request
                                      Create LangChain message

200ms   Main Orchestrator           → Parse request
                                      Extract: level=2, background="..."

250ms   Main Orchestrator           → Invoke Level 2 subagent
                                      (via task() delegation)

300ms   Level 2 Subagent            → Start assessment generation
                                      Parse user background domain

500ms   Level 2 Subagent            → Query KB (1st query)
        ↓
550ms   AWS Bedrock KB              → Return 10 results for "advanced prompting"
        ↑

800ms   Level 2 Subagent            → Query KB (2nd query)
        ↓
850ms   AWS Bedrock KB              → Return 10 results for "AI workflows"
        ↑

1200ms  Level 2 Subagent            → Query KB (3rd query)
        ↓
1250ms  AWS Bedrock KB              → Return 10 results for "tool orchestration"
        ↑

2000ms  Level 2 Subagent            → Generate 7 MC questions
                                      (uses Claude Sonnet 4.5)

3500ms  Level 2 Subagent            → Generate 3 open-ended questions

4000ms  Level 2 Subagent            → Validate assessment
                                      - 10 questions? ✓
                                      - 5+ modules? ✓
                                      - Document sources? ✓

4100ms  Level 2 Subagent            → Call upload_assessment_to_s3
        ↓                             (assessment_json, level=2)
4150ms  S3 Upload Tool              → Parse JSON to Assessment model
                                      Format as markdown

4200ms  S3 Upload Tool              → Upload JSON to S3
        ↓
4250ms  AWS S3                      → Confirm write (JSON)
        ↑                             level_2_20251106_034423.json

4300ms  S3 Upload Tool              → Upload Markdown to S3
        ↓
4350ms  AWS S3                      → Confirm write (Markdown)
        ↑                             level_2_20251106_034423.md

4400ms  Level 2 Subagent            → Return S3 URIs to orchestrator
        ↑

4500ms  Main Orchestrator           → Format response for user

4600ms  serve_bedrock.py            → Serialize response
                                      Return HTTP 200

4700ms  User                        ← Receive response with S3 URIs
```

### Data Transformations

```
User Request (String)
    ↓
Orchestrator Parsing
    ↓
Subagent Task (Dict)
    {
        "description": "Generate Level 2 assessment...",
        "subagent_type": "level-2-assessment-agent"
    }
    ↓
KB Query Results (List[Dict])
    [
        {
            "content": "Text from L2-M1...",
            "score": 0.85,
            "document_source": {"filename": "...", "s3_uri": "..."}
        },
        ...
    ]
    ↓
Assessment Generation (Pydantic Model → JSON)
    Assessment(
        level=2,
        multiple_choice_questions=[...],
        open_ended_questions=[...],
        user_background="...",
        modules_covered=[...]
    )
    ↓
    JSON String
    {
        "level": 2,
        "multiple_choice_questions": [...],
        "open_ended_questions": [...],
        ...
    }
    ↓
    ┌─────────────────┬─────────────────┐
    │ JSON Format     │ Markdown Format │
    │ (machine)       │ (human)         │
    └─────────────────┴─────────────────┘
           ↓                   ↓
    ┌─────────────────┬─────────────────┐
    │ S3 Upload       │ S3 Upload       │
    │ level_2_...json │ level_2_...md   │
    └─────────────────┴─────────────────┘
           ↓                   ↓
    ┌─────────────────────────────────┐
    │     Response to User            │
    │ {                               │
    │   "s3_uri_json": "s3://...",   │
    │   "s3_uri_markdown": "s3://..." │
    │ }                               │
    └─────────────────────────────────┘
```

## AWS Infrastructure

### IAM Role

**Role Name**: `agentcore-literacy_assessment-role-0511`

**Trust Policy**:
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {
      "Service": "bedrock-agentcore.amazonaws.com"
    },
    "Action": "sts:AssumeRole"
  }]
}
```

**Permissions** (Inline Policy):

**Bedrock**:
- `bedrock:InvokeModel` - Invoke Claude Sonnet 4.5
- `bedrock:InvokeModelWithResponseStream` - Streaming responses
- `bedrock:Retrieve` - Query Knowledge Bases
- `bedrock:RetrieveAndGenerate` - RAG operations

**S3**:
- `s3:GetObject` - Read knowledge base documents
- `s3:ListBucket` - List bucket contents
- `s3:PutObject` - Write assessments
- `s3:PutObjectAcl` - Set object permissions

**CloudWatch Logs**:
- `logs:CreateLogGroup` - Create log groups
- `logs:CreateLogStream` - Create log streams
- `logs:PutLogEvents` - Write logs
- `logs:DescribeLogGroups` - Query logs
- `logs:DescribeLogStreams` - Query streams

**ECR**:
- `ecr:BatchGetImage` - Pull container images
- `ecr:GetDownloadUrlForLayer` - Download layers
- `ecr:GetAuthorizationToken` - Authenticate

**Monitoring**:
- `xray:PutTraceSegments` - X-Ray tracing
- `cloudwatch:PutMetricData` - Custom metrics

**AgentCore**:
- `bedrock-agentcore:GetWorkloadAccessToken*` - Workload identity

### Network Configuration

**Mode**: PUBLIC
**Protocol**: HTTP
**Port**: 8080
**Host**: `0.0.0.0` (inside container)

**Security**:
- TLS termination at AgentCore layer
- IAM-based authentication
- VPC not required (public endpoint)

### Container Configuration

**Base Image**: `public.ecr.aws/docker/library/python:3.12-slim`
**Platform**: `linux/arm64`
**User**: `bedrock_agentcore` (UID 1000, non-root)

**Environment Variables**:
- `AWS_REGION=eu-central-1`
- `AWS_DEFAULT_REGION=eu-central-1`
- `DOCKER_CONTAINER=1` (flag for host binding logic)

**Installed Packages**:
- Python dependencies from `requirements.txt`
- `aws-opentelemetry-distro>=0.10.1` (observability)

**Exposed Ports**:
- `8080` - Main application (FastAPI)
- `8000` - Alternative port (not currently used)

**Entry Point**:
```dockerfile
CMD ["opentelemetry-instrument", "python", "-m", "serve_bedrock"]
```

## Deployment Architecture

### Build and Deploy Process

```
Local Development Machine
    │
    │ 1. python deploy.py
    ↓
┌─────────────────────────────────────────────────────────────────────┐
│  Deploy Script (deploy.py)                                          │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  Step 1: Create/Verify IAM Role                            │    │
│  │  - Check if role exists                                    │    │
│  │  - Create with all necessary permissions                   │    │
│  │  - Wait for IAM eventual consistency (30s)                 │    │
│  └────────────────────────────────────────────────────────────┘    │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  Step 2: Configure AgentCore Runtime                       │    │
│  │  - Set entrypoint: serve_bedrock.py                        │    │
│  │  - Set platform: linux/arm64                               │    │
│  │  - Set execution role ARN                                  │    │
│  │  - Set ECR repository                                      │    │
│  │  - Set network: PUBLIC, protocol: HTTP                     │    │
│  │  - Enable observability                                    │    │
│  └────────────────────────────────────────────────────────────┘    │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  Step 3: Build and Push Docker Image                       │    │
│  │  - Build from Dockerfile                                   │    │
│  │  - Tag with AgentCore conventions                          │    │
│  │  - Push to ECR repository                                  │    │
│  │  - AWS CodeBuild handles build process                     │    │
│  └────────────────────────────────────────────────────────────┘    │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  Step 4: Launch to AgentCore                               │    │
│  │  - Submit launch request                                   │    │
│  │  - Poll status until READY                                 │    │
│  │  - Typical time: 1-2 minutes                               │    │
│  └────────────────────────────────────────────────────────────┘    │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  Step 5: Smoke Test (Optional)                             │    │
│  │  - Invoke agent with test request                          │    │
│  │  - Verify response structure                               │    │
│  │  - Check S3 file creation                                  │    │
│  └────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────────┐
│  AWS CodeBuild                                                       │
│  Project: bedrock-agentcore-literacy_assessment-builder              │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  Build Execution                                            │    │
│  │  1. Pull source from S3                                     │    │
│  │  2. Execute docker build                                    │    │
│  │  3. Push image to ECR                                       │    │
│  │  4. Duration: ~60-90 seconds                                │    │
│  └────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────────┐
│  Amazon ECR                                                          │
│  Repository: YOUR_AWS_ACCOUNT_ID.dkr.ecr.eu-central-1.amazonaws.com/       │
│              bedrock-agentcore-literacy_assessment                   │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  Container Image Storage                                    │    │
│  │  - Tagged with build timestamps                             │    │
│  │  - Pulled by AgentCore for deployment                       │    │
│  │  - Lifecycle policies for cleanup                           │    │
│  └────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────────┐
│  AWS Bedrock AgentCore                                               │
│  Agent: literacy_assessment-nOAwV9Bfmp                               │
│  ARN: arn:aws:bedrock-agentcore:eu-central-1:YOUR_AWS_ACCOUNT_ID:runtime/  │
│       literacy_assessment-nOAwV9Bfmp                                 │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  Serverless Runtime                                         │    │
│  │  - Auto-scaling container instances                         │    │
│  │  - Pay-per-use pricing                                      │    │
│  │  - Automatic health checks                                  │    │
│  │  - CloudWatch integration                                   │    │
│  │  - Status: READY                                            │    │
│  └────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
```

### Observability

**CloudWatch Logs**:
- Log Group: `/aws/bedrock-agentcore/runtimes/literacy_assessment-nOAwV9Bfmp-DEFAULT`
- Structured JSON logging
- Request/response traces
- Tool execution details
- Performance metrics

**OpenTelemetry Instrumentation**:
- Automatic tracing via `opentelemetry-instrument`
- Distributed tracing across agent invocations
- Performance profiling
- Error tracking with context

**Metrics** (via CloudWatch):
- Invocation count
- Duration (P50, P90, P99)
- Error rate
- Tool execution time
- KB query latency
- S3 upload time

## Performance Characteristics

### Single-Level Assessment

**Typical Timeline** (Level 2 example):
- Request parsing: 50ms
- KB queries (3x): 750ms
- Question generation: 1500ms
- Assessment validation: 100ms
- S3 upload (both formats): 300ms
- **Total: ~2700ms (2.7 seconds)**

### Multi-Level Assessment (Parallel)

**Example**: Levels 1, 2, 3 requested together

**Sequential Execution** (theoretical):
- Level 1: 2500ms
- Level 2: 2700ms
- Level 3: 2900ms
- **Total: 8100ms (8.1 seconds)**

**Parallel Execution** (actual):
- All 3 levels execute concurrently
- **Total: ~3000ms (3.0 seconds)**
- **Speedup: 63% reduction**

### Bottlenecks

1. **Knowledge Base Queries**: 25-30% of total time
   - Mitigation: Cache frequently queried content
   - Alternative: Reduce max_results parameter

2. **LLM Generation**: 50-60% of total time
   - Mitigation: Use faster model (Haiku) for simple assessments
   - Alternative: Pre-generate question templates

3. **S3 Upload**: 10-15% of total time
   - Mitigation: Concurrent upload of JSON and Markdown
   - Alternative: Background upload (return immediately)

## Scaling Considerations

**Horizontal Scaling**:
- AgentCore automatically scales container instances
- No manual configuration required
- Handles burst traffic

**Vertical Scaling**:
- Container resources managed by AgentCore
- Default allocation sufficient for current load
- Can request larger instances if needed

**Rate Limits**:
- Bedrock API: 400 requests/minute (default)
- Knowledge Base: 100 queries/minute per KB
- S3: 3500 PUT requests/second (regional)

**Cost Optimization**:
- Use Haiku model for simple assessments (~10x cheaper)
- Cache KB query results (Redis/ElastiCache)
- Implement request batching for bulk generation
- S3 lifecycle policies for old assessments

## Security

**Data in Transit**:
- TLS 1.2+ for all AWS API calls
- HTTPS for AgentCore endpoint
- Signed requests (AWS SigV4)

**Data at Rest**:
- S3 server-side encryption (SSE-S3)
- CloudWatch Logs encryption
- ECR image scanning enabled

**Access Control**:
- IAM role with least-privilege permissions
- No hardcoded credentials
- Service-to-service authentication via IAM

**Secrets Management**:
- No API keys or passwords required
- AWS managed credentials (IAM role)
- Environment variables for configuration only

## Disaster Recovery

**Backup Strategy**:
- S3 assessments: Versioning enabled
- CloudWatch Logs: 7-day retention
- Container images: Multiple tagged versions in ECR

**Recovery Procedures**:
1. **Agent Failure**: AgentCore auto-restarts containers
2. **Deployment Rollback**: Redeploy previous ECR image tag
3. **Data Loss**: Restore from S3 versioning
4. **Region Failure**: Redeploy to alternate region (manual)

**RTO/RPO**:
- Recovery Time Objective: 5 minutes (redeploy)
- Recovery Point Objective: 0 seconds (S3 immediate consistency)

## Related Documentation

- [Tools and Subagents Reference](./TOOLS_AND_SUBAGENTS.md) - Detailed tool and subagent documentation
- [Testing Guide](./TESTING_GUIDE.md) - Testing procedures and best practices
- [Deployment README](../../README.md) - Deployment instructions and troubleshooting
- [Historical Documentation](./archive/) - Previous design documents and analysis
