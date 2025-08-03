# SRE Agent Memory System

## Overview

The SRE Agent includes a sophisticated long-term memory system built on Amazon Bedrock AgentCore Memory that enables persistent user preferences, cross-session learning, and personalized investigation experiences. This system remembers user preferences, learns from past investigations, and tailors reports based on individual user roles and workflows.

The system provides three distinct memory strategies for different types of information and comes pre-configured with user personas to demonstrate personalized investigations.

## Pre-configured User Personas

The system comes with two example user personas in [`scripts/user_config.yaml`](../scripts/user_config.yaml) that demonstrate how personalized investigations work:

### Alice - Technical SRE Engineer
- **Investigation Style**: Detailed, systematic, multi-dimensional investigations with comprehensive analysis
- **Communication**: Technical team channels (`#alice-alerts`, `#sre-team`) with detailed metrics and troubleshooting steps
- **Escalation**: Technical management (`alice.manager@company.com`) with 15-minute delay threshold
- **Reports**: Technical exposition with step-by-step methodologies and complete tool references
- **Preferences**: Detailed analysis, UTC timezone, includes troubleshooting steps

### Carol - Executive/Director  
- **Investigation Style**: Executive-focused with business impact analysis and streamlined presentation
- **Communication**: Strategic channels (`#carol-executive`, `#strategic-alerts`) with filtered notifications (critical only)
- **Escalation**: Executive team (`carol.director@company.com`) with faster 20-minute timeline
- **Reports**: Business-focused summaries without detailed technical steps, emphasizing impact and business consequences
- **Preferences**: Executive summary format, EST timezone, business impact focus

## Personalized Investigation Examples

When running investigations with different user IDs, the agent produces similar technical findings but presents them according to each user's preferences:

```bash
# Alice's detailed technical investigation
USER_ID=Alice sre-agent --prompt "API response times have degraded 3x in the last hour" --provider bedrock

# Carol's executive-focused investigation  
USER_ID=Carol sre-agent --prompt "API response times have degraded 3x in the last hour" --provider bedrock
```

Both commands identify identical technical issues but present them differently:
- **Alice** receives detailed technical analysis with step-by-step troubleshooting and comprehensive tool references
- **Carol** receives executive summaries focused on business impact with rapid escalation timelines

For a detailed comparison showing how the memory system personalizes identical incidents, see: [**Memory System Report Comparison**](examples/Memory_System_Analysis_User_Personalization_20250802_162648.md)

## Memory Strategies

### 1. User Preferences Memory
**Strategy:** Semantic Memory with 90-day retention  
**Purpose:** Remember user-specific operational preferences

**Captures:**
- Escalation contacts and procedures
- Notification channels (Slack, email, etc.)
- Investigation workflow preferences  
- Communication style preferences

**Example Usage:**
```python
# When user mentions "escalate to ops-team@company.com for database issues"
# The system automatically captures:
{
  "user_id": "user123",
  "preference_type": "escalation",
  "preference_value": {
    "contact": "ops-team@company.com",
    "service_category": "database"
  },
  "context": "Investigation of Redis connection failures"
}
```

### 2. Infrastructure Knowledge Memory
**Strategy:** Semantic Memory with 30-day retention  
**Purpose:** Build understanding of infrastructure patterns and relationships

**Captures:**
- Service dependencies and relationships
- Failure patterns and common issues
- Configuration insights and best practices
- Performance baselines and thresholds

**Example Usage:**
```python
# When investigating a service outage, the system learns:
{
  "service_name": "web-api",
  "knowledge_type": "dependency",
  "knowledge_data": {
    "depends_on": "postgres-db",
    "failure_mode": "connection_timeout",
    "typical_recovery_time": "2-5 minutes"
  },
  "confidence": 0.8
}
```

### 3. Investigation Summaries Memory
**Strategy:** Summary Memory with 60-day retention  
**Purpose:** Maintain history of investigations for learning and reference

