#!/usr/bin/env python3

import asyncio
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from langchain_core.tools import BaseTool

from .multi_agent_langgraph import create_multi_agent_system
from .agent_state import AgentState

# Configure logging with basicConfig
logging.basicConfig(
    level=logging.INFO,
    # Define log message format
    format="%(asctime)s,p%(process)s,{%(filename)s:%(lineno)d},%(levelname)s,%(message)s",
)

logger = logging.getLogger(__name__)

# Simple FastAPI app
app = FastAPI(title="SRE Agent Runtime", version="1.0.0")

# Simple request/response models
class InvocationRequest(BaseModel):
    input: Dict[str, Any]

class InvocationResponse(BaseModel):
    output: Dict[str, Any]

# Global variables for agent state
agent_graph = None
tools: list[BaseTool] = []

async def initialize_agent():
    """Initialize the SRE agent system using the same method as CLI."""
    global agent_graph, tools
    
    if agent_graph is not None:
        return  # Already initialized
    
    try:
        logger.info("Initializing SRE Agent system...")
        
        # Use the same initialization as the CLI
        provider = "anthropic"  # Default provider
        
        # Check if we should use bedrock instead
        if not os.getenv("ANTHROPIC_API_KEY") and (os.getenv("AWS_ACCESS_KEY_ID") or os.getenv("AWS_PROFILE")):
            provider = "bedrock"
        
        # Create multi-agent system using the same function as CLI
        agent_graph, tools = await create_multi_agent_system(provider)
        
        logger.info(f"SRE Agent system initialized successfully with {len(tools)} tools")
        
    except Exception as e:
        logger.error(f"Failed to initialize SRE Agent system: {e}")
        raise

@app.on_event("startup")
async def startup_event():
    """Initialize agent on startup."""
    await initialize_agent()

@app.post("/invocations", response_model=InvocationResponse)
async def invoke_agent(request: InvocationRequest):
    """Main agent invocation endpoint."""
    global agent_graph, tools
    
    try:
        # Ensure agent is initialized
        await initialize_agent()
        
        # Extract user prompt
        user_prompt = request.input.get("prompt", "")
        if not user_prompt:
            raise HTTPException(
                status_code=400,
                detail="No prompt found in input. Please provide a 'prompt' key in the input."
            )
        
        logger.info(f"Processing query: {user_prompt}")
        
        # Create initial state exactly like the CLI does
        initial_state: AgentState = {
            "messages": [HumanMessage(content=user_prompt)],
            "next": "supervisor",
            "agent_results": {},
            "current_query": user_prompt,
            "metadata": {},
            "requires_collaboration": False,
            "agents_invoked": [],
            "final_response": None,
        }
        
        # Process through the agent graph exactly like the CLI
        final_response = ""
        
        async for event in agent_graph.astream(initial_state):
            for node_name, node_output in event.items():
                # Capture final response from aggregate node
                if node_name == "aggregate":
                    final_response = node_output.get("final_response", "")
        
        if not final_response:
            final_response = "I encountered an issue processing your request. Please try again."
        
        # Simple response format
        response_data = {
            "message": final_response,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "model": "sre-multi-agent",
        }
        
        logger.info("Successfully processed agent request")
        return InvocationResponse(output=response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Agent processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Agent processing failed: {str(e)}")

@app.get("/ping")
async def ping():
    """Health check endpoint."""
    return {"status": "healthy"}


async def invoke_sre_agent_async(prompt: str, provider: str = "anthropic") -> str:
    """
    Programmatic interface to invoke SRE agent.
    
    Args:
        prompt: The user prompt/query
        provider: LLM provider ("anthropic" or "bedrock")
    
    Returns:
        The agent's response as a string
    """
    try:
        # Create the multi-agent system
        graph, tools = await create_multi_agent_system(provider=provider)
        
        # Create initial state
        initial_state: AgentState = {
            "messages": [HumanMessage(content=prompt)],
            "next": "supervisor",
            "agent_results": {},
            "current_query": prompt,
            "metadata": {},
            "requires_collaboration": False,
            "agents_invoked": [],
            "final_response": None,
        }
        
        # Execute and get final response
        final_response = ""
        async for event in graph.astream(initial_state):
            for node_name, node_output in event.items():
                if node_name == "aggregate":
                    final_response = node_output.get("final_response", "")
        
        return final_response or "I encountered an issue processing your request."
        
    except Exception as e:
        logger.error(f"Agent invocation failed: {e}")
        raise


def invoke_sre_agent(prompt: str, provider: str = "anthropic") -> str:
    """
    Synchronous wrapper for invoke_sre_agent_async.
    
    Args:
        prompt: The user prompt/query
        provider: LLM provider ("anthropic" or "bedrock")
    
    Returns:
        The agent's response as a string
    """
    return asyncio.run(invoke_sre_agent_async(prompt, provider))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080) 