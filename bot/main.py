import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import settings
from handlers.user_handlers import router
from models.database import Database


async def main():
    """Main function to run the bot"""
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    logger = logging.getLogger(__name__)
    logger.info("Starting AI Master 2025 Chatbot...")

    # Check if required settings exist
    if not settings.telegram_bot_token:
        logger.error("TELEGRAM_BOT_TOKEN is not set in environment variables")
        return

    if not settings.openai_api_key:
        logger.error("OPENAI_API_KEY is not set in environment variables")
        return

    # Initialize database
    Database()
    logger.info("Database initialized")

    # Initialize bot and dispatcher
    bot = Bot(
        token=settings.telegram_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN),
    )

    dp = Dispatcher(storage=MemoryStorage())

    # Include routers
    dp.include_router(router)

    logger.info("Bot configuration completed")

    try:
        # Start polling
        logger.info("Starting bot polling...")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Error during bot polling: {e}")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
