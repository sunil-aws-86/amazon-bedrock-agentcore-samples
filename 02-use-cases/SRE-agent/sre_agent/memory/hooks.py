import logging
import re
from typing import Dict, Any, Optional, List
from datetime import datetime

from .client import SREMemoryClient
from ..constants import SREConstants
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
    
    def on_investigation_start(
        self,
        query: str,
        user_id: str,
        actor_id: str,
        session_id: str,
        incident_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Hook called when investigation starts."""
        try:
            # Retrieve relevant memories to provide context
            preferences = self.memory_client.retrieve_memories(
                memory_type="preferences",
                actor_id=user_id,
                query=query,
                max_results=5
            )
            
            # Get infrastructure knowledge from all agents
            logger.info(f"Retrieving infrastructure knowledge from all agents for query: '{query}'")
            all_knowledge = self.memory_client.retrieve_memories(
                memory_type="infrastructure",
                actor_id="",  # Empty string to retrieve from all agents
                query=query,
                max_results=50,  # Increased limit to get more memories from all agents
                session_id=session_id  # Pass session_id for infrastructure namespace
            )
            
            # Organize knowledge by agent for later distribution
            knowledge_by_agent = self._organize_memories_by_agent(all_knowledge)
            logger.info(f"Retrieved infrastructure knowledge from {len(knowledge_by_agent)} different agents")
            
            # Get past investigation summaries for similar issues
            investigations = self.memory_client.retrieve_memories(
                memory_type="investigations",
                actor_id=actor_id,
                query=query,
                max_results=5,
                session_id=session_id  # Pass session_id for investigations namespace
            )
            
            memory_context = {
                "user_preferences": preferences,
                "infrastructure_by_agent": knowledge_by_agent,
                "past_investigations": investigations
            }
            
            total_knowledge = sum(len(memories) for memories in knowledge_by_agent.values())
            logger.info(f"Retrieved memory context for investigation: {len(preferences)} preferences, {total_knowledge} knowledge items from {len(knowledge_by_agent)} agents, {len(investigations)} past investigations")
            
            return memory_context
            
        except Exception as e:
            logger.error(f"Failed to retrieve memory context on investigation start: {e}")
            return {
                "user_preferences": [],
                "infrastructure_knowledge": [],
                "past_investigations": []
            }
    
    def on_agent_response(
        self,
        agent_name: str,
        response: Dict[str, Any],
        state: Dict[str, Any]
    ):
        """Hook called after each agent responds to capture knowledge."""
        try:
            user_id = state.get("user_id", SREConstants.agents.default_user_id)
            response_text = str(response.get("content", ""))
            response_length = len(response_text)
            
            logger.info(f"Processing {agent_name} agent response for memory capture: user_id={user_id}, response_length={response_length}")
            
            # Extract and save user preferences
            pref_count_before = len(self.memory_client.retrieve_memories("preferences", user_id, "recent", max_results=100))
            self._extract_user_preferences(
                response_text,
                user_id,
                agent_name
            )
            pref_count_after = len(self.memory_client.retrieve_memories("preferences", user_id, "recent", max_results=100))
            
            if pref_count_after > pref_count_before:
                logger.info(f"Extracted {pref_count_after - pref_count_before} new user preferences from {agent_name} response")
            
            # Extract infrastructure knowledge
            if agent_name in ["kubernetes", "metrics", "logs"]:
                logger.info(f"Extracting infrastructure knowledge from {agent_name} agent")
                self._extract_infrastructure_knowledge(
                    response_text,
                    agent_name,
                    state
                )
            else:
                logger.info(f"Skipping infrastructure extraction for {agent_name} (not in extraction list)")
            
        except Exception as e:
            logger.error(f"Failed to process agent response for memory capture: {e}", exc_info=True)
    
    def on_investigation_complete(
        self,
        state: Dict[str, Any],
        final_response: str,
        actor_id: str
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
            
            # Get session_id from state
            session_id = state.get("session_id")
            if not session_id:
                raise ValueError("session_id is required in state for investigation summary")
                
            success = _save_investigation_summary(
                self.memory_client,
                actor_id,
                incident_id,
                summary,
                session_id
            )
            
            if success:
                logger.info(f"Saved investigation summary for incident {incident_id}")
            else:
                logger.warning(f"Failed to save investigation summary for incident {incident_id}")
                
        except Exception as e:
            logger.error(f"Failed to save investigation summary: {e}")
    
    def _extract_user_preferences(
        self,
        response_text: str,
        user_id: str,
        context: str
    ):
        """Extract user preferences from response text."""
        logger.info(f"Extracting user preferences from {context} response for user {user_id}")
        
        # Extract escalation preferences
        escalation_patterns = [
            r"escalate to ([^\s,\.]+@[^\s,\.]+)",
            r"contact ([^\s,\.]+@[^\s,\.]+)",
            r"notify ([^\s,\.]+@[^\s,\.]+)",
            r"reach out to ([^\s,\.]+@[^\s,\.]+)"
        ]
        
        escalation_found = 0
        for pattern in escalation_patterns:
            matches = re.finditer(pattern, response_text, re.IGNORECASE)
            for match in matches:
                contact = match.group(1)
                logger.info(f"Found escalation pattern: '{match.group(0)}' -> contact: {contact}")
                
                preference = UserPreference(
                    user_id=user_id,
                    preference_type="escalation",
                    preference_value={"contact": contact},
                    context=f"Mentioned during {context} agent response"
                )
                
                success = _save_user_preference(
                    self.memory_client,
                    user_id,
                    preference
                )
                
                if success:
                    escalation_found += 1
                    logger.info(f"Captured escalation preference: {contact}")
                else:
                    logger.warning(f"Failed to save escalation preference: {contact}")
        
        if escalation_found == 0:
            logger.info(f"No escalation patterns found in {context} response")
        
        # Extract notification channel preferences
        channel_patterns = [
            r"send to (#[\w-]+)",
            r"notify (#[\w-]+)",
            r"alert (#[\w-]+)",
            r"post to (#[\w-]+)"
        ]
        
        channels_found = 0
        for pattern in channel_patterns:
            matches = re.finditer(pattern, response_text, re.IGNORECASE)
            for match in matches:
                channel = match.group(1)
                logger.info(f"Found notification pattern: '{match.group(0)}' -> channel: {channel}")
                
                preference = UserPreference(
                    user_id=user_id,
                    preference_type="notification",
                    preference_value={"channel": channel},
                    context=f"Mentioned during {context} agent response"
                )
                
                success = _save_user_preference(
                    self.memory_client,
                    user_id,
                    preference
                )
                
                if success:
                    channels_found += 1
                    logger.info(f"Captured notification preference: {channel}")
                else:
                    logger.warning(f"Failed to save notification preference: {channel}")
        
        if channels_found == 0:
            logger.info(f"No notification channel patterns found in {context} response")
        
        logger.info(f"Preference extraction complete: {escalation_found} escalations, {channels_found} channels")
    
    def _extract_infrastructure_knowledge(
        self,
        response_text: str,
        agent_name: str,
        state: Dict[str, Any]
    ):
        """Extract infrastructure knowledge from agent responses."""
        logger.info(f"Extracting infrastructure knowledge from {agent_name} agent response")
        
        # Extract service dependencies
        dependency_patterns = [
            r"(\w+) depends on (\w+)",
            r"(\w+) requires (\w+)",
            r"(\w+) connects to (\w+)"
        ]
        
        dependencies_found = 0
        for pattern in dependency_patterns:
            matches = re.finditer(pattern, response_text, re.IGNORECASE)
            for match in matches:
                service = match.group(1)
                dependency = match.group(2)
                logger.info(f"Found dependency pattern: '{match.group(0)}' -> {service} depends on {dependency}")
                
                knowledge = InfrastructureKnowledge(
                    service_name=service,
                    knowledge_type="dependency",
                    knowledge_data={
                        "depends_on": dependency,
                        "discovered_by": agent_name
                    },
                    confidence=0.7
                )
                
                success = _save_infrastructure_knowledge(
                    self.memory_client,
                    service,
                    knowledge,
                    state.get("session_id")
                )
                
                if success:
                    dependencies_found += 1
                    logger.info(f"Captured dependency: {service} -> {dependency}")
                else:
                    logger.warning(f"Failed to save dependency: {service} -> {dependency}")
        
        if dependencies_found == 0:
            logger.info(f"No dependency patterns found in {agent_name} response")
        
        # Extract performance baselines for metrics agent
        if agent_name == "metrics":
            logger.info("Extracting performance baselines from metrics agent")
            baseline_patterns = [
                r"baseline (\w+) is ([0-9\.]+)",
                r"normal (\w+) is ([0-9\.]+)",
                r"typical (\w+) ranges from ([0-9\.]+) to ([0-9\.]+)"
            ]
            
            baselines_found = 0
            for pattern in baseline_patterns:
                matches = re.finditer(pattern, response_text, re.IGNORECASE)
                for match in matches:
                    metric = match.group(1)
                    value = match.group(2)
                    logger.info(f"Found baseline pattern: '{match.group(0)}' -> {metric} = {value}")
                    
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
                    
                    success = _save_infrastructure_knowledge(
                        self.memory_client,
                        "system",
                        knowledge,
                        state.get("session_id")
                    )
                    
                    if success:
                        baselines_found += 1
                        logger.info(f"Captured baseline: {metric} = {value}")
                    else:
                        logger.warning(f"Failed to save baseline: {metric} = {value}")
            
            if baselines_found == 0:
                logger.info("No baseline patterns found in metrics agent response")
        
        logger.info(f"Infrastructure knowledge extraction complete for {agent_name}: {dependencies_found} dependencies found")
    
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
    
    def _organize_memories_by_agent(
        self,
        memories: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Organize memories by agent based on their namespace."""
        memories_by_agent = {}
        
        for memory in memories:
            # Extract agent from namespace (format: /sre/infrastructure/{agent_id})
            namespaces = memory.get("namespaces", [])
            if namespaces and len(namespaces) > 0:
                namespace = namespaces[0]
                # Extract agent_id from namespace like "/sre/infrastructure/kubernetes-agent"
                parts = namespace.split("/")
                if len(parts) >= 4 and parts[1] == "sre" and parts[2] == "infrastructure":
                    agent_id = parts[3]
                    if agent_id not in memories_by_agent:
                        memories_by_agent[agent_id] = []
                    memories_by_agent[agent_id].append(memory)
                else:
                    # Fallback for unknown namespace format
                    if "unknown" not in memories_by_agent:
                        memories_by_agent["unknown"] = []
                    memories_by_agent["unknown"].append(memory)
            else:
                # No namespace found
                if "unknown" not in memories_by_agent:
                    memories_by_agent["unknown"] = []
                memories_by_agent["unknown"].append(memory)
        
        return memories_by_agent