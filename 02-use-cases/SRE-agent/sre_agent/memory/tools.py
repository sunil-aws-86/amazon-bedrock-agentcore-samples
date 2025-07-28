import logging
import json
from typing import Dict, Any, Optional, List
from langchain_core.tools import Tool

from .client import SREMemoryClient
from .strategies import (
    UserPreference,
    InfrastructureKnowledge,
    InvestigationSummary,
    _save_user_preference,
    _save_infrastructure_knowledge,
    _save_investigation_summary,
    _retrieve_user_preferences,
    _retrieve_infrastructure_knowledge,
    _retrieve_investigation_summaries,
)

# Configure logging with basicConfig
logging.basicConfig(
    level=logging.INFO,  # Set the log level to INFO
    # Define log message format
    format="%(asctime)s,p%(process)s,{%(filename)s:%(lineno)d},%(levelname)s,%(message)s",
)

logger = logging.getLogger(__name__)


class SaveMemoryTool(Tool):
    """Tool for saving memories during SRE operations."""
    
    name = "save_memory"
    description = """Save important information to long-term memory.
    Use this to remember:
    - User preferences (escalation contacts, notification channels, workflows, styles)
    - Infrastructure knowledge (dependencies, patterns, configurations, baselines)
    - Investigation summaries (timeline, actions, findings, resolution status)
    
    Args:
        memory_type: Type of memory ('preference', 'infrastructure', 'investigation')
        content: Dictionary containing the memory data
        context: Optional context information
    
    Returns:
        String confirmation of what was saved
    """
    
    def __init__(
        self,
        memory_client: SREMemoryClient
    ):
        super().__init__(
            name=self.name,
            description=self.description,
            func=self._save_memory
        )
        self.memory_client = memory_client
    
    async def _save_memory(
        self,
        memory_type: str,
        content: Dict[str, Any],
        context: Optional[str] = None
    ) -> str:
        """Save memory based on type."""
        try:
            if memory_type == "preference":
                # Validate and create UserPreference
                if context:
                    content["context"] = context
                
                preference = UserPreference(**content)
                success = await _save_user_preference(
                    self.memory_client,
                    preference.user_id,
                    preference
                )
                
                if success:
                    return f"Saved user preference: {preference.preference_type} for user {preference.user_id}"
                else:
                    return f"Failed to save user preference: {preference.preference_type}"
            
            elif memory_type == "infrastructure":
                # Validate and create InfrastructureKnowledge
                knowledge = InfrastructureKnowledge(**content)
                success = await _save_infrastructure_knowledge(
                    self.memory_client,
                    knowledge.service_name,
                    knowledge
                )
                
                if success:
                    return f"Saved infrastructure knowledge: {knowledge.knowledge_type} for {knowledge.service_name}"
                else:
                    return f"Failed to save infrastructure knowledge for {knowledge.service_name}"
            
            elif memory_type == "investigation":
                # Validate and create InvestigationSummary
                summary = InvestigationSummary(**content)
                success = await _save_investigation_summary(
                    self.memory_client,
                    summary.incident_id,
                    summary
                )
                
                if success:
                    return f"Saved investigation summary for incident {summary.incident_id}"
                else:
                    return f"Failed to save investigation summary for {summary.incident_id}"
            
            else:
                return f"Unknown memory type: {memory_type}. Supported types: preference, infrastructure, investigation"
                
        except Exception as e:
            logger.error(f"Error saving memory: {e}")
            return f"Error saving {memory_type} memory: {str(e)}"


class RetrieveMemoryTool(Tool):
    """Tool for retrieving memories during SRE operations."""
    
    name = "retrieve_memory"
    description = """Retrieve relevant information from long-term memory.
    Query for:
    - User preferences for current context (escalation, notification, workflow preferences)
    - Infrastructure knowledge about services (dependencies, patterns, baselines)
    - Past investigation summaries (similar issues, resolution strategies)
    
    Args:
        memory_type: Type of memory ('preference', 'infrastructure', 'investigation')
        query: Search query to find relevant memories
        actor_id: Optional specific actor ID to search for
        max_results: Maximum number of results to return (default: 5)
    
    Returns:
        List of relevant memories as JSON string
    """
    
    def __init__(
        self,
        memory_client: SREMemoryClient
    ):
        super().__init__(
            name=self.name,
            description=self.description,
            func=self._retrieve_memory
        )
        self.memory_client = memory_client
    
    async def _retrieve_memory(
        self,
        memory_type: str,
        query: str,
        actor_id: Optional[str] = None,
        max_results: int = 5
    ) -> str:
        """Retrieve memories based on query."""
        try:
            if memory_type == "preference":
                if not actor_id:
                    return "Error: actor_id (user_id) is required for preference queries"
                
                preferences = await _retrieve_user_preferences(
                    self.memory_client,
                    actor_id,
                    query
                )
                
                # Convert to dict for JSON serialization
                results = [pref.model_dump() for pref in preferences[:max_results]]
                return json.dumps(results, indent=2, default=str)
            
            elif memory_type == "infrastructure":
                knowledge = await _retrieve_infrastructure_knowledge(
                    self.memory_client,
                    query,
                    actor_id
                )
                
                # Convert to dict for JSON serialization
                results = [know.model_dump() for know in knowledge[:max_results]]
                return json.dumps(results, indent=2, default=str)
            
            elif memory_type == "investigation":
                summaries = await _retrieve_investigation_summaries(
                    self.memory_client,
                    query,
                    actor_id
                )
                
                # Convert to dict for JSON serialization
                results = [summary.model_dump() for summary in summaries[:max_results]]
                return json.dumps(results, indent=2, default=str)
            
            else:
                return json.dumps({
                    "error": f"Unknown memory type: {memory_type}",
                    "supported_types": ["preference", "infrastructure", "investigation"]
                }, indent=2)
                
        except Exception as e:
            logger.error(f"Error retrieving memory: {e}")
            return json.dumps({
                "error": f"Error retrieving {memory_type} memory: {str(e)}"
            }, indent=2)


def _create_memory_tools(
    memory_client: SREMemoryClient
) -> List[Tool]:
    """Create memory tools for the agent."""
    return [
        SaveMemoryTool(memory_client),
        RetrieveMemoryTool(memory_client)
    ]