**Captures:**
- Investigation timeline and actions taken
- Key findings and root causes
- Resolution strategies and outcomes
- Cross-team collaboration context

**Example Usage:**
```python
{
  "incident_id": "incident_20250128_1045",
  "query": "Why is the checkout service responding slowly?",
  "timeline": [
    {"time": "10:45", "action": "Started investigation with metrics agent"},
    {"time": "10:47", "action": "Identified high CPU usage"},
    {"time": "10:50", "action": "Checked application logs for errors"}
  ],
  "actions_taken": [
    "Analyzed CPU and memory metrics",
    "Reviewed application error logs",  
    "Identified memory leak in payment processing"
  ],
  "resolution_status": "completed",
  "key_findings": [
    "Memory leak in payment service consuming 2GB/hour",
    "Database connection pool exhausted during peak traffic",
    "Missing circuit breaker causing cascade failures"
  ]
}
```

## Amazon Bedrock AgentCore Memory Architecture

The memory system uses Amazon Bedrock AgentCore Memory's sophisticated event-based model with automatic namespace routing:

### Memory Strategies and Namespaces
When the SRE Agent initializes, it creates three memory strategies with specific namespace patterns:

1. **User Preferences Strategy**: Namespace pattern `/sre/users/{user_id}/preferences`
2. **Infrastructure Knowledge Strategy**: Namespace pattern `/sre/infrastructure/{user_id}/{session_id}`  
3. **Investigation Memory Strategy**: Namespace pattern `/sre/investigations/{user_id}/{session_id}`

### How Namespace Routing Works
The key insight is that **the SRE Agent only needs to provide the actor_id** when calling `create_event()`. Amazon Bedrock AgentCore Memory automatically:

1. **Strategy Matching**: Examines all strategies associated with the memory resource
2. **Namespace Resolution**: Determines which namespace(s) the event belongs to based on the actor_id
3. **Automatic Routing**: Places the event in the correct strategy's namespace without requiring explicit namespace specification
4. **Multi-Strategy Storage**: A single event can be stored in multiple strategies if the namespaces match

### Event-based Model Benefits
- **Immutable Events**: All memory entries are stored as immutable events that cannot be modified
- **Accumulative Learning**: New events accumulate over time without deleting old ones
- **Strategy Aggregation**: Memory strategies aggregate events from their namespace to provide relevant context
- **Automatic Organization**: Events are automatically organized by user, session, and memory type

### Example Event Flow
```python
# SRE Agent calls create_event with just actor_id and content
memory_client.create_event(
    memory_id="sre_agent_memory-xyz",
    actor_id="Alice",  # Amazon Bedrock AgentCore Memory uses this to route to correct namespace
    session_id="investigation_2025_01_15",
    messages=[("preference_data", "ASSISTANT")]
)

# Amazon Bedrock AgentCore Memory automatically:
# 1. Checks all strategy namespaces for this memory
# 2. Matches actor_id "Alice" to namespace "/sre/users/Alice/preferences" 
# 3. Stores event in User Preferences Strategy
# 4. Makes event available for future retrievals
```

## How Memory Capture Works

The SRE Agent automatically captures information during investigations through a sophisticated pattern recognition and structured data conversion process:

### SRE Agent Pattern Recognition
The SRE Agent code (specifically `sre_agent/memory/hooks.py`) uses regex patterns to parse agent responses and extract structured information:

1. **Response Analysis**: After each agent response, the system scans the text for specific patterns
2. **Pattern Matching**: Uses regex to identify key information types
3. **Data Structuring**: Converts matched patterns into structured Pydantic models
4. **Memory Storage**: Calls Amazon Bedrock AgentCore Memory's `create_event()` API to store the structured data

### Specific Pattern Recognition (sre_agent/memory/hooks.py)
The system automatically extracts structured information from agent responses using regex patterns:
- **Email addresses for escalation**: Patterns like `r"escalate to ([^\s,\.]+@[^\s,\.]+)"`
- **Slack channels for notifications**: Patterns like `r"notify (#[\w-]+)"`
- **Service dependencies**: Patterns like `r"(\w+) depends on (\w+)"`
- **Performance baselines and thresholds**: Extracted from metrics agent responses
- **Error patterns and resolution strategies**: Captured during investigation completion

