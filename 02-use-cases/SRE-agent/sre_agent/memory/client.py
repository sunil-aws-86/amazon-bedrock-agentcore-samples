import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone, timedelta

from bedrock_agentcore.clients import MemoryClient
from bedrock_agentcore.models import MemoryStrategy
from pydantic import BaseModel, Field

from .config import _load_memory_config

# Configure logging with basicConfig
logging.basicConfig(
    level=logging.INFO,  # Set the log level to INFO
    # Define log message format
    format="%(asctime)s,p%(process)s,{%(filename)s:%(lineno)d},%(levelname)s,%(message)s",
)

logger = logging.getLogger(__name__)


class SREMemoryClient:
    """Wrapper for AgentCore Memory client tailored for SRE operations."""
    
    def __init__(
        self,
        memory_name: str = "sre-agent-memory",
        region: str = "us-east-1"
    ):
        self.client = MemoryClient(region_name=region)
        self.memory_name = memory_name
        self.config = _load_memory_config()
        self._initialize_memories()
    
    def _initialize_memories(self):
        """Initialize different memory strategies."""
        try:
            # User preferences memory
            self.client.create_memory(
                name=f"{self.memory_name}-preferences",
                namespace="/sre/users/{userId}/preferences",
                strategy=MemoryStrategy.SEMANTIC,
                event_expiry_days=self.config.preferences_retention_days
            )
            logger.info("Initialized user preferences memory")
            
            # Infrastructure knowledge memory
            self.client.create_memory(
                name=f"{self.memory_name}-infrastructure",
                namespace="/sre/infrastructure/{service}",
                strategy=MemoryStrategy.SEMANTIC,
                event_expiry_days=self.config.infrastructure_retention_days
            )
            logger.info("Initialized infrastructure knowledge memory")
            
            # Investigation summaries memory
            self.client.create_memory(
                name=f"{self.memory_name}-investigations",
                namespace="/sre/investigations/{incidentId}",
                strategy=MemoryStrategy.SUMMARY,
                event_expiry_days=self.config.investigation_retention_days
            )
            logger.info("Initialized investigation summaries memory")
            
        except Exception as e:
            logger.error(f"Failed to initialize memories: {e}")
            raise
    
    async def save_event(
        self,
        memory_type: str,
        actor_id: str,
        event_data: Dict[str, Any]
    ) -> bool:
        """Save an event to the specified memory type."""
        try:
            memory_name = f"{self.memory_name}-{memory_type}"
            
            # Create event with appropriate namespace
            namespace = self._get_namespace(memory_type, actor_id)
            
            result = await self.client.create_event(
                memory_name=memory_name,
                namespace=namespace,
                event_data=event_data
            )
            
            logger.info(f"Saved {memory_type} event for {actor_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save {memory_type} event: {e}")
            return False
    
    async def retrieve_memories(
        self,
        memory_type: str,
        actor_id: str,
        query: str,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """Retrieve memories from the specified memory type."""
        try:
            memory_name = f"{self.memory_name}-{memory_type}"
            namespace = self._get_namespace(memory_type, actor_id)
            
            result = await self.client.query_memory(
                memory_name=memory_name,
                namespace=namespace,
                query=query,
                max_results=max_results
            )
            
            logger.info(f"Retrieved {len(result)} {memory_type} memories for {actor_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to retrieve {memory_type} memories: {e}")
            return []
    
    async def get_all_events(
        self,
        memory_type: str,
        actor_id: str
    ) -> List[Dict[str, Any]]:
        """Get all events for a specific actor in a memory type."""
        try:
            memory_name = f"{self.memory_name}-{memory_type}"
            namespace = self._get_namespace(memory_type, actor_id)
            
            result = await self.client.list_events(
                memory_name=memory_name,
                namespace=namespace
            )
            
            logger.info(f"Retrieved all {memory_type} events for {actor_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to get all {memory_type} events: {e}")
            return []
    
    def _get_namespace(
        self,
        memory_type: str,
        actor_id: str
    ) -> str:
        """Get the appropriate namespace for a memory type and actor."""
        namespace_map = {
            "preferences": f"/sre/users/{actor_id}/preferences",
            "infrastructure": f"/sre/infrastructure/{actor_id}",
            "investigations": f"/sre/investigations/{actor_id}"
        }
        
        return namespace_map.get(memory_type, f"/sre/default/{actor_id}")
    
    async def clear_memory(
        self,
        memory_type: str,
        actor_id: Optional[str] = None
    ) -> bool:
        """Clear memories for a specific type and optionally actor."""
        try:
            memory_name = f"{self.memory_name}-{memory_type}"
            
            if actor_id:
                namespace = self._get_namespace(memory_type, actor_id)
                await self.client.clear_namespace(
                    memory_name=memory_name,
                    namespace=namespace
                )
                logger.info(f"Cleared {memory_type} memory for {actor_id}")
            else:
                await self.client.clear_memory(memory_name=memory_name)
                logger.info(f"Cleared all {memory_type} memory")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear {memory_type} memory: {e}")
            return False