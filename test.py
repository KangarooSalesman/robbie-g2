import easyocr
import os
from pathlib import Path
import shutil
import tempfile
from PIL import Image, ImageDraw, ImageTk
import numpy as np
from difflib import SequenceMatcher
import tkinter as tk
from tkinter import filedialog, messagebox

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
    temp_dir = tempfile.mkdtemp()
    temp_image_path = os.path.join(temp_dir, 'temp_image.png')

    try:
        # Copy the original file to the temporary location
        shutil.copy2(image_path, temp_image_path)

        original_image = Image.open(temp_image_path)
        ocr_results = find_all_text_with_bounding_boxes(temp_image_path)

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
        upscaled_image.save(temp_image_path)
        upscaled_image.close()

        upscaled_ocr_results = find_all_text_with_bounding_boxes(temp_image_path)

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
    finally:
        # Clean up the temporary file and directory
        original_image.close()
        try:
            os.remove(temp_image_path)
            os.rmdir(temp_dir)
        except Exception as e:
            print(f"Error cleaning up temporary files: {e}")

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Image Text Finder")
        self.geometry("600x400")

        self.image_path = None

        self.create_widgets()

    def create_widgets(self):
        self.image_label = tk.Label(self, text="No image selected")
        self.image_label.pack(pady=20)

        self.select_button = tk.Button(self, text="Select Image", command=self.select_image)
        self.select_button.pack(pady=10)

        self.text_entry = tk.Entry(self, width=50)
        self.text_entry.pack(pady=10)
        self.text_entry.insert(0, "Enter text to search")

        self.search_button = tk.Button(self, text="Search", command=self.search_text)
        self.search_button.pack(pady=10)

        self.result_label = tk.Label(self, text="")
        self.result_label.pack(pady=20)

    def select_image(self):
        self.image_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif")])
        if self.image_path:
            self.image_label.config(text=f"Image selected: {os.path.basename(self.image_path)}")

    def search_text(self):
        if not self.image_path:
            messagebox.showerror("Error", "Please select an image first")
            return

        search_text = self.text_entry.get()
        if search_text == "Enter text to search":
            messagebox.showerror("Error", "Please enter text to search")
            return

        result = find_coordinates(self.image_path, search_text)
        if result:
            self.result_label.config(text=f"Found '{result['text']}' at ({result['x']}, {result['y']})")
            with open('ocr_results.py', 'w') as f:
                f.write(f"ocr_results = [{result}]\n")
        else:
            self.result_label.config(text=f"Could not find '{search_text}'")

if __name__ == "__main__":
    app = App()
    app.mainloop()