### Agent Response Processing
Every individual agent response triggers automatic memory pattern extraction through the `on_agent_response()` hook. This ensures that valuable information discovered during domain-specific investigations is captured and made available for future use.

### Memory Storage Process
1. **Pattern Detection**: SRE agent code identifies relevant information in responses
2. **Data Conversion**: Creates structured objects (UserPreference, InfrastructureKnowledge, etc.)
3. **Event Creation**: Calls `create_event()` with actor_id and structured data
4. **Namespace Routing**: Amazon Bedrock AgentCore Memory automatically routes to correct namespace based on strategy configuration

## Manual Memory Management

Memory management is handled through the `manage_memories.py` script rather than direct SRE agent commands:

### Viewing Memories
```bash
# List all memory types
uv run python scripts/manage_memories.py list

# List specific memory type
uv run python scripts/manage_memories.py list --memory-type preferences

# List memories for specific user
uv run python scripts/manage_memories.py list --memory-type preferences --actor-id Alice
```

### Managing User Preferences
```bash
# Load user preferences from YAML configuration
uv run python scripts/manage_memories.py update

# Load from custom configuration file
uv run python scripts/manage_memories.py update --config-file custom_users.yaml
```

## Configuration

Memory system behavior can be configured through environment variables or configuration files:

```python
from sre_agent.memory.config import MemoryConfig

config = MemoryConfig(
    enabled=True,                        # Enable/disable memory system
    memory_name="sre-agent-memory",     # Base name for memory instances
    region="us-west-2",                 # AWS region for storage (default: "us-east-1")
    
    # Retention settings (days)
    preferences_retention_days=90,       # User preferences (default: 90)
    infrastructure_retention_days=30,   # Infrastructure knowledge (default: 30)
    investigation_retention_days=60,    # Investigation summaries (default: 60)
    
    # Auto-capture flags
    auto_capture_preferences=True,      # Automatically capture user preferences (default: True)
    auto_capture_infrastructure=True,   # Automatically capture infrastructure patterns (default: True)
    auto_generate_summaries=True        # Automatically generate investigation summaries (default: True)
)
```

## Memory Tool Architecture

The memory system uses a centralized architecture where **only the supervisor agent has direct access to memory tools**:

### Tool Distribution Architecture
- **Supervisor Agent**: Has access to all 4 memory tools (`retrieve_memory`, `save_preference`, `save_infrastructure`, `save_investigation`)
- **Individual Agents**: Have NO direct access to memory tools, only domain-specific tools:
  - **Kubernetes Agent**: 5 k8s-api tools (get_pod_status, get_deployment_status, etc.)
  - **Application Logs Agent**: 5 logs-api tools (search_logs, get_error_logs, etc.)  
  - **Performance Metrics Agent**: 5 metrics-api tools (get_performance_metrics, analyze_trends, etc.)
  - **Operational Runbooks Agent**: 5 runbooks-api tools (search_runbooks, get_incident_playbook, etc.)

### Centralized Memory Management
This design ensures:
- **Memory operations are coordinated** through the supervisor
- **Individual agents focus on their domain expertise** without memory complexity
- **Memory context is retrieved once** and distributed to agents as needed
- **Consistent memory patterns** across all investigations

### Available Memory Tools (Supervisor Only)
- **save_preference**: Saves user preferences to long-term memory
- **save_infrastructure**: Saves infrastructure knowledge to long-term memory
- **save_investigation**: Saves investigation summaries to long-term memory  
- **retrieve_memory**: Retrieves relevant information from long-term memory

### Memory Capture Methods
1. **Supervisor tool calls**: `retrieve_memory` called during planning; `save_investigation` called via planning agent
2. **Automatic pattern extraction**: Agent responses are processed by `on_agent_response()` hook to extract:
   - User preferences (escalation emails, Slack channels)
   - Infrastructure knowledge (service dependencies, baselines)
   - Calls `_save_*` functions directly (not tool calls)
