from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# User
class UserBase(BaseModel):
    telegram_id: int
    first_name: Optional[str]
    last_name: Optional[str]
    username: Optional[str]

class UserCreate(UserBase):
    pass

class UserRead(UserBase):
    id: int
    created_at: datetime
    class Config:
        orm_mode = True

# FAQ
class FAQBase(BaseModel):
    question: str
    answer: str

class FAQCreate(FAQBase):
    pass

class FAQRead(FAQBase):
    id: int
    class Config:
        orm_mode = True

# Question ticket
class QuestionBase(BaseModel):
    topic: str
    description: str

class QuestionCreate(QuestionBase):
    pass

class QuestionRead(QuestionBase):
    id: int
    user_id: int
    timestamp: datetime
    class Config:
        orm_mode = True

# Session & Messages
class MessageBase(BaseModel):
    session_id: Optional[int]
    user_id: int
    role: str
    text: str

class MessageCreate(MessageBase):
    pass

class MessageRead(MessageBase):
    id: int
    timestamp: datetime
    class Config:
        orm_mode = True

class SessionBase(BaseModel):
    user_id: int

class SessionCreate(SessionBase):
    pass

class SessionRead(SessionBase):
    id: int
    active: bool
    created_at: datetime
    messages: List[MessageRead] = []
    class Config:
        orm_mode = True