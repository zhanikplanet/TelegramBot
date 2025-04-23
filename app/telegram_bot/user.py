from telegram import Update
from telegram.ext import ContextTypes
from app.db.session import SessionLocal
from app.db.crud import get_user, create_user
from app.telegram_bot.keyboards import main_keyboard

async def handle_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Reply to /start with a greeting and show the main keyboard.
    """
    user = update.effective_user

    welcome = (
        f"👋 Привет, {user.first_name or 'гость'}!\n\n"
        "Я FAQ‑бот.\n"
        "• Нажми «FAQ», чтобы увидеть популярные вопросы.\n"
        "• Нажми «Новый вопрос», чтобы задать свой.\n"
        "Хорошего дня!"
    )

    # greet and show buttons
    await update.message.reply_text(
        welcome,
        reply_markup=main_keyboard(ai_count=0)
    )