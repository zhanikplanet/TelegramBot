from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db import crud, schemas, models
from typing import List


router = APIRouter(prefix="/questions", tags=["questions"])

def get_db():
    db = SessionLocal();
    try: yield db
    finally: db.close()

@router.post("/", response_model=schemas.QuestionRead)
def create_question(q: schemas.QuestionCreate, db: Session = Depends(get_db)):
    return crud.create_question(db, q, user_id=q.user_id)

@router.get("/", response_model=List[schemas.QuestionRead])
def list_questions(db: Session = Depends(get_db)):
    return db.query(models.Question).all()