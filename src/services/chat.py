"""
Service for managing chat sessions and messages.
"""

from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Dict, Optional
from shared.database.models.message import Message, MessageRole
from shared.database.models.chat import Chat
from config.logger import logger


class ChatService:
    """Service for chat operations."""

    def __init__(self, db: Session):
        self.db = db

    def save_message(self, chat_id: UUID, role: MessageRole, content: str) -> Message:
        """
        Save a message to the database.
        
        Args:
            chat_id: ID of the chat
            role: Message role (user or assistant)
            content: Message content
            
        Returns:
            Created Message object
        """
        try:
            message = Message(
                chat_id=chat_id,
                role=role,
                content=content
            )
            self.db.add(message)
            self.db.commit()
            self.db.refresh(message)
            return message
        except Exception as e:
            logger.error(f"Failed to save message: {e}")
            self.db.rollback()
            raise

    def get_chat_history(self, chat_id: UUID, limit: int = 10) -> List[Dict[str, str]]:
        """
        Get recent chat history formatted for LLM context.
        
        Args:
            chat_id: ID of the chat
            limit: Number of messages to retrieve
            
        Returns:
            List of message dicts [{"role": "...", "content": "..."}]
        """
        previous_messages = self.db.query(Message).filter(
            Message.chat_id == chat_id
        ).order_by(Message.created_at.desc()).limit(limit).all()
        
        return [
            {"role": msg.role.value, "content": msg.content}
            for msg in reversed(previous_messages)
        ]
