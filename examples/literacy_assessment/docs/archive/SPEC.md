# Literacy Assessment System - Specification

## Overview

The Literacy Assessment System generates personalized AI literacy assessments across 4 proficiency levels, using AWS Bedrock Knowledge Bases and Deep Agents framework to create background-aware questions with full source traceability.

## Problem Statement

Organizations need to assess employee AI literacy across different proficiency levels, but:
- Manual assessment creation is time-consuming and inconsistent
- Generic assessments don't adapt to user backgrounds
- Questions lack source traceability to training materials
- Sequential processing makes generating multiple assessments slow

## Solution

Multi-agent assessment generation system that:
1. Delegates to level-specific subagents for parallel processing
2. Queries AWS Bedrock Knowledge Bases for curriculum content
3. Generates background-aware questions (finance, IT, HR, etc.)
4. Tracks source PDFs per question for traceability
5. Produces JSON and Markdown outputs with continuous numbering

## User Scenarios

### Scenario 1: HR Director Generating Assessments
**Actor**: HR Director at 500-person company
**Goal**: Generate Level 1 and Level 2 assessments for new AI training program
**Flow**:
1. Runs comprehensive test script specifying target levels
2. System generates assessments in parallel using level-specific subagents
3. Reviews generated questions in markdown format
4. Verifies each question links to source training documents
5. Deploys assessments to learning management system

**Success Criteria**:
- All 4 levels generate successfully without throttling
- Each question shows source PDF(s) used for generation
- Questions numbered continuously from 1-10 (not restarting per section)
- Markdown files are human-readable and properly formatted

### Scenario 2: L&D Team Validating Question Quality
**Actor**: Learning & Development specialist
**Goal**: Verify assessment questions match curriculum and are appropriate for target audience
**Flow**:
1. Opens generated JSON assessment file
2. Reviews each question's kb_document_sources array
3. Cross-references with actual PDF documents in Knowledge Base
4. Validates difficulty progression across levels
5. Confirms background-aware personalization worked correctly

**Success Criteria**:
- Every question has non-empty kb_document_sources array
- Source documents are relevant to question content
- Questions adapt to user background (e.g., finance examples for finance analysts)
- Difficulty increases from Level 1 (beginner) to Level 4 (expert)

## Functional Requirements

### FR-1: Multi-Level Assessment Generation
- **Input**: User request specifying level(s) and background
- **Process**: Main orchestrator delegates to appropriate level-specific subagents
- **Output**: JSON and Markdown assessment files for each level
- **Constraints**:
  - Exactly 7 multiple choice + 3 open-ended questions per level
  - Minimum 5 different modules covered per assessment
  - Each level must complete within 6 minutes (accounting for Knowledge Base queries)

### FR-2: Background-Aware Question Generation
- **Input**: User background description (role, years of experience, domain)
- **Process**: Subagent parses background and adapts question scenarios
- **Output**: Questions using domain-appropriate examples (finance, IT, HR, etc.)
- **Rules**:
  - Technical backgrounds get technical scenarios (APIs, architecture)
  - Business backgrounds get business scenarios (ROI, budgets, compliance)
  - Domain terminology preserved while adjusting complexity by level

### FR-3: Knowledge Base Source Tracking
- **Input**: KB query results from AWS Bedrock with document metadata
- **Process**: Extract filename and S3 URI from each KB query result
- **Output**: Per-question kb_document_sources array with {filename, s3_uri}
- **Rules**:
  - Each question must track which KB queries were used for its generation
  - Aggregate unique sources for assessment-level summary
  - Preserve S3 URIs for downstream verification/auditing

### FR-4: Continuous Question Numbering
- **Input**: Assessment with 7 MC + 3 OE questions
- **Process**: Number questions 1-10 continuously across both sections
- **Output**: Markdown with "Question 1" through "Question 10"
- **Rules**:
  - Multiple choice: Questions 1-7
  - Open-ended: Questions 8-10
  - No number restarting between sections

### FR-5: Throttling and Retry Resilience
- **Input**: AWS Bedrock API throttling responses
- **Process**: Exponential backoff retry with max 5 attempts
- **Output**: Successful completion even under rate limiting
- **Configuration**:
  - Read timeout: 180 seconds
  - Connect timeout: 60 seconds
  - Retry mode: adaptive
  - Max attempts: 5

## Success Criteria

### Performance
- ✅ All 4 levels complete successfully in single test run
- ✅ Level 4 no longer fails with throttling errors
- ✅ Total execution time < 15 minutes for all 4 levels
- ✅ Retry logic handles rate limiting transparently

