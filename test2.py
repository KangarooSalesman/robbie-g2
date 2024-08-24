import pyautogui
import time
import tkinter as tk
from tkinter import messagebox

def move_to_location(x, y, text):
    print(f"Moving to '{text}' at ({x}, {y})")
    pyautogui.moveTo(x, y, duration=1)
    time.sleep(1)  # Pause for a second at each location

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Cursor Mover")
        self.geometry("300x150")

        self.create_widgets()

    def create_widgets(self):
        self.info_label = tk.Label(self, text="Click the button to move the cursor")
        self.info_label.pack(pady=20)

        self.move_button = tk.Button(self, text="Move Cursor", command=self.move_cursor)
        self.move_button.pack(pady=10)

    def move_cursor(self):
        try:
            from ocr_results import ocr_results
            if ocr_results:
                for result in ocr_results:
                    move_to_location(result["x"], result["y"], result["text"])
                messagebox.showinfo("Success", "Cursor movement complete!")
            else:
                messagebox.showwarning("Warning", "No results found. Run the search in the first app.")
        except ImportError:
            messagebox.showerror("Error", "No results file found. Run the search in the first app.")

if __name__ == "__main__":
    app = App()
    app.mainloop()