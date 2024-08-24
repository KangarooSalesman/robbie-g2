import easyocr
import os
from pathlib import Path
import shutil
import tempfile
from PIL import Image, ImageDraw
import numpy as np
from difflib import SequenceMatcher

# Constants
FIRST_OCR_THRESHOLD = 0.9
SECOND_OCR_THRESHOLD = 0.7
UPSCALE_FACTOR = 3

def similarity_ratio(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def find_all_text_with_bounding_boxes(image_path):
    reader = easyocr.Reader(['en'])
    results = reader.readtext(image_path)
    processed_results = []
    for box, text, confidence in results:
        result = {
            "x": int(box[0][0]),
            "y": int(box[0][1]),
            "w": int(box[2][0] - box[0][0]),
            "h": int(box[2][1] - box[0][1]),
            "text": text,
            "confidence": float(confidence)
        }
        processed_results.append(result)
    return processed_results

def find_coordinates(image_path, search_text):
    original_image = Image.open(image_path)
    ocr_results = find_all_text_with_bounding_boxes(image_path)

    # First OCR pass
    best_matches = [box for box in ocr_results if similarity_ratio(box['text'], search_text) >= FIRST_OCR_THRESHOLD]
    if len(best_matches) == 1:
        best_match = best_matches[0]
        return {
            "x": best_match["x"] + best_match["w"] // 2,
            "y": best_match["y"] + best_match["h"] // 2,
            "text": best_match["text"]
        }

    # Second OCR pass with upscaling
    upscaled_image = original_image.resize((original_image.width * UPSCALE_FACTOR, original_image.height * UPSCALE_FACTOR), Image.LANCZOS)
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
        upscaled_image_path = temp_file.name
        upscaled_image.save(upscaled_image_path)

    upscaled_ocr_results = find_all_text_with_bounding_boxes(upscaled_image_path)
    os.remove(upscaled_image_path)

    best_matches = [box for box in upscaled_ocr_results if similarity_ratio(box['text'], search_text) >= SECOND_OCR_THRESHOLD]
    if len(best_matches) == 1:
        best_match = best_matches[0]
        return {
            "x": best_match["x"] // UPSCALE_FACTOR + best_match["w"] // (2 * UPSCALE_FACTOR),
            "y": best_match["y"] // UPSCALE_FACTOR + best_match["h"] // (2 * UPSCALE_FACTOR),
            "text": best_match["text"]
        }

    # Fallback: return the closest match
    if best_matches:
        best_match = max(best_matches, key=lambda x: x['confidence'])
        return {
            "x": best_match["x"] // UPSCALE_FACTOR + best_match["w"] // (2 * UPSCALE_FACTOR),
            "y": best_match["y"] // UPSCALE_FACTOR + best_match["h"] // (2 * UPSCALE_FACTOR),
            "text": best_match["text"]
        }

    return None

# Main execution
original_image_path = Path(r"C:\Users\marpa\OneDrive\Εικόνες\Στιγμιότυπα οθόνης\o1.png")

try:
    if not original_image_path.exists():
        raise FileNotFoundError(f"The file {original_image_path} does not exist.")

    # Create a temporary file with a simple name
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
        temp_image_path = temp_file.name

    # Copy the original file to the temporary location
    shutil.copy2(original_image_path, temp_image_path)

    # List of texts to search for
    search_texts = ["fsfs", "Dayz", "Some text that might not exist"]

    results = []
    for search_text in search_texts:
        result = find_coordinates(temp_image_path, search_text)
        if result:
            results.append(result)
            print(f"Found '{result['text']}' at ({result['x']}, {result['y']})")
        else:
            print(f"Could not find '{search_text}'")

    # Save results for test2.py
    with open('ocr_results.py', 'w') as f:
        f.write(f"ocr_results = {results}\n")

except FileNotFoundError as e:
    print(f"File error: {e}")
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    # Clean up the temporary file
    if 'temp_image_path' in locals():
        os.remove(temp_image_path)

# Print additional debug information
print(f"\nDebug Info:")
print(f"Original image path: {original_image_path}")
print(f"Original image exists: {original_image_path.exists()}")
print(f"Original image is file: {original_image_path.is_file()}")