import os
from pydantic_settings import BaseSettings
from typing import List
class Settings(BaseSettings):
    bot_token: str
    openai_api_key: str
    database_url: str
    operator_chat_ids: List[int]

    class Config:
        env_file = ".env"

settings = Settings()
