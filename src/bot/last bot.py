import os
import json
import logging
from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from google import genai
from PIL import Image
import io
import time
import aiohttp

# ============================================================
# 1. НАСТРОЙКИ
# ============================================================
# Telegram Bot Token (получить у @BotFather)
TELEGRAM_TOKEN = "8470000861:AAFP_Fe1SGA07XTl-wu-63mVl8hyBHjMHDk"

# Gemini API Key (получить в Google AI Studio)
GEMINI_API_KEY = "AIzaSyAZGA6I62jmTxfOElRwt0qz20IudqW5iLE"

# Папка для временного хранения фото
TEMP_DIR = "temp_photos"

# Создаём папку, если её нет
os.makedirs(TEMP_DIR, exist_ok=True)

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Инициализация Gemini клиента
client = genai.Client(api_key=GEMINI_API_KEY)

print("✅ Яндекс.Спеллер будет использоваться для исправления ошибок")

# Промпт для Gemini
PROMPT_TEXT = """Внимательно прочитай весь русский рукописный текст на изображении.
Распознай и выведи ВЕСЬ текст ПОЛНОСТЬЮ, от начала до конца.
Не сокращай, не пропускай абзацы, не обрезай.
Верни только текст, без комментариев и пояснений.
Если текст неразборчив, напиши [НЕРАЗБОРЧИВО].
"""

# ============================================================
# 2. ФУНКЦИЯ РАСПОЗНАВАНИЯ ТЕКСТА ЧЕРЕЗ GEMINI
# ============================================================
def recognize_text(image_path: str) -> str:
    """
    Отправляет фото в Gemini API и возвращает распознанный текст
    """
    try:
        img = Image.open(image_path)
        
        response = client.models.generate_content(
            model="gemini-flash-lite-latest",
            contents=[PROMPT_TEXT, img],
            config={
                "max_output_tokens": 2048,
                "temperature": 0.1
            }
        )
        
        text = response.text.strip()
        return text if text else "[НЕ РАСПОЗНАНО]"
        
    except Exception as e:
        logger.error(f"Ошибка Gemini API: {e}")
        return f"[ОШИБКА: {e}]"

# ============================================================
# 2.5 ФУНКЦИЯ ИСПРАВЛЕНИЯ ОШИБОК ЧЕРЕЗ ЯНДЕКС.СПЕЛЛЕР
# ============================================================
async def fix_spelling_with_yandex(text: str) -> str:
    """
    Исправляет орфографические ошибки через Яндекс.Спеллер API
    """
    if not text or len(text.strip()) == 0:
        return text
    
    url = "https://speller.yandex.net/services/spellservice.json/checkText"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data={
                "text": text,
                "lang": "ru",
                "format": "plain"
            }) as response:
                if response.status == 200:
                    result = await response.json()
                    
                    # Применяем исправления (с конца, чтобы не сбивать индексы)
                    corrected_text = text
                    for error in reversed(result):
                        if error.get('s') and len(error['s']) > 0:
                            start = error['pos']
                            end = error['pos'] + error['len']
                            correction = error['s'][0]
                            corrected_text = corrected_text[:start] + correction + corrected_text[end:]
                    
                    return corrected_text
                else:
                    logger.warning(f"Яндекс.Спеллер ошибка: {response.status}")
                    return text
    except Exception as e:
        logger.error(f"Ошибка при вызове Яндекс.Спеллера: {e}")
        return text

# ============================================================
# 3. КОМАНДЫ БОТА
# ============================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Приветственное сообщение"""
    await update.message.reply_text(
        "👋 Привет! Я бот для распознавания орфографических ошибок в рукописном тексте.\n\n"
        "📸 Отправь мне фото страницы с текстом,\n"
        "и исправлю все ошибки.\n\n"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Справка"""
    await update.message.reply_text(
        "📖 Как пользоваться:\n"
        "1. Отправь фото рукописного текста\n"
        "2. Подожди несколько секунд\n"
        "3. Получи распознанный и исправленный текст\n\n"
    )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка фото от пользователя"""
    
    # Отправляем сообщение о начале обработки
    status_msg = await update.message.reply_text("⏳ Обрабатываю изображение...")
    
    try:
        # Получаем фото самого высокого качества
        photo_file = await update.message.photo[-1].get_file()
        
        # Сохраняем фото временно
        file_path = os.path.join(TEMP_DIR, f"photo_{update.message.from_user.id}_{int(time.time())}.jpg")
        await photo_file.download_to_drive(file_path)
        
        # Распознаём текст через Gemini
        recognized_text = recognize_text(file_path)
        
        # ИСПРАВЛЯЕМ ОРФОГРАФИЧЕСКИЕ ОШИБКИ ЧЕРЕЗ ЯНДЕКС.СПЕЛЛЕР
        recognized_text = await fix_spelling_with_yandex(recognized_text)
        
        # Удаляем временный файл
        os.remove(file_path)
        
        # Отправляем результат
        await status_msg.delete()
        
        # Формируем ответ
        response = f"📝 **Распознанный текст:**\n\n{recognized_text}"
        
        # Если текст слишком длинный (больше 4096 символов), разбиваем на части
        if len(response) > 4000:
            for i in range(0, len(response), 4000):
                await update.message.reply_text(response[i:i+4000], parse_mode='Markdown')
        else:
            await update.message.reply_text(response, parse_mode='Markdown')
        
        logger.info(f"Пользователь {update.message.from_user.id}: успешно обработано фото")
        
    except Exception as e:
        await status_msg.delete()
        error_msg = f"❌ Ошибка при обработке фото: {str(e)}"
        await update.message.reply_text(error_msg)
        logger.error(f"Ошибка у пользователя {update.message.from_user.id}: {e}")

# ============================================================
# 4. ЗАПУСК БОТА
# ============================================================
def main():
    """Запуск бота"""
    
    # Создаём приложение
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Регистрируем команды
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    
    # Регистрируем обработчик фото
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    # Запускаем бота
    print("🤖 Бот запущен...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()