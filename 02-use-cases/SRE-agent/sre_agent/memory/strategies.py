import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

# Configure logging with basicConfig
logging.basicConfig(
    level=logging.INFO,  # Set the log level to INFO
    # Define log message format
    format="%(asctime)s,p%(process)s,{%(filename)s:%(lineno)d},%(levelname)s,%(message)s",
)

logger = logging.getLogger(__name__)


class UserPreference(BaseModel):
    """User preference memory model."""
    
    user_id: str = Field(
        description="Unique identifier for the user"
    )
    preference_type: str = Field(
        description="Type of preference: escalation, notification, workflow, style"
    )
    preference_value: Dict[str, Any] = Field(
        description="The actual preference data"
    )
    context: Optional[str] = Field(
        default=None,
        description="Context where this preference was captured"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="When this preference was recorded"
    )


class InfrastructureKnowledge(BaseModel):
    """Infrastructure knowledge memory model."""
    
    service_name: str = Field(
        description="Name of the service or infrastructure component"
    )
    knowledge_type: str = Field(
        description="Type of knowledge: dependency, pattern, config, baseline"
    )
    knowledge_data: Dict[str, Any] = Field(
        description="The actual knowledge data"
    )
    confidence: float = Field(
        default=0.8,
        ge=0.0,
        le=1.0,
        description="Confidence level in this knowledge (0.0-1.0)"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="When this knowledge was captured"
    )


class InvestigationSummary(BaseModel):
    """Investigation summary memory model."""
    
    incident_id: str = Field(
        description="Unique identifier for the incident"
    )
    query: str = Field(
        description="Original user query that started the investigation"
    )
    timeline: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Timeline of investigation events"
    )
    actions_taken: List[str] = Field(
        default_factory=list,
        description="List of actions taken during investigation"
    )
    resolution_status: str = Field(
        description="Status of the investigation: completed, ongoing, escalated"
    )
    key_findings: List[str] = Field(
        default_factory=list,
        description="Key findings from the investigation"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="When this summary was created"
    )


async def _save_user_preference(
    client,
    user_id: str,
    preference: UserPreference
) -> bool:
    """Save user preference to memory."""
    try:
        return await client.save_event(
            memory_type="preferences",
            actor_id=user_id,
            event_data=preference.model_dump()
        )
    except Exception as e:
        logger.error(f"Failed to save user preference: {e}")
        return False


async def _retrieve_user_preferences(
    client,
    user_id: str,
    query: str
) -> List[UserPreference]:
    """Retrieve relevant user preferences."""
    try:
        memories = await client.retrieve_memories(
            memory_type="preferences",
            actor_id=user_id,
            query=query
        )
        return [UserPreference(**mem) for mem in memories]
    except Exception as e:
        logger.error(f"Failed to retrieve user preferences: {e}")
        return []


async def _save_infrastructure_knowledge(
    client,
    service_name: str,
    knowledge: InfrastructureKnowledge
) -> bool:
    """Save infrastructure knowledge to memory."""
    try:
        return await client.save_event(
            memory_type="infrastructure",
            actor_id=service_name,
            event_data=knowledge.model_dump()
        )
    except Exception as e:
        logger.error(f"Failed to save infrastructure knowledge: {e}")
        return False


async def _retrieve_infrastructure_knowledge(
    client,
    query: str,
    service_name: Optional[str] = None
) -> List[InfrastructureKnowledge]:
    """Retrieve relevant infrastructure knowledge."""
    try:
        memories = await client.retrieve_memories(
            memory_type="infrastructure",
            actor_id=service_name or "default",
            query=query
        )
        return [InfrastructureKnowledge(**mem) for mem in memories]
    except Exception as e:
        logger.error(f"Failed to retrieve infrastructure knowledge: {e}")
        return []


async def _save_investigation_summary(
    client,
    incident_id: str,
    summary: InvestigationSummary
) -> bool:
    """Save investigation summary to memory."""
    try:
        return await client.save_event(
            memory_type="investigations",
            actor_id=incident_id,
            event_data=summary.model_dump()
        )
    except Exception as e:
        logger.error(f"Failed to save investigation summary: {e}")
        return False


async def _retrieve_investigation_summaries(
    client,
    query: str,
    incident_id: Optional[str] = None
) -> List[InvestigationSummary]:
    """Retrieve relevant investigation summaries."""
    try:
        memories = await client.retrieve_memories(
            memory_type="investigations",
            actor_id=incident_id or "default",
            query=query
        )
        return [InvestigationSummary(**mem) for mem in memories]
    except Exception as e:
        logger.error(f"Failed to retrieve investigation summaries: {e}")
        return []