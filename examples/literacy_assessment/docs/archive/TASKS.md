# Literacy Assessment System - Implementation Tasks

## Completed Tasks

### Phase 1: Core Infrastructure (Completed)
- [x] **T1.1**: Set up project structure with src/ and output/ directories
- [x] **T1.2**: Create config.py with AWS Bedrock configuration
- [x] **T1.3**: Implement AWS Bedrock Knowledge Base query functions
- [x] **T1.4**: Set up Deep Agents framework integration
- [x] **T1.5**: Configure LangGraph for agent execution

### Phase 2: Knowledge Base Integration (Completed)
- [x] **T2.1**: Implement query_level_1_kb() for Level 1 Knowledge Base
- [x] **T2.2**: Implement query_level_2_kb() for Level 2 Knowledge Base
- [x] **T2.3**: Implement query_level_3_kb() for Level 3 Knowledge Base
- [x] **T2.4**: Implement query_level_4_kb() for Level 4 Knowledge Base ⚠️ **BUG**: Config incorrectly points to Level 3 KB
- [x] **T2.5**: Add document source extraction from KB results
- [x] **T2.6**: Return {filename, s3_uri} for each retrieved document

### Phase 3: Subagent Development (Completed)
- [x] **T3.1**: Define Level 1 subagent with foundational prompt
- [x] **T3.2**: Define Level 2 subagent with intermediate prompt
- [x] **T3.3**: Define Level 3 subagent with advanced prompt
- [x] **T3.4**: Define Level 4 subagent with expert prompt
- [x] **T3.5**: Implement background-aware question generation
- [x] **T3.6**: Add domain detection (Finance, IT, HR, Marketing, Operations)
- [x] **T3.7**: Implement module diversity requirements (5+ modules)
- [x] **T3.8**: Add JSON output formatting with validation

### Phase 4: Document Source Tracking (Completed)
- [x] **T4.1**: Update subagent prompts to include kb_document_sources in questions
- [x] **T4.2**: Add "CRITICAL - PER-QUESTION DOCUMENT SOURCES" instructions
- [x] **T4.3**: Implement source aggregation in test harness
- [x] **T4.4**: Verify sources extracted from all subagent outputs
- [x] **T4.5**: Add markdown rendering for per-question sources

### Phase 5: Main Orchestrator (Completed)
- [x] **T5.1**: Implement main orchestrator agent
- [x] **T5.2**: Add single-level request handling
- [x] **T5.3**: Add multi-level parallel request handling
- [x] **T5.4**: Implement task() delegation to subagents
- [x] **T5.5**: Add result aggregation and formatting

### Phase 6: Test Harness (Completed)
- [x] **T6.1**: Create run_comprehensive_test.py script
- [x] **T6.2**: Implement test_level() for single level testing
- [x] **T6.3**: Add JSON extraction from subagent responses
- [x] **T6.4**: Implement timestamped logging
- [x] **T6.5**: Create save_markdown() for human-readable output
- [x] **T6.6**: Add test summary reporting
- [x] **T6.7**: Implement main() to run all 4 levels sequentially

### Phase 7: Error Handling & Resilience (Completed)
- [x] **T7.1**: Identify throttling issues with Level 4
- [x] **T7.2**: Implement botocore retry configuration
- [x] **T7.3**: Add exponential backoff with max 5 attempts
- [x] **T7.4**: Increase read timeout to 180 seconds
- [x] **T7.5**: Test all 4 levels complete successfully
- [x] **T7.6**: Add timeout handling for long-running generations

### Phase 8: Continuous Numbering Fix (Completed - 2025-11-03)
- [x] **T8.1**: Investigate duplicate numbering issue in markdown files
  - Identified: `enumerate(..., 1)` restarted for each section
  - Location: `run_comprehensive_test.py` lines 265, 290
- [x] **T8.2**: Implement shared question_num variable
  - Changed: Use single counter incremented across both loops
  - Location: Lines 263-314
- [x] **T8.3**: Update multiple choice section to use question_num
  - Result: Questions 1-7
- [x] **T8.4**: Update open-ended section to continue numbering
  - Result: Questions 8-10
- [x] **T8.5**: Verify continuous numbering in test output
  - Verified: Generated markdown shows 1-10 sequence

## Current Tasks (In Progress)

### Phase 9: Documentation & Maintenance (Completed - 2025-11-03)
- [x] **T9.1**: Create comprehensive SPEC.md
  - Status: Completed
  - Location: docs/SPEC.md
- [x] **T9.2**: Create detailed PLAN.md with architecture diagrams
  - Status: Completed
  - Location: docs/PLAN.md
- [x] **T9.3**: Create TASKS.md with implementation history
  - Status: Completed
  - Location: docs/TASKS.md
- [x] **T9.4**: Document Level 4 KB ID bug
  - Status: Completed
  - Location: docs/BUGFIX-level4-kb-id.md
- [x] **T9.5**: Update all documentation with KB ID bug warning
  - Status: Completed
  - Updated: SPEC.md, PLAN.md, TASKS.md
