from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from typing import List
from app.db.crud import get_faqs
from app.db.session import SessionLocal

def main_keyboard(ai_count: int) -> ReplyKeyboardMarkup:
    buttons = [[KeyboardButton("FAQ"), KeyboardButton("Начать диалог")]]
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

# Inline-меню для FAQ (не изменилось)

def faq_keyboard() -> InlineKeyboardMarkup:
    db = SessionLocal()
    items = get_faqs(db)
    db.close()
    buttons = [[InlineKeyboardButton(item.question, callback_data=f"faq_{item.id}")] for item in items]
    return InlineKeyboardMarkup(buttons)
