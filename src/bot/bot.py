import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import Command
import asyncio
import sys


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

TOKEN = "8470000861:AAFP_Fe1SGA07XTl-wu-63mVl8hyBHjMHDk"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ~~~~~~~~~~~~~~~~~
# МЕСТО ДЛЯ ВАЛИКА 
# ~~~~~~~~~~~~~~~~~


async def main():
    logger.info("Запуск бота...")
    logger.info(f"Bot token: {TOKEN[:10]}...")
    
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        raise
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)