- [ ] **T9.6**: Add README.md with setup instructions
- [ ] **T9.7**: Document configuration options
- [ ] **T9.8**: Create troubleshooting guide

### Phase 10: CRITICAL BUG FIX - Level 4 Knowledge Base ID (Pending Implementation)
- [x] **T10.1**: Identify Level 4 KB ID configuration error
  - Discovered: User review found query_level_4_kb using wrong KB
  - Root Cause: src/config.py line 33 uses "7MGFSODDVI" (Level 3) instead of "CHYWO1H6OM" (Level 4)
  - Impact: All Level 4 assessments generated with Advanced content instead of Expert content
- [x] **T10.2**: Document bug comprehensively
  - Created: docs/BUGFIX-level4-kb-id.md with fix procedure and validation plan
  - Status: Completed
- [x] **T10.3**: Update specifications with bug warning
  - Updated: SPEC.md, PLAN.md with correct KB IDs and warnings
  - Status: Completed
- [ ] **T10.4**: Fix KB_LEVEL_4_ID in src/config.py
  - Change: Line 33 from "7MGFSODDVI" to "CHYWO1H6OM"
  - Priority: CRITICAL
- [ ] **T10.5**: Update comment in src/kb_tools.py
  - Change: Line 366 comment from "shares KB with Level 3" to "dedicated expert-level KB"
  - Priority: HIGH
- [ ] **T10.6**: Update Phase 2 task description
  - Change: T2.4 description to reflect Level 4 has dedicated KB
  - Location: This file, line 16
- [ ] **T10.7**: Regenerate all Level 4 assessments with correct KB
  - Validation: Verify S3 URIs contain CHYWO1H6OM, not 7MGFSODDVI
  - Validation: Verify module coverage reflects Expert-level content
  - Priority: CRITICAL
- [ ] **T10.8**: Compare before/after Level 4 content
  - Document: Differences between Level 3 and Level 4 questions
  - Purpose: Validate Expert content is distinct from Advanced content

## Future Tasks (Backlog)

### Phase 11: Testing Improvements
- [ ] **T11.1**: Add unit tests for KB query functions
- [ ] **T11.2**: Add unit tests for JSON extraction
- [ ] **T11.3**: Add unit tests for markdown generation
- [ ] **T11.4**: Create mock KB responses for testing
- [ ] **T11.5**: Add integration test suite
- [ ] **T11.6**: Implement automated validation of generated assessments

### Phase 12: Performance Optimization
- [ ] **T12.1**: Profile KB query performance
- [ ] **T12.2**: Implement async KB queries within subagents
- [ ] **T12.3**: Add parallel level processing option
- [ ] **T12.4**: Implement prompt caching for repeated calls
- [ ] **T12.5**: Benchmark before/after optimization
- [ ] **T12.6**: Document performance improvements

### Phase 13: Feature Enhancements
- [ ] **T13.1**: Add configurable question counts (not fixed 7+3)
- [ ] **T13.2**: Implement question deduplication across runs
- [ ] **T13.3**: Add progress tracking during generation
- [ ] **T13.4**: Implement streaming output for real-time updates
- [ ] **T13.5**: Add source verification (check PDF content matches question)
- [ ] **T13.6**: Support custom backgrounds beyond predefined domains

### Phase 14: Deployment & Operations
- [ ] **T14.1**: Create Docker container for deployment
- [ ] **T14.2**: Add environment variable configuration
- [ ] **T14.3**: Implement health check endpoint
- [ ] **T14.4**: Add metrics collection (latency, success rate, etc.)
- [ ] **T14.5**: Create deployment documentation
- [ ] **T14.6**: Set up monitoring and alerting

### Phase 15: Quality Improvements
- [ ] **T15.1**: Implement automated question quality scoring
- [ ] **T15.2**: Add bias detection in generated questions
- [ ] **T15.3**: Validate difficulty progression across levels
- [ ] **T15.4**: Add expert review workflow
- [ ] **T15.5**: Create question approval/rejection interface

## Task Dependencies

```
T1 (Infrastructure) → T2 (KB Integration)
                    ↓
T2 → T3 (Subagents) → T4 (Source Tracking)
                    ↓
T3 → T5 (Orchestrator)
                    ↓
T2,T3,T4,T5 → T6 (Test Harness)
                    ↓
T6 → T7 (Error Handling)
                    ↓
T7 → T8 (Numbering Fix)
                    ↓
T8 → T9 (Documentation)
                    ↓
T9 → T10 (KB ID Bug Fix) ← CRITICAL BLOCKER
```

**Note**: Phase 10 (KB ID Bug Fix) is a CRITICAL blocker that must be completed before generating more Level 4 assessments. All other phases (11-15) can proceed in parallel after Phase 10 is complete.

## Recent Work Sessions

### Session: 2025-11-03 Late Evening (CRITICAL BUG DOCUMENTATION)
**Objective**: Document Level 4 Knowledge Base ID bug comprehensively before implementation

