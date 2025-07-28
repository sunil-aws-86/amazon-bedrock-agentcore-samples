import pytest
import json
from unittest.mock import Mock, AsyncMock, patch

from sre_agent.memory.tools import SaveMemoryTool, RetrieveMemoryTool
from sre_agent.memory.client import SREMemoryClient


class TestSaveMemoryTool:
    """Tests for SaveMemoryTool."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock memory client."""
        mock = Mock(spec=SREMemoryClient)
        return mock
    
    @pytest.fixture
    def save_tool(self, mock_client):
        """Create SaveMemoryTool with mock client."""
        return SaveMemoryTool(mock_client)
    
    @pytest.mark.asyncio
    async def test_save_preference_success(self, save_tool, mock_client):
        """Test saving user preference successfully."""
        with patch('sre_agent.memory.tools._save_user_preference', new_callable=AsyncMock) as mock_save:
            mock_save.return_value = True
            
            result = await save_tool._save_memory(
                memory_type="preference",
                content={
                    "user_id": "user123",
                    "preference_type": "escalation",
                    "preference_value": {"contact": "ops@company.com"}
                }
            )
            
            assert "Saved user preference: escalation for user user123" in result
            mock_save.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_save_preference_failure(self, save_tool, mock_client):
        """Test saving user preference failure."""
        with patch('sre_agent.memory.tools._save_user_preference', new_callable=AsyncMock) as mock_save:
            mock_save.return_value = False
            
            result = await save_tool._save_memory(
                memory_type="preference",
                content={
                    "user_id": "user123",
                    "preference_type": "escalation",
                    "preference_value": {"contact": "ops@company.com"}
                }
            )
            
            assert "Failed to save user preference: escalation" in result
    
    @pytest.mark.asyncio
    async def test_save_infrastructure_knowledge(self, save_tool, mock_client):
        """Test saving infrastructure knowledge."""
        with patch('sre_agent.memory.tools._save_infrastructure_knowledge', new_callable=AsyncMock) as mock_save:
            mock_save.return_value = True
            
            result = await save_tool._save_memory(
                memory_type="infrastructure",
                content={
                    "service_name": "web-service",
                    "knowledge_type": "dependency",
                    "knowledge_data": {"depends_on": "database"}
                }
            )
            
            assert "Saved infrastructure knowledge: dependency for web-service" in result
            mock_save.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_save_investigation_summary(self, save_tool, mock_client):
        """Test saving investigation summary."""
        with patch('sre_agent.memory.tools._save_investigation_summary', new_callable=AsyncMock) as mock_save:
            mock_save.return_value = True
            
            result = await save_tool._save_memory(
                memory_type="investigation",
                content={
                    "incident_id": "incident_123",
                    "query": "Why is service down?",
                    "resolution_status": "completed",
                    "timeline": [],
                    "actions_taken": [],
                    "key_findings": []
                }
            )
            
            assert "Saved investigation summary for incident incident_123" in result
            mock_save.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_save_unknown_memory_type(self, save_tool, mock_client):
        """Test saving with unknown memory type."""
        result = await save_tool._save_memory(
            memory_type="unknown",
            content={}
        )
        
        assert "Unknown memory type: unknown" in result
    
    @pytest.mark.asyncio
    async def test_save_memory_validation_error(self, save_tool, mock_client):
        """Test saving with invalid content that fails validation."""
        result = await save_tool._save_memory(
            memory_type="preference",
            content={"invalid": "data"}  # Missing required fields
        )
        
        assert "Error saving preference memory" in result


