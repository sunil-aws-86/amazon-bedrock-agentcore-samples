import logging
import json
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
    context: Optional[str] = Field(
        default=None,
        description="Context where this knowledge was discovered"
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
    context: Optional[str] = Field(
        default=None,
        description="Context describing the investigation circumstances"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="When this summary was created"
    )


def _save_user_preference(
    client,
    user_id: str,
    preference: UserPreference
) -> bool:
    """Save user preference to memory."""
    try:
        logger.info(f"Saving user preference: type={preference.preference_type}, user_id={user_id}")
        success = client.save_event(
            memory_type="preferences",
            actor_id=user_id,
            event_data=preference.model_dump()
        )
        if success:
            logger.info(f"Saved {preference.preference_type} preference for user {user_id}")
        else:
            logger.warning(f"Failed to save {preference.preference_type} preference for user {user_id}")
        return success
    except Exception as e:
        logger.error(f"Failed to save user preference: {e}", exc_info=True)
        return False


def _retrieve_user_preferences(
    client,
    user_id: str,
    query: str
) -> List[UserPreference]:
    """Retrieve relevant user preferences."""
    try:
        logger.info(f"Retrieving user preferences: user_id={user_id}, query='{query}'")
        memories = client.retrieve_memories(
            memory_type="preferences",
            actor_id=user_id,
            query=query
        )
        logger.info(f"Retrieved {len(memories)} preference memories from storage")
        
        # Note: Need to parse the memory content structure
        preferences = []
        for i, mem in enumerate(memories):
            try:
                # Extract content from memory structure
                content = mem.get("content", {})
                logger.info(f"Processing preference memory {i}: content type={type(content)}")
                
                if isinstance(content, dict):
                    preferences.append(UserPreference(**content))
                elif isinstance(content, str):
                    # Try to parse as JSON
                    import json
                    data = json.loads(content)
                    preferences.append(UserPreference(**data))
                
                logger.info(f"Successfully parsed preference memory {i}")
            except Exception as e:
                logger.warning(f"Failed to parse preference memory {i}: {e}")
                continue
        
        logger.info(f"Retrieved {len(preferences)} parsed user preferences for {user_id}")
        return preferences
    except Exception as e:
        logger.error(f"Failed to retrieve user preferences: {e}", exc_info=True)
        return []


def _save_infrastructure_knowledge(
    client,
    actor_id: str,
    knowledge: InfrastructureKnowledge,
    session_id: str
) -> bool:
    """Save infrastructure knowledge to memory."""
    try:
        logger.info(f"Saving infrastructure knowledge: type={knowledge.knowledge_type}, service={knowledge.service_name}, confidence={knowledge.confidence}, actor_id={actor_id}")
        success = client.save_event(
            memory_type="infrastructure",
            actor_id=actor_id,
            event_data=knowledge.model_dump(),
            session_id=session_id
        )
        if success:
            logger.info(f"Saved {knowledge.knowledge_type} knowledge for service {knowledge.service_name} by actor {actor_id}")
        else:
            logger.warning(f"Failed to save {knowledge.knowledge_type} knowledge for service {knowledge.service_name} by actor {actor_id}")
        return success
    except Exception as e:
        logger.error(f"Failed to save infrastructure knowledge: {e}", exc_info=True)
        return False


def _retrieve_infrastructure_knowledge(
    client,
    actor_id: str,
    query: str
) -> List[InfrastructureKnowledge]:
    """Retrieve relevant infrastructure knowledge."""
    try:
        memories = client.retrieve_memories(
            memory_type="infrastructure",
            actor_id=actor_id,
            query=query
        )
        # Parse memory content structure
        knowledge_items = []
        for mem in memories:
            try:
                content = mem.get("content", {})
                if isinstance(content, dict):
                    knowledge_items.append(InfrastructureKnowledge(**content))
                elif isinstance(content, str):
                    import json
                    data = json.loads(content)
                    knowledge_items.append(InfrastructureKnowledge(**data))
            except Exception as e:
                logger.warning(f"Failed to parse infrastructure memory: {e}")
                continue
        return knowledge_items
    except Exception as e:
        logger.error(f"Failed to retrieve infrastructure knowledge: {e}")
        return []


def _save_investigation_summary(
    client,
    actor_id: str,
    incident_id: str,
    summary: InvestigationSummary,
    session_id: str
) -> bool:
    """Save investigation summary to memory."""
    try:
        logger.info(f"Saving investigation summary: incident_id={incident_id}, actor_id={actor_id}, session_id={session_id}, status={summary.resolution_status}, actions_count={len(summary.actions_taken)}, findings_count={len(summary.key_findings)}")
        logger.info(f"Full investigation summary for incident_id={incident_id}:\n{json.dumps(summary.model_dump(), indent=2, default=str)}")
        success = client.save_event(
            memory_type="investigations",
            actor_id=actor_id,
            event_data=summary.model_dump(),
            session_id=session_id
        )
        if success:
            logger.info(f"Saved investigation summary for incident {incident_id} with status {summary.resolution_status}")
        else:
            logger.warning(f"Failed to save investigation summary for incident {incident_id}")
        return success
    except Exception as e:
        logger.error(f"Failed to save investigation summary: {e}", exc_info=True)
        return False


def _retrieve_investigation_summaries(
    client,
    actor_id: str,
    query: str
) -> List[InvestigationSummary]:
    """Retrieve relevant investigation summaries."""
    try:
        memories = client.retrieve_memories(
            memory_type="investigations",
            actor_id=actor_id,
            query=query
        )
        # Parse memory content structure
        summaries = []
        for mem in memories:
            try:
                content = mem.get("content", {})
                if isinstance(content, dict):
                    summaries.append(InvestigationSummary(**content))
                elif isinstance(content, str):
                    import json
                    data = json.loads(content)
                    summaries.append(InvestigationSummary(**data))
            except Exception as e:
                logger.warning(f"Failed to parse investigation memory: {e}")
                continue
        return summaries
    except Exception as e:
        logger.error(f"Failed to retrieve investigation summaries: {e}")
        return []