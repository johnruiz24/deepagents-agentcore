# Implementation Tasks: Dynamic Literacy Level Assessment System

**Feature**: 001-literacy-level-assessment | **Branch**: `001-literacy-level-assessment` | **Date**: 2025-11-04

**Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md) | **Data Model**: [data-model.md](./data-model.md)

**Status**: 🚀 **Phase 8 & 9: S3 Upload + CloudWatch Logging** (61/119 tasks complete)

**Last Updated**: 2025-11-04

---

## Task Format

Each task follows this format:
```
- [ ] T### [Priority] [Story] Task description (file: path/to/file.py)
```

**Priorities**: P1 (MVP), P2 (Core), P3 (Enhancement), P4 (Polish)

**Parallelization**: Tasks marked with `[P]` can be executed concurrently.

---

## Phase 0: Setup & Foundation ✅ (Complete)

**Status**: Planning complete. Ready to implement.

- [x] T000 [P1] [Setup] Create feature branch `001-literacy-level-assessment`
- [x] T001 [P1] [Setup] Write feature specification (file: specs/001-literacy-level-assessment/spec.md)
- [x] T002 [P1] [Setup] Research AWS Bedrock KB integration patterns (file: specs/001-literacy-level-assessment/research.md)
- [x] T003 [P1] [Setup] Define data models and entities (file: specs/001-literacy-level-assessment/data-model.md)
- [x] T004 [P1] [Setup] Document API contracts (file: specs/001-literacy-level-assessment/contracts/assessment-interface.md)
- [x] T005 [P1] [Setup] Create quickstart guide (file: specs/001-literacy-level-assessment/quickstart.md)
- [x] T006 [P1] [Setup] Document implementation notes with AWS KB IDs (file: specs/001-literacy-level-assessment/IMPLEMENTATION_NOTES.md)

---

## Phase 1: Directory Structure & Dependencies ✅ (Complete)

**Goal**: Create isolated example directory with configuration and dependencies.

**Critical Constraint**: ⚠️ All work happens in `examples/literacy-assessment/` - DO NOT modify `src/` or `deploy/` folders.

### T100 Series: Directory Creation

- [x] T100 [P1] [Setup] Create main directory `examples/literacy-assessment/`
- [x] T101 [P1] [Setup] Create tests directory `examples/literacy-assessment/tests/`
- [x] T102 [P1] [Setup] Create `examples/literacy-assessment/__init__.py`
- [x] T103 [P1] [Setup] Create `examples/literacy-assessment/tests/__init__.py`

### T110 Series: Configuration Files

- [x] T110 [P1] [Setup] Copy `.env.example` to `examples/literacy-assessment/.env.example`
- [x] T111 [P1] [Setup] Create `examples/literacy-assessment/.gitignore`
- [x] T112 [P1] [Setup] Create `examples/literacy-assessment/requirements.txt`

---

## Phase 2: Foundation Components ✅ (Complete)

**Goal**: Implement configuration, data models, and AWS Bedrock KB client.

### T200 Series: Configuration Management

- [x] T200 [P1] [Story-1] Implement `examples/literacy-assessment/src/config.py`
- [x] T201 [P1] [Setup] Create configuration validation script `examples/literacy-assessment/scripts/validate_config.py`

### T210 Series: Data Models [PARALLEL with T200]

- [x] T210 [P1] [Story-1] Implement `examples/literacy-assessment/src/models.py`

### T220 Series: AWS Bedrock Knowledge Base Tools [PARALLEL with T210]

- [x] T220 [P1] [Story-1] Implement `examples/literacy-assessment/src/kb_tools.py`
- [x] T221 [P1] [Story-1] Implement `KnowledgeBaseClient.query()` method
- [x] T222 [P1] [Story-1] Implement `gather_diverse_content()` function
- [x] T223 [P1] [Story-1] Create level-specific KB query tool functions

---

