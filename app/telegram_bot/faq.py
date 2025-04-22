from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler
from app.telegram_bot.keyboards import faq_keyboard, main_keyboard
from app.db.session import SessionLocal
from app.db.crud import get_faqs, create_message

async def faq_command(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Используя этот чат, вы даёте согласие на обработку...")
    await update.message.reply_text(
        "Выберите вопрос:", reply_markup=faq_keyboard())

async def faq_choice(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    db = SessionLocal()
    data = update.callback_query.data
    faq_id = int(data.split('_')[1])
    faqs = get_faqs(db)
    answer = next((f.answer for f in faqs if f.id == faq_id), "" )
    # save to history (no session yet)
    create_message(db, schemas.MessageCreate(
        session_id=None,
        user_id=update.effective_user.id,
        role="user",
        text=f"FAQ запрос {faq_id}"
    ))
    create_message(db, schemas.MessageCreate(
        session_id=None,
        user_id=update.effective_user.id,
        role="bot",
        text=answer
    ))
    db.close()
    await update.callback_query.answer()
    await update.callback_query.message.reply_text(answer)
    await update.callback_query.message.reply_text(
        "Чем ещё помочь?",
        reply_markup=main_keyboard(ctx.user_data.get('ai_count',0))
    )