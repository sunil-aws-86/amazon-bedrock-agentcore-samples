<div align="center">
  <div>
    <a href="https://aws.amazon.com/bedrock/agentcore/">
      <img width="150" height="150" alt="image" src="https://github.com/user-attachments/assets/b8b9456d-c9e2-45e1-ac5b-760f21f1ac18" />
   </a>
  </div>

  <h1>
      Amazon Bedrock AgentCore Samples
  </h1>

  <h2>
    Deploy and operate AI agents securely at scale - using any framework and model
  </h2>

  <div align="center">
    <a href="https://github.com/awslabs/amazon-bedrock-agentcore-samples/graphs/commit-activity"><img alt="GitHub commit activity" src="https://img.shields.io/github/commit-activity/m/awslabs/amazon-bedrock-agentcore-samples"/></a>
    <a href="https://github.com/awslabs/amazon-bedrock-agentcore-samples/issues"><img alt="GitHub open issues" src="https://img.shields.io/github/issues/awslabs/amazon-bedrock-agentcore-samples"/></a>
    <a href="https://github.com/awslabs/amazon-bedrock-agentcore-samples/pulls"><img alt="GitHub open pull requests" src="https://img.shields.io/github/issues-pr/awslabs/amazon-bedrock-agentcore-samples"/></a>
    <a href="https://github.com/awslabs/amazon-bedrock-agentcore-samples/blob/main/LICENSE"><img alt="License" src="https://img.shields.io/github/license/awslabs/amazon-bedrock-agentcore-samples"/></a>
  </div>
  
  <p>
    <a href="https://docs.aws.amazon.com/bedrock-agentcore/">Documentation</a>
    ◆ <a href="https://github.com/aws/bedrock-agentcore-sdk-python">Python SDK</a>
    ◆ <a href="https://github.com/aws/bedrock-agentcore-starter-toolkit">Starter Toolkit </a>
    ◆ <a href="https://discord.gg/bedrockagentcore-preview">Discord</a>
  </p>
</div>

Welcome to the Amazon Bedrock AgentCore Samples repository! 

