from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    name: str
    contact: str

class QuestionCreate(BaseModel):
    user_id: int
    topic: str
    description: str

class DialogCreate(BaseModel):
    user_id: int
    messages: str
    finished: Optional[bool] = False
