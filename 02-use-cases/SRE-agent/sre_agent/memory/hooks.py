import logging
import re
from typing import Dict, Any, Optional, List
from datetime import datetime

from .client import SREMemoryClient
from .strategies import (
    UserPreference,
    InfrastructureKnowledge,
    InvestigationSummary,
    _save_user_preference,
    _save_infrastructure_knowledge,
    _save_investigation_summary,
)

# Configure logging with basicConfig
logging.basicConfig(
    level=logging.INFO,  # Set the log level to INFO
    # Define log message format
    format="%(asctime)s,p%(process)s,{%(filename)s:%(lineno)d},%(levelname)s,%(message)s",
)

logger = logging.getLogger(__name__)


class MemoryHookProvider:
    """Provides hooks for automatic memory capture during SRE operations."""
    
    def __init__(
        self,
        memory_client: SREMemoryClient
    ):
        self.memory_client = memory_client
    
    async def on_investigation_start(
        self,
        query: str,
        user_id: str,
        incident_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Hook called when investigation starts."""
        try:
            # Retrieve relevant memories to provide context
            preferences = await self.memory_client.retrieve_memories(
                memory_type="preferences",
                actor_id=user_id,
                query=query,
                max_results=5
            )
            
            # Get infrastructure knowledge related to the query
            knowledge = await self.memory_client.retrieve_memories(
                memory_type="infrastructure",
                actor_id="default",
                query=query,
                max_results=10
            )
            
            # Get past investigation summaries for similar issues
            investigations = await self.memory_client.retrieve_memories(
                memory_type="investigations",
                actor_id="default",
                query=query,
                max_results=5
            )
            
            memory_context = {
                "user_preferences": preferences,
                "infrastructure_knowledge": knowledge,
                "past_investigations": investigations
            }
            
            logger.info(f"Retrieved memory context for investigation: {len(preferences)} preferences, {len(knowledge)} knowledge items, {len(investigations)} past investigations")
            
            return memory_context
            
        except Exception as e:
            logger.error(f"Failed to retrieve memory context on investigation start: {e}")
            return {
                "user_preferences": [],
                "infrastructure_knowledge": [],
                "past_investigations": []
            }
    
    async def on_agent_response(
        self,
        agent_name: str,
        response: Dict[str, Any],
        state: Dict[str, Any]
    ):
        """Hook called after each agent responds to capture knowledge."""
        try:
            user_id = state.get("user_id", "default")
            response_text = str(response.get("content", ""))
            
            # Extract and save user preferences
            await self._extract_user_preferences(
                response_text,
                user_id,
                agent_name
            )
            
            # Extract infrastructure knowledge
            if agent_name in ["kubernetes", "metrics", "logs"]:
                await self._extract_infrastructure_knowledge(
                    response_text,
                    agent_name,
                    state
                )
            
        except Exception as e:
            logger.error(f"Failed to process agent response for memory capture: {e}")
    
    async def on_investigation_complete(
        self,
        state: Dict[str, Any],
        final_response: str
    ):
        """Hook called when investigation completes to save summary."""
        try:
            incident_id = state.get("incident_id") or f"incident_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            # Extract timeline from agent results
            timeline = self._extract_timeline(state.get("agent_results", {}))
            
            # Extract actions taken
            actions_taken = self._extract_actions(
                state.get("agents_invoked", []),
                state.get("agent_results", {})
            )
            
            # Extract key findings
            key_findings = self._extract_key_findings(final_response)
            
            # Determine resolution status
            resolution_status = self._determine_resolution_status(final_response)
            
            summary = InvestigationSummary(
                incident_id=incident_id,
                query=state.get("current_query", ""),
                timeline=timeline,
                actions_taken=actions_taken,
                resolution_status=resolution_status,
                key_findings=key_findings
            )
            
            success = await _save_investigation_summary(
                self.memory_client,
                incident_id,
                summary
            )
            
            if success:
                logger.info(f"Saved investigation summary for incident {incident_id}")
            else:
                logger.warning(f"Failed to save investigation summary for incident {incident_id}")
                
        except Exception as e:
            logger.error(f"Failed to save investigation summary: {e}")
    
    async def _extract_user_preferences(
        self,
        response_text: str,
        user_id: str,
        context: str
    ):
        """Extract user preferences from response text."""
        # Extract escalation preferences
        escalation_patterns = [
            r"escalate to ([^\s,\.]+@[^\s,\.]+)",
            r"contact ([^\s,\.]+@[^\s,\.]+)",
            r"notify ([^\s,\.]+@[^\s,\.]+)",
            r"reach out to ([^\s,\.]+@[^\s,\.]+)"
        ]
        
        for pattern in escalation_patterns:
            matches = re.finditer(pattern, response_text, re.IGNORECASE)
            for match in matches:
                contact = match.group(1)
                preference = UserPreference(
                    user_id=user_id,
                    preference_type="escalation",
                    preference_value={"contact": contact},
                    context=f"Mentioned during {context} agent response"
                )
                
                await _save_user_preference(
                    self.memory_client,
                    user_id,
                    preference
                )
                logger.info(f"Captured escalation preference: {contact}")
        
        # Extract notification channel preferences
        channel_patterns = [
            r"send to (#[\w-]+)",
            r"notify (#[\w-]+)",
            r"alert (#[\w-]+)",
            r"post to (#[\w-]+)"
        ]
        
        for pattern in channel_patterns:
            matches = re.finditer(pattern, response_text, re.IGNORECASE)
            for match in matches:
                channel = match.group(1)
                preference = UserPreference(
                    user_id=user_id,
                    preference_type="notification",
                    preference_value={"channel": channel},
                    context=f"Mentioned during {context} agent response"
                )
                
                await _save_user_preference(
                    self.memory_client,
                    user_id,
                    preference
                )
                logger.info(f"Captured notification preference: {channel}")
    
    async def _extract_infrastructure_knowledge(
        self,
        response_text: str,
        agent_name: str,
        state: Dict[str, Any]
    ):
        """Extract infrastructure knowledge from agent responses."""
        # Extract service dependencies
        dependency_patterns = [
            r"(\w+) depends on (\w+)",
            r"(\w+) requires (\w+)",
            r"(\w+) connects to (\w+)"
        ]
        
        for pattern in dependency_patterns:
            matches = re.finditer(pattern, response_text, re.IGNORECASE)
            for match in matches:
                service = match.group(1)
                dependency = match.group(2)
                
                knowledge = InfrastructureKnowledge(
                    service_name=service,
                    knowledge_type="dependency",
                    knowledge_data={
                        "depends_on": dependency,
                        "discovered_by": agent_name
                    },
                    confidence=0.7
                )
                
                await _save_infrastructure_knowledge(
                    self.memory_client,
                    service,
                    knowledge
                )
                logger.info(f"Captured dependency: {service} -> {dependency}")
        
        # Extract performance baselines for metrics agent
        if agent_name == "metrics":
            baseline_patterns = [
                r"baseline (\w+) is ([0-9\.]+)",
                r"normal (\w+) is ([0-9\.]+)",
                r"typical (\w+) ranges from ([0-9\.]+) to ([0-9\.]+)"
            ]
            
            for pattern in baseline_patterns:
                matches = re.finditer(pattern, response_text, re.IGNORECASE)
                for match in matches:
                    metric = match.group(1)
                    value = match.group(2)
                    
                    knowledge = InfrastructureKnowledge(
                        service_name="system",
                        knowledge_type="baseline",
                        knowledge_data={
                            "metric": metric,
                            "value": value,
                            "discovered_by": agent_name
                        },
                        confidence=0.8
                    )
                    
                    await _save_infrastructure_knowledge(
                        self.memory_client,
                        "system",
                        knowledge
                    )
                    logger.info(f"Captured baseline: {metric} = {value}")
    
    def _extract_timeline(
        self,
        agent_results: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Extract timeline from agent results."""
        timeline = []
        
        for agent, result in agent_results.items():
            timeline.append({
                "timestamp": datetime.utcnow().isoformat(),
                "agent": agent,
                "action": f"Executed {agent} agent",
                "result_summary": str(result)[:200] + "..." if len(str(result)) > 200 else str(result)
            })
        
        return timeline
    
    def _extract_actions(
        self,
        agents_invoked: List[str],
        agent_results: Dict[str, Any]
    ) -> List[str]:
        """Extract actions taken during investigation."""
        actions = []
        
        for agent in agents_invoked:
            actions.append(f"Invoked {agent} agent for investigation")
        
        # Add specific actions based on agent results
        for agent, result in agent_results.items():
            result_str = str(result).lower()
            if "error" in result_str or "failed" in result_str:
                actions.append(f"{agent} agent detected issues")
            elif "found" in result_str or "identified" in result_str:
                actions.append(f"{agent} agent found relevant information")
        
        return actions
    
    def _extract_key_findings(
        self,
        final_response: str
    ) -> List[str]:
        """Extract key findings from final response."""
        findings = []
        
        # Look for common finding patterns
        finding_patterns = [
            r"(?:found|discovered|identified|detected):\s*([^\.]+)",
            r"(?:issue|problem|error):\s*([^\.]+)",
            r"(?:solution|fix|resolution):\s*([^\.]+)"
        ]
        
        for pattern in finding_patterns:
            matches = re.finditer(pattern, final_response, re.IGNORECASE)
            for match in matches:
                finding = match.group(1).strip()
                if finding and len(finding) > 10:  # Filter out very short findings
                    findings.append(finding)
        
        return findings[:5]  # Limit to top 5 findings
    
    def _determine_resolution_status(
        self,
        final_response: str
    ) -> str:
        """Determine resolution status from final response."""
        response_lower = final_response.lower()
        
        if any(word in response_lower for word in ["resolved", "fixed", "solved", "completed"]):
            return "completed"
        elif any(word in response_lower for word in ["escalat", "contact", "need help"]):
            return "escalated"
        else:
            return "ongoing"