class TestRetrieveMemoryTool:
    """Tests for RetrieveMemoryTool."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock memory client."""
        mock = Mock(spec=SREMemoryClient)
        return mock
    
    @pytest.fixture
    def retrieve_tool(self, mock_client):
        """Create RetrieveMemoryTool with mock client."""
        return RetrieveMemoryTool(mock_client)
    
    @pytest.mark.asyncio
    async def test_retrieve_preferences_success(self, retrieve_tool, mock_client):
        """Test retrieving user preferences successfully."""
        mock_preferences = [
            Mock(model_dump=Mock(return_value={
                "user_id": "user123",
                "preference_type": "escalation",
                "preference_value": {"contact": "ops@company.com"}
            }))
        ]
        
        with patch('sre_agent.memory.tools._retrieve_user_preferences', new_callable=AsyncMock) as mock_retrieve:
            mock_retrieve.return_value = mock_preferences
            
            result = await retrieve_tool._retrieve_memory(
                memory_type="preference",
                query="escalation contacts",
                actor_id="user123"
            )
            
            result_data = json.loads(result)
            assert len(result_data) == 1
            assert result_data[0]["user_id"] == "user123"
            mock_retrieve.assert_called_once_with(mock_client, "user123", "escalation contacts")
    
    @pytest.mark.asyncio
    async def test_retrieve_preferences_no_actor_id(self, retrieve_tool, mock_client):
        """Test retrieving preferences without actor_id."""
        result = await retrieve_tool._retrieve_memory(
            memory_type="preference",
            query="escalation contacts"
        )
        
        result_data = json.loads(result)
        assert "Error" in result_data
        assert "actor_id (user_id) is required" in result_data["Error"]
    
    @pytest.mark.asyncio
    async def test_retrieve_infrastructure_knowledge(self, retrieve_tool, mock_client):
        """Test retrieving infrastructure knowledge."""
        mock_knowledge = [
            Mock(model_dump=Mock(return_value={
                "service_name": "web-service",
                "knowledge_type": "dependency",
                "knowledge_data": {"depends_on": "database"}
            }))
        ]
        
        with patch('sre_agent.memory.tools._retrieve_infrastructure_knowledge', new_callable=AsyncMock) as mock_retrieve:
            mock_retrieve.return_value = mock_knowledge
            
            result = await retrieve_tool._retrieve_memory(
                memory_type="infrastructure",
                query="service dependencies",
                actor_id="web-service"
            )
            
            result_data = json.loads(result)
            assert len(result_data) == 1
            assert result_data[0]["service_name"] == "web-service"
            mock_retrieve.assert_called_once_with(mock_client, "service dependencies", "web-service")
    
    @pytest.mark.asyncio
    async def test_retrieve_investigation_summaries(self, retrieve_tool, mock_client):
        """Test retrieving investigation summaries."""
        mock_summaries = [
            Mock(model_dump=Mock(return_value={
                "incident_id": "incident_123",
                "query": "Service down",
                "resolution_status": "completed"
            }))
        ]
        
        with patch('sre_agent.memory.tools._retrieve_investigation_summaries', new_callable=AsyncMock) as mock_retrieve:
            mock_retrieve.return_value = mock_summaries
            
            result = await retrieve_tool._retrieve_memory(
                memory_type="investigation",
                query="service outage",
                max_results=3
            )
            
            result_data = json.loads(result)
            assert len(result_data) == 1
            assert result_data[0]["incident_id"] == "incident_123"
            mock_retrieve.assert_called_once_with(mock_client, "service outage", None)
    
    @pytest.mark.asyncio
    async def test_retrieve_unknown_memory_type(self, retrieve_tool, mock_client):
        """Test retrieving with unknown memory type."""
        result = await retrieve_tool._retrieve_memory(
            memory_type="unknown",
            query="test query"
        )
        
        result_data = json.loads(result)
        assert "error" in result_data
        assert "Unknown memory type: unknown" in result_data["error"]
        assert "supported_types" in result_data
    
    @pytest.mark.asyncio
    async def test_retrieve_memory_exception(self, retrieve_tool, mock_client):
        """Test handling exceptions during retrieval."""
        with patch('sre_agent.memory.tools._retrieve_user_preferences', new_callable=AsyncMock) as mock_retrieve:
            mock_retrieve.side_effect = Exception("Database error")
            
            result = await retrieve_tool._retrieve_memory(
                memory_type="preference",
                query="test query",
                actor_id="user123"
            )
            
            result_data = json.loads(result)
            assert "error" in result_data
            assert "Error retrieving preference memory" in result_data["error"]