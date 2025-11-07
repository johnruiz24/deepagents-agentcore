# Literacy Assessment System - Implementation Plan

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Main Orchestrator Agent                   │
│  - Parses user request (level, background)                  │
│  - Delegates to level-specific subagents                    │
│  - Formats and saves final output                           │
└───────────────┬─────────────────────────────────────────────┘
                │
                ├─────────────────────────────────────┬───────────────────┬───────────────────┐
                │                                     │                   │                   │
        ┌───────▼─────────┐                ┌────────▼────────┐  ┌───────▼──────────┐ ┌────▼──────────┐
        │ Level 1 Subagent│                │ Level 2 Subagent│  │Level 3 Subagent  │ │Level 4 Subagent│
        │ (Foundational)  │                │ (Intermediate)  │  │(Advanced)        │ │(Expert)        │
        │ - 7 MC + 3 OE   │                │ - 7 MC + 3 OE   │  │- 7 MC + 3 OE     │ │- 7 MC + 3 OE   │
        └───────┬─────────┘                └────────┬────────┘  └───────┬──────────┘ └────┬──────────┘
                │                                    │                   │                  │
                └──────────────────┬─────────────────┴───────────────────┴──────────────────┘
                                   │
                         ┌─────────▼─────────┐
                         │ AWS Bedrock       │
                         │ Knowledge Bases   │
                         │ - L1: QADZTSAPWX  │
                         │ - L2: KGGD2PTQ2N  │
                         │ - L3: 7MGFSODDVI  │
                         │ - L4: CHYWO1H6OM  │
                         │ ⚠️  BUG: config   │
                         │ uses L3 for L4!   │
                         └───────────────────┘
```

## Component Design

### 1. Knowledge Base Tools (`src/kb_tools.py`)

**Purpose**: Query AWS Bedrock Knowledge Bases and extract document sources

**Functions**:
- `query_level_1_kb(query: str)` → Dict with content + document_sources
- `query_level_2_kb(query: str)` → Dict with content + document_sources
- `query_level_3_kb(query: str)` → Dict with content + document_sources
- `query_level_4_kb(query: str)` → Dict with content + document_sources

**Key Implementation Details**:
```python
# Extract document sources from KB results
for result in results:
    location = result.get('location', {})
    s3_location = location.get('s3Location', {})
    if s3_location:
        uri = s3_location.get('uri', '')
        filename = uri.split('/')[-1]
        document_sources.append({
            "filename": filename,
            "s3_uri": uri
        })
```

### 2. Subagent Definitions (`src/agent.py`)

**Purpose**: Level-specific assessment generation with KB integration

**Structure** (per level):
```python
{
    "name": "level-N-assessment-agent",
    "description": "Generates Level N assessments",
    "system_prompt": """
        - Parse user background (domain, experience)
        - Query KB multiple times for diverse content
        - Generate 7 MC + 3 OE questions
        - Adapt scenarios to user domain
        - Track KB sources per question
        - Output ONLY valid JSON
    """,
    "tools": [query_level_N_kb]
}
```

**Critical Prompt Requirements**:
1. Include `kb_document_sources` in EACH question object
2. Extract sources from KB query results used for that question
3. Final output must be pure JSON (no markdown wrappers)
4. Ensure 5+ unique modules covered

### 3. Main Orchestrator (`src/agent.py` - create_literacy_assessment_agent)

**Purpose**: Delegate to subagents and aggregate results

**System Prompt**:
```python
MAIN_AGENT_PROMPT = """
- Parse level(s) and background from user request
- For single level: delegate to one subagent
- For multiple levels: invoke ALL subagents IN PARALLEL
- Return formatted assessment(s)
"""
```

**Key**: Parallel execution for multi-level requests via single response with multiple task() calls

### 4. Test Harness (`run_comprehensive_test.py`)

**Purpose**: End-to-end testing with logging and output generation

**Key Functions**:
- `create_model_with_fallback()`: Configure model with retry logic
- `test_level(level, background)`: Generate and save one assessment
- `extract_assessment_json(result)`: Parse JSON from subagent response
- `save_markdown(assessment, ...)`: Generate human-readable markdown
- `main()`: Run all 4 levels sequentially with logging

**Continuous Numbering Fix** (lines 263-314):
```python
# Multiple choice - continuous numbering
question_num = 1
for q in assessment['multiple_choice_questions']:
    f.write(f"### Question {question_num}\n\n")
    # ... render question ...
    question_num += 1

