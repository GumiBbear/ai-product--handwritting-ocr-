import os
import json
from google import genai
from PIL import Image
import time

API_KEY = "AIzaSyArV9uuaEeUIYhNdmW2C0pbDnjqd7tkQew" # ключ проекта

INPUT_DIR = "data/train" # путь к папке с изображениями
OUTPUT_FILE = "data/recognize_text.json" # путь к файлу с расшифровкой

print(f"Текущая рабочая директория: {os.getcwd()}")
print(f"Полный путь к OUTPUT_FILE: {os.path.abspath(OUTPUT_FILE)}")

# Промпт для Gemini
PROMPT_TEXT = """Внимательно прочитай весь русский рукописный текст на изображении.
Распознай и выведи ВЕСЬ текст ПОЛНОСТЬЮ, от начала до конца.
Не сокращай, не пропускай абзацы, не обрезай.
Верни только текст, без комментариев и пояснений.
Если текст длинный — выведи его целиком.
"""

client = genai.Client(api_key=API_KEY)

# Список фото
photos = [f for f in os.listdir(INPUT_DIR) if f.endswith(('.jpg', '.jpeg', '.png'))]
print(f"Найдено фото: {len(photos)}")

# Обработка
for i, photo in enumerate(photos, 1):
    print(f"\n[{i}/{len(photos)}] Обработка: {photo}")
    
    try:
        img_path = os.path.join(INPUT_DIR, photo)
        img = Image.open(img_path)

        # Отправляем запрос в новом формате
        response = client.models.generate_content(
            model="gemini-2.5-flash", # Модель Gemini
            contents=[PROMPT_TEXT, img],
            config={
                "max_output_tokens": 8192, 
                "temperature": 0.1          
            }
        )
        
        text = response.text.strip()
        result = {"image": photo, "text": text}
        
        # Сохраняем результат сразу
        with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(result, ensure_ascii=False) + '\n')
        
        os.remove(img_path) 
        print(f"Распознано: {text[:80]}...")
        
    except Exception as e:
        print(f"Ошибка: {e}")
        
            
    
    time.sleep(1) # Задержка для соблюдения лимитов

print("\nГотово!")

# gemini-2.5-flash 
# gemini-2.0-flash 
# gemini-2.5-pro 
# gemini-2.0-flash-lite 
# gemini-2.0-flash-001 
# gemini-flash-latest 
# gemini-flash-lite-latest -
# gemini-pro-latest 
# gemini-2.5-flash-lite 
