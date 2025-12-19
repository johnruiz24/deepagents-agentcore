import time
from bedrock_agentcore_starter_toolkit import Runtime
from pathlib import Path
import json
import re
import html

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

def format_text(text):
    """Clean and format the response text."""
    # Decode HTML entities
    text = html.unescape(text)
    
    # Replace escaped newlines with actual newlines
    text = text.replace('\\n', '\n')
    
    # Remove excessive whitespace
    lines = text.split('\n')
    formatted_lines = []
    
    for line in lines:
        line = line.strip()
        if line and not line.startswith('{') and not line.startswith('"'):
            # Remove markdown formatting for cleaner display
            line = re.sub(r'\*\*(.*?)\*\*', r'\1', line)  # Remove bold
            line = re.sub(r'\*(.*?)\*', r'\1', line)      # Remove italic
            line = re.sub(r'`(.*?)`', r'\1', line)        # Remove code backticks
            formatted_lines.append(line)
    
    return '\n'.join(formatted_lines)

agentcore_runtime = Runtime()
agentcore_runtime._config_path = Path(".bedrock_agentcore.yaml")

print("=" * 80)
print("TESTING LITERACY ASSESSMENT AGENT")
print("=" * 80)

start_time = time.time()

print("\n📝 Test Request:")
print("   Generate a Level 2 assessment for a software engineer with 5 years")
print("   of experience in full-stack development")
print("\n⏳ Waiting for agent response...\n")

# Capture the printed output during invocation
import sys
from io import StringIO

old_stdout = sys.stdout
sys.stdout = captured_output = StringIO()

try:
    response = invoke_with_retry(
        agentcore_runtime,
        {"prompt": "Generate a Level 2 assessment for a software engineer with 5 years of experience in full-stack development"},
        max_retries=5
    )
finally:
    sys.stdout = old_stdout

# Get the captured output
output_text = captured_output.getvalue()

execution_time = time.time() - start_time

print("\n" + "=" * 80)
print("RESULTS")
print("=" * 80)
print(f"⏱️  Execution time: {execution_time:.2f}s\n")

# Parse the captured output for the actual response
if "Assessment Generated Successfully" in output_text:
    print("✅ AGENT TEST PASSED!")
    
    # Extract S3 URIs
    s3_uris = re.findall(r's3://[^\s"]+\.(?:json|md)', output_text)
    
    # Extract key information
    mc_match = re.search(r'(\d+)\s+multiple[- ]choice', output_text, re.IGNORECASE)
    oe_match = re.search(r'(\d+)\s+open[- ]ended', output_text, re.IGNORECASE)
    modules_match = re.search(r'(\d+)\s+(?:different\s+)?modules?', output_text, re.IGNORECASE)
    
    print("\n📊 Assessment Details:")
    print("   - Level: 2 (Intermediate)")
    if mc_match:
        print(f"   - Multiple Choice Questions: {mc_match.group(1)}")
    if oe_match:
        print(f"   - Open-Ended Questions: {oe_match.group(1)}")
    if modules_match:
        print(f"   - Modules Covered: {modules_match.group(1)}")
    
    if s3_uris:
        print("\n📁 Generated Files:")
        for uri in s3_uris:
            file_type = "JSON" if uri.endswith('.json') else "Markdown"
            print(f"   - {file_type}: {uri}")
    
    print("\n🎯 Assessment Features:")
    if "software engineer" in output_text.lower():
        print("   ✅ Tailored for software engineers")
    if "production" in output_text.lower():
        print("   ✅ Production-grade scenarios")
    if "intermediate" in output_text.lower():
        print("   ✅ Intermediate complexity")
    
    # Show formatted response
    print("\n📋 Assessment Generation Summary:")
    print("=" * 80)
    
    # Extract and format the main content
    start_marker = "Assessment Generated Successfully"
    if start_marker in output_text:
        start_idx = output_text.find(start_marker)
        # Get up to 10K characters
        relevant_text = output_text[start_idx:start_idx+10000]
        
        # Format the text
        formatted_text = format_text(relevant_text)
        
        # Split into manageable sections
        lines = formatted_text.split('\n')
        current_section = []
        
        for line in lines:
            if line.strip():
                current_section.append(line)
                
                # Print section when we hit a natural break or reach reasonable length
                if (len(current_section) > 3 and 
                    (line.endswith(':') or line.startswith('###') or len('\n'.join(current_section)) > 500)):
                    print('\n'.join(current_section))
                    print()  # Add spacing
                    current_section = []
        
        # Print any remaining content
        if current_section:
            print('\n'.join(current_section))
    
    print("=" * 80)
    
else:
    print("⚠️  No clear success indicators found")
    print(f"\n📋 Raw Response: {response}")
    if output_text:
        print(f"\n📋 Captured Output (first 10000 chars):")
        formatted_output = format_text(output_text[:10000])
        print(formatted_output)

print("\n" + "=" * 80)