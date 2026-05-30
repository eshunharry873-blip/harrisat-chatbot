from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None

class User(UserBase):
    id: str
    is_active: bool
    is_admin: bool
    created_at: datetime
    last_login: Optional[datetime]
    
    class Config:
        from_attributes = True

# Token Schemas
class Token(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: Optional[str] = None

# Message Schemas
class MessageCreate(BaseModel):
    content: str

class Message(BaseModel):
    id: str
    role: str
    content: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Conversation Schemas
class ConversationCreate(BaseModel):
    title: Optional[str] = None

class ConversationUpdate(BaseModel):
    title: Optional[str] = None

class Conversation(BaseModel):
    id: str
    title: Optional[str]
    created_at: datetime
    updated_at: datetime
    messages: List[Message] = []
    
    class Config:
        from_attributes = True

# File Upload Schemas
class FileUploadResponse(BaseModel):
    id: str
    filename: str
    file_size: int
    file_type: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Settings Schemas
class UserSettings(BaseModel):
    dark_mode: bool = False
    notifications_enabled: bool = True
    language: str = "en"
    theme: str = "dark"

# Admin Schemas
class AdminStats(BaseModel):
    total_users: int
    total_conversations: int
    total_messages: int
    active_users_today: int

# Chat Schemas
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatResponse(BaseModel):
    id: str
    message: str
    role: str = "assistant"
    created_at: datetime
