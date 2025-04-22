from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from typing import List
from app.db.crud import get_faqs
from app.db.session import SessionLocal
from app.db.crud import get_faqs

# Main menu

def main_keyboard(ai_count: int) -> ReplyKeyboardMarkup:
    buttons = [[KeyboardButton("FAQ"), KeyboardButton("Новый вопрос")]]
    if ai_count >= 2:
        buttons.append([KeyboardButton("Оператор")])
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

# FAQ inline menu

def faq_keyboard() -> InlineKeyboardMarkup:
    db = SessionLocal()
    items = get_faqs(db)
    db.close()
    buttons = [InlineKeyboardButton(q.question, callback_data=f"faq_{q.id}") for q in items]
    return InlineKeyboardMarkup([[btn] for btn in buttons])