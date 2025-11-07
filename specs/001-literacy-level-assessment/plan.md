# Implementation Plan: Dynamic Literacy Level Assessment System

**Branch**: `001-literacy-level-assessment` | **Date**: 2025-11-06 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-literacy-level-assessment/spec.md`

## Summary

Build a multi-level literacy assessment system using Deep Agents framework with parallel subagent orchestration. The system extracts curriculum content from 4 level-specific AWS Bedrock Knowledge Bases to dynamically generate customized 10-question assessments (7 multiple-choice, 3 open-ended) calibrated to user background. Supports single or multi-level assessment requests with parallel execution for efficiency.

**Current Status**: Core assessment generation implemented and tested. AgentCore deployment infrastructure complete. Ready for AWS deployment.

## Technical Context

**Language/Version**: Python 3.12
**Primary Dependencies**:
- LangChain/LangGraph (agent orchestration)
- Deep Agents framework (middleware, subagent parallelization)
- AWS Bedrock SDK (Knowledge Base access, Claude Sonnet 4.5)
- Pydantic v2 (data validation)
- boto3 (AWS S3, IAM)

**Storage**:
- AWS S3 (`literacy-framework-development-961105418118-eu-central-1`)
  - Source: `learning_path/levels/` (knowledge base documents)
  - Output: `learning_path/assessments/` (generated assessments)
- AWS Bedrock Knowledge Bases (4 level-specific):
  - Level 1: `QADZTSAPWX` (foundational)
  - Level 2: `KGGD2PTQ2N` (intermediate)
  - Level 3: `7MGFSODDVI` (advanced)
  - Level 4: `CHYWO1H6OM` (expert)

**Testing**: pytest, integration tests with live Knowledge Bases
**Target Platform**:
- Local development (MacOS, Linux)
- AWS Bedrock AgentCore (serverless containerized deployment)

**Project Type**: Single Python project with example implementation
**Performance Goals**:
- Single-level assessment: <60 seconds
- Multi-level parallel: <120 seconds for 4 levels
- Parallelization efficiency: ≥40% time reduction vs sequential

**Constraints**:
- Token budget per assessment: ~50K tokens (input) + ~15K tokens (output)
- Knowledge Base query latency: ~2-5 seconds per query
- S3 upload with retry: exponential backoff (3 attempts max)
- AgentCore timeout: 300 seconds per invocation

**Scale/Scope**:
- 4 literacy levels, each with dedicated Knowledge Base
- 10 questions per assessment (7 MC, 3 OE)
- Concurrent user support via AgentCore auto-scaling
- Knowledge Bases contain 100+ curriculum documents across modules

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Middleware-First Architecture ✅

**Status**: COMPLIANT

- Uses Deep Agents framework with composable middleware
- `TodoListMiddleware`, `SubAgentMiddleware` utilized for planning and parallelization
- No modifications to core framework - follows framework patterns

**Evidence**: `examples/literacy_assessment/src/agent.py` uses `create_deep_agent()` with middleware configuration.

### II. Backward Compatibility ✅

**Status**: COMPLIANT (N/A - new feature)

- New example implementation, no changes to existing APIs
- No breaking changes to Deep Agents framework
- Uses stable LangChain/LangGraph APIs

### III. Framework Agnostic (LangGraph Native) ✅

**Status**: COMPLIANT

- Returns standard LangGraph `CompiledGraph` via `create_deep_agent()`
- Uses LangGraph StateGraph for state management
- No custom wrappers hiding LangGraph concepts
- Compatible with LangGraph streaming, checkpointing

**Evidence**: Agent created with `create_deep_agent()` which returns LangGraph CompiledGraph.

### IV. Model Agnostic ✅

**Status**: COMPLIANT

- Defaults to Claude Sonnet 4.5 but accepts any `BaseChatModel`
- Model specified via string: `"anthropic:claude-sonnet-4-20250514"`
- No model-specific features in implementation

**Evidence**: `config.py` uses model string identifiers compatible with LangChain model registry.

### V. Test Coverage for Core Features ⚠️

**Status**: PARTIALLY COMPLIANT

- Integration tests exist (`run_comprehensive_test.py`)
- Manual testing with live Knowledge Bases successful
- **Missing**: Unit tests for individual components (kb_tools, questions, models)
- **Missing**: Contract tests for tool schemas

**Justification**: Initial implementation prioritized end-to-end validation with real AWS services. Unit tests recommended for future iterations.

### VI. Clear, Comprehensive Documentation ✅

**Status**: COMPLIANT

- README with architecture overview
- AgentCore deployment README with step-by-step instructions
- Inline docstrings for all modules
- Example usage scripts provided

**Evidence**:
- `examples/literacy_assessment/README.md`
- `deploy/agentcore_literacy_assessment/README.md`
- `examples/literacy_assessment/docs/` directory

### VII. Performance and Cost Consciousness ✅

**Status**: COMPLIANT

- Token usage documented and monitored
- Parallel execution reduces cost (fewer sequential calls)
- S3 upload with retry prevents duplicate generations
- Rate limiting in AgentCore entrypoint (0.5s between yields)

**Evidence**:
- Knowledge Base retrieval optimized with `top_k` limits
- Parallel subagent execution documented
- Cost considerations in deployment README

## Project Structure

### Documentation (this feature)

```text
specs/001-literacy-level-assessment/
├── spec.md              # Feature specification (complete)
├── plan.md              # This file - implementation plan (IN PROGRESS)
├── research.md          # Phase 0 output (TO BE CREATED)
├── data-model.md        # Phase 1 output (TO BE CREATED)
├── quickstart.md        # Phase 1 output (TO BE CREATED)
├── contracts/           # Phase 1 output (TO BE CREATED)
└── tasks.md             # Phase 2 output (created separately via /speckit.tasks)
```

### Source Code (repository root)

```text
# Literacy Assessment Implementation
examples/literacy_assessment/
├── src/
│   ├── __init__.py
│   ├── agent.py            # Main agent & subagent definitions (orchestrator + 4 level agents)
│   ├── config.py           # AWS config, Knowledge Base IDs, model settings
│   ├── kb_tools.py         # Knowledge Base query tools (4 level-specific tools)
│   ├── models.py           # Pydantic models (Assessment, Question, MultipleChoice, OpenEnded)
│   ├── questions.py        # Question generation prompts and logic
│   └── s3_uploader.py      # S3 upload utilities with retry logic
├── tests/
│   ├── test_config.py      # Configuration validation tests
│   ├── test_models.py      # Pydantic model validation tests
│   └── test_question_gen.py # Question generation tests
├── scripts/
│   ├── validate_config.py  # AWS credentials and KB access validation
│   ├── display_sample_assessment.py  # Assessment visualization
│   └── example_usage.py    # Quick start example
├── output/
│   ├── assessments/        # Generated assessment JSON and Markdown files
│   │   ├── level_1/
│   │   ├── level_2/
│   │   ├── level_3/
│   │   └── level_4/
│   └── logs/               # Test execution logs
├── docs/
│   ├── README.md           # Implementation documentation
│   ├── TESTING_GUIDE.md    # Testing instructions
│   └── PHASE2_DESIGN.md    # Design decisions
├── run_comprehensive_test.py  # Integration test suite
├── validate_s3.py          # S3 bucket and permissions validation
└── requirements.txt        # Python dependencies