3. **Manual configuration**: User preferences loaded via `manage_memories.py update`
4. **Conversation storage**: All agent responses and tool calls stored as conversation memory

### Memory Operation Logging
The system provides comprehensive logging of all memory operations for monitoring and debugging:

#### Message Composition Tracking
Each agent execution logs message composition before storing conversations:
```
Performance Metrics Agent - Message breakdown: 1 USER, 1 ASSISTANT, 7 TOOL messages
Performance Metrics Agent - Tools called: metrics-api___get_performance_metrics, metrics-api___get_resource_metrics, metrics-api___get_error_rates, metrics-api___get_availability_metrics, metrics-api___analyze_trends
```

#### Pattern Extraction Monitoring
Automatic pattern extraction is logged for each agent response:
```
Performance Metrics Agent - Extracting user preferences from Performance Metrics Agent response for user Alice
Performance Metrics Agent - Extracting infrastructure knowledge from Performance Metrics Agent
Performance Metrics Agent - Processed agent response for memory pattern extraction
```

#### Memory Persistence Verification
All memory save operations are logged with event IDs for verification:
```
Saved preferences event for Alice (event_id: 0000001754188852000#36d4c356)
Saved investigation summary for incident payment-slowness-20250803 with status ongoing
Successfully stored conversation batch of 13 messages (event_id: 0000001754188967000#b704c436)
```

## Memory Flow During Investigation

```
┌─────────────┐    ┌─────────────────────┐    ┌──────────────────────┐
│    User     │    │     Supervisor      │    │  Amazon Bedrock      │
│             │    │      Agent          │    │  AgentCore Memory    │
└──────┬──────┘    └──────────┬──────────┘    └──────────┬───────────┘
       │                      │                          │
       │ Investigation Query  │                          │
       ├─────────────────────►│                          │
       │                      │                          │
       │              ┌───────▼───────┐                  │
       │              │ on_investigation_start()         │
       │              │ (memory_hooks) │                 │
       │              └───────┬───────┘                  │
       │                      │                          │
       │                      │ retrieve_memory(preferences) │
       │                      ├─────────────────────────►│
       │                      │◄─────────────────────────┤
       │                      │ User preferences (10)    │
       │                      │                          │
       │                      │ retrieve_memory(infrastructure) │
       │                      ├─────────────────────────►│
       │                      │◄─────────────────────────┤
       │                      │ Infrastructure data (50) │
       │                      │                          │
       │                      │ retrieve_memory(investigations) │
       │                      ├─────────────────────────►│
       │                      │◄─────────────────────────┤
       │                      │ Past investigations (5)  │
       │                      │                          │
       │              ┌───────▼───────┐                  │
       │              │ Create Investigation Plan        │
       │              │ (with memory context)           │
       │              └───────┬───────┘                  │
       │                      │                          │
       │                      │ save_investigation()     │
       │                      │ (planning summary)       │
       │                      ├─────────────────────────►│
       │                      │◄─────────────────────────┤
       │                      │ Event ID                 │
       │                      │                          │
       │              ┌───────▼───────┐                  │
       │              │ Execute Investigation           │
       │              │ (dispatch to agents)            │
       │              └───────┬───────┘                  │
       │                      │                          │
       │                      ├─► Metrics Agent          │
       │                      ├─► Logs Agent             │
       │                      ├─► K8s Agent              │
       │                      ├─► Runbooks Agent         │
       │                      │                          │
       │              ┌───────▼───────┐                  │
       │              │ Agent Response Processing        │
       │              │ (in agent_nodes.py)             │
       │              └───────┬───────┘                  │
       │                      │                          │
       │                      │ Store conversation       │
       │                      │ (agent response + tools) │
       │                      ├─────────────────────────►│
       │                      │                          │
       │              ┌───────▼───────┐                  │
       │              │ on_agent_response()              │
       │              │ (pattern recognition)            │
       │              └───────┬───────┘                  │
       │                      │                          │
       │                      │ _save_infrastructure_knowledge() │
       │                      │ (direct function call)  │
       │                      ├─────────────────────────►│
       │                      │                          │
       │                      │ _save_user_preference()  │
       │                      │ (direct function call)  │
       │                      ├─────────────────────────►│
       │                      │                          │
       │              ┌───────▼───────┐                  │
       │              │ on_investigation_complete()      │
       │              │ (memory_hooks) │                 │
       │              └───────┬───────┘                  │
       │                      │                          │
       │                      │ _save_investigation_summary() │
       │                      │ (direct function call)  │
       │                      ├─────────────────────────►│
       │                      │◄─────────────────────────┤
       │                      │ Final Event ID           │
       │                      │                          │
       │ Final Response       │                          │
       │◄─────────────────────┤                          │
       │                      │                          │
```

