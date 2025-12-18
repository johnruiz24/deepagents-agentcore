Deep Agents Technical Deep Dive: Building Production-Ready AI Agents with LangChain
1. Deep Agents Benefits & Features
What Makes an Agent "Deep"?
Traditional LLM agents use a simple loop: call LLM → execute tools → repeat. This works for simple tasks but fails on complex, multi-step problems. Deep Agents solve this with four core capabilities:

1.1 Planning with TodoListMiddleware
Problem: Agents lose track of complex tasks.

Solution: Built-in write_todos tool for explicit planning.

from deepagents import create_deep_agent

agent = create_deep_agent(
    tools=[your_tools],
    system_prompt="Use write_todos to plan multi-step tasks"
)

How it works:

Agent writes a TODO list before starting

Updates it as tasks complete

Adapts plan when new information emerges

Example from our implementation:

# Agent internally calls:
write_todos([
    "Query Level 1 KB for module overview",
    "Query 5+ different modules for diversity", 
    "Generate 7 MC questions",
    "Generate 3 open-ended questions",
    "Upload to S3"
])

1.2 Reflection & Validation via Subagents
Problem: Agents don't self-check their work.

Solution: Dedicated validation subagents.

validation_subagent = {
    "name": "validation-agent",
    "description": "Validates final output quality",
    "system_prompt": "Check: completeness, accuracy, format",
    "tools": [read_file]  # Reads output to validate
}

agent = create_deep_agent(
    subagents=[worker_agent, validation_subagent]
)

In our literacy assessment:

Each level agent validates: exactly 10 questions, 5+ modules, correct JSON format

Main agent validates: all requested levels completed

1.3 Subagents for Context Isolation
Problem: Long contexts confuse agents and hit token limits.

Solution: Spawn specialized subagents with clean context.

# Main agent stays clean
main_agent = create_deep_agent(
    system_prompt="Coordinate assessment generation",
    subagents=[level_1_agent, level_2_agent, level_3_agent, level_4_agent]
)

# Each subagent has focused context
level_1_agent = {
    "name": "level-1-agent",
    "system_prompt": "ONLY generate Level 1 assessments",
    "tools": [query_level_1_kb]  # Only Level 1 KB access
}

Benefits:

Main agent context: ~2K tokens (just coordination)

Subagent context: ~10K tokens (focused on one level)

Total capacity: 50K+ tokens across all agents

1.4 Parallelization - The Game Changer
Problem: Sequential execution is slow.

Solution: Subagents run in parallel automatically.

# User requests Levels 1, 2, 3
# Main agent calls ALL THREE in same response:
task("Generate Level 1", "level-1-agent")
task("Generate Level 2", "level-2-agent")  
task("Generate Level 3", "level-3-agent")

# LangGraph executes them CONCURRENTLY
# Time: ~50s instead of 150s (3x speedup)

Technical implementation:

# In agent.py - Main agent prompt
"""
Multi-Level Request:
Call ALL subagents IN PARALLEL (in the SAME response):
   task("Level 1...", "level-1-agent")
   task("Level 2...", "level-2-agent")
   task("Level 3...", "level-3-agent")
"""

Performance in our system:

Single level: 40-50s

3 levels parallel: 50-55s (65% time reduction vs sequential)

2. Deployment in AWS Bedrock AgentCore
2.1 What is AgentCore?
AWS Bedrock AgentCore = Managed LangGraph deployment platform

Runs LangGraph agents as containerized services

Built-in memory, observability, scaling

No Kubernetes/ECS management needed

2.2 Deployment Architecture
Local Development
    ↓
serve_bedrock.py (entrypoint)
    ↓
Docker Container (linux/arm64)
    ↓
AWS ECR (container registry)
    ↓
Bedrock AgentCore Runtime
    ↓
Invocations via SDK/API

2.3 Key Files
serve_bedrock.py - AgentCore entrypoint:
deploy.py - Deployment automation:



from bedrock_agentcore_starter_toolkit import Runtime

runtime = Runtime()

# 1. Configure
runtime.configure(
    entrypoint="serve_bedrock.py",
    execution_role=iam_role_arn,
    auto_create_ecr=True,
    region="eu-central-1",
    agent_name="literacy_assessment"
)

# 2. Launch (builds Docker, pushes to ECR, deploys)
runtime.launch()

# 3. Invoke
response = runtime.invoke({
    "prompt": "Generate Level 1 assessment..."
})
utils.py - IAM role with permissions:

role_policy = {
    "Statement": [{
        "Action": [
            "bedrock:InvokeModel",
            "bedrock:Retrieve"  # For Knowledge Base access
        ],
        "Resource": "*"
    }]
}
2.4 Deployment Flow
# 1. Local test
python test_agent.py

# 2. Deploy to AgentCore
python deploy.py
What happens:

Toolkit reads serve_bedrock.py and requirements.txt

Builds Docker image with dependencies

Pushes to ECR (auto-created)

Creates AgentCore runtime with IAM role

Deploys container

Waits for READY status

Runs test invocations

2.5 Production Features
Memory (STM_ONLY):

# .bedrock_agentcore.yaml
memory:
  mode: STM_ONLY  # Short-term memory per session
  event_expiry_days: 30
Observability:

CloudWatch Logs: /aws/bedrock-agentcore/runtimes/literacy_assessment

X-Ray tracing: Automatic

CloudWatch Metrics: bedrock-agentcore namespace

Scaling:

Auto-scales based on load

Supports 10+ concurrent users

Cold start: ~3-5s

3. Technical Implementation Details
3.1 Knowledge Base Integration
# kb_tools.py
import boto3

bedrock_client = boto3.client(
    'bedrock-agent-runtime',
    region_name='eu-central-1'
)

def query_level_1_kb(query: str, max_results: int = 10):
    response = bedrock_client.retrieve(
        knowledgeBaseId='QADZTSAPWX',
        retrievalQuery={'text': query},
        retrievalConfiguration={
            'vectorSearchConfiguration': {
                'numberOfResults': max_results
            }
        }
    )
    
    return [{
        'content': r['content']['text'],
        'score': r['score'],
        'source': r['location']['s3Location']
    } for r in response['retrievalResults']]
3.2 Subagent Tool Binding
# Each subagent gets ONLY its level's KB tool
level_1_subagent = {
    "name": "level-1-agent",
    "tools": [query_level_1_kb],  # Only Level 1 access
}

level_2_subagent = {
    "name": "level-2-agent", 
    "tools": [query_level_2_kb],  # Only Level 2 access
}
Why this matters: Prevents cross-contamination, ensures correct curriculum per level.

3.3 Parallel Execution Mechanism
# Main agent system prompt instructs:
"""
For multi-level requests, call ALL subagents in SAME response:
   task("Level 1...", "level-1-agent")
   task("Level 2...", "level-2-agent")
"""

# LangGraph's SubAgentMiddleware detects multiple task() calls
# Executes them concurrently via asyncio.gather()
4. Performance Metrics
Metric	Target	Achieved
Single level generation	<60s	40-50s
Multi-level (3) parallel	<60s	50-55s
Parallel speedup	60%+	65-70%
Module diversity	5+	6-7
Concurrent users	10+	✅
5. Key Takeaways for Article
Deep Agents = Planning + Subagents + Filesystem + Prompts

Parallelization is automatic when subagents called together

Context isolation prevents token limit issues

AgentCore deployment is Docker + IAM + one command

Production-ready with observability, scaling, memory built-in

Pronto! Este é o conteúdo técnico detalhado que precisas para o artigo. Tudo em inglês como pediste!

