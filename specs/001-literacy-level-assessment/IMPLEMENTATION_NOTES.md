# Implementation Notes: Literacy Level Assessment System

**Date**: 2025-11-03
**Branch**: 001-literacy-level-assessment
**Status**: Planning Complete - Ready for Implementation

---

## Critical Constraints ⚠️

### 1. **Isolated Implementation**

**DO NOT modify these directories:**
- ❌ `src/` - Core deepagents library code
- ❌ `deploy/` - Deployment configurations

**Only work in:**
- ✅ `examples/literacy-assessment/` - NEW directory for this feature
- ✅ `specs/001-literacy-level-assessment/` - Documentation
- ✅ `docs/` - Optional documentation additions

**Rationale**: This is a demonstration/example application, not a core library feature. Keep it completely isolated to show how to use Deep Agents for assessment generation.

---

## Pre-Configured AWS Resources

### Knowledge Base IDs (eu-central-1, profile: mll-dev)

| Level | Knowledge Base ID | Content |
|-------|-------------------|---------|
| Level 1 | `QADZTSAPWX` | Foundational literacy content |
| Level 2 | `KGGD2PTQ2N` | Intermediate literacy content |
| Level 3 | `7MGFSODDVI` | Advanced literacy content |
| Level 4 | `7MGFSODDVI` | Expert content (shared with Level 3) |

**AWS Configuration**:
- Region: `eu-central-1`
- Profile: `mll-dev`
- Credentials: Loaded from `~/.aws/credentials` profile

**Required IAM Permissions**:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock-agent-runtime:Retrieve",
        "bedrock-agent-runtime:RetrieveAndGenerate"
      ],
      "Resource": [
        "arn:aws:bedrock:eu-central-1:*:knowledge-base/QADZTSAPWX",
        "arn:aws:bedrock:eu-central-1:*:knowledge-base/KGGD2PTQ2N",
        "arn:aws:bedrock:eu-central-1:*:knowledge-base/7MGFSODDVI"
      ]
    }
  ]
}
```

---

## Directory Structure to Create

```
examples/
└── literacy-assessment/           # NEW - Create this entire directory
    ├── __init__.py
    ├── literacy_agent.py          # Main orchestrator with 4 subagents
    ├── knowledge_base_tools.py    # Bedrock KB query functions
    ├── question_generator.py      # Question formatting & validation
    ├── config.py                  # Configuration management
    ├── models.py                  # Pydantic data models
    ├── cli.py                     # Optional command-line interface
    ├── validate_config.py         # Configuration validation script
    ├── example_usage.py           # Usage examples
    ├── README.md                  # Quick reference guide
    ├── requirements.txt           # boto3, pydantic, python-dotenv
    ├── .env.example               # Copy from specs/001-.../
    ├── .gitignore                 # Ignore .env
    └── tests/
        ├── __init__.py
        ├── test_literacy_agent.py
        ├── test_kb_tools.py
        ├── test_question_gen.py
        └── test_config.py
```

---

## Implementation Checklist

### Phase 0: Setup ✅ (Complete)
- [x] Create branch: 001-literacy-level-assessment
- [x] Write feature specification
- [x] Research AWS Bedrock KB integration patterns
- [x] Define data models and entities
- [x] Document API contracts
- [x] Create setup guide (quickstart.md)

### Phase 1: Foundation (Next Steps)
- [ ] Create `examples/literacy-assessment/` directory structure
- [ ] Copy `.env.example` from specs folder
- [ ] Create `requirements.txt` with dependencies:
  - boto3>=1.34.0
  - pydantic>=2.0.0
  - python-dotenv>=1.0.0
- [ ] Set up `.gitignore` to exclude `.env` files
- [ ] Create `config.py` with LiteracyAssessmentConfig class
- [ ] Create `models.py` with Pydantic data models

### Phase 2: Core Components
- [ ] Implement `knowledge_base_tools.py`:
  - KnowledgeBaseClient class
  - Query functions for each level
  - Error handling for AWS SDK
- [ ] Implement `question_generator.py`:
  - Question formatting functions
  - Validation logic (10 questions, 5+ modules)
  - Mix enforcement (70% MC, 30% open-ended)
- [ ] Create `validate_config.py` script:
  - Check AWS credentials
  - Verify KB access for all 4 levels
  - Display configuration status

### Phase 3: Agent Implementation
- [ ] Implement `literacy_agent.py`:
  - Define 4 level-specific subagents
  - Main orchestrator agent prompt
  - Parallel execution logic
  - create_literacy_assessment_agent() function
- [ ] Test single-level assessment generation
- [ ] Test multi-level parallel generation
- [ ] Verify 60-second performance target

### Phase 4: Testing & Documentation
- [ ] Write unit tests for KB tools
- [ ] Write integration tests for agent
- [ ] Create `example_usage.py` with demos
- [ ] Write `README.md` for the example
- [ ] Optional: Create CLI interface

---

## Key Implementation Details

### 1. boto3 Session with Profile

```python
import boto3
from config import LiteracyAssessmentConfig