## Phase 3: User Story 1 - Single Level Assessment Generation (P1 MVP) ✅ (Complete)

**Story**: "As a curriculum administrator, I want to generate a single-level literacy assessment by providing a user's background, so I can evaluate their proficiency for that specific level."

**Success Criteria**: SC-001 (10 questions), SC-002 (<60s), SC-005 (5+ modules)

### T300 Series: Question Generation

- [x] T300 [P1] [US1] Implement `examples/literacy-assessment/src/questions.py`
- [x] T301 [P1] [US1] Implement MC question generation logic
- [x] T302 [P1] [US1] Implement open-ended question generation logic
- [x] T303 [P1] [US1] Implement question format validation

### T310 Series: Single-Level Subagent Definition

- [x] T310 [P1] [US1] Implement Level 1 subagent in `examples/literacy-assessment/src/agent.py`
- [x] T311 [P1] [US1] Implement Level 2 subagent
- [x] T312 [P1] [US1] Implement Level 3 subagent
- [x] T313 [P1] [US1] Implement Level 4 subagent

### T320 Series: Main Agent Orchestrator

- [x] T320 [P1] [US1] Implement main agent system prompt in `examples/literacy-assessment/src/agent.py`
- [x] T321 [P1] [US1] Implement `create_literacy_assessment_agent()` function
- [x] T322 [P1] [US1] Implement `format_assessment` tool function

### T330 Series: Testing & Validation

- [x] T330 [P1] [US1] Write unit tests `examples/literacy-assessment/tests/test_kb_tools.py`
- [x] T331 [P1] [US1] Write unit tests `examples/literacy-assessment/tests/test_question_gen.py`
- [x] T332 [P1] [US1] Write integration test `examples/literacy-assessment/tests/test_literacy_agent.py`
- [x] T333 [P1] [US1] Create example usage script `examples/literacy-assessment/scripts/example_usage.py`

---

## Phase 4: User Story 2 - Multi-Level Parallel Assessment (P2)

**Story**: "As an educational platform, I want to generate assessments for multiple literacy levels simultaneously using parallel subagent execution, so I can reduce total generation time and improve user experience."

**Success Criteria**: SC-003 (parallel execution), SC-004 (60% time reduction)

### T400 Series: Parallel Execution Logic

- [ ] T400 [P2] [US2] Update main agent prompt to support multi-level requests in `examples/literacy-assessment/src/agent.py`
- [ ] T401 [P2] [US2] Implement result aggregation logic in `examples/literacy-assessment/src/agent.py`

### T410 Series: Performance Tracking

- [ ] T410 [P2] [US2] Add performance tracking to main agent in `examples/literacy-assessment/src/agent.py`
- [ ] T411 [P2] [US2] Add performance summary formatting in `examples/literacy-assessment/src/agent.py`

### T420 Series: Testing Multi-Level

- [ ] T420 [P2] [US2] Write integration test for multi-level parallel generation in `examples/literacy-assessment/tests/test_parallel.py`
- [ ] T421 [P2] [US2] Update `examples/literacy-assessment/scripts/example_usage.py` with multi-level example

---

## Phase 5: User Story 3 - Background Calibration (P3)

**Story**: "As a user, I want the assessment difficulty to be calibrated based on my experience and background, so the questions are appropriately challenging for my skill level within the target literacy level."

**Success Criteria**: SC-006 (calibration working), FR-006 (complexity adjustment)

### T500 Series: Background Parsing

- [ ] T500 [P3] [US3] Implement `parse_user_background()` function in `examples/literacy-assessment/src/agent.py`
- [ ] T501 [P3] [US3] Update subagent prompts to use background profile in `examples/literacy-assessment/src/agent.py`

### T510 Series: Difficulty Calibration

- [ ] T510 [P3] [US3] Implement difficulty calibration logic in `examples/literacy-assessment/src/questions.py`
- [ ] T511 [P3] [US3] Add difficulty validation to Assessment model in `examples/literacy-assessment/src/models.py`

