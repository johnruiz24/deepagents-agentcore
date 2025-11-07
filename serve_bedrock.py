"""
AgentCore entrypoint for the Literacy Assessment Agent.

This module serves the literacy assessment agent through AWS Bedrock AgentCore,
enabling serverless deployment with automatic scaling and CloudWatch logging.
"""

import sys
import os

# Add src directory to path for deepagents module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
# Ensure current directory is in path for local imports
sys.path.insert(0, os.path.dirname(__file__))

from bedrock_agentcore.runtime import BedrockAgentCoreApp
from langchain_core.messages import HumanMessage
from examples.literacy_assessment.src.agent import create_literacy_assessment_agent

# Initialize AgentCore app
app = BedrockAgentCoreApp()

# Create the literacy assessment agent
agent = create_literacy_assessment_agent()


@app.entrypoint
async def literacy_assessment_bedrock(payload: dict):
    """
    AgentCore entrypoint for literacy assessment generation.

    Expected payload format:
    {
        "prompt": "Generate a Level 2 assessment for a software engineer with 5 years experience",
        // OR for multiple levels:
        "prompt": "Generate assessments for Levels 1-4 for a CTO with 15 years experience"
    }

    The agent will:
    1. Parse the request to identify target level(s) and user background
    2. Delegate to appropriate level-specific subagents (in parallel if multi-level)
    3. Stream assessment generation progress
    4. Return formatted assessment JSON with metadata

    Args:
        payload: Dictionary with 'prompt' key containing the assessment request

    Yields:
        Assessment generation progress and final results as JSON
    """
    import asyncio

    user_input = payload.get("prompt", "")

    if not user_input:
        yield {"error": "No prompt provided. Please specify level and user background."}
        return

    # Track last yield time for rate limiting (avoid overwhelming the stream)
    last_yield = asyncio.get_event_loop().time()

    # Stream agent responses
    async for chunk in agent.astream(
        {"messages": [HumanMessage(content=user_input)]},
        stream_mode="values",
    ):
        # Rate limit: minimum 0.5s between yields to avoid overwhelming AgentCore
        now = asyncio.get_event_loop().time()
        if now - last_yield < 0.5:
            await asyncio.sleep(0.5)
        last_yield = asyncio.get_event_loop().time()

        yield chunk


if __name__ == "__main__":
    # Run the AgentCore app
    # This will be invoked by AgentCore's container runtime
    app.run()