### Key Memory Interactions

1. **Investigation Startup** (supervisor.py:299):
   - Supervisor calls `on_investigation_start()` hook
   - Hook automatically retrieves user preferences, infrastructure knowledge, and past investigations
   - Memory context is included in investigation planning

2. **Planning Phase**:
   - Supervisor's planning agent may call `save_investigation` tool to document planning summary
   - This is a **tool call** through the LangChain agent framework

3. **Agent Execution**:
   - Individual agents focus **exclusively** on their domain tools (metrics-api, logs-api, etc.)
   - Individual agents **do NOT have access** to memory tools (`retrieve_memory` not available)
   - Each agent response is automatically processed for memory capture

4. **Response Processing** (agent_nodes.py:310-375):
   - **Message composition logging**: Message breakdown logged (X USER, Y ASSISTANT, Z TOOL messages)  
   - **Tool execution tracking**: All tool names called during agent execution are logged
   - Agent responses and tool calls are stored as conversation memory
   - `on_agent_response()` hook is called to analyze responses using pattern recognition
   - Pattern extraction identifies:
     - Escalation contacts (e.g., "escalate to team@company.com")
     - Notification channels (e.g., "notify #sre-alerts")
     - Service dependencies (e.g., "web-api depends on postgres-db")
     - Performance baselines (e.g., "normal response time is 150ms")
   - Calls `_save_infrastructure_knowledge()` and `_save_user_preference()` **directly** (not tool calls)
   - Uses regex patterns to extract structured data from agent responses
   - **Agent identification**: Uses SREConstants for proper agent name matching in infrastructure extraction

5. **Investigation Completion** (supervisor.py:686):
   - Supervisor calls `on_investigation_complete()` hook  
   - Hook calls `_save_investigation_summary()` **directly** (not tool call)
   - Stores final investigation summary with timeline, actions, and findings

## Integration with Existing Agents

The memory system integrates seamlessly with existing SRE agents:

### Kubernetes Agent
- **Captures:** Service dependencies, deployment patterns, resource baselines
- **Uses:** Past deployment issues, known resource requirements

### Logs Agent  
- **Captures:** Common error patterns, log query preferences, resolution strategies
- **Uses:** Similar error patterns, effective log queries from past investigations

### Metrics Agent
- **Captures:** Performance baselines, alert thresholds, metric correlations  
- **Uses:** Historical baselines, known performance patterns

### Runbooks Agent
- **Captures:** Successful resolution procedures, team escalation paths
- **Uses:** Proven resolution strategies, appropriate runbook recommendations

## Memory Context in Planning

When creating investigation plans, the supervisor agent incorporates memory context:

```python
# Enhanced planning prompt includes:
"""
User's query: Why is my Redis service down?

Relevant User Preferences:
- Escalation contact: redis-team@company.com
- Notification channel: #redis-alerts

Relevant Infrastructure Knowledge:
- Redis typically recovers within 2-3 minutes
- Common cause: Memory pressure from data ingestion spikes
- Dependencies: User-service, Session-service, Cart-service

Similar Past Investigations:
- Incident_20250115: Redis OOM caused by memory leak (Resolution: Restart + config tuning)
- Incident_20250120: Redis slow response due to disk I/O (Resolution: Moved to SSD)

Create an investigation plan considering this context...
"""
```

