# Упрощённый импорт основных объектов работы с БД

from .session import SessionLocal, engine, Base
from .models import User, FAQ, Question, Session, Message
from .schemas import (
    UserBase, UserCreate, UserRead,
    FAQBase, FAQCreate, FAQRead,
    QuestionBase, QuestionCreate, QuestionRead,
    MessageBase, MessageCreate, MessageRead,
    SessionBase, SessionCreate, SessionRead,
)
from .crud import (
    get_user, create_user,
    get_faqs,
    create_question,
    get_active_session, create_session, close_session,
    create_message, get_session_messages,
)

__all__ = [
    "SessionLocal", "engine", "Base",
    "User", "FAQ", "Question", "Session", "Message",
    "UserBase", "UserCreate", "UserRead",
    "FAQBase", "FAQCreate", "FAQRead",
    "QuestionBase", "QuestionCreate", "QuestionRead",
    "MessageBase", "MessageCreate", "MessageRead",
    "SessionBase", "SessionCreate", "SessionRead",
    "get_user", "create_user",
    "get_faqs",
    "create_question",
    "get_active_session", "create_session", "close_session",
    "create_message", "get_session_messages",
]
