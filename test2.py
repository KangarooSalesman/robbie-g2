import pyautogui
import time

def move_to_location(x, y, text):
    print(f"Moving to '{text}' at ({x}, {y})")
    pyautogui.moveTo(x, y, duration=1)
    time.sleep(1)  # Pause for a second at each location

# Sample data from EasyOCR (you would typically get this from your OCR script)
ocr_results = [
    {"text": "fsfs", "x": 115, "y": 1185},
    {"text": "Dayz", "x": 281, "y": 291}
]

input("Press Enter to start moving the cursor...")

for result in ocr_results:
    move_to_location(result["x"], result["y"], result["text"])

print("Cursor movement complete!")