# Open-ended - continue numbering
for q in assessment['open_ended_questions']:
    f.write(f"### Question {question_num}\n\n")
    # ... render question ...
    question_num += 1
```

## Data Flow

### 1. Assessment Request Flow

```
User Request
    ↓
Main Orchestrator parses level + background
    ↓
task(prompt, "level-N-assessment-agent")
    ↓
Level-N Subagent:
  1. Parse background → identify domain
  2. query_level_N_kb("module 1 concepts")
  3. query_level_N_kb("module 2 concepts")
  4. ... (query 6+ times for diversity)
  5. Generate 7 MC questions with domain-adapted scenarios
  6. Generate 3 OE questions with domain-adapted scenarios
  7. Track KB sources used for each question
  8. Return JSON with kb_document_sources per question
    ↓
Main Orchestrator receives JSON result
    ↓
Test harness:
  1. Extract JSON from result
  2. Aggregate unique sources from questions
  3. Save JSON to output/assessments/
  4. Generate markdown with continuous numbering
  5. Log execution metrics
```

### 2. Knowledge Base Query Flow

```
Subagent calls query_level_N_kb(query)
    ↓
boto3 → AWS Bedrock Knowledge Base retrieve_and_generate
    ↓
Response includes:
  - citations: [{ retrievedReferences: [{ location: { s3Location: { uri } } }] }]
  - output: { text: "generated content" }
    ↓
Extract document sources:
  - Parse s3Location.uri
  - Extract filename from URI
  - Return {"filename": ..., "s3_uri": ...}
    ↓
Subagent tracks which KB queries were used for each question
    ↓
Includes sources in question's kb_document_sources array
```

### 3. Output Generation Flow

```
JSON Assessment (from subagent)
    ↓
Extraction (run_comprehensive_test.py):
  1. Parse JSON from ToolMessage content
  2. Aggregate unique sources from all questions
  3. Save to output/assessments/level_N_TIMESTAMP.json
    ↓
Markdown Generation:
  1. Header: level, timing, background
  2. Overview: question counts, modules
  3. Multiple Choice (Questions 1-7):
     - For each question:
       - Number (continuous)
       - Module, difficulty
       - Source documents (per-question)
       - Question text
       - Options with ✅/⬜ markers
       - Explanation
  4. Open-Ended (Questions 8-10):
     - For each question:
       - Number (continuous from MC)
       - Module, difficulty
       - Source documents (per-question)
       - Question text
       - Expected key points
       - Evaluation criteria
```

## Error Handling Strategy

### 1. Throttling (AWS Bedrock Rate Limits)

**Problem**: "Too many tokens" errors when running all 4 levels
**Solution**: Botocore config with exponential backoff
```python
config = botocore.config.Config(
    read_timeout=180,
    retries={
        'max_attempts': 5,
        'mode': 'adaptive'  # Exponential backoff
    }
)
```

### 2. Timeouts (Long-Running Assessments)

**Problem**: Levels 2-4 timeout at default 60 seconds
**Solution**: Increased read_timeout to 180 seconds
**Rationale**: Levels 2-4 have longer prompts + more KB queries

### 3. JSON Extraction Failures

**Problem**: Subagent returns markdown-wrapped JSON or invalid format
**Solution**: Multi-strategy parsing
```python
# Try ToolMessage content first
if "```json" in content:
    # Extract from code block
# Else:
    # Find JSON object boundaries
```

### 4. Missing Document Sources

**Problem**: KB tool returns results without location metadata
**Solution**: Defensive extraction
```python
location = result.get('location', {})
s3_location = location.get('s3Location', {})
if s3_location:  # Only add if present
    ...
```

## Testing Strategy

### Unit Testing (Not Yet Implemented)
- Mock AWS Bedrock KB responses
- Test JSON extraction with various formats
- Validate markdown generation with different question counts

### Integration Testing (`run_comprehensive_test.py`)
- Tests all 4 levels end-to-end
- Validates:
  - Successful generation (no throttling/timeouts)
  - Correct question counts (7 MC + 3 OE)
  - Module diversity (5+ per level)
  - Source tracking (non-empty kb_document_sources)
  - Continuous numbering (1-10 in markdown)

### Manual Validation
- Review generated markdown for readability
- Verify source PDFs match question content
- Check background-aware personalization
- Confirm difficulty progression across levels

## Deployment Considerations

### Prerequisites
- AWS credentials configured (boto3 default credential chain)
- Bedrock Knowledge Bases created and populated with PDFs
- Python 3.10+ with dependencies from requirements.txt
- Write permissions for output/ directory

### Configuration Files
- `src/config.py`: Model IDs, region, KB IDs, temperature, max_tokens
- No environment-specific config needed (uses AWS credential chain)

### Running Assessments
```bash
# Single comprehensive test (all 4 levels)
python run_comprehensive_test.py