Amazon Bedrock AgentCore is both framework-agnostic and model-agnostic, giving you the flexibility to deploy and operate advanced AI agents securely and at scale. Whether you’re building with [Strands Agents](https://strandsagents.com/latest/), [CrewAI](https://www.crewai.com/), [LangGraph](https://www.langchain.com/langgraph), [LlamaIndex](https://www.llamaindex.ai/), or any other framework—and running them on any Large Language Model (LLM)—Amazon Bedrock AgentCore provides the infrastructure to support them. By eliminating the undifferentiated heavy lifting of building and managing specialized agent infrastructure, Amazon Bedrock AgentCore lets you bring your preferred framework and model, and deploy without rewriting code.

This collection provides examples and tutorials to help you understand, implement, and integrate Amazon Bedrock AgentCore capabilities into your applications.

> [!IMPORTANT]
> The examples provided in this repository are for experimental and educational purposes only. They demonstrate concepts and techniques but are not intended for direct use in production environments.

## 📁 Repository Structure

### 📚 [`01-tutorials/`](./01-tutorials/)
**Interactive Learning & Foundation**

This folder contains notebook-based tutorials that teach you the fundamentals of Amazon Bedrock AgentCore capabilities through hands-on examples.

The structure is divided by AgentCore component:
* **[Runtime](./01-tutorials/01-AgentCore-runtime)**: Amazon Bedrock AgentCore Runtime is a secure, serverless runtime capability that empowers organizations to deploy and scale both AI agents and tools, regardless of framework, protocol, or model choice—enabling rapid prototyping, seamless scaling, and accelerated time to market
* **[Gateway](./01-tutorials/02-AgentCore-gateway)**: AI agents need tools to perform real-world tasks—from searching databases to sending messages. Amazon Bedrock AgentCore Gateway automatically converts APIs, Lambda functions, and existing services into MCP-compatible tools so developers can quickly make these essential capabilities available to agents without managing integrations. 
* **[Memory](./01-tutorials/03-AgentCore-identity)**: Amazon Bedrock AgentCore Memory makes it easy for developer to build rich, personalized agent experiences with fully-manged memory infrastructure and the ability to customize memory for your needs.
* **[Identity](./01-tutorials/04-AgentCore-memory)**: Amazon Bedrock AgentCore Identity provides seamless agent identity and access management across AWS services and third-party applications such as Slack and Zoom while supporting any standard identity providers such as Okta, Entra, and Amazon Cognito.
* **[Tools](./01-tutorials/05-AgentCore-tools)**: Amazon Bedrock AgentCore provides two built-in tools to simplify your agentic AI application development: Amazon Bedrock AgentCore **Code Interpreter** tool enables AI agents to write and execute code securely, enhancing their accuracy and expanding their ability to solve complex end-to-end tasks. Amazon Bedrock AgentCore **Browser Tool** is an enterprise-grade capability that enables AI agents to navigate websites, complete multi-step forms, and perform complex web-based tasks with human-like precision within a fully managed, secure sandbox environment with low latency
* **[Observability](./01-tutorials/06-AgentCore-observability)**: Amazon Bedrock AgentCore Observability helps developers trace, debug, and monitor agent performance through unified operational dashboards. With support for OpenTelemetry compatible telemetry and detailed visualizations of each step of the agent workflow, Amazon Bedrock AgentCore Observability enables developers to easily gain visibility into agent behavior and maintain quality standards at scale.

* **[AgentCore end-to-end](./01-tutorials/07-AgentCore-E2E)**: In this tutorial we will move a customer support agent from prototype to production using Amazon Bedrock AgentCore services.


The examples provided as perfect for beginners and those looking to understand the underlying concepts before building AI Agents applications.

### 💡 [`02-use-cases/`](./02-use-cases/)
**End-to-end Applications**

Explore practical use case implementations that demonstrate how to apply Amazon Bedrock AgentCore capabilities to solve real business problems.

Each use case includes complete implementation focused on the AgentCore components with detailed explanations.

### 🔌 [`03-integrations/`](./03-integrations/)
**Framework & Protocol Integration**

Learn how to integrate Amazon Bedrock AgentCore capabilities with popular Agentic frameworks such as Strands Agents, LangChain and CrewAI.

Set agent-to-agent communication with A2A and different multi-agent collaboration patterns. Integrate agentic interfaces and learn how to use 
Amazon Bedrock AgentCore with different entry points.

## 🚀 Quick Start

**Clone the repository**

   ```bash
   git clone https://github.com/awslabs/amazon-bedrock-agentcore-samples.git
   ```

You will need to install the pre-requisites for deploying your agent into AgentCore Runtime. Follow the instructions below to get your environment up and running:

1. Install Docker or Finch. You can get started [here](https://www.docker.com/get-started/)
1. Make sure that you Docker or Finch is running
1. For better package control it is strongly recommended that you create a virtual environment to run your applications. `uv` tool is a high-speed package and project manager for Python. We recommend using `uv` to manager your environment here. You can install uv with the instructions from [here](https://docs.astral.sh/uv/getting-started/installation/)
1. Once you have `uv` installed, create and activate a new environment using the following commands:
```commandline
uv python install 3.10
uv venv --python 3.10
source .venv/bin/activate
uv init
```
Next add the required packages to your `uv` environment:
```commandline
uv add -r requirements.txt --active
```
You can start a Jupyter notebook instance from your `uv` environment using:
```commandline
uv run --with jupyter jupyter lab
```

## 📋 Prerequisites

- Python 3.10 or higher
- AWS account
- Docker or Finch installed and running
- Jupyter Notebook (for tutorials)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details on:

- Adding new samples
- Improving existing examples
- Reporting issues
- Suggesting enhancements

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: Report bugs or request features via [GitHub Issues](https://github.com/awslabs/amazon-bedrock-agentcore-samples/issues)
- **Documentation**: Check individual folder READMEs for specific guidance

## 🔄 Updates

This repository is actively maintained and updated with new capabilities and examples. Watch the repository to stay updated with the latest additions.
