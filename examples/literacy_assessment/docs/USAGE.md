# Literacy Level Assessment System

A Deep Agents-based system that dynamically generates custom literacy assessments by orchestrating 4 specialized subagents (one per literacy level 1-4). Each subagent queries dedicated AWS Bedrock Knowledge Bases containing curriculum content to generate tailored 10-question assessments.

## Features

- **4 Literacy Levels**: Foundational (L1), Intermediate (L2), Advanced (L3), Expert (L4)
- **Mixed Question Format**: 70% multiple choice (7 questions) + 30% open-ended (3 questions)
- **Background Calibration**: Questions adjusted based on user's experience and domain
- **Module Diversity**: Each assessment covers 5+ curriculum modules
- **Parallel Execution**: Multi-level requests processed concurrently (60%+ speedup)
- **AWS Bedrock Integration**: Queries real curriculum content from Knowledge Bases

## Architecture

```
Main Orchestrator Agent
├── Level 1 Subagent → KB: YOUR_LEVEL_1_KB_ID (Foundational content)
├── Level 2 Subagent → KB: YOUR_LEVEL_2_KB_ID (Intermediate content)
├── Level 3 Subagent → KB: YOUR_LEVEL_3_KB_ID (Advanced content)
└── Level 4 Subagent → KB: YOUR_LEVEL_3_KB_ID (Expert content, shared with L3)
```

## Quick Start

### 1. Install Dependencies

```bash
# Install core Deep Agents library
pip install -e .

# Install additional dependencies for this example
cd examples/literacy-assessment
pip install -r requirements.txt
```

### 2. Configure AWS Credentials

Create a `.env` file from the template:

```bash
cp .env.example .env
```

The `.env` file is already pre-configured with the knowledge base IDs:

```bash
AWS_REGION=eu-central-1
AWS_PROFILE=your-aws-profile

KB_LEVEL_1_ID=YOUR_LEVEL_1_KB_ID
KB_LEVEL_2_ID=YOUR_LEVEL_2_KB_ID
KB_LEVEL_3_ID=YOUR_LEVEL_3_KB_ID
KB_LEVEL_4_ID=YOUR_LEVEL_3_KB_ID
```

Ensure your `~/.aws/credentials` file has the `your-aws-profile` profile configured:

```ini
[your-aws-profile]
aws_access_key_id = YOUR_ACCESS_KEY
aws_secret_access_key = YOUR_SECRET_KEY
```

### 3. Validate Configuration

Run the validation script to ensure everything is set up correctly:

```bash
python -m examples.literacy_assessment.validate_config
```

Expected output:

```
✓ AWS credentials configured (profile: your-aws-profile)
✓ AWS region set: eu-central-1
✓ Knowledge Base Level 1: YOUR_LEVEL_1_KB_ID (accessible)
✓ Knowledge Base Level 2: YOUR_LEVEL_2_KB_ID (accessible)
✓ Knowledge Base Level 3: YOUR_LEVEL_3_KB_ID (accessible)
✓ Knowledge Base Level 4: YOUR_LEVEL_3_KB_ID (accessible)
✓ All 4 knowledge bases validated
✓ Configuration complete!
```

### 4. Run Examples

```bash
python examples/literacy-assessment/example_usage.py
```

This runs 4 examples demonstrating:
1. Single-level assessment for beginner (Level 1)
2. Single-level assessment for intermediate user (Level 2)
3. **Multi-level parallel assessment** (Levels 1, 2, 3) - Key feature showcase
4. Single-level assessment for advanced user (Level 3)

## Usage

### Python API

```python
from examples.literacy_assessment import create_literacy_assessment_agent

# Create agent
agent = create_literacy_assessment_agent()

# Generate single-level assessment
result = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "Generate a Level 2 assessment for someone with 3 years of software development experience"
    }]
})

# Access result
assessment_json = result['messages'][-1].content
print(assessment_json)
```

### Multi-Level Parallel Execution

