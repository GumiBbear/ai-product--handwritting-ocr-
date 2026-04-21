#cd C:\mybot


import logging
import asyncio
import tempfile
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
import easyocr
from spellchecker import SpellChecker

logging.basicConfig(level=logging.INFO)

TOKEN = "8470000861:AAFP_Fe1SGA07XTl-wu-63mVl8hyBHjMHDk"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Путь к папке с ботом
script_dir = os.path.dirname(os.path.abspath(__file__))

# 1. Загружаем словарь для проверки орфографии
print("📚 Загружаю словарь для проверки орфографии...")
spell = SpellChecker(language='ru')

dict_path = os.path.join(script_dir, 'russian.txt')
print(f"🔍 Ищу словарь по пути: {dict_path}")

# 2. Загружаем EasyOCR
print("📸 Загружаю EasyOCR...")
reader = easyocr.Reader(['ru', 'en'])
print("✅ EasyOCR готов!")

def recognize_text(image_data):
    """Распознаёт текст с фото через EasyOCR"""
    # Сохраняем в папку с ботом (где есть права)
    temp_path = os.path.join(script_dir, "temp_photo.jpg")
    with open(temp_path, "wb") as f:
        f.write(image_data.getvalue())
    
    result = reader.readtext(temp_path, detail=0, paragraph=True)
    
    # Удаляем временный файл
    try:
        os.remove(temp_path)
    except:
        pass
    
    return " ".join(result) if result else "❌ Текст на фото не найден"

def fix_spelling(text):
    """Исправляет орфографию через pyspellchecker"""
    words = text.split()
    corrected_words = []
    for word in words:
        clean_word = word.strip('.,!?;:()')
        if clean_word and not spell[clean_word]:
            correction = spell.correction(clean_word)
            corrected_words.append(correction if correction else clean_word)
        else:
            corrected_words.append(clean_word)
    return ' '.join(corrected_words)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 Привет! Я бот для распознавания текста с фото.\n\n"
        "📸 Отправь фото с текстом, и я:\n"
        "1️⃣ Распознаю текст (EasyOCR)\n"
        "2️⃣ Исправлю ошибки\n"
        "3️⃣ Отправлю результат"
    )

@dp.message(F.photo)
async def handle_photo(message: types.Message):
    status_msg = await message.answer("✉ Обрабатываю...")
    
    try:
        photo = message.photo[-1]
        file = await bot.get_file(photo.file_id)
        file_data = await bot.download_file(file.file_path)
        
        raw_text = recognize_text(file_data)
        fixed_text = fix_spelling(raw_text)
        
        result = f"📝 **Исходный текст:**\n{raw_text}\n\n✅ **Исправленный текст:**\n{fixed_text}"
        await status_msg.edit_text(result, parse_mode="Markdown")
        
    except Exception as e:
        await status_msg.edit_text(f"❌ Ошибка: {e}")

@dp.message()
async def unknown_message(message: types.Message):
    await message.answer("📸 Пожалуйста, отправь мне **фото** с текстом!")

async def main():
    print("🚀 Бот запущен! Отправляй фото с текстом.")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
