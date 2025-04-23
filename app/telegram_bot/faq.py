# app/telegram_bot/faq.py
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from app.db.session import SessionLocal
from app.db import models      # если FAQ хранится в БД

# ─────────────────────────────────────────────────────────────
def _load_faq() -> list[tuple[int, str, str]]:
    db = SessionLocal()
    try:
        rows = db.query(models.FAQ).all()           # модель FAQ(id,q,a)
        return [(row.id, row.question, row.answer) for row in rows]
    finally:
        db.close()

# ─────────────────────────────────────────────────────────────
async def faq_command(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    faq = _load_faq()
    if not faq:
        return await ctx.bot.send_message(chat_id, "FAQ пока пуст.")

    keyboard = [[InlineKeyboardButton(q, callback_data=f"faq_{fid}")]
                for fid, q, _ in faq]
    await ctx.bot.send_message(
        chat_id,
        "Частые вопросы:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ─────────────────────────────────────────────────────────────
async def faq_choice(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    parts = query.data.split("_", 1)
    if len(parts) != 2 or not parts[1].isdigit():
        return              # пришёл невалидный callback

    fid = int(parts[1])
    faq = {i: (q, a) for i, q, a in _load_faq()}
    question, answer = faq.get(fid, ("Не найдено", "—"))

    # показываем ответ + кнопку «⬅︎ Назад»
    kb = InlineKeyboardMarkup(
        [[InlineKeyboardButton("⬅︎ Назад к FAQ", callback_data="faq_back")]]
    )
    await query.edit_message_text(
        f"❓ <b>{question}</b>\n\n{answer}",
        reply_markup=kb,
        parse_mode="HTML"
    )

# ─────────────────────────────────────────────────────────────
async def faq_back(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    # удаляем сообщение с ответом
    await query.message.delete()

    # отправляем список FAQ заново
    await faq_command(update, ctx)