import pyautogui
import time
from ocr_results import ocr_results

def move_to_location(x, y, text):
    print(f"Moving to '{text}' at ({x}, {y})")
    pyautogui.moveTo(x, y, duration=1)
    time.sleep(1)  # Pause for a second at each location

input("Press Enter to start moving the cursor...")

for result in ocr_results:
    move_to_location(result["x"], result["y"], result["text"])

print("Cursor movement complete!")