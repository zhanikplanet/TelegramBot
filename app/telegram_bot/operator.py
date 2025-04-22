from telegram import Update
from telegram.ext import ContextTypes
from app.db.session import SessionLocal
from app.db.crud import (
    get_active_session, create_session, close_session,
    create_message, get_session_messages
)
from app.config import settings

async def escalate_to_operator(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db = SessionLocal()
    # ensure user exists, then create session
    active = get_active_session(db, user.id)
    if not active:
        sess = create_session(db, user.id)
    else:
        sess = active

    # send history to all operators
    history = get_session_messages(db, sess.id)
    text = f"🔔 Сессия #{sess.id} от @{user.username or user.id}\n\n"
    for m in history:
        ts = m.timestamp.strftime("%Y-%m-%d %H:%M")
        text += f"[{ts}] {m.role.upper()}: {m.text}\n"

    for op_id in settings.operator_chat_ids:
        await ctx.bot.send_message(chat_id=op_id, text=text)

    db.close()
    ctx.user_data['session_id'] = sess.id
    ctx.user_data['session_active'] = True
    await update.message.reply_text("Вы подключены к оператору.")

async def handle_operator_reply(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in settings.operator_chat_ids:
        return
    db = SessionLocal()
    # find latest active session
    sess = get_active_session(db, None)  # custom filter inside crud
    if not sess:
        await update.message.reply_text("Нет активных сессий.")
        db.close(); return
    text = update.message.text
    # save and forward
    create_message(db, schemas.MessageCreate(
        session_id=sess.id,
        user_id=sess.user_id,
        role="operator",
        text=text
    ))
    await ctx.bot.send_message(chat_id=sess.user_id, text=f"Оператор: {text}")
    await update.message.reply_text("Сообщение отправлено пользователю.")
    db.close()