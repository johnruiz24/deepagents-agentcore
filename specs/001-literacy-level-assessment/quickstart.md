# Quickstart Guide: Literacy Level Assessment System

**Purpose**: Step-by-step setup and usage instructions
**Target Audience**: Developers, educators, assessment administrators
**Estimated Setup Time**: 30-45 minutes

## Prerequisites

### Required

- Python 3.11 or higher
- AWS account with Bedrock access
- AWS credentials configured (IAM role or access keys)
- 4 AWS Bedrock Knowledge Bases (one per literacy level) with curriculum content loaded

### Recommended

- Basic familiarity with LangChain/LangGraph
- Understanding of Deep Agents concepts (see [Deep Agents docs](../../docs/README.md))
- AWS CLI installed for KB management

---

## Step 1: Clone and Install Dependencies

```bash
# Navigate to project root
cd /path/to/deepagents

# Install core dependencies (if not already installed)
pip install -e .

# Install additional dependencies for this example
cd examples/literacy-assessment
pip install -r requirements.txt
```

**requirements.txt contents**:
```txt
boto3>=1.34.0
pydantic>=2.0.0
python-dotenv>=1.0.0
```

---

## Step 2: Configure AWS Bedrock Knowledge Bases

### 2.1 Create Knowledge Bases (if not already created)

For each literacy level (1-4), create a separate Bedrock Knowledge Base:

```bash
# Using AWS CLI (example for Level 1)
aws bedrock-agent create-knowledge-base \
  --name "Literacy-Level-1-Curriculum" \
  --description "Level 1 foundational literacy content" \
  --role-arn "arn:aws:iam::ACCOUNT_ID:role/BedrockKBRole" \
  --knowledge-base-configuration '{
    "type": "VECTOR",
    "vectorKnowledgeBaseConfiguration": {
      "embeddingModelArn": "arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-embed-text-v1"
    }
  }' \
  --storage-configuration '{
    "type": "OPENSEARCH_SERVERLESS",
    "opensearchServerlessConfiguration": {
      "collectionArn": "arn:aws:aoss:us-east-1:ACCOUNT_ID:collection/COLLECTION_ID",
      "vectorIndexName": "literacy-level-1-index",
      "fieldMapping": {
        "vectorField": "embedding",
        "textField": "text",
        "metadataField": "metadata"
      }
    }
  }'
```

Repeat for Levels 2, 3, and 4 with appropriate names.

### 2.2 Upload Curriculum Content

Upload curriculum documents to each KB's S3 data source:

```bash
# Example: Upload Level 1 curriculum files
aws s3 sync ./curriculum/level-1/ s3://your-kb-bucket/level-1/

# Trigger KB sync
aws bedrock-agent start-ingestion-job \
  --knowledge-base-id "KB_ID_LEVEL_1" \
  --data-source-id "DATA_SOURCE_ID"
```

**Content Organization**:
```
curriculum/
├── level-1/
│   ├── module-01-foundations.pdf
│   ├── module-02-basics.pdf
│   ├── module-03-concepts.pdf
│   └── ...
├── level-2/
│   ├── module-01-intermediate.pdf
│   └── ...
├── level-3/
│   └── ...
└── level-4/
    └── ...
```

Ensure each level has content covering at least 5-6 distinct modules/courses for diversity requirements.

### 2.3 Note Knowledge Base IDs

**Pre-configured Knowledge Base IDs** (already created):

```bash
# Literacy Level Knowledge Bases (eu-central-1, profile: mll-dev)
KB_LEVEL_1: QADZTSAPWX
KB_LEVEL_2: KGGD2PTQ2N
KB_LEVEL_3: 7MGFSODDVI
KB_LEVEL_4: 7MGFSODDVI (shared with Level 3)
```

These KBs are already configured with curriculum content. To verify access:

```bash
aws bedrock-agent get-knowledge-base \
  --knowledge-base-id QADZTSAPWX \
  --profile mll-dev \
  --region eu-central-1
```

---

## Step 3: Configure Environment Variables

Create a `.env` file in `examples/literacy-assessment/`:

```bash
cd examples/literacy-assessment
cp .env.example .env
```

Edit `.env` with the pre-configured values:

```bash
# AWS Configuration
AWS_REGION=eu-central-1
AWS_PROFILE=mll-dev

# AWS Bedrock Knowledge Base IDs (pre-configured)
KB_LEVEL_1_ID=QADZTSAPWX
KB_LEVEL_2_ID=KGGD2PTQ2N
KB_LEVEL_3_ID=7MGFSODDVI
KB_LEVEL_4_ID=7MGFSODDVI

# Note: Level 3 and 4 share the same knowledge base
# AWS credentials are loaded from the 'mll-dev' profile in ~/.aws/credentials

# LLM Configuration (optional, defaults to Claude Sonnet 4.5)
# ANTHROPIC_API_KEY=your_anthropic_key  # If using Anthropic models
```

**Security Note**: Never commit `.env` files to version control. The `.gitignore` should already exclude them.

---

## Step 4: Verify Configuration

Run the configuration validation script:

```bash
python -m examples.literacy_assessment.validate_config
```

Expected output:
```
✓ AWS credentials configured (profile: mll-dev)
✓ AWS region set: eu-central-1
✓ Knowledge Base Level 1: QADZTSAPWX (accessible)
✓ Knowledge Base Level 2: KGGD2PTQ2N (accessible)
✓ Knowledge Base Level 3: 7MGFSODDVI (accessible)
✓ Knowledge Base Level 4: 7MGFSODDVI (accessible, shared with Level 3)
✓ All 4 knowledge bases validated
✓ Configuration complete!
```

If errors occur:
- **"Knowledge base not found"**: Verify KB IDs are correct
- **"Access denied"**: Check AWS credentials and IAM permissions
- **"Region mismatch"**: Ensure AWS_REGION matches KB locations

---

## Step 5: Run Your First Assessment

### 5.1 Interactive Python

```python
from examples.literacy_assessment import create_literacy_assessment_agent

# Create agent
agent = create_literacy_assessment_agent()

# Generate single level assessment
result = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "Generate a Level 2 assessment for someone with 3 years of software development experience"
    }]
})

# Print result
print(result['messages'][-1].content)
```

### 5.2 Command Line Interface

```bash
# Single level
python -m examples.literacy_assessment.cli generate \
  --level 2 \
  --background "3 years software development experience" \
  --output assessment_level_2.md

# Multiple levels (parallel)
python -m examples.literacy_assessment.cli generate \
  --levels 1,2,3 \
  --background "Undergraduate CS student" \
  --output multi_level_assessment.md
```

### 5.3 Example Script

```python
# examples/literacy_assessment/example_usage.py
import asyncio
from examples.literacy_assessment import create_literacy_assessment_agent

async def main():
    # Create agent
    agent = create_literacy_assessment_agent()

    # Example 1: Beginner assessment
    print("Generating Level 1 assessment for beginner...")
    result1 = agent.invoke({
        "messages": [{
            "role": "user",
            "content": "Generate a Level 1 assessment for someone with no prior technical knowledge"
        }]
    })

    # Example 2: Multi-level placement test
    print("\nGenerating multi-level placement assessment...")
    result2 = agent.invoke({
        "messages": [{
            "role": "user",
            "content": "Generate assessments for Levels 1, 2, and 3 for a data analyst with 2 years experience"
        }]
    })

    # Assessments saved to agent filesystem
    # Access via result['messages'][-1].content

if __name__ == "__main__":
    asyncio.run(main())
```

Run it:
```bash
python examples/literacy_assessment/example_usage.py
```

---

## Step 6: Understanding the Output

### Assessment Structure

Each generated assessment includes:

**1. Multiple Choice Questions (7)**
- 4 options labeled A-D
- Correct answer indicated
- Explanation provided
- Source module noted
- Difficulty level shown

**2. Open-Ended Questions (3)**
- Requires text response
- Key points to address listed
- Evaluation criteria provided
- Source module noted

**3. Metadata**
- Generation timestamp
- User background used for calibration
- Modules covered (minimum 5)
- Generation time (should be <60s)

### Performance Metrics

For multi-level assessments, check the Performance Summary:
- Total time
- Parallel execution speedup
- Number of assessments generated

