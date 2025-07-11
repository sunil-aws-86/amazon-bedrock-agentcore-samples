# Hosting Strands Agents with Amazon Bedrock models in Amazon Bedrock AgentCore Runtime

## Overview

In this tutorial we will learn how to host your existing agent, using Amazon Bedrock AgentCore Runtime. We will provide examples using Amazon Bedrock models and non-Bedrock models such as Azure OpenAI and Gemini.


### tutorial details


| Information         | Details                                                                          |
|:--------------------|:---------------------------------------------------------------------------------|
| tutorial type       | conversational                                                                   |
| Agent type          | Single                                                                           |
| tutorial components | hosting tools on AgentCore Runtime. Using Strands Agent and Amazon Bedrock Model |
| tutorial vertical   | cross-vertical                                                                   |
| Example complexity  | Easy                                                                             |
| SDK used            | Amazon BedrockAgentCore Python SDK                                               |

### Tutorial Architecture

In this tutorial we will describe how to deploy an existing agent to AgentCore runtime. 

For demonstration purposes, we will  use a Strands Agent using Amazon Bedrock models

In our example we will use a very simple agent with two tools: `get_weather` and `get_time`. 

<div style="text-align:left">
    <img src="images/architecture_runtime.png" width="100%"/>
</div>

### tutorial key Features

* Hosting Agents on Amazon Bedrock AgentCore Runtime
* Using Amazon Bedrock models
* Using Strands Agents