### T520 Series: Testing Calibration

- [ ] T520 [P3] [US3] Write tests for background parsing in `examples/literacy-assessment/tests/test_calibration.py`
- [ ] T521 [P3] [US3] Write tests for difficulty calibration in `examples/literacy-assessment/tests/test_calibration.py`

---

## Phase 6: User Story 4 - Result Tracking (P4)

**Story**: "As a system administrator, I want to review generated assessment metadata (generation time, modules covered, question distribution) so I can monitor system performance and content quality."

**Success Criteria**: SC-007 (metadata included), FR-015 (JSON format)

### T600 Series: Metadata Collection

- [ ] T600 [P4] [US4] Enhance Assessment model with comprehensive metadata in `examples/literacy-assessment/src/models.py`
- [ ] T601 [P4] [US4] Implement metadata aggregation during generation in `examples/literacy-assessment/src/agent.py`

### T610 Series: Result Export

- [ ] T610 [P4] [US4] Implement assessment export functions in `examples/literacy-assessment/src/export.py`
- [ ] T611 [P4] [US4] Implement result retrieval interface in `examples/literacy-assessment/src/export.py`

### T620 Series: Analytics & Reporting

- [ ] T620 [P4] [US4] Create analytics script `examples/literacy-assessment/scripts/analyze_results.py`

---

## Phase 7: Documentation & Polish ✅ (Partial Complete)

**Goal**: Complete documentation, CLI interface, and final testing.

### T700 Series: Documentation

- [x] T700 [P2] [Setup] Write `examples/literacy-assessment/README.md`
- [x] T701 [P3] [Setup] Add inline documentation to all modules

### T710 Series: Command-Line Interface (Optional)

- [ ] T710 [P3] [US1,US2] Create `examples/literacy-assessment/cli.py`
- [ ] T711 [P3] [US4] Add CLI commands for result management in `examples/literacy-assessment/cli.py`

### T720 Series: Final Testing & Validation

- [ ] T720 [P1] [Setup] Run full test suite
- [ ] T721 [P1] [Setup] Run configuration validation
- [ ] T722 [P2] [US1] End-to-end test: Single level assessment
- [ ] T723 [P2] [US2] End-to-end test: Multi-level parallel
- [ ] T724 [P3] [US3] End-to-end test: Background calibration

---

## Phase 8: User Story 5 - S3 Assessment Upload (P2) 🆕

**Story**: "As a system administrator, I want assessment files (JSON and Markdown) automatically uploaded to S3 after generation, so assessments are durably stored and accessible across systems."

**Why this priority**: This provides persistent, scalable storage for generated assessments and enables downstream processing, reporting, and audit trails. S3 storage is critical for production deployments.

**Independent Test**: Generate a Level 1 assessment and verify that both JSON and Markdown files are uploaded to the configured S3 bucket with correct naming and metadata.

**Success Criteria**:
- Assessment JSON files uploaded to S3 with path: `s3://<bucket>/assessments/<level>/level_<level>_<timestamp>.json`
- Assessment Markdown files uploaded to S3 with path: `s3://<bucket>/assessments/<level>/level_<level>_<timestamp>.md`
- S3 object metadata includes: generation_time, user_background_hash, modules_count
- Upload completes within 5 seconds for typical assessment sizes (<500KB)
- Failed uploads are retried with exponential backoff (max 3 attempts)
- Upload errors are logged but do not block assessment generation

### T800 Series: S3 Configuration

- [ ] T800 [P2] [US5] Add S3 configuration to `examples/literacy-assessment/src/config.py`
  - Add `S3_BUCKET_NAME` environment variable (default: literacy-assessments-dev)
  - Add `S3_PREFIX` environment variable (default: assessments/)
  - Add `S3_REGION` environment variable (inherits from AWS_REGION)
  - Add `ENABLE_S3_UPLOAD` boolean flag (default: True)
  - Add `validate_s3_config()` method to check S3 bucket accessibility