```python
# Request multiple levels - subagents execute in parallel
result = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "Generate assessments for Levels 1, 2, and 3 for a data analyst with 2 years experience"
    }]
})
```

The agent automatically:
1. Parses the request to identify levels [1, 2, 3]
2. Invokes all 3 level-specific subagents **in parallel** (same response)
3. Collects results and returns all assessments
4. Calculates parallel speedup metrics

## Assessment Structure

Each generated assessment contains:

### Multiple Choice Questions (7)

```json
{
  "type": "multiple_choice",
  "question_text": "What is the primary purpose of...?",
  "options": ["Option A", "Option B", "Option C", "Option D"],
  "correct_answer_index": 2,
  "explanation": "Option C is correct because...",
  "module_source": "Module 3: Advanced Concepts",
  "difficulty": "intermediate"
}
```

### Open-Ended Questions (3)

```json
{
  "type": "open_ended",
  "question_text": "Explain the relationship between...?",
  "expected_key_points": [
    "Should mention concept X",
    "Should explain relationship Y",
    "Should provide example Z"
  ],
  "evaluation_criteria": "Response should demonstrate understanding of...",
  "module_source": "Module 5: Applications",
  "difficulty": "intermediate"
}
```

### Metadata

- `assessment_id`: Unique UUID
- `level`: Literacy level (1-4)
- `generated_at`: ISO timestamp
- `user_background`: Original background text
- `modules_covered`: List of 5+ unique modules
- `metadata`: Generation time, KB query count, difficulty distribution

## Requirements

### Functional

- ✅ **FR-001**: 10 questions per assessment (7 MC + 3 OE)
- ✅ **FR-002**: Mixed format (70% MC, 30% open-ended)
- ✅ **FR-005**: 5+ curriculum modules covered
- ✅ **FR-006**: Background-calibrated difficulty
- ✅ **FR-008**: Parallel subagent execution
- ✅ **FR-013**: <60 second generation time (single level)

### Success Criteria

- ✅ **SC-001**: Exactly 10 questions per assessment
- ✅ **SC-002**: Generation time <60s for single level
- ✅ **SC-003**: Parallel execution for multi-level requests
- ✅ **SC-004**: 60%+ time reduction vs sequential
- ✅ **SC-005**: 5+ modules covered per assessment

## Performance Targets

| Metric | Target | Typical |
|--------|--------|---------|
| Single-level generation | <60s | ~40-50s |
| Multi-level (3 levels) parallel | <60s | ~50-55s |
| Parallel speedup vs sequential | 60%+ | ~65-70% |
| Module diversity | 5+ | 6-7 |
| Question uniqueness | 100% | 100% |

## Project Structure

```
examples/literacy-assessment/
├── __init__.py                 # Module exports
├── requirements.txt            # Python dependencies
├── .env.example                # Environment template
├── .gitignore                  # Git ignore rules
├── docs/                       # Documentation
│   ├── README.md               # This file - Complete documentation
│   ├── START_HERE.md           # Quick start guide
│   ├── TESTING_GUIDE.md        # Testing instructions
│   └── PHASE2_DESIGN.md        # Phase 2 design (interactive flow)
├── src/                        # Core source code
│   ├── __init__.py             # Source module exports
│   ├── agent.py                # Main agent + 4 subagents
│   ├── config.py               # AWS Bedrock configuration
│   ├── models.py               # Pydantic data models
│   ├── kb_tools.py             # Knowledge Base query functions
│   └── questions.py            # Question validation utilities
├── scripts/                    # Utility scripts
│   ├── __init__.py             # Scripts module
│   ├── validate_config.py      # Configuration validation
│   └── example_usage.py        # Usage examples
└── tests/                      # Unit and integration tests
    ├── __init__.py
    ├── test_config.py
    ├── test_models.py
    └── test_question_gen.py
```

## Troubleshooting

### "Knowledge base not found"

**Cause**: KB ID incorrect or KB doesn't exist in the region.

