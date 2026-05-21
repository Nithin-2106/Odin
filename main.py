import pyautogui
import keyboard
import PIL.Image
import os
import tkinter as tk
import threading
from datetime import datetime
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# --- Overlay UI ---
class OdinOverlay:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Odin")
        self.root.geometry("400x150+1470+20")  # position: top-right corner
        self.root.attributes("-topmost", True)  # always on top
        self.root.attributes("-alpha", 0.9)     # slight transparency
        self.root.configure(bg="#1e1e1e")
        self.root.overrideredirect(True)        # no title bar

        self.label = tk.Label(
            self.root,
            text="Odin is watching...",
            wraplength=380,
            justify="left",
            fg="#00ff99",
            bg="#1e1e1e",
            font=("Consolas", 11),
            padx=10,
            pady=10
        )
        self.label.pack(fill="both", expand=True)

        # click and drag to move
        self.label.bind("<ButtonPress-1>", self.start_move)
        self.label.bind("<B1-Motion>", self.do_move)

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def do_move(self, event):
        dx = event.x - self.x
        dy = event.y - self.y
        x = self.root.winfo_x() + dx
        y = self.root.winfo_y() + dy
        self.root.geometry(f"+{x}+{y}")

    def update_text(self, text):
        self.label.config(text=text)

    def run(self):
        self.root.mainloop()


# --- Core Functions ---
def get_current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def capture_screen():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"capture_{timestamp}.png"
    screenshot = pyautogui.screenshot()
    screenshot.save(filename)
    return filename

def ask_gemini(image_path, question):
    overlay.update_text("Thinking...")
    image = PIL.Image.open(image_path)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[question, image]
    )
    overlay.update_text(response.text)
    # also print to terminal
    print(f"Odin: {response.text}")

def capture_and_ask():
    image_path = capture_screen()
    question = input("Ask Odin: ")
    threading.Thread(target=ask_gemini, args=(image_path, question)).start()


# --- Start ---
overlay = OdinOverlay()

print("Odin is watching...")
print("Press 's' to capture and ask. Press 'q' to quit.")

keyboard.add_hotkey('s', capture_and_ask)
threading.Thread(target=lambda: keyboard.wait('q'), daemon=True).start()

overlay.run()