**Example**:
```
Performance Summary:
- Total Time: 52.3s
- Parallel Execution: ✅ 61% faster than sequential
- Assessments Generated: 3 (Levels 1, 2, 3)
```

---

## Troubleshooting

### Issue: "Knowledge base not found"

**Cause**: KB ID incorrect or KB deleted

**Solution**:
1. Verify KB access with correct profile:
   ```bash
   aws bedrock-agent get-knowledge-base \
     --knowledge-base-id QADZTSAPWX \
     --profile mll-dev \
     --region eu-central-1
   ```
2. Ensure AWS profile 'mll-dev' is configured in `~/.aws/credentials`
3. Verify region is set to eu-central-1

---

### Issue: "Access denied" errors

**Cause**: Insufficient IAM permissions

**Solution**:
Ensure your IAM user/role has these permissions:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:Retrieve",
        "bedrock:RetrieveAndGenerate"
      ],
      "Resource": "arn:aws:bedrock:*:*:knowledge-base/*"
    }
  ]
}
```

---

### Issue: Assessments taking >60 seconds

**Cause**: KB queries slow or content too large

**Solution**:
1. Check KB sync status (ensure indexing complete)
2. Optimize query patterns (reduce `max_results` in research.md)
3. Consider smaller curriculum chunks
4. Check AWS Bedrock service health

---

### Issue: Questions not diverse (< 5 modules)

**Cause**: KB content concentrated in few modules

**Solution**:
1. Verify curriculum content uploaded for all modules
2. Check KB has indexed all documents: `aws bedrock-agent list-data-sources`
3. Ensure module metadata is properly structured
4. Trigger manual KB sync if needed

---

### Issue: Questions too easy/hard despite background calibration

**Cause**: Background parsing not extracting experience level correctly

**Solution**:
1. Provide more explicit background info: "beginner", "5 years experience", etc.
2. Check `parsed_experience_level` in logs
3. Adjust prompt in `literacy_agent.py` if needed

---

## Advanced Usage

### Custom Model

Use a different LLM:

```python
from langchain.chat_models import init_chat_model

model = init_chat_model("openai:gpt-4")
agent = create_literacy_assessment_agent(model=model)
```

### Streaming Responses

Stream assessment generation in real-time:

```python
async for chunk in agent.astream({
    "messages": [{"role": "user", "content": "Generate Level 2 assessment..."}]
}, stream_mode="values"):
    if "messages" in chunk:
        print(chunk["messages"][-1].content)
```

### Accessing Structured Data

Get assessments as Python objects:

```python
from examples.literacy_assessment.models import Assessment

# Agent writes JSON to filesystem
# Access via FilesystemMiddleware
assessment_json = result['state']['filesystem']['/assessments/level_2_assessment.json']
assessment = Assessment.parse_raw(assessment_json)

print(f"Level: {assessment.level}")
print(f"Modules: {assessment.modules_covered}")
print(f"Generation time: {assessment.generation_time_seconds}s")
```

---

## Testing

Run the test suite:

```bash
# All tests
pytest examples/literacy_assessment/tests/

# Specific test file
pytest examples/literacy_assessment/tests/test_literacy_agent.py

# With coverage
pytest examples/literacy_assessment/tests/ --cov=examples.literacy_assessment
```

---

## Next Steps

1. **Customize Subagent Prompts**: Edit prompts in `literacy_agent.py` for domain-specific terminology
2. **Extend Question Types**: Add true/false, matching, or coding questions
3. **Integrate with LMS**: Export assessments to SCORM or xAPI format
4. **Add Scoring**: Implement auto-grading for MC questions, rubric scoring for open-ended
5. **Build UI**: Create web interface for assessment delivery and results

---

## Resources

- **Deep Agents Documentation**: [docs/README.md](../../docs/README.md)
- **Example Code**: [examples/literacy-assessment/](.)
- **AWS Bedrock Knowledge Bases**: [AWS Docs](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base.html)
- **LangGraph**: [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)

---

## Support

For issues or questions:
1. Check this quickstart guide
2. Review example code in `examples/literacy-assessment/`
3. Consult AWS Bedrock KB documentation
4. Open GitHub issue with logs and configuration (redact sensitive info)
