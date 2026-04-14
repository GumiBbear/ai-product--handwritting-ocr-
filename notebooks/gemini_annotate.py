import os
import json
from google import genai
from PIL import Image
import time


API_KEY = "AIzaSyBvLuxOnaHrq_8LoIGVD-DrN9nsjA7hVJ4"

INPUT_DIR = "data/raw"
OUTPUT_FILE = "data/annotated_dataset.jsonl"

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
results = []
for i, photo in enumerate(photos, 1):
    print(f"\n[{i}/{len(photos)}] Обработка: {photo}")
    
    try:
        img_path = os.path.join(INPUT_DIR, photo)
        img = Image.open(img_path)

        # Отправляем запрос в новом формате
        response = client.models.generate_content(
            model="gemini-flash-lite-latest", # Модель Gemini
            contents=[PROMPT_TEXT, img],
            config={
                "max_output_tokens": 8192,  # максимум токенов в ответе
                "temperature": 0.1          
            }
        )
        
        text = response.text.strip()
        results.append({"image": photo, "text": text})
        print(f"  ✅ Распознано: {text[:80]}...")
        
    except Exception as e:
        print(f"  ❌ Ошибка: {e}")
        results.append({"image": photo, "text": "[ОШИБКА]"})
    
    time.sleep(1) # Задержка для соблюдения лимитов

# Сохранение результатов
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    for item in results:
        f.write(json.dumps(item, ensure_ascii=False) + '\n')

print("\nГотово!")