# Use session with profile
session = boto3.Session(
    profile_name=LiteracyAssessmentConfig.AWS_PROFILE,
    region_name=LiteracyAssessmentConfig.AWS_REGION
)

client = session.client('bedrock-agent-runtime')
```

### 2. Subagent Definitions

Each level gets its own subagent:

```python
level_1_subagent = {
    "name": "level-1-assessment-agent",
    "description": "Generates Level 1 literacy assessments...",
    "system_prompt": """You are a Level 1 literacy assessment specialist...""",
    "tools": [query_level_1_kb, format_assessment],
}

# Repeat for levels 2, 3, 4 with different KB access
```

### 3. Main Agent Orchestration

```python
from deepagents import create_deep_agent

agent = create_deep_agent(
    tools=[query_kb, format_assessment],
    system_prompt=orchestrator_prompt,
    subagents=[
        level_1_subagent,
        level_2_subagent,
        level_3_subagent,
        level_4_subagent,
    ],
)
```

### 4. Parallel Execution Pattern

Main agent calls multiple subagents in parallel:

```python
# In main agent prompt:
"""
When user requests multiple levels (e.g., Levels 1, 2, 3):

Call the level-specific subagents in PARALLEL by invoking them
in the same response:

task("Generate Level 1 assessment for <background>", "level-1-assessment-agent")
task("Generate Level 2 assessment for <background>", "level-2-assessment-agent")
task("Generate Level 3 assessment for <background>", "level-3-assessment-agent")

This will execute concurrently, significantly reducing total time.
"""
```

---

## Testing Strategy

### 1. Configuration Validation
```bash
python -m examples.literacy_assessment.validate_config
```
Should verify:
- AWS credentials accessible
- All 4 KBs accessible via mll-dev profile
- Region set correctly to eu-central-1

### 2. Unit Tests
```bash
pytest examples/literacy-assessment/tests/test_kb_tools.py
pytest examples/literacy-assessment/tests/test_question_gen.py
```

### 3. Integration Tests
```bash
pytest examples/literacy-assessment/tests/test_literacy_agent.py
```
Should verify:
- Single-level assessment generation
- Multi-level parallel generation
- Question format validation (7 MC + 3 open-ended)
- Module diversity (5+ modules)

### 4. Performance Tests
```bash
# Measure single-level generation time
time python -m examples.literacy_assessment.example_usage --level 1

# Measure multi-level parallel speedup
time python -m examples.literacy_assessment.example_usage --levels 1,2,3
```

Target: <60s for single level, <60% of sequential time for parallel

---

## Common Pitfalls to Avoid

### ❌ Don't Do This:
1. **Modifying core library**: Don't touch `src/deepagents/`
2. **Hardcoding KB IDs**: Use environment variables and config.py
3. **Single query strategy**: Won't achieve module diversity
4. **Sequential subagent calls**: Won't demonstrate parallelization
5. **Missing profile in boto3**: Must specify profile for mll-dev

### ✅ Do This:
1. **Keep code in examples/**: Completely isolated implementation
2. **Use configuration class**: Centralized config management
3. **Multi-query KB access**: Query multiple modules for diversity
4. **Parallel subagent invocation**: Call multiple agents in one response
5. **Session with profile**: `boto3.Session(profile_name='mll-dev')`

---

## Next Steps

1. **Run `/speckit.tasks`** to generate detailed implementation tasks
2. **Create directory structure**: `mkdir -p examples/literacy-assessment/tests`
3. **Copy .env.example**: `cp specs/001-literacy-level-assessment/.env.example examples/literacy-assessment/`
4. **Start with foundation**: Implement config.py and models.py first
5. **Iterate**: Build KB tools → Question gen → Agent → Tests

---

## Support & References

- **Planning Docs**: `specs/001-literacy-level-assessment/`
- **Deep Agents Docs**: `docs/README.md`
- **Example Patterns**: `examples/parallel/`, `examples/research/`
- **AWS Bedrock KB Docs**: https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base.html
- **boto3 bedrock-agent-runtime**: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agent-runtime.html

---

## Contact

For questions about AWS resources (KB IDs, credentials):
- Check with AWS admin for `mll-dev` profile access
- Verify Knowledge Base IDs haven't changed in eu-central-1

For questions about implementation approach:
- Review existing examples in `examples/parallel/` and `examples/research/`
- Consult Deep Agents documentation in `docs/`
