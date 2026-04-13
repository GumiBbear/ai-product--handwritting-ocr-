import os
import json
import google.generativeai as genai
from PIL import Image
import time

# API-ключ Gemini 
API_KEY = "AIzaSyChPgftXyJGqEUOfYD5TCPHo6gMlF5eXzM"

# Фото для разметки
INPUT_DIR = "data/raw"

# Выходной файл с результатами разметки
OUTPUT_FILE = "data/annotated_dataset.jsonl"

# Промпт для Gemini
PROMPT = """Распознай русский рукописный текст на изображении.
Верни ТОЛЬКО распознанный текст, без комментариев и пояснений.
Если текст неразборчив, напиши [НЕРАЗБОРЧИВО].
Сохрани орфографию и пунктуацию как есть.
Не добавляй слова от себя."""

# Настройка Gemini
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Список фото
photos = [f for f in os.listdir(INPUT_DIR) if f.endswith(('.jpg', '.jpeg', '.png'))]
print(f"Найдено фото: {len(photos)}")
print(f"Папка: {INPUT_DIR}")
print(f"Результаты будут сохранены в: {OUTPUT_FILE}")
print("=" * 60)

# Обработка
results = []
for i, photo in enumerate(photos, 1):
    print(f"\n[{i}/{len(photos)}] Обработка: {photo}")
    
    try:
        # Открываем фото
        img_path = os.path.join(INPUT_DIR, photo)
        img = Image.open(img_path)
        
        # Отправляем в Gemini
        response = model.generate_content([PROMPT, img])
        text = response.text.strip()
        
        # Сохраняем результат
        results.append({
            "image": photo,
            "text": text
        })
        
        print(f"Распознано: {text[:80]}...")
        
    except Exception as e:
        print(f"Ошибка: {e}")
        results.append({
            "image": photo,
            "text": "[ОШИБКА]"
        })
    
    # Задержка между запросами (не более 60 запросов в минуту)
    time.sleep(1)

# Результаты
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    for item in results:
        f.write(json.dumps(item, ensure_ascii=False) + '\n')

print("\n" + "=" * 60)
print(f"Готово! Обработано фото: {len(results)}")
print(f"Результаты сохранены в: {OUTPUT_FILE}")
print("=" * 60)
