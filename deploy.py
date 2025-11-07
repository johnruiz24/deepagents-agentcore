"""
AgentCore deployment script for the Literacy Assessment Agent.

This script:
1. Creates IAM role with all necessary permissions
2. Configures AgentCore runtime
3. Launches the agent to AWS
4. Waits for deployment to complete
5. Tests the deployed agent with a sample request
"""

import time
import json
from bedrock_agentcore_starter_toolkit import Runtime
from utils import create_agentcore_role

try:
    from IPython.display import Markdown, display
    HAS_IPYTHON = True
except ImportError:
    HAS_IPYTHON = False
    print("IPython not available, using regular print for output")


def invoke_with_retry(runtime, input_data, max_retries=5):
    """
    Invoke agent with retry logic for streaming errors and throttling.

    Args:
        runtime: AgentCore Runtime instance
        input_data: Payload dictionary with 'prompt' key
        max_retries: Maximum number of retry attempts

    Returns:
        dict: Agent response

    Raises:
        Exception: If all retries fail
    """
    for attempt in range(max_retries):
        try:
            print(f"🔄 Invoking agent (attempt {attempt + 1}/{max_retries})...")
            return runtime.invoke(input_data)
        except Exception as e:
            error_msg = str(e)

            # Handle streaming errors
            if 'IncompleteRead' in error_msg or 'ResponseStreamingError' in error_msg:
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 5
                    print(f"⚠️  Streaming error - retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue

            # Handle rate limiting
            elif 'ThrottlingException' in error_msg or 'Too many tokens' in error_msg:
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) * 3
                    print(f"⚠️  Rate limit - waiting {wait_time}s...")
                    time.sleep(wait_time)
                    continue

            # Re-raise other errors
            raise

    raise Exception(f"Failed after {max_retries} attempts")


def main():
    """Main deployment workflow."""
    print("="*80)
    print("LITERACY ASSESSMENT AGENT - AgentCore Deployment")
    print("="*80)
    print()

    # Agent configuration
    agent_name = "literacy_assessment"
    region = "eu-central-1"

    # Step 1: Create AgentCore runtime
    print("📦 Initializing AgentCore Runtime...")
    agentcore_runtime = Runtime()
    print("✓ Runtime initialized")
    print()

    # Step 2: Create IAM role with all necessary permissions
    print("🔐 Creating IAM role with permissions...")
    print(f"   - Bedrock model invocation (Claude Sonnet 4.5)")
    print(f"   - Bedrock Knowledge Base access (4 level-specific KBs)")
    print(f"   - S3 bucket access (reading KB + writing assessments)")
    print(f"   - CloudWatch Logs (AgentCore automatic logging)")
    print(f"   - ECR, X-Ray, Metrics, Workload Identity")
    print()

    agentcore_iam_role = create_agentcore_role(agent_name=agent_name)
    role_arn = agentcore_iam_role["Role"]["Arn"]
    print()
    print(f"✓ IAM Role ARN: {role_arn}")
    print()

    # Step 3: Configure AgentCore
    print("⚙️  Configuring AgentCore...")
    config_response = agentcore_runtime.configure(
        entrypoint="serve_bedrock.py",
        execution_role=role_arn,
        auto_create_ecr=True,
        requirements_file="requirements.txt",
        region=region,
        agent_name=agent_name#,
        #memory_config={"mode": "STM_ONLY"}
    )
    print(f"✓ Configuration complete")
    print(f"   Config: {config_response}")
    print()

    # Step 4: Launch deployment
    print("🚀 Launching agent to AWS...")
    print("   This will:")
    print("   - Build Docker container with dependencies")
    print("   - Push to ECR")
    print("   - Deploy to AgentCore serverless runtime")
    print("   - Configure automatic CloudWatch logging")
    print()

    launch_result = agentcore_runtime.launch()
    print(f"✓ Launch initiated")
    print()

    # Step 5: Wait for deployment to complete
    print("⏳ Waiting for deployment to complete...")
    status_response = agentcore_runtime.status()
    status = status_response.endpoint['status']
    end_status = ['READY', 'CREATE_FAILED', 'DELETE_FAILED', 'UPDATE_FAILED']

    while status not in end_status:
        time.sleep(5)
        status_response = agentcore_runtime.status()
        status = status_response.endpoint['status']
        print(f"   Status: {status}")

    if status == 'READY':
        print()
        print("✓ Deployment successful!")
        print()
    else:
        print()
        print(f"✗ Deployment failed with status: {status}")
        return

    # Wait for system to stabilize
    print("⏳ Waiting for system to stabilize (60s)...")
    time.sleep(60)
    print("✓ System ready")
    print()

    # Step 6: Test the deployed agent
    print("="*80)
    print("TESTING DEPLOYED AGENT")
    print("="*80)
    print()

    test_prompt = (
        "Generate a Level 2 assessment for a software engineer with 5 years of "
        "experience in full-stack development"
    )

    print(f"📝 Test Prompt:")
    print(f"   {test_prompt}")
    print()

    start_time = time.time()

    print("🔄 Invoking agent...")
    response = invoke_with_retry(
        agentcore_runtime,
        {"prompt": test_prompt},
        max_retries=5
    )

    execution_time = time.time() - start_time

    print()
    print("="*80)
    print("AGENT RESPONSE")
    print("="*80)
    print()

    if 'messages' in response:
        messages = response['messages']

        # Find final AI message
        final_message = None
        for msg in reversed(messages):
            if msg.get('type') == 'ai' and isinstance(msg.get('content'), str):
                final_message = msg['content']
                break

        if final_message:
            print(final_message[:1000])  # Print first 1000 chars
            if len(final_message) > 1000:
                print(f"\n... ({len(final_message) - 1000} more characters)")

        # Try to parse as JSON if it looks like JSON
        if final_message and final_message.strip().startswith('{'):
            try:
                assessment_json = json.loads(final_message)
                print()
                print("="*80)
                print("ASSESSMENT SUMMARY")
                print("="*80)
                print(f"   Level: {assessment_json.get('level', 'N/A')}")
                print(f"   Multiple Choice: {len(assessment_json.get('multiple_choice_questions', []))}")
                print(f"   Open-Ended: {len(assessment_json.get('open_ended_questions', []))}")
                print(f"   Modules: {len(assessment_json.get('modules_covered', []))}")
                print(f"   User Background: {assessment_json.get('user_background', 'N/A')[:100]}...")
            except json.JSONDecodeError:
                print()
                print("⚠️  Response doesn't appear to be valid JSON")

    print()
    print("="*80)
    print(f"Total execution time: {execution_time:.2f} seconds")
    print("="*80)
    print()

    # Deployment summary
    print("="*80)
    print("DEPLOYMENT SUMMARY")
    print("="*80)
    print(f"✓ Agent Name: {agent_name}")
    print(f"✓ Region: {region}")
    print(f"✓ Status: {status}")
    print(f"✓ IAM Role: {role_arn}")
    print(f"✓ CloudWatch Logs: /aws/bedrock-agentcore/runtimes/*")
    print()
    print("🎉 Literacy Assessment Agent is deployed and operational!")
    print()


if __name__ == "__main__":
    main()