### Quality
- ✅ 100% of questions have non-empty kb_document_sources
- ✅ Questions numbered continuously 1-10 in all markdown files
- ✅ Each level covers 5+ unique modules from Knowledge Base
- ✅ Background-aware personalization evident in question scenarios

### Traceability
- ✅ Every generated question traceable to source PDF(s)
- ✅ Markdown displays source documents under each question
- ✅ JSON includes both question-level and assessment-level sources
- ✅ S3 URIs enable programmatic verification

## Key Entities

### Assessment
```python
{
  "level": int,  # 1-4
  "multiple_choice_questions": [MCQuestion],
  "open_ended_questions": [OEQuestion],
  "user_background": str,
  "modules_covered": [str],
  "kb_document_sources": [DocumentSource]  # Aggregated from questions
}
```

### MCQuestion / OEQuestion
```python
{
  "question_text": str,
  "module_source": str,
  "difficulty": str,  # "beginner", "intermediate", "advanced"
  "kb_document_sources": [DocumentSource],  # NEW: Per-question tracking
  # ... type-specific fields
}
```

### DocumentSource
```python
{
  "filename": str,  # e.g., "L1-M1_Introduction_to_AI.pdf"
  "s3_uri": str     # Full S3 path
}
```

## Technical Constraints

- AWS Bedrock Knowledge Base IDs:
  - Level 1 (Foundational): QADZTSAPWX
  - Level 2 (Intermediate): KGGD2PTQ2N
  - Level 3 (Advanced): 7MGFSODDVI
  - Level 4 (Expert): CHYWO1H6OM
  - **⚠️ KNOWN ISSUE**: `src/config.py` line 33 incorrectly uses 7MGFSODDVI for Level 4 - see `docs/BUGFIX-level4-kb-id.md`
- Model: Claude Sonnet 4 (eu.anthropic.claude-sonnet-4-20250514-v1:0)
- Region: eu-central-1
- Deep Agents framework for subagent orchestration
- LangGraph for agent execution

## Assumptions

1. Knowledge Base PDFs contain sufficient diverse content for 10 questions per level
2. User backgrounds provided are specific enough for domain identification
3. AWS credentials are properly configured for Bedrock access
4. File system is writable for output/assessments/ and output/logs/ directories
5. Test runs are sequential (not concurrent parallel executions)

## Out of Scope

- Question difficulty validation (assumed correct if from appropriate level KB)
- Answer key generation for open-ended questions
- Real-time question generation (all assessment creation is batch)
- Multi-language support (English only)
- Question pool management / deduplication across multiple runs
- Integration with Learning Management Systems (LMS)

## Recent Changes (2025-11-03)

### Fixed Continuous Question Numbering
- **Problem**: Markdown files restarted numbering at Question 1 for Open-Ended section
- **Root Cause**: `enumerate(questions, 1)` used separately for MC and OE loops
- **Solution**: Use shared `question_num` variable incremented across both loops
- **Files Modified**: `run_comprehensive_test.py` lines 263-314
- **Verification**: Questions now numbered 1-7 (MC) then 8-10 (OE)

### Added Per-Question Source Tracking
- **Problem**: Source PDFs shown only at assessment level, not per question
- **Solution**: Updated subagent prompts to include kb_document_sources in each question
- **Impact**: Enables tracing each individual question to its source documents
- **Files Modified**: `src/agent.py` (all 4 subagent prompts), `run_comprehensive_test.py` (extraction logic)

### Improved Throttling Resilience
- **Problem**: Level 4 consistently failed with "Too many tokens" throttling error
- **Solution**: Added botocore retry config with max_attempts=5, adaptive mode
- **Impact**: All 4 levels now complete successfully in comprehensive test
- **Files Modified**: `run_comprehensive_test.py` create_model_with_fallback()

### CRITICAL BUG IDENTIFIED (2025-11-03): Wrong Knowledge Base for Level 4
- **Problem**: Level 4 using Level 3's Knowledge Base (7MGFSODDVI) instead of dedicated Level 4 KB (CHYWO1H6OM)
- **Impact**: All Level 4 assessments generated to date use Advanced content instead of Expert content
- **Root Cause**: `src/config.py` line 33 has incorrect default value
- **Status**: Documented in `docs/BUGFIX-level4-kb-id.md`, awaiting fix implementation
- **Priority**: CRITICAL - must fix before generating more Level 4 assessments
- **Validation**: After fix, regenerate Level 4 and verify document sources reference CHYWO1H6OM KB
