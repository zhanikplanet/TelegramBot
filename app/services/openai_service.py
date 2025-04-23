from openai import AsyncOpenAI
from app.config import settings

client = AsyncOpenAI(api_key=settings.openai_api_key)   # ① создаём клиент

MODEL_NAME = settings.openai_model                      # "gpt-4o-mini" и т.д.

async def ask_openai(prompt: str) -> str:
    """Отдаёт ответ ассистента на один промпт."""
    response = await client.chat.completions.create(    # ② новый вызов
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()
