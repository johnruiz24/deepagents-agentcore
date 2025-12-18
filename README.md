# Literacy Assessment Agent - AgentCore Deployment

AWS Bedrock AgentCore deployment for the multi-level literacy assessment agent system.

## Overview

This deployment package enables serverless deployment of the Literacy Assessment Agent to AWS Bedrock AgentCore with:

- **Automatic scaling**: Handles variable load without manual intervention
- **CloudWatch logging**: Automatic structured logging for observability
- **S3 integration**: Reads knowledge base files and writes assessment outputs in both JSON and Markdown formats
- **Knowledge Base access**: Queries 4 level-specific Bedrock Knowledge Bases
- **Multi-level assessment**: Supports Levels 1-4 with parallel execution

## Architecture

```
User Request → AgentCore Endpoint → serve_bedrock.py → Literacy Assessment Agent
                                                              ├─ Level 1 KB (YOUR_LEVEL_1_KB_ID)
                                                              ├─ Level 2 KB (YOUR_LEVEL_2_KB_ID)
                                                              ├─ Level 3 KB (YOUR_LEVEL_3_KB_ID)
                                                              └─ Level 4 KB (YOUR_LEVEL_4_KB_ID)
                                                                      ↓
                                                              Assessment JSON
                                                                      ↓
                                                              S3 Bucket (optional)
```

## Files

| File | Purpose |
|------|---------|
| `serve_bedrock.py` | AgentCore entrypoint - wraps the literacy agent for serverless execution |
| `deploy.py` | Deployment orchestration script - creates IAM role, configures and launches agent |
| `utils.py` | IAM role creation with all necessary AWS permissions |
| `requirements.txt` | Python dependencies for the containerized agent |
| `README.md` | This file - deployment documentation |

## Prerequisites

### AWS Permissions

Your AWS profile (`your-aws-profile`) must have permissions to:

- Create/delete IAM roles and policies
- Access Bedrock (invoke models, query knowledge bases)
- Access S3 bucket (`literacy-framework-development-YOUR_AWS_ACCOUNT_ID-eu-central-1`)
- Use AgentCore (configure, launch, invoke)
- Create ECR repositories
- Create CloudWatch log groups

### Knowledge Base Setup

Ensure the following Bedrock Knowledge Bases are created and accessible:

| Level | KB ID | Purpose |
|-------|-------|---------|
| Level 1 | `YOUR_LEVEL_1_KB_ID` | Foundational content |
| Level 2 | `YOUR_LEVEL_2_KB_ID` | Intermediate content |
| Level 3 | `YOUR_LEVEL_3_KB_ID` | Advanced content |
| Level 4 | `YOUR_LEVEL_4_KB_ID` | Expert content (shares with Level 3) |

### S3 Bucket Structure

```
s3://literacy-framework-development-YOUR_AWS_ACCOUNT_ID-eu-central-1/
├── learning_path/
│   ├── levels/              # Knowledge base source documents (read)
│   │   ├── level_1/
│   │   ├── level_2/
│   │   ├── level_3/
│   │   └── level_4/
│   └── assessments/         # Generated assessments (write - both JSON and Markdown)
│       ├── level_1/
│       │   ├── level_1_YYYYMMDD_HHMMSS.json
│       │   └── level_1_YYYYMMDD_HHMMSS.md
│       ├── level_2/
│       │   ├── level_2_YYYYMMDD_HHMMSS.json
│       │   └── level_2_YYYYMMDD_HHMMSS.md
│       ├── level_3/
│       │   ├── level_3_YYYYMMDD_HHMMSS.json
│       │   └── level_3_YYYYMMDD_HHMMSS.md
│       └── level_4/
│           ├── level_4_YYYYMMDD_HHMMSS.json
│           └── level_4_YYYYMMDD_HHMMSS.md
```

## Deployment Steps

### 1. Navigate to Deployment Directory

```bash
cd /Users/john.ruiz/Documents/projects/deepagents/deploy/agentcore_literacy_assessment
```

### 2. Set AWS Credentials

Ensure your AWS profile is configured:

```bash
export AWS_PROFILE=your-aws-profile
export AWS_REGION=eu-central-1
```

### 3. Run Deployment Script

```bash
python deploy.py
```

The script will:

1. ✅ Create IAM role (`agentcore-literacy_assessment-role-0511`) with all permissions
2. ✅ Configure AgentCore with `serve_bedrock.py` entrypoint
3. ✅ Build and push Docker container to ECR
4. ✅ Launch agent to AgentCore serverless runtime
5. ✅ Wait for deployment to complete (`READY` status)
6. ✅ Test the deployed agent with a sample Level 2 request

### 4. Monitor Deployment

The script provides real-time status updates:

```
📦 Initializing AgentCore Runtime...
🔐 Creating IAM role with permissions...
⚙️  Configuring AgentCore...
🚀 Launching agent to AWS...
⏳ Waiting for deployment to complete...
   Status: CREATING
   Status: UPDATING
   Status: READY
✓ Deployment successful!
```

## Usage

### Example Requests

**Single Level Assessment:**

```python
payload = {
    "prompt": "Generate a Level 2 assessment for a software engineer with 5 years experience"
}
```

**Multi-Level Assessment (Parallel):**

```python
payload = {
    "prompt": "Generate assessments for Levels 1-4 for a CTO with 15 years experience"
}
```

### Expected Response Format

The agent returns both S3 URIs (JSON and Markdown formats):

