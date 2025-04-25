# app/db/models.py

from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, ForeignKey
)
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.session import Base

class User(Base):
    __tablename__ = "users"

    id       = Column(Integer, primary_key=True, index=True)
    name     = Column(String)
    contact  = Column(String)

    # вопросы (тикеты)
    questions = relationship(
        "Question",
        back_populates="user",
        foreign_keys="[Question.user_id]",
        cascade="all, delete-orphan"
    )

    # сессии как клиент
    sessions = relationship(
        "Session",
        back_populates="user",
        foreign_keys="[Session.user_id]",
        cascade="all, delete-orphan"
    )

    # сессии как оператор
    operator_sessions = relationship(
        "Session",
        back_populates="operator",
        foreign_keys="[Session.operator_id]",
        cascade="all, delete-orphan"
    )

    # история смен операторов
    shifts = relationship(
        "OperatorShift",
        back_populates="operator",
        cascade="all, delete-orphan"
    )

class FAQ(Base):
    __tablename__ = "faq"

    id       = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    answer   = Column(Text, nullable=False)

class Question(Base):
    __tablename__ = "questions"

    id          = Column(Integer, primary_key=True, index=True)
    user_id     = Column(Integer, ForeignKey("users.id"), nullable=False)
    topic       = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    timestamp   = Column(DateTime, default=datetime.utcnow)

    user = relationship(
        "User",
        back_populates="questions",
        foreign_keys=[user_id]
    )

class Session(Base):
    __tablename__ = "sessions"

    id          = Column(Integer, primary_key=True, index=True)
    user_id     = Column(Integer, ForeignKey("users.id"), nullable=False)
    operator_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    active      = Column(Boolean, default=True)
    created_at  = Column(DateTime, default=datetime.utcnow)

    user = relationship(
        "User",
        back_populates="sessions",
        foreign_keys=[user_id]
    )
    operator = relationship(
        "User",
        back_populates="operator_sessions",
        foreign_keys=[operator_id]
    )
    messages = relationship(
        "Message",
        back_populates="session",
        cascade="all, delete-orphan"
    )

class Message(Base):
    __tablename__ = "messages"

    id         = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=True)
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=False)
    role       = Column(String, nullable=False)  # "user"|"bot"|"operator"
    text       = Column(Text, nullable=False)
    timestamp  = Column(DateTime, default=datetime.utcnow)

    session = relationship(
        "Session",
        back_populates="messages"
    )

class OperatorShift(Base):
    __tablename__ = "operator_shifts"

    id          = Column(Integer, primary_key=True, index=True)
    operator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    start_time  = Column(DateTime, default=datetime.utcnow)
    end_time    = Column(DateTime, nullable=True)

    operator = relationship(
        "User",
        back_populates="shifts",
        foreign_keys=[operator_id]
    )
