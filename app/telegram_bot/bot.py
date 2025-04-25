
import asyncio
from datetime import timedelta
from typing import List

from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

from app.config import settings
from app.db.session import SessionLocal
from app.db import crud, models, schemas
from app.services.openai_service import ask_openai
from app.telegram_bot.faq import faq_command, faq_choice, faq_back
from app.utils import format_ts

# ---------------------------------------------------------------------------
#   CONSTANTS
# ---------------------------------------------------------------------------
BTN_FAQ             = "FAQ"
BTN_START_DIALOG    = "Начать диалог"
BTN_OPERATOR        = "Оператор"
BTN_END_DIALOG      = "🔴 Завершить диалог"
BTN_START_SHIFT     = "🟢 Начать смену"
BTN_END_SHIFT       = "🔴 Закончить смену"

WELCOME_TEMPLATE = (
    "Привет, {name}!\n"
    "Я — бот‑помощник. Здесь вы можете:\n"
    "– найти ответ в FAQ;\n"
    "– пообщаться с ИИ, чтобы найти ответ;\n"
    "– обратиться к оператору (после трёх ответов ИИ).\n"
    "Используя данного бота, вы даёте согласие на обработку ваших данных."
)

# ---------------------------------------------------------------------------
#   HELPERS
# ---------------------------------------------------------------------------
def user_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [[KeyboardButton(BTN_FAQ), KeyboardButton(BTN_START_DIALOG)]],
        resize_keyboard=True,
    )

def operator_keyboard(on_shift: bool) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton(BTN_FAQ)],
            [KeyboardButton(BTN_END_SHIFT if on_shift else BTN_START_SHIFT)],
            [KeyboardButton(BTN_END_DIALOG)],
        ],
        resize_keyboard=True,
    )

def session_keyboard(ai_count: int) -> ReplyKeyboardMarkup:
    buttons: List[List[KeyboardButton]] = []
    if ai_count >= 2:
        buttons.append([KeyboardButton(BTN_OPERATOR)])
    buttons.append([KeyboardButton(BTN_END_DIALOG)])
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

