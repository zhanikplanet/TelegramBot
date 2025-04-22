from fastapi import FastAPI
import asyncio, threading

from app.db.session import Base, engine
from app.api import question, faq, operator
from app.telegram_bot.bot import main_bot   # импортируем коррутину бота

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Telegram‑FAQ‑Bot API")
app.include_router(question.router)
app.include_router(faq.router)
app.include_router(operator.router)

# 👉 Запускаем Telegram‑бот в фоне при старте FastAPI
#@app.on_event("startup")
#async def start_telegram_bot() -> None:
#    loop = asyncio.get_event_loop()
#    threading.Thread(
#        target=lambda: loop.create_task(main_bot()),
#        daemon=True
#    ).start()
