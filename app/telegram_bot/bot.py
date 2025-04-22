import asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)
from telegram.request import HTTPXRequest

from app.config import settings
from app.telegram_bot.keyboards import main_keyboard
from app.telegram_bot.faq import faq_command, faq_choice
from app.telegram_bot.operator import (
    escalate_to_operator, handle_operator_reply
)
from app.services.openai_service import ask_openai
from app.db.session import SessionLocal
from app.db import schemas, crud

# ─────────────────────────────────────────────────────────────
async def start_command(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    ctx.user_data.clear()
    ctx.user_data["ai_count"] = 0
    user = update.effective_user
    welcome_text = (
        f"👋 Привет, {user.first_name or 'друг'}!\n\n"
        "Я FAQ‑бот.\n"
        "• Нажми «FAQ», чтобы увидеть популярные вопросы.\n"
        "• Нажми «Новый вопрос», чтобы задать свой.\n"
        "После двух ответов ИИ можно будет вызвать оператора."
    )
    await update.message.reply_text(welcome_text, reply_markup=main_keyboard(ai_count=0))

# ─────────────────────────────────────────────────────────────
async def user_message(update, ctx):
    text = update.message.text
    uid = update.effective_user.id
    db = SessionLocal()

    if text.lower() == 'оператор' and ctx.user_data.get('ai_count', 0) >= 2:
        db.close()
        return await escalate_to_operator(update, ctx)

    if ctx.user_data.get('session_active'):
        sess_id = ctx.user_data['session_id']
        crud.create_message(db, schemas.MessageCreate(
            session_id=sess_id, user_id=uid, role='user', text=text
        ))
        for op in settings.operator_chat_ids:
            await ctx.bot.send_message(op, f"User#{uid}: {text}")
        db.close()
        return await update.message.reply_text("✅ Отправлено оператору.")

    if text == 'FAQ':
        db.close()
        return await faq_command(update, ctx)

    if text == 'Новый вопрос':
        ctx.user_data['mode'] = 'ai'
        db.close()
        return await update.message.reply_text("Задайте ваш вопрос:")

    if ctx.user_data.get('mode') == 'ai':
        crud.create_message(db, schemas.MessageCreate(
            session_id=None, user_id=uid, role='user', text=text
        ))
        answer = await ask_openai(text)
        crud.create_message(db, schemas.MessageCreate(
            session_id=None, user_id=uid, role='bot', text=answer
        ))
        ctx.user_data['ai_count'] = ctx.user_data.get('ai_count', 0) + 1
        await update.message.reply_text(answer)

        if ctx.user_data['ai_count'] == 2:
            await update.message.reply_text(
                "После двух ответов AI можно вызвать оператора.",
                reply_markup=main_keyboard(2)
            )
        db.close()
        return

    await update.message.reply_text(
        "Выберите команду меню.",
        reply_markup=main_keyboard(ctx.user_data.get('ai_count', 0))
    )

# ─────────────────────────────────────────────────────────────
async def main_bot():
    request = HTTPXRequest(connect_timeout=10, read_timeout=10)
    app = ApplicationBuilder().token(settings.bot_token).request(request).build()

    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CallbackQueryHandler(faq_choice, pattern='^faq_'))
    app.add_handler(MessageHandler(filters.TEXT & filters.User(settings.operator_chat_ids), handle_operator_reply))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, user_message))

    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    print("✅ Бот запущен")

    while True:
        await asyncio.sleep(1)
