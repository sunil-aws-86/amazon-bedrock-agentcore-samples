"""
DynamoDB Conversation Manager
Handles conversation persistence and retrieval
"""
import json
import boto3
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

class ConversationManager:
    def __init__(self, table_name: str, region: str = "us-east-1"):
        self.table_name = table_name
        self.dynamodb = boto3.resource('dynamodb', region_name=region)
        self.table = self.dynamodb.Table(table_name)
        
    async def get_conversation_history(self, conversation_id: str, max_messages: int = 50) -> List[Dict]:
        """Retrieve conversation history from DynamoDB"""
        try:
            response = self.table.get_item(
                Key={'conversation_id': conversation_id}
            )
            
            if 'Item' not in response:
                logger.info(f"No conversation found for ID: {conversation_id}")
                return []
            
            item = response['Item']
            messages = json.loads(item.get('messages', '[]'))
            
            # Return last N messages to keep context manageable
            if len(messages) > max_messages:
                messages = messages[-max_messages:]
                logger.info(f"Trimmed conversation to last {max_messages} messages")
            
            logger.info(f"Retrieved {len(messages)} messages for conversation {conversation_id}")
            return messages
            
        except ClientError as e:
            logger.error(f"Error retrieving conversation {conversation_id}: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error retrieving conversation {conversation_id}: {str(e)}")
            return []
    
    async def save_conversation_history(self, conversation_id: str, messages: List[Dict]) -> bool:
        """Save conversation history to DynamoDB"""
        try:
            # Keep only last 100 messages to prevent item size limits
            if len(messages) > 100:
                messages = messages[-100:]
            
            # Prepare item for DynamoDB
            item = {
                'conversation_id': conversation_id,
                'messages': json.dumps(messages),
                'updated_at': datetime.utcnow().isoformat(),
                'message_count': len(messages),
                # TTL: expire conversations after 30 days
                'ttl': int((datetime.utcnow() + timedelta(days=30)).timestamp())
            }
            
            # Save to DynamoDB
            self.table.put_item(Item=item)
            
            logger.info(f"Saved {len(messages)} messages for conversation {conversation_id}")
            return True
            
        except ClientError as e:
            logger.error(f"Error saving conversation {conversation_id}: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error saving conversation {conversation_id}: {str(e)}")
            return False
    
    async def add_message_to_conversation(self, conversation_id: str, role: str, content: str) -> bool:
        """Add a single message to conversation history"""
        try:
            # Get current history
            current_messages = await self.get_conversation_history(conversation_id)
            
            # Add new message
            new_message = {
                "role": role,
                "content": content,
                "timestamp": datetime.utcnow().isoformat()
            }
            current_messages.append(new_message)
            
            # Save updated history
            return await self.save_conversation_history(conversation_id, current_messages)
            
        except Exception as e:
            logger.error(f"Error adding message to conversation {conversation_id}: {str(e)}")
            return False
    
    async def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation from DynamoDB"""
        try:
            self.table.delete_item(
                Key={'conversation_id': conversation_id}
            )
            logger.info(f"Deleted conversation {conversation_id}")
            return True
            
        except ClientError as e:
            logger.error(f"Error deleting conversation {conversation_id}: {str(e)}")
            return False
    
    async def get_conversation_metadata(self, conversation_id: str) -> Optional[Dict]:
        """Get conversation metadata without full message history"""
        try:
            response = self.table.get_item(
                Key={'conversation_id': conversation_id},
                ProjectionExpression='conversation_id, updated_at, message_count'
            )
            
            if 'Item' in response:
                return response['Item']
            return None
            
        except ClientError as e:
            logger.error(f"Error getting metadata for conversation {conversation_id}: {str(e)}")
            return None
