import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import cv2
import numpy as np
import mss
import pytesseract
import google.generativeai as genai
import os 
import time
import subprocess



# ========== CONFIGURATION ==========
api_key = os.environ.get('GOOGLE_API_KEY')
genai.configure(api_key=api_key)
# ===================================

def capture_screen():
    with mss.mss() as sct:
        monitor = sct.monitors[1]  # Full screen
        screenshot = sct.grab(monitor)
        img = np.array(screenshot)
        return img

def extract_text(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(gray)
    return text.strip()

def ask_gemini(question_text):
    try:
        model = genai.GenerativeModel("gemini-2.5-pro")
        response = model.generate_content(f"Answer this quiz question:\n{question_text}")
        return response.text.strip()
    except Exception as e:
        return f"Error: {e}"

class QuizAssistantApp:
    def __init__(self, master):
        self.master = master
        master.title("Quiz Assistant (Gemini)")
        master.geometry("800x500")

        self.label = tk.Label(master, text="Click 'Scan & Answer' to detect a quiz and generate answer")
        self.label.pack(pady=10)

        self.answer_box = tk.Text(master, height=20, width=90, wrap=tk.WORD)
        self.answer_box.pack(pady=10)

        self.scan_button = tk.Button(master, text="📷 Scan & Answer", font=("Arial", 12), command=self.process_quiz)
        self.scan_button.pack(pady=10)

    def hide_window_offscreen(self):
        # Move window off visible screen (e.g., x= -2000, y= -2000)
        self.master.geometry('+{}+{}'.format(-2000, -2000))
        self.master.update()

    def restore_window(self):
        # Move window back to normal position (adjust as needed)
        self.master.geometry('+100+100')
        self.master.update()
        
    def process_quiz(self):
        self.answer_box.delete(1.0, tk.END)
        self.label.config(text="🖼 Capturing screen...")
        self.master.update()

       # Move GUI off-screen before screenshot
        self.hide_window_offscreen()
        time.sleep(0.5)  # Give time for window to move

        img = capture_screen()

        # Restore GUI window to visible area
        self.restore_window()

        question = extract_text(img)

        if not question:
            messagebox.showerror("Error", "No text detected. Try again.")
            self.label.config(text="No quiz found on screen.")
            return

        self.label.config(text="🧠 Asking Gemini...")
        self.master.update()

        answer = ask_gemini(question)

        self.label.config(text="✅ Answer generated below:")
        self.answer_box.insert(tk.END, answer)

if __name__ == "__main__":
    root = tk.Tk()
    app = QuizAssistantApp(root)
    root.mainloop()
