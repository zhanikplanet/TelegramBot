# Чтобы при импорте app.api были сразу доступны роутеры
from .question import router as question_router
from .faq import router as faq_router
from .operator import router as operator_router

__all__ = [
    "question_router",
    "faq_router",
    "operator_router",
]
