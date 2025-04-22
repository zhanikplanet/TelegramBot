from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    contact = Column(String, unique=True, index=True)
    dialogs = relationship("Dialog", back_populates="user")
    questions = relationship("Ticket", back_populates="user")

class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    topic = Column(String)
    description = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="questions")

class Dialog(Base):
    __tablename__ = "dialogs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    messages = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    finished = Column(Boolean, default=False)

    user = relationship("User", back_populates="dialogs")
