from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from shared.database.session import Base


class Chat(Base):
    __tablename__ = "chats"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    chat_type_id = Column(Integer, ForeignKey("chat_types.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="chats")
    chat_type = relationship("ChatType", back_populates="chats")
    messages = relationship("Message", back_populates="chat", cascade="all, delete-orphan", order_by="Message.created_at")
    
    def __repr__(self):
        return f"<Chat(id={self.id}, title='{self.title}', user_id={self.user_id}, chat_type_id={self.chat_type_id})>"
