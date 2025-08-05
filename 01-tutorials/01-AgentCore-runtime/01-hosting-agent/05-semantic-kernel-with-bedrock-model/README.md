# Hosting Semantic Kernel Agents with Amazon Bedrock models in Amazon Bedrock AgentCore Runtime

This tutorial demonstrates how to deploy a Microsoft Semantic Kernel agent using Amazon Bedrock models to Amazon Bedrock AgentCore Runtime.

## Overview

In this tutorial, you will learn how to:
- Create a Semantic Kernel agent with custom plugins
- Use function calling with Semantic Kernel and Amazon Bedrock
- Deploy your agent to AgentCore Runtime
- Invoke your deployed agent using both the toolkit and boto3

## Prerequisites

Before starting this tutorial, ensure you have:
- Python 3.10+
- AWS credentials configured
- Docker or Finch running
- Access to Amazon Bedrock models (Claude Sonnet)

## Quick Start

1. Install dependencies:
```bash
uv add -r requirements.txt --active
```

2. Run the agent locally:
```bash
python semantic_kernel_bedrock.py '{"prompt": "What is the weather now?"}'
```

3. Deploy to AgentCore Runtime:
Follow the steps in the Jupyter notebook `runtime_with_semantic_kernel_and_bedrock_models.ipynb`

## Agent Features

The example agent includes three tools:
- **Calculator**: Performs mathematical calculations using safe eval
- **Weather**: Returns weather information (dummy implementation)
- **Get Time**: Returns the current timestamp

## Architecture

The agent uses:
- **Framework**: Microsoft Semantic Kernel
- **Model**: Amazon Bedrock (Claude Sonnet 3)
- **Runtime**: Amazon Bedrock AgentCore Runtime
- **Tools**: Custom plugins with function calling

## Files

- `semantic_kernel_bedrock.py`: The main agent implementation
- `runtime_with_semantic_kernel_and_bedrock_models.ipynb`: Step-by-step tutorial notebook
- `requirements.txt`: Python dependencies
- `images/`: Architecture diagrams

## Key Concepts

### Semantic Kernel Plugins
Plugins in Semantic Kernel are classes that contain kernel functions. Each function is decorated with `@kernel_function` and can be automatically discovered and used by the AI model through function calling.

### Function Calling
The agent uses Semantic Kernel's built-in function calling capabilities with Amazon Bedrock. When configured with `FunctionChoiceBehavior.Auto()`, the model can automatically decide when to call functions based on the user's input.

### AgentCore Runtime Integration
The agent is deployed as a containerized service on AgentCore Runtime, providing:
- Serverless execution
- Automatic scaling
- Built-in monitoring
- Secure execution environment

## Next Steps

After completing this tutorial, you can:
- Add more sophisticated plugins (e.g., database access, API calls)
- Experiment with different Amazon Bedrock models
- Integrate with other AgentCore capabilities (Memory, Gateway, Tools)
- Build multi-agent systems using Semantic Kernel

## Troubleshooting

If you encounter issues:
1. Ensure Docker/Finch is running
2. Verify AWS credentials are configured
3. Check that you have access to the specified Bedrock model
4. Review the agent logs in CloudWatch

## Related Tutorials

- [Strands Agents with Amazon Bedrock](../01-strands-with-bedrock-model)
- [LangGraph with Amazon Bedrock](../02-langgraph-with-bedrock-model)
- [CrewAI with Amazon Bedrock](../04-crewai-with-bedrock-model)