# SRE Agent Memory System

## Overview

The SRE Agent now includes a sophisticated long-term memory system that transforms it from a stateless tool into a learning assistant that becomes more valuable over time. The system is built on Amazon Bedrock AgentCore Memory and provides three distinct memory strategies for different types of information.

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

## Automatic Memory Capture

The memory system automatically captures information during investigations through several mechanisms:

### Investigation Hooks
- **On Start:** Retrieves relevant memories to provide context
- **During Agent Responses:** Extracts preferences and knowledge patterns
- **On Completion:** Saves investigation summary with key findings

### Pattern Recognition
The system uses regex patterns and context analysis to identify:
- Email addresses mentioned for escalation
- Slack channels referenced for notifications  
- Service dependencies mentioned in responses
- Performance baselines and thresholds
- Error patterns and resolution strategies

## Manual Memory Management

Users can also explicitly save and query memories:

### Saving Memories
```bash
# Save a user preference
sre-agent "Remember that for database issues, always escalate to db-team@company.com"

# Save infrastructure knowledge
sre-agent "Note that the payment service depends on Redis and typically recovers within 5 minutes"

# Save investigation notes
sre-agent "Document that the last outage was caused by a memory leak in the user-service"
```

### Querying Memories
```bash
# Query user preferences
sre-agent "What are my escalation contacts for database issues?"

# Query infrastructure knowledge  
sre-agent "What do we know about Redis connection failures?"

# Query past investigations
sre-agent "Show me similar outages in the payment service"
```

## Configuration

Memory system behavior can be configured through environment variables or configuration files:

```python
from sre_agent.memory.config import MemoryConfig

config = MemoryConfig(
    enabled=True,                        # Enable/disable memory system
    memory_name="sre-agent-memory",     # Base name for memory instances
    region="us-east-1",                 # AWS region for storage
    
    # Retention settings (days)
    preferences_retention_days=90,       # User preferences
    infrastructure_retention_days=30,   # Infrastructure knowledge  
    investigation_retention_days=60,    # Investigation summaries
    
    # Auto-capture flags
    auto_capture_preferences=True,      # Automatically capture user preferences
    auto_capture_infrastructure=True,   # Automatically capture infrastructure patterns
    auto_generate_summaries=True        # Automatically generate investigation summaries
)
```

## Memory Tools

The system provides LangChain tools that agents can use:

### SaveMemoryTool
```python
# Usage by agents
await save_memory_tool._save_memory(
    memory_type="preference",
    content={
        "user_id": "user123",
        "preference_type": "escalation", 
        "preference_value": {"contact": "ops@company.com"}
    },
    context="Mentioned during incident response"
)
```

### RetrieveMemoryTool  
```python
# Usage by agents
memories = await retrieve_memory_tool._retrieve_memory(
    memory_type="infrastructure",
    query="Redis connection issues",
    max_results=5
)
```

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

## Getting Started

1. **Enable Memory System:** Ensure `enabled=True` in memory configuration
2. **Set AWS Credentials:** Configure AWS credentials for Bedrock access
3. **Start Using:** Begin investigations - memory capture happens automatically
4. **Monitor:** Check logs for memory save/retrieve operations
5. **Query:** Use natural language to query accumulated memories

The memory system requires no changes to existing workflows - it operates transparently while building knowledge that makes future investigations more effective.