from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, ForeignKey
)
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.session import Base

class User(Base):
    __tablename__ = "users"
    id           = Column(Integer, primary_key=True, index=True)
    telegram_id  = Column(Integer, unique=True, index=True, nullable=False)
    first_name   = Column(String)
    last_name    = Column(String)
    username     = Column(String)
    created_at   = Column(DateTime, default=datetime.utcnow)

    # relationships
    questions    = relationship("Question", back_populates="user")
    sessions     = relationship("Session", back_populates="user")

class FAQ(Base):
    __tablename__ = "faq"
    id       = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    answer   = Column(Text, nullable=False)

class Question(Base):  # user tickets
    __tablename__ = "questions"
    id          = Column(Integer, primary_key=True, index=True)
    user_id     = Column(Integer, ForeignKey("users.id"), nullable=False)
    topic       = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    timestamp   = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="questions")

class Session(Base):  # escalation session
    __tablename__ = "sessions"
    id               = Column(Integer, primary_key=True, index=True)
    user_id          = Column(Integer, ForeignKey("users.id"), nullable=False)
    active           = Column(Boolean, default=True)
    created_at       = Column(DateTime, default=datetime.utcnow)

    user     = relationship("User", back_populates="sessions")
    messages = relationship("Message", back_populates="session")

class Message(Base):
    __tablename__ = "messages"
    id          = Column(Integer, primary_key=True, index=True)
    session_id  = Column(Integer, ForeignKey("sessions.id"), nullable=True)
    user_id     = Column(Integer, ForeignKey("users.id"), nullable=False)
    role        = Column(String, nullable=False)  # "user" | "bot" | "operator"
    text        = Column(Text, nullable=False)
    timestamp   = Column(DateTime, default=datetime.utcnow)

    session = relationship("Session", back_populates="messages")