## Benefits

### For Users
- **Personalized Experience:** Remembers preferences and communication styles
- **Faster Resolution:** Leverages past investigation knowledge  
- **Consistent Escalation:** Automatically suggests appropriate contacts
- **Historical Context:** References similar past issues and solutions

### For Teams
- **Knowledge Sharing:** Captures tribal knowledge automatically
- **Pattern Recognition:** Identifies recurring infrastructure issues
- **Onboarding Support:** New team members benefit from accumulated knowledge
- **Continuous Learning:** System becomes more effective over time

### For Operations
- **Reduced MTTR:** Faster problem resolution through historical context
- **Better Escalation:** Appropriate team routing based on past patterns
- **Knowledge Retention:** Preserves institutional knowledge even with team changes
- **Trend Analysis:** Identifies patterns across multiple incidents

## Privacy and Data Management

### Data Retention
- User preferences: 90 days (configurable)
- Infrastructure knowledge: 30 days (configurable)  
- Investigation summaries: 60 days (configurable)

### Data Export
```python
from sre_agent.memory.export import MemoryExporter

exporter = MemoryExporter(memory_client)

# Export all user preferences
preferences = await exporter.export_user_preferences("user123", format="json")

# Export investigation history  
history = await exporter.export_investigation_history(
    start_date=datetime(2025, 1, 1),
    end_date=datetime(2025, 1, 31)
)
```

### Memory Cleanup
```python
# Clear specific user's preferences
await memory_client.clear_memory("preferences", actor_id="user123")

# Clear all infrastructure knowledge
await memory_client.clear_memory("infrastructure")
```

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────┐
│   Supervisor    │    │   Memory Hooks   │    │  AgentCore Memory   │
│     Agent       │◄──►│    Provider      │◄──►│     (Bedrock)       │
└─────────────────┘    └──────────────────┘    └─────────────────────┘
         ▲                        ▲                         ▲
         │                        │                         │
         ▼                        ▼                         ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────┐
│  Memory Tools   │    │  Memory Client   │    │   Memory Storage    │
│ (Save/Retrieve) │◄──►│   (SRE-specific) │◄──►│   (AWS Backend)     │
└─────────────────┘    └──────────────────┘    └─────────────────────┘
```

## Setting Up Memory System

### Initial Setup

The memory system is automatically initialized during the setup process:

```bash
# Initialize memory system and load user preferences (included in setup instructions)
uv run python scripts/manage_memories.py update
```

This command:
1. Creates a new memory resource if none exists
2. Configures the three memory strategies
3. Loads user preferences from `scripts/user_config.yaml`
4. Stores the memory ID in `.memory_id` for future use

### Adding User Preferences

To add new users or modify existing preferences:

1. Edit `scripts/user_config.yaml` to add new user configurations
2. Run the update command to load new preferences:
```bash
uv run python scripts/manage_memories.py update
```

### Managing Memories

```bash
# List all memory types
uv run python scripts/manage_memories.py list

# List specific memory type
uv run python scripts/manage_memories.py list --memory-type preferences

# List preferences for specific user
uv run python scripts/manage_memories.py list --memory-type preferences --actor-id Alice
```

## Getting Started

1. **Initialize Memory:** Run `uv run python scripts/manage_memories.py update` during setup
2. **Set User Context:** Use `USER_ID=username` environment variable for personalized investigations  
3. **Start Investigating:** Begin investigations - memory capture happens automatically
4. **Monitor:** Check logs for memory save/retrieve operations and pattern extraction activities
5. **Query:** Use natural language to query accumulated memories

The memory system requires no changes to existing workflows - it operates transparently while building knowledge that makes future investigations more effective.