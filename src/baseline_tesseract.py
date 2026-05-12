import os
import json
import pytesseract
from PIL import Image

IMAGES_DIR = "data/raw"
TEST_CASES_FILE = "data/test_cases/queries_answers.json"
RESULTS_FILE = "data/baseline_results.json"

def calculate_cer(ref, hyp):
    ref = ref.replace(" ", "").replace("\n", "")
    hyp = hyp.replace(" ", "").replace("\n", "")
    if len(ref) == 0:
        return 0.0
    diff = 0
    for i in range(min(len(ref), len(hyp))):
        if ref[i] != hyp[i]:
            diff += 1
    diff += abs(len(ref) - len(hyp))
    return diff / len(ref)

def calculate_wer(ref, hyp):
    ref_words = ref.split()
    hyp_words = hyp.split()
    if len(ref_words) == 0:
        return 0.0
    errors = 0
    for i in range(min(len(ref_words), len(hyp_words))):
        if ref_words[i] != hyp_words[i]:
            errors += 1
    errors += abs(len(ref_words) - len(hyp_words))
    return errors / len(ref_words)

with open(TEST_CASES_FILE, 'r', encoding='utf-8') as f:
    test_cases = json.load(f)

results = []
total_cer = 0
total_wer = 0

for case in test_cases:
    img_path = os.path.join(IMAGES_DIR, case["image"])
    if not os.path.exists(img_path):
        continue
    
    img = Image.open(img_path)
    recognized = pytesseract.image_to_string(img, lang='rus').strip()
    recognized = ' '.join(recognized.split())
    
    expected = case["expected_text"].strip()
    
    cer = calculate_cer(expected, recognized)
    wer = calculate_wer(expected, recognized)
    
    total_cer += cer
    total_wer += wer
    
    results.append({
        "image": case["image"],
        "recognized": recognized,
        "expected": expected,
        "cer": cer,
        "wer": wer
    })

avg_cer = total_cer / len(test_cases)
avg_wer = total_wer / len(test_cases)

with open(RESULTS_FILE, 'w', encoding='utf-8') as f:
    json.dump({
        "avg_cer": avg_cer,
        "avg_wer": avg_wer,
        "details": results
    }, f, ensure_ascii=False, indent=2)

print(f"CER: {avg_cer:.2%}, WER: {avg_wer:.2%}")
print(f"Results saved to {RESULTS_FILE}")
