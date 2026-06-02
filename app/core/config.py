from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    supabase_url: str
    supabase_key: str
    groq_api_key: str
    telegram_bot_token: str
    telegram_chat_id: str
    redis_url: str

    class Config:
        env_file = ".env"

settings = Settings()