from fastapi import FastAPI
from .config import settings
from .db.session import Base, engine
from .api.question import router as question_router
from .api.faq import router as faq_router
from .api.operator import router as operator_router

# Автоматически создаём все таблицы в БД при старте приложения
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Telegram‑FAQ‑Bot API")

# Включаем роутеры
app.include_router(question_router)
app.include_router(faq_router)
app.include_router(operator_router)