# ---------------------------------------------------------------------------
#   /start
# ---------------------------------------------------------------------------
async def start_command(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    db = SessionLocal()
    try:
        # Create user in DB if not exists
        crud.get_or_create_user(db, user.id, user.first_name)

        if user.id in settings.operator_chat_ids:
            on_shift = crud.is_operator_on_shift(db, user.id)
            kb = operator_keyboard(on_shift)
        else:
            kb = user_keyboard()

        await update.message.reply_text(
            WELCOME_TEMPLATE.format(name=user.first_name or "друг"),
            reply_markup=kb,
        )

        # purge context for user start
        ctx.user_data.clear()
    finally:
        db.close()

# ---------------------------------------------------------------------------
#   OPERATOR SHIFT
# ---------------------------------------------------------------------------
async def start_shift(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    db = SessionLocal()
    crud.create_shift(db, operator_id=update.effective_user.id)
    db.close()
    await update.message.reply_text("Смена началась ✅", reply_markup=operator_keyboard(on_shift=True))

async def end_shift(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    db = SessionLocal()
    crud.finish_shift(db, operator_id=update.effective_user.id)
    db.close()
    await update.message.reply_text("Смена завершена 🛑", reply_markup=operator_keyboard(on_shift=False))

# ---------------------------------------------------------------------------
#   END SESSION FOR USER OR OPERATOR
# ---------------------------------------------------------------------------
async def end_session(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    uid = update.effective_user.id
    db = SessionLocal()
    try:
        # Operator pressed
        if uid in settings.operator_chat_ids:
            sess = crud.get_active_session_by_operator(db, uid)
            if not sess:
                await update.message.reply_text("Нет активной сессии.")
                return
            crud.close_session(db, sess.id)
            # notify user
            await ctx.bot.send_message(
                chat_id=sess.user_id,
                text="Разговор завершён. Надеюсь, вам помог оператор.",
                reply_markup=user_keyboard(),
            )
            await update.message.reply_text("Диалог завершён.")
            return

        # User pressed
        sess_id = ctx.user_data.get("session_id")
        if not sess_id:
            await update.message.reply_text("Нет активной сессии.")
            return

        in_operator = ctx.user_data.get("in_operator", False)
        crud.close_session(db, sess_id)
        msg = (
            "Разговор завершён. Надеюсь, вам помог оператор."
            if in_operator
            else "Разговор завершён. Надеюсь, ИИ ответил на ваш вопрос."
        )
        await update.message.reply_text(msg, reply_markup=user_keyboard())
        ctx.user_data.clear()
    finally:
        db.close()

# ---------------------------------------------------------------------------
#   ESCALATE TO OPERATOR
# ---------------------------------------------------------------------------
async def escalate_to_operator(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    uid = update.effective_user.id
    db = SessionLocal()
    try:
        sess_id = ctx.user_data.get("session_id")
        if not sess_id:
            await update.message.reply_text("Сессия не найдена, начните диалог сначала.")
            return
        # find free operator
        op = crud.find_free_operator(db, settings.operator_chat_ids)
        if not op:
            await update.message.reply_text("Сейчас все операторы заняты, попробуйте позже.")
            return
        # assign
        crud.assign_operator_to_session(db, sess_id, op.id)
        ctx.user_data["in_operator"] = True
        ctx.user_data["operator_id"] = op.id

        # send full history
        history = crud.get_session_messages(db, sess_id)
        text_history = f"🔔 Сессия #{sess_id} от @{update.effective_user.username or uid}\n\n"
        for m in history:
            text_history += f"[{format_ts(m.timestamp)}] {m.role.upper()}: {m.text}\n"
        await ctx.bot.send_message(chat_id=op.id, text=text_history)

        await update.message.reply_text("✅ Оператор подключен, ожидайте его ответа…")
    finally:
        db.close()

# ---------------------------------------------------------------------------
#   OPERATOR REPLY
# ---------------------------------------------------------------------------
async def operator_reply(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    op_id = update.effective_user.id
    if op_id not in settings.operator_chat_ids:
        return  # ignore strangers

    db = SessionLocal()
    try:
        sess = crud.get_active_session_by_operator(db, op_id)
        if not sess:
            await update.message.reply_text("Нет активных сессий.")
            return
        text = update.message.text
        # save
        crud.create_message(
            db,
            schemas.MessageCreate(
                session_id=sess.id,
                user_id=sess.user_id,
                role="operator",
                text=text,
            ),
        )
        # forward to user
        await ctx.bot.send_message(chat_id=sess.user_id, text=f"Оператор: {text}")
        await update.message.reply_text("Сообщение отправлено пользователю.")
    finally:
        db.close()

# ---------------------------------------------------------------------------
#   USER MESSAGE HANDLER
# ---------------------------------------------------------------------------
async def user_message(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text
    uid = update.effective_user.id

    # ----- Operators text falls here when not command -----
    if uid in settings.operator_chat_ids:
        # shift toggle
        if text in (BTN_START_SHIFT, BTN_END_SHIFT):
            if text == BTN_START_SHIFT:
                await start_shift(update, ctx)
            else:
                await end_shift(update, ctx)
            return
        if text == BTN_END_DIALOG:
            await end_session(update, ctx)
            return
        # otherwise treat as operator reply
        await operator_reply(update, ctx)
        return

    # ----- Regular user flow -----
    # 1. FAQ
    if text == BTN_FAQ:
        await faq_command(update, ctx)
        return

    # 2. Start dialog
    if text == BTN_START_DIALOG:
        db = SessionLocal()
        try:
            sess = crud.create_session(db, uid)
            ctx.user_data.update(
                session_id=sess.id,
                ai_count=0,
                in_operator=False,
            )
            await update.message.reply_text(
                "Ждём ваш вопрос…", reply_markup=session_keyboard(ai_count=0)
            )
        finally:
            db.close()
        return

    # 3. End dialog
    if text == BTN_END_DIALOG:
        await end_session(update, ctx)
        return

    # 4. Escalate
    if text == BTN_OPERATOR:
        await escalate_to_operator(update, ctx)
        return

    # 5. If user in operator session -> relay to operator
    if ctx.user_data.get("in_operator"):
        op_id = ctx.user_data["operator_id"]
        db = SessionLocal()
        try:
            # save
            crud.create_message(
                db,
                schemas.MessageCreate(
                    session_id=ctx.user_data["session_id"],
                    user_id=uid,
                    role="user",
                    text=text,
                ),
            )
        finally:
            db.close()
        await ctx.bot.send_message(chat_id=op_id, text=f"Пользователь: {text}")
        return

    # 6. If no active session
    if not ctx.user_data.get("session_id"):
        await update.message.reply_text(
            "Нажмите «Начать диалог», чтобы задать вопрос ИИ.", reply_markup=user_keyboard()
        )
        return

    # 7. Conversation with AI
    db = SessionLocal()
    try:
        sess_id = ctx.user_data["session_id"]

        # --- сохраняем сообщение пользователя ---
        crud.create_message(
            db,
            schemas.MessageCreate(
                session_id=sess_id,
                user_id=uid,
                role="user",
                text=text,
            ),
        )

        # --- спрашиваем ИИ ---
        answer = await ask_openai(text)

        # --- инкрементируем счётчик ДО отправки, чтобы
        #     кнопка появлялась уже на втором ответе ---
        ctx.user_data["ai_count"] = ctx.user_data.get("ai_count", 0) + 1

        # --- сохраняем ответ ИИ ---
        crud.create_message(
            db,
            schemas.MessageCreate(
                session_id=sess_id,
                user_id=uid,
                role="bot",
                text=answer,
            ),
        )

        # --- отправляем ответ + актуальную клавиатуру ---
        await update.message.reply_text(
            answer,
            reply_markup=session_keyboard(ctx.user_data["ai_count"])
        )

    finally:
        db.close()


# ---------------------------------------------------------------------------
#   SESSION TIMEOUT LOOP (unchanged)
# ---------------------------------------------------------------------------
async def session_timeout_loop():
    while True:
        db = SessionLocal()
        try:
            stale = crud.find_stale_sessions(db, older_than=timedelta(minutes=3))
            for s in stale:
                crud.close_session(db, s.id)
                await app.bot.send_message(
                    s.user_id, "Сессия закрыта по таймауту.", reply_markup=user_keyboard()
                )
                if s.operator_id:
                    await app.bot.send_message(s.operator_id, "Сессия закрыта по таймауту.")
        finally:
            db.close()
        await asyncio.sleep(60)

# ---------------------------------------------------------------------------
#   MAIN BOT
# ---------------------------------------------------------------------------
async def main_bot():
    global app
    app = (
        ApplicationBuilder()
        .token(settings.bot_token)
        .concurrent_updates(True)
        .build()
    )

    # 0. FAQ callbacks
    app.add_handler(CallbackQueryHandler(faq_choice, pattern=r"^faq_\d+$"), group=0)
    app.add_handler(CallbackQueryHandler(faq_back, pattern=r"^faq_back$"), group=0)

    # 1. Commands
    app.add_handler(CommandHandler("start", start_command), group=1)

    # 2. End session
    app.add_handler(MessageHandler(filters.Regex(fr"^{BTN_END_DIALOG}$"), end_session), group=2)

    # 3. All text
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, user_message), group=3)

    # Start
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    asyncio.create_task(session_timeout_loop())
    print("✅ Бот запущен")

    while True:
        await asyncio.sleep(1)
