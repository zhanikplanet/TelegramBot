from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db import crud, schemas
from typing import List

router = APIRouter(prefix="/operators", tags=["operators"])

def get_db():
    db = SessionLocal();
    try: yield db
    finally: db.close()

@router.post("/sessions/{session_id}/close")
def close_session(session_id: int, db: Session = Depends(get_db)):
    sess = crud.get_session(db, session_id)
    if not sess: raise HTTPException(404, "Session not found")
    crud.close_session(db, session_id)
    return {"status":"closed"}

@router.get("/sessions/{session_id}", response_model=schemas.SessionRead)
def read_session(session_id: int, db: Session = Depends(get_db)):
    sess = crud.get_session(db, session_id)
    if not sess: raise HTTPException(404, "Session not found")
    return sess