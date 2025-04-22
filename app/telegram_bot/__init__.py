# Делает telegram_bot пакетом и сразу экспортирует основные функции

from .bot import main_bot
from .keyboards import main_keyboard, faq_keyboard
from .user import handle_start
from .faq import faq_command, faq_choice
from .operator import escalate_to_operator, handle_operator_reply

__all__ = [
    "main_bot",
    "main_keyboard", "faq_keyboard",
    "handle_start",
    "faq_command", "faq_choice",
    "escalate_to_operator", "handle_operator_reply",
]
