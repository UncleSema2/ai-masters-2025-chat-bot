import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    # Telegram Bot Configuration
    telegram_bot_token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")

    # OpenAI Configuration
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4.1-mini-2025-04-14")

    # Database Configuration
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./data/chatbot.db")

    # Application Configuration
    debug: bool = os.getenv("DEBUG", "True").lower() == "true"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    # Web Scraping Configuration
    request_delay: int = int(os.getenv("REQUEST_DELAY", "1"))
    user_agent: str = os.getenv("USER_AGENT", "AI-Master-2025-Chatbot/1.0")

    class Config:
        env_file = ".env"


settings = Settings()
