from sqlalchemy.orm import Session
from typing import List, Optional
from app.db import models, schemas

# User
def get_user_by_telegram_id(db: Session, telegram_id: int) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.telegram_id == telegram_id).first()

def create_user(db: Session, user_in: schemas.UserCreate) -> models.User:
    db_user = models.User(**user_in.dict())
    db.add(db_user)
    db.commit(); db.refresh(db_user)
    return db_user

# FAQ
def get_faqs(db: Session) -> List[models.FAQ]:
    return db.query(models.FAQ).order_by(models.FAQ.id).all()

# Question (ticket)
def create_question(db: Session, q_in: schemas.QuestionCreate, user_id: int) -> models.Question:
    db_q = models.Question(user_id=user_id, **q_in.dict())
    db.add(db_q)
    db.commit(); db.refresh(db_q)
    return db_q

# Session

def get_active_session(db: Session, user_id: int) -> Optional[models.Session]:
    return (
        db.query(models.Session)
          .filter(models.Session.user_id == user_id, models.Session.active)
          .order_by(models.Session.created_at.desc())
          .first()
    )

def create_session(db: Session, user_id: int) -> models.Session:
    sess = models.Session(user_id=user_id)
    db.add(sess)
    db.commit(); db.refresh(sess)
    return sess

def close_session(db: Session, session_id: int) -> None:
    db.query(models.Session).filter(models.Session.id == session_id).update({"active": False})
    db.commit()

# Messages
def create_message(db: Session, m_in: schemas.MessageCreate) -> models.Message:
    db_m = models.Message(**m_in.dict())
    db.add(db_m)
    db.commit(); db.refresh(db_m)
    return db_m

def get_session_messages(db: Session, session_id: int) -> List[models.Message]:
    return (
        db.query(models.Message)
          .filter(models.Message.session_id == session_id)
          .order_by(models.Message.timestamp)
          .all()
    )