- [ ] T801 [P] [US5] Update `.env.example` with S3 configuration
  - Add S3_BUCKET_NAME example
  - Add S3_PREFIX example
  - Add ENABLE_S3_UPLOAD flag
  - Add documentation comments explaining S3 requirements

### T810 Series: S3 Upload Implementation

- [ ] T810 [P2] [US5] Create S3 upload client in `examples/literacy-assessment/src/s3_uploader.py`
  - Implement `S3UploaderClient` class with boto3 s3 client
  - `__init__(bucket_name: str, prefix: str, region: str, profile: str)`
  - Use boto3.Session with profile for authentication
  - Initialize S3 client with region

- [ ] T811 [P2] [US5] Implement `upload_assessment()` method in `S3UploaderClient`
  - Parameters: `assessment: Assessment, file_format: Literal["json", "markdown"]`
  - Generate S3 key: `{prefix}/level_{level}/level_{level}_{timestamp}.{ext}`
  - Convert Assessment to JSON or Markdown format
  - Upload with metadata: ContentType, generation_time, user_background_hash, modules_count
  - Return S3 URI (s3://bucket/key) on success
  - Handle `ClientError` exceptions (access denied, bucket not found)
  - Reference: Similar pattern to kb_tools.py lines 22-50

- [ ] T812 [P2] [US5] Implement retry logic with exponential backoff
  - Wrap S3 upload in retry decorator
  - Max 3 attempts with exponential backoff (1s, 2s, 4s)
  - Retry on transient errors: Throttling, ServiceUnavailable, RequestTimeout
  - Do not retry on permanent errors: AccessDenied, NoSuchBucket
  - Log each retry attempt with reason

- [ ] T813 [P] [US5] Implement batch upload function for multiple assessments
  - `upload_multiple_assessments(assessments: List[Assessment], formats: List[str])`
  - Upload assessments concurrently using ThreadPoolExecutor (max 5 workers)
  - Return dict mapping assessment_id to S3 URIs
  - Aggregate success/failure statistics

### T820 Series: Integration with Assessment Generation

- [ ] T820 [P2] [US5] Integrate S3 upload into `run_comprehensive_test.py`
  - After assessment generation and local file save, upload to S3
  - Upload both JSON and Markdown formats
  - Log S3 URIs to test log file
  - Handle upload failures gracefully (log error, continue test)
  - Add S3 upload time to performance metrics

- [ ] T821 [P2] [US5] Update Assessment model with S3 metadata in `examples/literacy-assessment/src/models.py`
  - Add optional `s3_uri_json: str | None` field
  - Add optional `s3_uri_markdown: str | None` field
  - Add optional `s3_upload_time: datetime | None` field
  - Update JSON serialization to include S3 URIs

- [ ] T822 [P2] [US5] Add S3 upload to main agent workflow in `examples/literacy-assessment/src/agent.py`
  - After `format_assessment` creates Assessment, upload to S3
  - Update Assessment object with S3 URIs
  - Log upload success/failure to agent messages
  - Make upload optional based on ENABLE_S3_UPLOAD config

### T830 Series: Testing S3 Upload

- [ ] T830 [P] [US5] Write unit tests for S3 uploader in `examples/literacy-assessment/tests/test_s3_uploader.py`
  - Test `S3UploaderClient.upload_assessment()` with mocked boto3 client
  - Test successful JSON upload
  - Test successful Markdown upload
  - Test retry logic on transient errors
  - Test permanent error handling (AccessDenied)
  - Test S3 URI generation format

- [ ] T831 [P] [US5] Write integration test for S3 upload in `examples/literacy-assessment/tests/test_s3_integration.py`
  - Generate Level 1 assessment
  - Upload to real S3 bucket (test bucket)
  - Verify object exists in S3
  - Verify metadata is correct
  - Verify content matches generated assessment
  - Clean up test objects after test

- [ ] T832 [P2] [US5] Update `scripts/validate_config.py` to validate S3 access
  - Check S3 bucket exists and is accessible
  - Test write permissions with dummy object
  - Test read permissions
  - Delete test object
  - Print S3 validation status ✓/✗

---

## Phase 9: User Story 6 - Structured Logging for AgentCore/CloudWatch (P2) 🆕

**Story**: "As a system administrator, I want application logs emitted in structured JSON format compatible with AgentCore's logging infrastructure, so logs are automatically captured in CloudWatch when deployed to AgentCore."

**Why this priority**: AgentCore automatically creates CloudWatch log groups and captures application logs. By emitting structured JSON logs using standard Python logging, the application becomes deployment-ready for AgentCore without managing CloudWatch infrastructure directly.

**Independent Test**: Generate an assessment and verify that structured JSON logs are emitted to stdout/file in the correct format that AgentCore can capture and forward to CloudWatch.

**Success Criteria**:
- All application logs use standard Python logging with structured JSON formatting
- JSON log format includes: timestamp, level, message, context (assessment_level, user_background), execution_time_ms
- Critical events logged: assessment_started, assessment_completed, assessment_failed, kb_query, s3_upload
- Logs are emitted to stdout (AgentCore captures stdout logs)
- Log format is compatible with CloudWatch Insights queries
- Logging adds <50ms overhead to operations

### T900 Series: Logging Configuration

- [ ] T900 [P2] [US6] Add logging configuration to `examples/literacy-assessment/src/config.py`
  - Add `LOG_LEVEL` environment variable (default: INFO)
  - Add `LOG_FORMAT` environment variable (default: "json" for AgentCore, "text" for local dev)
  - Add `ENABLE_STRUCTURED_LOGGING` boolean flag (default: True)
  - No CloudWatch-specific config needed (AgentCore handles log group creation)

- [ ] T901 [P] [US6] Update `.env.example` with logging configuration
  - Add LOG_LEVEL options (DEBUG, INFO, WARNING, ERROR)
  - Add LOG_FORMAT options (json, text)
  - Add ENABLE_STRUCTURED_LOGGING flag
  - Add documentation explaining AgentCore will capture logs automatically

### T910 Series: Structured JSON Logger Implementation

- [ ] T910 [P2] [US6] Create structured JSON formatter in `examples/literacy-assessment/src/structured_logger.py`
  - Implement `StructuredJSONFormatter` class extending logging.Formatter
  - Format log records as JSON with fields:
    - `timestamp`: ISO 8601 format with milliseconds
    - `level`: DEBUG/INFO/WARNING/ERROR/CRITICAL
    - `message`: Log message
    - `context`: Dict with contextual data (assessment_level, user_background_hash, run_id, etc.)
    - `execution_time_ms`: For timed operations
    - `error_type`: For exceptions (exception class name)
    - `stack_trace`: For exceptions (formatted traceback)
  - Output single-line JSON per log entry (no pretty-printing)
  - Compatible with CloudWatch Insights JSON parsing

- [ ] T911 [P2] [US6] Implement text formatter for local development
  - Create `ColoredTextFormatter` class extending logging.Formatter
  - Format: `[{timestamp}] {level:8} | {message}` with optional context
  - Add color coding for different log levels (using ANSI codes)
  - Make format human-readable for local debugging

- [ ] T912 [P2] [US6] Create logging setup utility function
  - `setup_logger(name: str, level: str, format: str, run_id: str) -> logging.Logger`
  - Configure logger with appropriate formatter based on LOG_FORMAT
  - Add StreamHandler for stdout (AgentCore captures stdout)
  - Add optional FileHandler for local file logging
  - Return configured logger instance
  - Support context injection via contextvars for run_id, assessment_level

### T920 Series: Integration with Application Logging

- [ ] T920 [P2] [US6] Initialize structured logging in `run_comprehensive_test.py`
  - Call `setup_logger()` at start of test with run_id
  - Configure logger based on environment (JSON for production, text for dev)
  - Get logger instance and use throughout test
  - Ensure all log output goes to stdout for AgentCore capture

- [ ] T921 [P2] [US6] Add structured logging to assessment generation workflow in `run_comprehensive_test.py`
  - Log event: `assessment_started` with context: {level, background_hash, run_id}
  - Log event: `kb_query_started` with context: {level, kb_id, query_summary}
  - Log event: `kb_query_completed` with context: {level, kb_id, result_count, execution_time_ms}
  - Log event: `assessment_generated` with context: {level, question_count, modules_covered, execution_time_ms}
  - Log event: `assessment_completed` with context: {level, total_time_ms, success: true}
  - Log event: `assessment_failed` with context: {level, error_type, error_message}
  - Use logger.info() for successful operations, logger.error() for failures

- [ ] T922 [P2] [US6] Add logging to KB tools in `src/kb_tools.py`
  - Import logger from structured_logger
  - Log KB query attempts: logger.info("kb_query_started", extra={"context": {...}})
  - Log KB query results with document count and retrieval time
  - Log KB query failures with error type and message
  - Log retry attempts for failed queries
  - Include KB ID and query summary in all KB-related logs

- [ ] T923 [P2] [US6] Add logging to S3 uploader in `src/s3_uploader.py`
  - Import logger from structured_logger
  - Log S3 upload attempts with assessment ID, format, destination
  - Log S3 upload success with URI and upload time
  - Log S3 upload failures with error type and retry count
  - Log batch upload statistics (success rate, total time)
  - Use structured context for all S3-related metadata

### T930 Series: Testing Structured Logging

- [ ] T930 [P] [US6] Write unit tests for structured logger in `examples/literacy-assessment/tests/test_structured_logger.py`
  - Test StructuredJSONFormatter formatting
  - Verify JSON output is valid and single-line
  - Test all required fields present (timestamp, level, message, context)
  - Test exception handling (error_type, stack_trace included)
  - Test ColoredTextFormatter for readability
  - Test setup_logger() configuration

- [ ] T931 [P] [US6] Write integration test for logging in `examples/literacy-assessment/tests/test_logging_integration.py`
  - Generate Level 1 assessment with structured logging enabled
  - Capture stdout/stderr output
  - Parse JSON log lines
  - Verify critical events logged (assessment_started, assessment_completed, kb_query)
  - Verify context fields populated correctly
  - Verify execution_time_ms tracked for timed operations
  - Verify log format compatible with CloudWatch Insights JSON parsing

### T940 Series: Monitoring & Dashboards (Optional Enhancement)

- [ ] T940 [P3] [US6] Create CloudWatch dashboard configuration in `examples/literacy-assessment/cloudwatch/dashboard.json`
  - Widget: Assessment generation rate (count per hour)
  - Widget: Average execution time by level
  - Widget: Success vs failure rate
  - Widget: KB query latency percentiles (p50, p95, p99)
  - Widget: S3 upload success rate
  - Widget: Error count by error type

- [ ] T941 [P3] [US6] Create CloudWatch Insights queries in `examples/literacy-assessment/cloudwatch/queries.md`
  - Query: Find all failed assessments
  - Query: Calculate average execution time by level
  - Query: Find slowest KB queries
  - Query: Count assessments by user background type
  - Query: Find all S3 upload failures

- [ ] T942 [P3] [US6] Create CloudWatch alarms configuration in `examples/literacy-assessment/cloudwatch/alarms.json`
  - Alarm: Assessment failure rate > 5%
  - Alarm: Average execution time > 60s
  - Alarm: S3 upload failure rate > 10%
  - Alarm: KB query errors > 5 in 5 minutes
  - SNS topic for alarm notifications

---

## Task Summary

| Phase | Priority | Task Count | Status |
|-------|----------|------------|--------|
| Phase 0: Setup & Foundation | P1 | 7 | ✅ Complete |
| Phase 1: Directory Structure | P1 | 13 | ✅ Complete |
| Phase 2: Foundation Components | P1 | 13 | ✅ Complete |
| Phase 3: Single Level (MVP) | P1 | 24 | ✅ Complete |
| Phase 4: Multi-Level Parallel | P2 | 12 | ⏳ Ready |
| Phase 5: Background Calibration | P3 | 12 | ⏳ Ready |
| Phase 6: Result Tracking | P4 | 11 | ⏳ Ready |
| Phase 7: Documentation & Polish | P2-P3 | 15 | ✅ Partial (README + docs complete) |
| **Phase 8: S3 Upload (NEW)** | **P2** | **18** | **⏳ Pending** |
| **Phase 9: Structured Logging (NEW)** | **P2** | **14** | **⏳ Pending** |
| **Total** | | **111** | **61 complete (MVP), 50 pending (P2-P4)** |

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
- **S3 Upload (Phase 8)**: Can start after Phase 3 (MVP) complete - Independent from Phases 4-6
- **CloudWatch (Phase 9)**: Can start after Phase 3 (MVP) complete - Independent from Phases 4-6
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: ✅ Complete - MVP foundation
- **User Story 2 (P2)**: Depends on US1 - Uses same agent infrastructure
- **User Story 3 (P3)**: Depends on US1 - Extends question generation
- **User Story 4 (P4)**: Depends on US1 - Adds metadata tracking
- **User Story 5 (P2) - S3 Upload**: Depends on US1 - Extends file output
- **User Story 6 (P2) - CloudWatch**: Depends on US1 - Adds logging layer

### Parallel Opportunities for Phases 8 & 9

- **Phase 8 (S3) and Phase 9 (CloudWatch) can run in parallel** - They touch different files:
  - S3: `s3_uploader.py`, `test_s3_uploader.py`, `test_s3_integration.py`
  - CloudWatch: `cloudwatch_logger.py`, `logger.py`, `test_cloudwatch_logger.py`, `test_cloudwatch_integration.py`
  - Both update: `config.py` (separate sections), `.env.example` (separate sections), `validate_config.py` (separate validation functions)

- Within Phase 8:
  - T800 and T801 can run in parallel (config.py vs .env.example)
  - T810, T811, T812, T813 can run in sequence (s3_uploader.py methods)
  - T830 and T831 can run in parallel (unit tests vs integration tests)

- Within Phase 9:
  - T900 and T901 can run in parallel (config.py vs .env.example)
  - T910, T911, T912, T913 can run in sequence (cloudwatch_logger.py implementation)
  - T920, T921, T922, T923 can run after T920 (integration tasks)
  - T930 and T931 can run in parallel (unit tests vs integration tests)

---

## MVP Definition (P1 Only) ✅

**Status**: **COMPLETE** - MVP successfully delivered and tested!

**MVP Delivered**: User Story 1 - Single Level Assessment Generation

**Completed MVP Tasks**:
- ✅ Phase 1: T100-T112 (Directory structure, dependencies)
- ✅ Phase 2: T200-T223 (Configuration, models, KB tools)
- ✅ Phase 3: T300-T333 (Question generation, single-level subagents, main agent)
- ✅ Phase 7: T700, T720-T722 (Documentation, basic testing)

**MVP Success Criteria - ALL ACHIEVED**:
1. ✅ Can generate single-level assessment for any level (1-4)
2. ✅ Assessment contains 7 MC + 3 OE questions
3. ✅ Questions cover 5+ curriculum modules
4. ✅ Generation completes in <60 seconds
5. ✅ Output is valid Assessment JSON
6. ✅ Configuration validation passes
7. ✅ Unit tests pass
8. ✅ Integration test passes

**Test Results**:
- All 4 levels successfully generated
- Total execution: ~18.5 minutes (sequential)
- Level 1: 293.5s | 7MC + 3OE | 7 modules | 7 KB docs
- Level 2: 287.7s | 7MC + 3OE | 7 modules | 7 KB docs
- Level 3: 357.8s | 7MC + 3OE | 10 modules | 10 KB docs
- Level 4: 475.8s | 7MC + 3OE | 7 modules | 7 KB docs

---

## Next Phase Recommendation: Phase 8 (S3 Upload) + Phase 9 (CloudWatch)

**Why these phases now?**:
1. **Production-ready infrastructure**: S3 and CloudWatch are essential for deployment
2. **Parallel execution**: Both phases can be implemented simultaneously by different developers
3. **Independent of user stories**: Don't block on P3/P4 features - add infrastructure now
4. **Enable monitoring**: CloudWatch logging provides visibility into production performance

**Execution Strategy**:

### Week 1: Infrastructure (P2)
**Developer A - S3 Upload (Phase 8)**:
- Days 1-2: T800-T813 (S3 configuration and uploader implementation)
- Days 3-4: T820-T822 (Integration with assessment workflow)
- Day 5: T830-T832 (Testing and validation)

**Developer B - CloudWatch Logging (Phase 9)**:
- Days 1-2: T900-T913 (CloudWatch configuration and logger implementation)
- Days 3-4: T920-T923 (Integration with application logging)
- Day 5: T930-T932 (Testing and validation)

**Both developers can work in parallel with minimal conflicts!**

### Week 2: Core Features (P2-P3)
After infrastructure is complete, proceed with:
- Phase 4 (Multi-level parallel) - P2 priority
- Phase 5 (Background calibration) - P3 priority

---

## Execution Notes

**For S3 Upload (Phase 8)**:
- Requires AWS S3 bucket setup before development (create: `literacy-assessments-dev`)
- Use same boto3 session pattern as KB tools for authentication
- Test with small S3 bucket first, expand to production later
- Consider S3 lifecycle policies for cost optimization

**For Structured Logging (Phase 9)**:
- Uses standard Python logging (no CloudWatch SDK dependencies)
- AgentCore automatically captures stdout logs and sends to CloudWatch
- AgentCore manages log group creation and retention
- Use structured JSON format for CloudWatch Insights compatibility
- Logs emitted to stdout for AgentCore capture

**General**:
- Both features are optional (controlled by environment flags)
- Graceful degradation if AWS services unavailable
- Update quickstart.md with new AWS permissions required
- Add S3 and CloudWatch sections to README.md

---

## Critical Path Updates

**New blocking dependencies**:
1. **T800**: S3 Config (blocks T810-T832)
2. **T810**: S3 Uploader Client (blocks T811-T813, T820-T822)
3. **T900**: CloudWatch Config (blocks T910-T932)
4. **T910**: CloudWatch Handler (blocks T911-T913, T920-T923)

**Parallel opportunities**:
- T800 and T900 can run in parallel (different config sections)
- T810 series and T910 series can run in parallel (different files)
- T830 and T930 can run in parallel (different test files)

---

## Notes

- **AWS Configuration**: S3 bucket name will be added to `.env.example` (no CloudWatch config needed)
- **Isolation**: All code continues in `examples/literacy-assessment/` - no core library changes
- **Testing**: Mock S3 client for unit tests, real S3 for integration tests; structured logging tested via stdout capture
- **Performance**: S3 upload adds ~1-5s, structured logging adds <50ms per assessment
- **Cost**: S3 storage ~$0.023/GB/month; CloudWatch Logs managed by AgentCore (no direct cost from application)
- **AgentCore Integration**: Application emits JSON logs to stdout, AgentCore automatically captures and forwards to CloudWatch

**Ready to implement? Start with T800 (S3 Config) and T900 (Logging Config) in parallel!**
