# app/db/schemas.py

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# --- User ----------------------

class UserBase(BaseModel):
    id: int                 # telegram id
    name: Optional[str]
    contact: Optional[str]

class UserCreate(UserBase):
    pass

class UserRead(UserBase):
    created_at: datetime
    class Config:
        from_attributes = True


# --- FAQ -----------------------

class FAQBase(BaseModel):
    question: str
    answer: str

class FAQCreate(FAQBase):
    pass

class FAQRead(FAQBase):
    id: int
    class Config:
        from_attributes = True


# --- Question ------------------

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
        from_attributes = True


# --- Message -------------------

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
        from_attributes = True


# --- Session -------------------

class SessionBase(BaseModel):
    user_id: int
    operator_id: Optional[int] = None

class SessionCreate(SessionBase):
    pass

class SessionRead(SessionBase):
    id: int
    active: bool
    created_at: datetime
    messages: List[MessageRead] = []
    class Config:
        from_attributes = True