```json
{
  "status": "success",
  "s3_uri_json": "s3://.../level_2_20251106_034423.json",
  "s3_uri_markdown": "s3://.../level_2_20251106_034423.md",
  "level": 2,
  "timestamp": "2025-11-06T03:44:22.918557"
}
```

Both files contain the complete assessment with this structure:

```json
{
  "level": 2,
  "multiple_choice_questions": [
    {
      "type": "multiple_choice",
      "question_text": "...",
      "options": ["A", "B", "C", "D"],
      "correct_answer_index": 1,
      "explanation": "...",
      "module_source": "...",
      "difficulty": "intermediate",
      "kb_document_sources": [...]
    }
    // ... 6 more MC questions
  ],
  "open_ended_questions": [
    {
      "type": "open_ended",
      "question_text": "...",
      "expected_key_points": ["...", "...", "..."],
      "evaluation_criteria": "...",
      "module_source": "...",
      "difficulty": "intermediate",
      "kb_document_sources": [...]
    }
    // ... 2 more OE questions
  ],
  "user_background": "software engineer with 5 years experience",
  "modules_covered": ["Module 1", "Module 2", ...]
}
```

### Output Formats

**JSON Format** (`.json`):
- Machine-readable structure for programmatic processing
- Full Pydantic model serialization
- Suitable for integration with other systems

**Markdown Format** (`.md`):
- Human-readable document with proper formatting
- Includes assessment metadata header
- Questions organized with clear sections
- Suitable for review, printing, or sharing

## CloudWatch Logs

AgentCore automatically creates CloudWatch log groups for agent invocations:

**Log Group Pattern:**
```
/aws/bedrock-agentcore/runtimes/literacy_assessment-*
```

**Log Structure:**
- Structured JSON logs from the agent
- Streaming progress updates
- Error traces with context
- Performance metrics

### Viewing Logs

```bash
# List log groups
aws logs describe-log-groups \
  --profile your-aws-profile \
  --region eu-central-1 \
  --log-group-name-prefix /aws/bedrock-agentcore/runtimes/literacy_assessment

# Tail recent logs
aws logs tail /aws/bedrock-agentcore/runtimes/literacy_assessment-<id> \
  --profile your-aws-profile \
  --region eu-central-1 \
  --follow
```

## IAM Permissions

The deployment creates an IAM role with these permissions:

### Bedrock
- `bedrock:InvokeModel` - For Claude Sonnet 4.5 model invocation
- `bedrock:InvokeModelWithResponseStream` - For streaming responses
- `bedrock:Retrieve` - For knowledge base queries
- `bedrock:RetrieveAndGenerate` - For RAG operations

### S3
- `s3:GetObject` - Read knowledge base documents
- `s3:ListBucket` - List bucket contents
- `s3:PutObject` - Write generated assessments
- `s3:PutObjectAcl` - Set object permissions

### CloudWatch Logs
- `logs:CreateLogGroup` - Create log groups automatically
- `logs:CreateLogStream` - Create log streams
- `logs:PutLogEvents` - Write log events
- `logs:DescribeLogGroups` - Query log groups
- `logs:DescribeLogStreams` - Query log streams

### ECR
- `ecr:BatchGetImage` - Pull container images
- `ecr:GetDownloadUrlForLayer` - Download image layers
- `ecr:GetAuthorizationToken` - Authenticate to ECR

### Monitoring
- `xray:PutTraceSegments` - X-Ray tracing
- `cloudwatch:PutMetricData` - Custom metrics

### AgentCore
- `bedrock-agentcore:GetWorkloadAccessToken*` - Workload identity

## Troubleshooting

### Deployment Fails with "Role Not Found"

Wait 10-30 seconds after IAM role creation before launching. The script includes automatic delays, but AWS IAM eventual consistency may require patience.

### "AccessDeniedException" for Knowledge Base

Verify:
1. Knowledge Base IDs are correct in `utils.py`
2. IAM role has `bedrock:Retrieve` permission
3. Knowledge Bases are in the same region (`eu-central-1`)

### "S3 Access Denied"

Verify:
1. S3 bucket name is correct in `utils.py`
2. IAM role has S3 read/write permissions
3. Bucket is in the same region

### Agent Timeout

For long-running assessments (Level 3-4):
- Increase AgentCore timeout in `deploy.py` configuration
- Consider splitting into multiple single-level requests
- Monitor CloudWatch logs for progress

### Import Error: "No module named 'deepagents'"

The Deep Agents framework must be in the Python path. The `serve_bedrock.py` adds project root to `sys.path` automatically. Verify:

```python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
```

## Cost Considerations

### Per Invocation Costs

- **Claude Sonnet 4.5**: ~$15 per 1M input tokens, ~$75 per 1M output tokens
- **AgentCore**: Charged per compute time (serverless, pay-per-use)
- **Bedrock Knowledge Base**: Queries charged per retrieval
- **S3**: Minimal (GET/PUT operations + storage)

### Optimization Tips

1. **Batch requests** when possible (multi-level parallel execution)
2. **Cache results** if the same user background is used frequently
3. **Monitor CloudWatch metrics** to identify expensive operations
4. **Use S3 lifecycle policies** to archive old assessments

## Support

For issues or questions:

1. Check CloudWatch logs first
2. Review IAM role permissions
3. Verify Knowledge Base and S3 access
4. Check AgentCore status: `agentcore_runtime.status()`

## License

Internal use only - see project LICENSE file
