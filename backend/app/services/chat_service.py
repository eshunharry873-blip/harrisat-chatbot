from sqlalchemy.orm import Session
from app.models import Conversation, Message
from app.schemas import MessageCreate
from app.logger import logger
from typing import List, Optional
from datetime import datetime

class ChatService:
    @staticmethod
    def create_conversation(db: Session, user_id: str, title: Optional[str] = None) -> Conversation:
        conversation = Conversation(user_id=user_id, title=title)
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        logger.info(f"Conversation created: {conversation.id}")
        return conversation
    
    @staticmethod
    def get_conversation(db: Session, conversation_id: str, user_id: str) -> Optional[Conversation]:
        return db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        ).first()
    
    @staticmethod
    def get_user_conversations(db: Session, user_id: str, limit: int = 50, offset: int = 0) -> List[Conversation]:
        return db.query(Conversation).filter(
            Conversation.user_id == user_id
        ).order_by(Conversation.updated_at.desc()).offset(offset).limit(limit).all()
    
    @staticmethod
    def add_message(db: Session, conversation_id: str, role: str, content: str) -> Message:
        message = Message(conversation_id=conversation_id, role=role, content=content)
        db.add(message)
        db.commit()
        db.refresh(message)
        return message
    
    @staticmethod
    def get_conversation_messages(db: Session, conversation_id: str, limit: int = 100) -> List[Message]:
        return db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at.asc()).limit(limit).all()
    
    @staticmethod
    def update_conversation_title(db: Session, conversation_id: str, title: str):
        conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if conversation:
            conversation.title = title
            conversation.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(conversation)
        return conversation
    
    @staticmethod
    def delete_conversation(db: Session, conversation_id: str, user_id: str):
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        ).first()
        if conversation:
            db.delete(conversation)
            db.commit()
            logger.info(f"Conversation deleted: {conversation_id}")
            return True
        return False
