from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.db import models, schemas

# --- User -----------------------------------

def get_user(db: Session, user_id: int) -> Optional[models.User]:
    return db.get(models.User, user_id)

def create_user(db: Session, user_id: int, name: Optional[str] = None,
                contact: Optional[str] = None) -> models.User:
    user = models.User(id=user_id, name=name, contact=contact)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_or_create_user(db: Session, user_id: int,
                       name: Optional[str] = None) -> models.User:
    user = db.get(models.User, user_id)
    if user:
        return user
    return create_user(db, user_id, name)


# --- FAQ ------------------------------------

def get_faqs(db: Session) -> List[models.FAQ]:
    return db.query(models.FAQ).order_by(models.FAQ.id).all()


# --- Question (ticket) ----------------------

def create_question(db: Session, q_in: schemas.QuestionCreate, user_id: int) -> models.Question:
    db_q = models.Question(user_id=user_id, **q_in.dict())
    db.add(db_q)
    db.commit()
    db.refresh(db_q)
    return db_q


# --- Session --------------------------------

def get_session(db: Session, session_id: int) -> Optional[models.Session]:
    return db.query(models.Session).filter(models.Session.id == session_id).first()

def get_active_session(db: Session, user_id: int) -> Optional[models.Session]:
    return (
        db.query(models.Session)
          .filter(models.Session.user_id == user_id, models.Session.active.is_(True))
          .order_by(models.Session.created_at.desc())
          .first()
    )

def get_active_session_by_operator(db: Session, operator_id: int) -> Optional[models.Session]:
    return (
        db.query(models.Session)
          .filter(
              models.Session.operator_id == operator_id,
              models.Session.active.is_(True)
          )
          .order_by(models.Session.created_at.desc())
          .first()
    )

def create_session(
    db: Session,
    user_id: int,
    operator_id: Optional[int] = None
) -> models.Session:
    sess = models.Session(user_id=user_id, operator_id=operator_id)
    db.add(sess)
    db.commit()
    db.refresh(sess)
    return sess

def close_session(db: Session, session_id: int) -> None:
    db.query(models.Session) \
      .filter(models.Session.id == session_id) \
      .update({ "active": False })
    db.commit()

def find_stale_sessions(db: Session, older_than: timedelta) -> List[models.Session]:
    cutoff = datetime.utcnow() - older_than
    return (
        db.query(models.Session)
          .filter(
              models.Session.active.is_(True),
              models.Session.created_at < cutoff
          )
          .all()
    )


# --- Messages -------------------------------

def create_message(db: Session, m_in: schemas.MessageCreate) -> models.Message:
    db_m = models.Message(**m_in.dict())
    db.add(db_m)
    db.commit()
    db.refresh(db_m)
    return db_m

def get_session_messages(db: Session, session_id: int) -> List[models.Message]:
    return (
        db.query(models.Message)
          .filter(models.Message.session_id == session_id)
          .order_by(models.Message.timestamp)
          .all()
    )


# --- Operator shifts ------------------------

def is_operator_on_shift(db: Session, operator_id: int) -> bool:
    return db.query(models.OperatorShift) \
        .filter(
            models.OperatorShift.operator_id == operator_id,
            models.OperatorShift.end_time.is_(None)
        ).first() is not None

def create_shift(db: Session, operator_id: int) -> models.OperatorShift:
    shift = models.OperatorShift(operator_id=operator_id)
    db.add(shift)
    db.commit()
    db.refresh(shift)
    return shift

def finish_shift(db: Session, operator_id: int) -> None:
    db.query(models.OperatorShift) \
      .filter(
          models.OperatorShift.operator_id == operator_id,
          models.OperatorShift.end_time.is_(None)
      ).update({ "end_time": datetime.utcnow() })
    db.commit()

def find_free_operator(db: Session, operator_ids: list[int]) -> Optional[models.User]:
    subq = (
        db.query(models.Session.operator_id)
          .filter(
              models.Session.active.is_(True),
              models.Session.operator_id.isnot(None)        # <-- критично
          )
    )
    return (
        db.query(models.User)
          .join(models.OperatorShift,
                (models.OperatorShift.operator_id == models.User.id) &
                (models.OperatorShift.end_time.is_(None)))
          .filter(models.User.id.in_(operator_ids))
          .filter(~models.User.id.in_(subq))
          .first()
    )


def assign_operator_to_session(db: Session, session_id: int, operator_id: int) -> None:
    """Назначает оператора сессии."""
    db.query(models.Session) \
        .filter(models.Session.id == session_id) \
        .update({"operator_id": operator_id})
    db.commit()
