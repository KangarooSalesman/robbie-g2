import easyocr
import os
from pathlib import Path
import shutil
import tempfile

# Initialize the reader with the desired languages
reader = easyocr.Reader(['en'])  # You can add more languages if needed

# Use the correct file path with Path object
original_image_path = Path(r"C:\Users\marpa\OneDrive\Εικόνες\Στιγμιότυπα οθόνης\o1.png")

try:
    if not original_image_path.exists():
        raise FileNotFoundError(f"The file {original_image_path} does not exist.")
    
    # Create a temporary file with a simple name
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
        temp_image_path = temp_file.name
    
    # Copy the original file to the temporary location
    shutil.copy2(original_image_path, temp_image_path)
    
    # Use the temporary file for OCR
    result = reader.readtext(temp_image_path)

    # Print the results with location information
    for detection in result:
        bbox, text, confidence = detection
        x_min, y_min = bbox[0]
        x_max, y_max = bbox[2]
        print(f"Detected text: '{text}'")
        print(f"Confidence: {confidence:.2f}")
        print(f"Location: Top-left ({x_min:.2f}, {y_min:.2f}), Bottom-right ({x_max:.2f}, {y_max:.2f})")
        print(f"Width: {x_max - x_min:.2f}, Height: {y_max - y_min:.2f}")
        print("---")

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
if 'temp_image_path' in locals():
    print(f"Temporary image path: {temp_image_path}")