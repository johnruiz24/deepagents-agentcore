import time
from bedrock_agentcore_starter_toolkit import Runtime
from pathlib import Path
import json

def invoke_with_retry(runtime, input_data, max_retries=5):
    """Invoke agent with retry logic for streaming errors and throttling."""
    for attempt in range(max_retries):
        try:
            print(f"🔄 Invoking agent (attempt {attempt + 1}/{max_retries})...")
            return runtime.invoke(input_data)
        except Exception as e:
            error_msg = str(e)

            if 'IncompleteRead' in error_msg or 'ResponseStreamingError' in error_msg:
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 5
                    print(f"⚠️  Streaming error - retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
            elif 'ThrottlingException' in error_msg or 'Too many tokens' in error_msg:
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) * 3
                    print(f"⚠️  Rate limit - waiting {wait_time}s...")
                    time.sleep(wait_time)
                    continue
            raise
    raise Exception(f"Failed after {max_retries} attempts")


agentcore_runtime = Runtime()
agentcore_runtime._config_path = Path(".bedrock_agentcore.yaml")

print("="*80)
print("TESTING LITERACY ASSESSMENT AGENT ON AGENTCORE")
print("="*80)

start_time = time.time()

print("\n📝 Test Request:")
print("   Generate a Level 2 assessment for a software engineer with 5 years")
print("   of experience in full-stack development")
print("\n⏳ Waiting for agent response (this may take 2-3 minutes)...\n")

response = invoke_with_retry(
    agentcore_runtime,
    {"prompt": "Generate a Level 2 assessment for a software engineer with 5 years of experience in full-stack development"},
    max_retries=5
)

execution_time = time.time() - start_time

print("\n" + "="*80)
print("RESULTS")
print("="*80)
print(f"⏱️  Execution time: {execution_time:.2f}s\n")

if isinstance(response, dict) and "messages" in response:
    messages = response["messages"]
    final_msg = messages[-1] if messages else None

    if final_msg and final_msg.get("type") == "ai":
        content = final_msg.get("content", "")

        # Try to parse as JSON assessment
        try:
            # Look for JSON in the content
            if content.strip().startswith('{'):
                assessment = json.loads(content)

                print("✅ Assessment Generated Successfully!")
                print(f"\n📊 Assessment Details:")
                print(f"   - Level: {assessment.get('level', 'N/A')}")
                print(f"   - Multiple Choice Questions: {len(assessment.get('multiple_choice_questions', []))}")
                print(f"   - Open-Ended Questions: {len(assessment.get('open_ended_questions', []))}")
                print(f"   - Modules Covered: {len(assessment.get('modules_covered', []))}")

                # Show module coverage
                if assessment.get('modules_covered'):
                    print(f"\n📚 Modules Covered:")
                    for module in assessment.get('modules_covered', []):
                        print(f"   - {module}")

                # Show first MC question as example
                mc_questions = assessment.get('multiple_choice_questions', [])
                if mc_questions:
                    print(f"\n💡 Example Multiple Choice Question:")
                    q = mc_questions[0]
                    print(f"   Question: {q.get('question_text', '')[:100]}...")
                    print(f"   Module: {q.get('module_source', 'N/A')}")
                    print(f"   Difficulty: {q.get('difficulty', 'N/A')}")

                print("\n✅ DEPLOYMENT TEST PASSED!")

            else:
                # Not JSON, show raw content
                print("⚠️  Response is not in JSON format:")
                print(content[:1000])  # First 1000 chars

        except json.JSONDecodeError as e:
            print("⚠️  Failed to parse assessment JSON:")
            print(f"   Error: {e}")
            print(f"\nRaw content (first 500 chars):")
            print(content[:500])
    else:
        print("⚠️  No final AI message found")
        print(f"Response structure: {type(response)}")
else:
    print("⚠️  Unexpected response format")
    print(f"Response type: {type(response)}")
    if isinstance(response, dict):
        print(f"Keys: {response.keys()}")

print("\n" + "="*80)