# AgentCore Deployment Package
deploy/agentcore_literacy_assessment/
├── src/
│   └── deepagents/         # Deep Agents framework (copied for container)
│       ├── graph.py
│       └── middleware/
├── examples/
│   └── literacy_assessment/  # Complete agent implementation (copied for container)
│       └── [same structure as above]
├── serve_bedrock.py        # AgentCore entrypoint (async streaming interface)
├── deploy.py               # Deployment orchestration script
├── utils.py                # IAM role creation with all permissions
├── requirements.txt        # Container dependencies
├── Dockerfile              # Container definition (uv-based, opentelemetry)
└── README.md               # Deployment documentation

# Deep Agents Framework (Core)
src/deepagents/
├── __init__.py
├── graph.py                # create_deep_agent() - main API
└── middleware/
    ├── __init__.py
    ├── filesystem.py       # Filesystem middleware
    ├── subagents.py        # SubAgent middleware for parallelization
    └── patch_tool_calls.py # Tool call patching utilities

tests/
├── contract/               # Tool schema contract tests
├── integration/            # End-to-end integration tests
└── unit/                   # Component unit tests
```

**Structure Decision**: Single Python project with examples directory following Deep Agents framework conventions. The AgentCore deployment package copies necessary framework and example code into a self-contained directory for Docker containerization with `COPY . .` pattern.

## Implementation Progress

### Phase 0: Research & Architecture ✅ COMPLETE

**Status**: Implementation-first approach taken based on existing Deep Agents patterns.

**Key Decisions**:
1. **Agent Architecture**: Orchestrator pattern with 4 level-specific subagents
   - Rationale: Isolates level-specific logic, enables parallelization, aligns with Deep Agents subagent middleware
   - Alternative considered: Single monolithic agent - rejected due to lack of parallelization and harder maintenance

2. **Knowledge Base Integration**: Direct Bedrock Knowledge Base queries via custom tools
   - Rationale: Native AWS integration, low latency, built-in semantic search
   - Alternative considered: Pre-fetching all content - rejected due to token limits and stale data risk

3. **Question Mix**: 70% multiple-choice (7 questions), 30% open-ended (3 questions)
   - Rationale: Balances automated assessment with depth evaluation per FR-010
   - Alternative considered: 100% MC - rejected due to inability to assess deeper understanding

4. **S3 Upload Strategy**: Post-generation upload with separate metadata tracking
   - Rationale: Clean separation between assessment data and operational metadata
   - Alternative considered: Inline metadata - rejected due to data model pollution

5. **Deployment Target**: AWS Bedrock AgentCore for serverless auto-scaling
   - Rationale: No infrastructure management, automatic CloudWatch logging, built-in observability
   - Alternative considered: ECS/Lambda - rejected due to complexity and manual logging setup

### Phase 1: Core Implementation ✅ COMPLETE

**Components Delivered**:

1. **Data Models** (`src/models.py`)
   - `Assessment`: Top-level assessment with metadata
   - `MultipleChoiceQuestion`: 4-option MC with correct answer index
   - `OpenEndedQuestion`: Free-text with evaluation criteria
   - S3 metadata fields removed after user feedback (kept clean)

2. **Knowledge Base Tools** (`src/kb_tools.py`)
   - 4 level-specific query tools (Level1KBTool, Level2KBTool, etc.)
   - Each tool queries corresponding Bedrock Knowledge Base
   - Returns document sources with metadata

3. **Agent Architecture** (`src/agent.py`)
   - Main orchestrator agent: Routes requests to appropriate level subagent(s)
   - 4 level-specific subagents: Each generates 10 questions for its level
   - Parallel execution via Deep Agents SubAgentMiddleware
   - Streaming support for progress updates

4. **S3 Integration** (`src/s3_uploader.py`)
   - Upload assessments in JSON and Markdown formats
   - Exponential backoff retry (3 attempts)
   - Separate S3 metadata tracking files (*.s3_metadata.json)

5. **Configuration** (`src/config.py`)
   - AWS credentials and region
   - Knowledge Base IDs for all 4 levels
   - Model configuration (Claude Sonnet 4.5)
   - S3 bucket and path configuration

**Testing Evidence**:
- Integration tests pass for all 4 levels
- Multi-level parallel execution validated
- S3 uploads successful with retry logic
- Knowledge Base queries return relevant curriculum content

### Phase 2: AgentCore Deployment Infrastructure ✅ COMPLETE

**Delivered on 2025-11-06**:

1. **IAM Role Creation** (`utils.py`)
   - Bedrock model invocation permissions (InvokeModel, InvokeModelWithResponseStream)
   - Knowledge Base access (Retrieve, RetrieveAndGenerate) for all 4 KBs
   - S3 read/write permissions (GetObject, PutObject, ListBucket)
   - CloudWatch Logs (CreateLogGroup, PutLogEvents, DescribeLogGroups)
   - ECR access (GetAuthorizationToken, BatchGetImage)
   - X-Ray tracing and CloudWatch metrics
   - AgentCore workload identity permissions

2. **AgentCore Entrypoint** (`serve_bedrock.py`)
   - Async streaming interface for AgentCore
   - Rate limiting (0.5s between yields to prevent overwhelming)
   - Error handling and graceful degradation
   - Proper Python path setup for container environment

3. **Deployment Orchestration** (`deploy.py`)
   - Automated IAM role creation
   - AgentCore configuration (entrypoint, execution role, region)
   - Docker container build and push to ECR
   - Launch to AgentCore serverless runtime
   - Status monitoring (waits for READY state)
   - Test invocation with retry logic

4. **Container Definition** (`Dockerfile`)
   - Base: `ghcr.io/astral-sh/uv:python3.12-bookworm-slim`
   - Dependencies installed via uv (fast)
   - OpenTelemetry instrumentation for observability
   - Non-root user for security
   - Exposes ports 9000, 8000, 8080
   - Copies entire project with `COPY . .`

5. **Project Structure Setup**
   - Copied `src/deepagents/` framework to deployment folder
   - Copied `examples/literacy_assessment/` to deployment folder
   - Updated import paths for container environment
   - Created comprehensive deployment README

**Deployment Ready**: All files in place for `python deploy.py` execution.

### Phase 3: Production Readiness (PENDING)

**Remaining Tasks**:
1. Execute deployment to AWS (`cd deploy/agentcore_literacy_assessment && python deploy.py`)
2. Validate deployed agent with test invocations
3. Monitor CloudWatch logs for errors
4. Performance testing under load
5. Cost analysis and optimization recommendations

## Complexity Tracking

**No Constitution Violations** - All implementation follows Deep Agents framework patterns and principles.

**Justified Complexities**:

| Decision | Rationale | Simpler Alternative Rejected |
|----------|-----------|------------------------------|
| 4 level-specific subagents | Parallel execution, level isolation, maintainability | Single agent with level parameter - no parallelization, harder to maintain |
| Separate S3 metadata files | Data model purity, clean assessment JSON | Inline metadata - pollutes assessment data, violates separation of concerns |
| AgentCore deployment | Auto-scaling, observability, no infrastructure management | Lambda/ECS - more complex, manual logging, no AgentCore benefits |
| Retry logic in S3 upload | Transient error resilience, cost savings (no duplicate generations) | No retry - fail on transient errors, expensive retries |

## Next Steps

1. **Deploy to AgentCore**:
   ```bash
   cd deploy/agentcore_literacy_assessment
   export AWS_PROFILE=mll-dev
   export AWS_REGION=eu-central-1
   python deploy.py
   ```

2. **Monitor Deployment**:
   - Verify READY status
   - Test with sample Level 2 request
   - Check CloudWatch logs for errors

3. **Production Validation**:
   - Load testing (10+ concurrent users)
   - Cost analysis per assessment
   - Performance profiling (identify bottlenecks)

4. **Documentation Updates**:
   - Create `research.md` documenting architecture decisions
   - Create `data-model.md` with Pydantic schema details
   - Create `quickstart.md` for new users
   - Create `contracts/` directory with API contracts

5. **Future Enhancements** (Out of Scope for MVP):
   - Assessment result tracking and scoring
   - Historical assessment storage
   - Analytics dashboard
   - Multi-language support
