from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db import crud, schemas
from typing import List

router = APIRouter(prefix="/faq", tags=["faq"])

def get_db():
    db = SessionLocal();
    try: yield db
    finally: db.close()

@router.get("/", response_model=List[schemas.FAQRead])
def list_faq(db: Session = Depends(get_db)):
    return crud.get_faqs(db)

@router.post("/", response_model=schemas.FAQRead)
def create_faq(f: schemas.FAQCreate, db: Session = Depends(get_db)):
    db_f = models.FAQ(**f.dict())
    db.add(db_f); db.commit(); db.refresh(db_f)
    return db_f