# Custom level/background (use agent programmatically)
from src.agent import create_literacy_assessment_agent
agent = create_literacy_assessment_agent()
result = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "Generate Level 2 assessment for data scientist"
    }]
})
```

### Output Locations
- JSON: `output/assessments/level_N_TIMESTAMP.json`
- Markdown: `output/assessments/level_N_TIMESTAMP.md`
- Logs: `output/logs/test_run_TIMESTAMP.log`

## Performance Optimization

### Current Performance (2025-11-03)
- Level 1: ~202 seconds (3.4 minutes)
- Level 2: ~274 seconds (4.6 minutes)
- Level 3: ~317 seconds (5.3 minutes)
- Level 4: ~316 seconds (5.3 minutes)
- **Total: ~1109 seconds (18.5 minutes)**

### Bottlenecks
1. **Sequential KB Queries**: Subagents query KB 6+ times sequentially
2. **Sequential Level Processing**: test_level() runs one at a time
3. **LLM Latency**: Claude Sonnet 4 generation time per question

### Potential Optimizations (Future)
1. **Parallel KB Queries**: Use asyncio to query KB concurrently within subagent
2. **Parallel Level Generation**: Run test_level() for all levels concurrently
3. **Prompt Caching**: Enable Anthropic prompt caching for repeated subagent calls
4. **Model Selection**: Use Haiku for simpler questions, Sonnet for complex

**Estimated Impact**:
- Parallel KB queries: 30-40% reduction per level (150-200s → 100-120s)
- Parallel level processing: 4x total time reduction if KB optimized
- Combined: ~5 minutes total for all 4 levels

## Maintenance & Evolution

### Adding New Levels
1. Create new Knowledge Base in AWS Bedrock
2. Add `query_level_N_kb()` in `src/kb_tools.py`
3. Define `level_N_subagent` in `src/agent.py`
4. Register subagent in `create_literacy_assessment_agent()`
5. Add test case to `run_comprehensive_test.py`

### Updating Prompts
- Subagent prompts: `src/agent.py` (lines 36-533)
- Main orchestrator: `MAIN_AGENT_PROMPT` (lines 542-595)
- **Critical**: Maintain "CRITICAL - PER-QUESTION DOCUMENT SOURCES" section
- **Test**: Run comprehensive test after any prompt changes

### Updating Question Format
1. Modify JSON schema in subagent prompts
2. Update `extract_assessment_json()` if parsing changes
3. Update `save_markdown()` to render new fields
4. Update test validation logic

## Known Issues & Limitations

1. **No Question Deduplication**: Running multiple times may generate similar questions
2. **Background Parsing**: Simple keyword matching, could be improved with NLP
3. **Source Verification**: No automatic check that sources match question content
4. **Single Language**: English only, no i18n support
5. **Fixed Question Counts**: Always 7 MC + 3 OE, not configurable
6. **No Progress Tracking**: User sees no output during 3-5 minute generation time

## Recent Changes Log

### 2025-11-03: Continuous Question Numbering Fix
- **Modified**: `run_comprehensive_test.py` save_markdown() function
- **Change**: Replaced `enumerate(questions, 1)` with shared `question_num` variable
- **Lines**: 263-314
- **Impact**: Markdown now shows Questions 1-10 continuously
- **Testing**: Verified with comprehensive test run

### 2025-11-03: Per-Question Source Tracking
- **Modified**: `src/agent.py` (all 4 subagent prompts)
- **Change**: Added kb_document_sources to question-level JSON schema
- **Impact**: Each question now traceable to specific source PDFs
- **Testing**: Verified sources present in generated assessments

### 2025-11-03: Throttling Resilience
- **Modified**: `run_comprehensive_test.py` create_model_with_fallback()
- **Change**: Added botocore retry config with max_attempts=5, adaptive mode
- **Impact**: Level 4 no longer fails with throttling errors
- **Testing**: All 4 levels complete successfully in comprehensive test
