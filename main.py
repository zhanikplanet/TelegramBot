from fastapi import FastAPI
from routers.api import router as api_router
from database import engine, Base

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(api_router)
