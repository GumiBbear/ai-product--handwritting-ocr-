import os
import json
import pytesseract
from PIL import Image
import re

# CER (символьная ошибка)
def calculate_cer(reference, hypothesis):
    ref = reference.replace(" ", "").replace("\n", "")
    hyp = hypothesis.replace(" ", "").replace("\n", "")
    
    if len(ref) == 0:
        return 0.0 if len(hyp) == 0 else 1.0
    
    diff = 0
    for i in range(min(len(ref), len(hyp))):
        if ref[i] != hyp[i]:
            diff += 1
    diff += abs(len(ref) - len(hyp))
    
    return diff / len(ref)

# WER (словесная ошибка)
def calculate_wer(reference, hypothesis):
    ref_words = reference.split()
    hyp_words = hypothesis.split()
    
    if len(ref_words) == 0:
        return 0.0 if len(hyp_words) == 0 else 1.0
    
    # Подсчёт ошибок
    errors = 0
    for i in range(min(len(ref_words), len(hyp_words))):
        if ref_words[i] != hyp_words[i]:
            errors += 1
    errors += abs(len(ref_words) - len(hyp_words))
    
    return errors / len(ref_words)

# Пути
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
images_dir = os.path.join(project_dir, "data", "raw", "images")
test_cases_file = os.path.join(project_dir, "data", "test_cases", "queries_answers.json")

# Загрузка тестовых кейсов
with open(test_cases_file, 'r', encoding='utf-8') as f:
    test_cases = json.load(f)

print("=" * 60)
print("BASELINE: Tesseract OCR")
print(f"Тестовых кейсов: {len(test_cases)}")
print("=" * 60)

results = []
total_cer = 0
total_wer = 0

for i, case in enumerate(test_cases, 1):
    image_path = os.path.join(images_dir, case["image"])
    expected = case["expected_text"].strip()
    
    if not os.path.exists(image_path):
        print(f"[{i}] ❌ Файл не найден: {case['image']}")
        continue
    
    # Распознавание
    img = Image.open(image_path)
    recognized = pytesseract.image_to_string(img, lang='rus').strip()
    
    # Очистка от лишних переносов
    recognized = re.sub(r'\n+', ' ', recognized)
    recognized = re.sub(r' +', ' ', recognized)
    
    # Расчёт метрик
    cer = calculate_cer(expected, recognized)
    wer = calculate_wer(expected, recognized)
    
    total_cer += cer
    total_wer += wer
    
    print(f"\n[{i}] {case['image']}")
    print(f"  Распознано: {recognized[:80]}...")
    print(f"  Ожидалось:  {expected[:80]}...")
    print(f"  CER: {cer:.2%} | WER: {wer:.2%}")
    
    results.append({
        "image": case["image"],
        "recognized": recognized,
        "expected": expected,
        "cer": cer,
        "wer": wer
    })

# Итоговые метрики
avg_cer = total_cer / len(test_cases)
avg_wer = total_wer / len(test_cases)

print("\n" + "=" * 60)
print("BASELINE РЕЗУЛЬТАТЫ (Tesseract)")
print("=" * 60)
print(f"Средняя символьная ошибка (CER): {avg_cer:.2%}")
print(f"Средняя словесная ошибка (WER):  {avg_wer:.2%}")
print("=" * 60)

# Сохранить результаты
results_file = os.path.join(project_dir, "data", "test_cases", "baseline_results.json")
with open(results_file, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"\nРезультаты сохранены в: {results_file}")
