# Changelog

All notable changes to the Literacy Assessment Agent deployment will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Added - 2025-11-06

#### Markdown Format Support for S3 Uploads

**Feature**: Assessments are now uploaded to S3 in both JSON and Markdown formats automatically.

**Implementation Details**:
- Modified `s3_uploader.py:_prepare_assessment_content()` to support markdown format conversion
- Updated `upload_assessment_to_s3()` tool function to upload both formats with synchronized timestamps
- All 4 level-specific subagents (Level 1-4) now return both S3 URIs in their responses
- Markdown files use human-readable format with proper headers, sections, and formatting

**Files Modified**:
- `examples/literacy_assessment/src/s3_uploader.py` (lines 147-167, 337-399)
- `examples/literacy_assessment/src/agent.py` (lines 151-152, 283-284, 419-420, 558-559)

**S3 Output Structure**:
```
s3://literacy-framework-development-961105418118-eu-central-1/
└── learning_path/
    └── assessments/
        ├── level_1/
        │   ├── level_1_YYYYMMDD_HHMMSS.json
        │   └── level_1_YYYYMMDD_HHMMSS.md
        ├── level_2/
        │   ├── level_2_YYYYMMDD_HHMMSS.json
        │   └── level_2_YYYYMMDD_HHMMSS.md
        ├── level_3/
        │   ├── level_3_YYYYMMDD_HHMMSS.json
        │   └── level_3_YYYYMMDD_HHMMSS.md
        └── level_4/
            ├── level_4_YYYYMMDD_HHMMSS.json
            └── level_4_YYYYMMDD_HHMMSS.md
```

**Benefits**:
- **Machine-readable**: JSON format for programmatic processing and integration
- **Human-readable**: Markdown format for easy review, printing, and sharing
- **Synchronized**: Both formats use the same timestamp for consistent naming
- **Automatic**: No changes required to agent invocation - both formats uploaded automatically

**Deployment Status**: ✅ Deployed and verified on 2025-11-06
- Agent ARN: `arn:aws:bedrock-agentcore:eu-central-1:961105418118:runtime/literacy_assessment-nOAwV9Bfmp`
- Build time: 1m 21s
- Test verification: Confirmed both JSON (21KB) and Markdown (19KB) files in S3

**Example Response**:
```json
{
  "status": "success",
  "s3_uri_json": "s3://.../level_2_20251106_034423.json",
  "s3_uri_markdown": "s3://.../level_2_20251106_034423.md",
  "level": 2,
  "timestamp": "2025-11-06T03:44:22.918557"
}
```

## [1.0.0] - 2025-11-05

### Added

#### Initial AgentCore Deployment
- AWS Bedrock AgentCore deployment infrastructure
- Multi-level literacy assessment agent (Levels 1-4)
- Deep Agents framework integration with 4 specialized subagents
- Knowledge Base integration for all 4 literacy levels
- S3 integration for reading KB documents and writing assessments (JSON format)
- IAM role automation with all necessary permissions
- CloudWatch logging with structured logs
- Docker containerization for serverless execution
- Parallel execution support for multi-level assessments
- Background-aware question generation
- Document source traceability per question

### Components

**Core Files**:
- `serve_bedrock.py` - AgentCore entrypoint wrapper
- `deploy.py` - Deployment orchestration
- `utils.py` - IAM role creation with permissions
- `examples/literacy_assessment/src/agent.py` - Multi-agent orchestrator
- `examples/literacy_assessment/src/kb_tools.py` - Knowledge Base query tools
- `examples/literacy_assessment/src/s3_uploader.py` - S3 upload client
- `examples/literacy_assessment/src/config.py` - Configuration management
- `examples/literacy_assessment/src/models.py` - Pydantic data models
- `examples/literacy_assessment/src/questions.py` - Question generation and formatting

**Infrastructure**:
- IAM Role: `agentcore-literacy_assessment-role-0511`
- ECR Repository: `961105418118.dkr.ecr.eu-central-1.amazonaws.com/bedrock-agentcore-literacy_assessment`
- S3 Bucket: `literacy-framework-development-961105418118-eu-central-1`
- Region: `eu-central-1`

**Knowledge Bases**:
- Level 1 (Foundational): `QADZTSAPWX`
- Level 2 (Intermediate): `KGGD2PTQ2N`
- Level 3 (Advanced): `7MGFSODDVI`
- Level 4 (Expert): `CHYWO1H6OM`

### Features

**Assessment Generation**:
- 7 multiple-choice questions per level (4 options each)
- 3 open-ended questions per level (with evaluation rubrics)
- Minimum 5 modules covered per assessment
- Background-aware question tailoring (domain-specific scenarios)
- Difficulty calibration per level
- Document source traceability

**Deployment**:
- One-command deployment: `python deploy.py`
- Automatic IAM role creation with least-privilege permissions
- Container build and push to ECR
- AgentCore configuration and launch
- Smoke test validation
- ~2-3 minute deployment time

**Monitoring**:
- CloudWatch Logs integration
- Structured JSON logging
- Performance metrics
- Error traces with context

### Technical Details

**Models Used**:
- Primary: `eu.anthropic.claude-sonnet-4-5-20250929-v1:0`
- Fast operations: `eu.anthropic.claude-haiku-4-5-20251001-v1:0`
- Fallback: `eu.anthropic.claude-sonnet-4-20250514-v1:0`

**Timeouts**:
- Bedrock read timeout: 300s (5 minutes)
- Bedrock connect timeout: 60s
- Assessment timeout: 60s per level

**Scaling**:
- Automatic scaling via AgentCore
- Serverless architecture (pay-per-use)
- Concurrent execution support for multi-level requests
