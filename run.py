import threading, asyncio, uvicorn
from app.telegram_bot.bot import main_bot

if __name__ == '__main__':
    threading.Thread(
        target=lambda: asyncio.run(main_bot()),
        daemon=True
    ).start()

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000)