**Solution**:
1. Verify KB IDs in `.env` match actual KBs
2. Check AWS region is `eu-central-1`
3. Run: `aws bedrock-agent get-knowledge-base --knowledge-base-id YOUR_LEVEL_1_KB_ID --profile your-aws-profile --region eu-central-1`

### "Access denied" errors

**Cause**: Insufficient IAM permissions.

**Solution**: Ensure IAM user/role has these permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "bedrock-agent-runtime:Retrieve",
      "bedrock-agent-runtime:RetrieveAndGenerate",
      "bedrock-agent:GetKnowledgeBase"
    ],
    "Resource": [
      "arn:aws:bedrock:eu-central-1:*:knowledge-base/YOUR_LEVEL_1_KB_ID",
      "arn:aws:bedrock:eu-central-1:*:knowledge-base/YOUR_LEVEL_2_KB_ID",
      "arn:aws:bedrock:eu-central-1:*:knowledge-base/YOUR_LEVEL_3_KB_ID"
    ]
  }]
}
```

### Assessments taking >60 seconds

**Cause**: KB queries slow or network latency.

**Solution**:
1. Check KB sync status (ensure indexing complete)
2. Reduce `KB_MAX_RESULTS` in `.env` (default: 10)
3. Check AWS Bedrock service health
4. Consider using a smaller curriculum dataset

### Questions not diverse (< 5 modules)

**Cause**: KB content concentrated in few modules or indexing incomplete.

**Solution**:
1. Verify curriculum content uploaded for all modules
2. Check KB indexing: `aws bedrock-agent list-data-sources --knowledge-base-id YOUR_LEVEL_1_KB_ID --profile your-aws-profile`
3. Trigger manual sync if needed
4. Ensure curriculum documents have clear module metadata

## Testing

Run the test suite:

```bash
# All tests
pytest examples/literacy-assessment/tests/ -v

# Specific test file
pytest examples/literacy-assessment/tests/test_kb_tools.py -v

# With coverage
pytest examples/literacy-assessment/tests/ --cov=examples.literacy_assessment
```

## Advanced Usage

### Custom Model

Use a different AWS Bedrock model:

```python
from langchain_aws import ChatBedrockConverse

# Use Claude Sonnet 4.5 with custom settings (default)
model = ChatBedrockConverse(
    model="eu.anthropic.claude-sonnet-4-5-20250929-v1:0",
    region_name="eu-central-1",
    temperature=0.5,
    max_tokens=8192,
)
agent = create_literacy_assessment_agent(model=model)

# Or use Claude Haiku 4.5 for faster responses
haiku_model = ChatBedrockConverse(
    model="eu.anthropic.claude-haiku-4-5-20251001-v1:0",
    region_name="eu-central-1",
    temperature=0.3,
    max_tokens=4096,
)
agent = create_literacy_assessment_agent(model=haiku_model)
```

### Accessing Structured Data

Parse assessment JSON:

```python
import json
from examples.literacy_assessment.models import Assessment

# Get assessment JSON from result
assessment_json = result['messages'][-1].content

# Parse to Pydantic model
assessment_data = json.loads(assessment_json)
assessment = Assessment(**assessment_data)

# Access fields
print(f"Level: {assessment.level}")
print(f"Modules: {assessment.modules_covered}")
print(f"Question count: {len(assessment.multiple_choice_questions) + len(assessment.open_ended_questions)}")
```

## References

- **Deep Agents Documentation**: [../../docs/README.md](../../docs/README.md)
- **Feature Specification**: [../../specs/001-literacy-level-assessment/spec.md](../../specs/001-literacy-level-assessment/spec.md)
- **Quickstart Guide**: [../../specs/001-literacy-level-assessment/quickstart.md](../../specs/001-literacy-level-assessment/quickstart.md)
- **AWS Bedrock Knowledge Bases**: [AWS Documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base.html)
- **LangGraph**: [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)

## License

This example is part of the Deep Agents project. See project root for license information.