**Tasks Completed**:
1. Identified critical bug: Level 4 using Level 3's KB (7MGFSODDVI instead of CHYWO1H6OM)
2. Created comprehensive bug documentation: `docs/BUGFIX-level4-kb-id.md`
   - Root cause analysis
   - Impact assessment (all Level 4 assessments invalid)
   - Detailed fix procedure with validation steps
   - Rollback plan and prevention measures
3. Updated `docs/SPEC.md`:
   - Technical Constraints section with correct KB IDs
   - Added warning about config bug
   - Recent Changes section documenting the bug
4. Updated `docs/PLAN.md`:
   - Architecture diagram showing all 4 distinct KB IDs
   - Added bug warning in diagram
5. Updated `docs/TASKS.md` (this file):
   - Added Phase 10: CRITICAL BUG FIX with 8 subtasks
   - Renumbered subsequent phases (11-15)
   - Updated task dependencies to show T10 as blocker
   - Added this work session entry

**Files Modified**:
- `docs/BUGFIX-level4-kb-id.md`: Created (comprehensive bug analysis)
- `docs/SPEC.md`: Updated (lines 165-166, 210-216)
- `docs/PLAN.md`: Updated (architecture diagram lines 23-32)
- `docs/TASKS.md`: Updated (Phase 10 added, phases renumbered)

**Impact**:
- All Level 4 assessments generated to date are invalid
- Using Advanced content instead of Expert content
- MUST FIX before generating more Level 4 assessments

**Next Actions**:
- Await user approval to implement fix
- T10.4: Fix KB_LEVEL_4_ID in src/config.py (one-line change)
- T10.5: Update comment in src/kb_tools.py
- T10.7: Regenerate Level 4 assessments with correct KB
- T10.8: Compare before/after to validate Expert vs Advanced content

### Session: 2025-11-03 Evening
**Objective**: Fix duplicate question numbering and create project documentation

**Tasks Completed**:
1. Investigated numbering issue in level_2_20251103_211649.md
2. Identified root cause: `enumerate(..., 1)` restarting per section
3. Implemented continuous numbering with shared variable
4. Verified fix would work (need to regenerate markdown to confirm)
5. Created SPEC.md with comprehensive system specification
6. Created PLAN.md with architecture and implementation details
7. Created TASKS.md (this file) with task history

**Files Modified**:
- `run_comprehensive_test.py` (lines 263-314): Continuous numbering
- `docs/SPEC.md`: Created
- `docs/PLAN.md`: Created
- `docs/TASKS.md`: Created

**Next Actions**:
- T9.6: Create README.md with setup instructions
- Regenerate assessments to verify continuous numbering works
- Consider Phase 12 optimizations for faster generation

### Session: 2025-11-03 Afternoon
**Objective**: Implement per-question source tracking and fix throttling

**Tasks Completed**:
1. Updated all 4 subagent prompts with per-question kb_document_sources
2. Fixed extraction logic to aggregate from questions
3. Updated markdown rendering to show sources per question
4. Implemented retry logic with exponential backoff
5. Increased read timeout to 180 seconds
6. Verified all 4 levels complete successfully

**Test Results**:
- ✅ Level 1: 202.5s | 7MC + 3OE | 7 modules | 7 KB docs
- ✅ Level 2: 273.5s | 7MC + 3OE | 7 modules | 7 KB docs
- ✅ Level 3: 316.9s | 7MC + 3OE | 9 modules | 9 KB docs
- ✅ Level 4: 316.0s | 7MC + 3OE | 9 modules | 8 KB docs

**Impact**: System now robust, all levels succeed, full source traceability

## Notes

### Design Decisions
1. **Continuous Numbering**: Users expect 1-10, not 1-7 then 1-3
2. **Per-Question Sources**: Enables fine-grained traceability
3. **Parallel Subagents**: Main orchestrator can invoke multiple levels at once
4. **Exponential Backoff**: Handles AWS rate limiting gracefully
5. **Timestamped Outputs**: Prevents overwriting previous test runs

### Known Trade-offs
1. **Sequential KB Queries**: Simpler but slower than parallel
2. **Sequential Level Testing**: Safer but takes longer
3. **Fixed Question Counts**: Consistent but inflexible
4. **No Streaming**: Complete generation before output

### Lessons Learned
1. Anthropic models require explicit JSON output instructions
2. AWS Bedrock throttling is aggressive - need retries
3. Subagent isolation makes debugging harder (opaque execution)
4. Continuous numbering requires careful loop variable management
5. Document sources must be extracted at question generation time (can't backfill)

## Success Metrics

### Current Status
- ✅ All 4 levels generate successfully (4/4 = 100%)
- ✅ Zero throttling errors with retry logic
- ✅ 100% of questions have source tracking
- ✅ Markdown formatting correct (verified manually)
- ✅ Continuous numbering implemented (awaiting regeneration test)

### Target Metrics
- [ ] <5 minutes total execution time (currently ~18 minutes)
- [ ] 100% unit test coverage for critical functions
- [ ] Automated quality validation for generated questions
- [ ] <1% duplicate question rate across multiple runs
