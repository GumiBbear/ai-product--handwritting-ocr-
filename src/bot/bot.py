import logging
from aiogram import Bot, Dispatcher, types, F
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

#начало фронтенда
# Обработчик команды /start
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "👋 Привет! Я бот для распознавания текста с фото.\n\n"
        "📸 Как пользоваться:\n"
        "1. Отправь мне любое фото с текстом\n"
        "2. Я исправлю грамматические ошибки\n"
        "3. Верну исправленный текст\n\n"
    )

# Обработчик фото (с индикатором загрузки и заглушкой)
@dp.message(F.photo)
async def handle_photo(message: Message):
    # Индикатор загрузки
    status_msg = await message.answer("⏳ Обрабатываю...")
    
    # Имитация обработки
    await asyncio.sleep(1)
    
    # Заглушка ответа
    await status_msg.edit_text(
        "✅ Фото принято!\n\n"
        "`Это заглушка. Модель в разработке.`\n\n"
        "💡 Настоящее распознавание текста появится позже."
    )

# На случай, если отправят не фото
@dp.message()
async def unknown_message(message: Message):
    await message.answer("📸 Пожалуйста, отправь **фото** с текстом!")

#конец фронтенда


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
