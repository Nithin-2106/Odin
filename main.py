import pyautogui
import keyboard
import PIL.Image
import os
import tkinter as tk
import threading
import time
from datetime import datetime
from dotenv import load_dotenv
from google import genai
from memory import save_memory, load_memory

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

class OdinOverlay:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Odin")
        self.root.geometry("360x520+1530+20")
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.96)
        self.root.configure(bg="#0f0f0f")
        self.root.overrideredirect(True)
        self.root.withdraw()  # start hidden

        self.visible = False

        # --- Title bar ---
        self.titlebar = tk.Frame(self.root, bg="#141414", height=40)
        self.titlebar.pack(fill="x")
        self.titlebar.pack_propagate(False)

        self.brand = tk.Label(
            self.titlebar, text="⬡ ODIN",
            fg="#00e87a", bg="#141414",
            font=("Consolas", 11, "bold"), padx=14
        )
        self.brand.pack(side="left", pady=8)

        self.status_label = tk.Label(
            self.titlebar, text="watching",
            fg="#444444", bg="#141414",
            font=("Consolas", 9)
        )
        self.status_label.pack(side="right", padx=14)

        self.close_btn = tk.Button(
            self.titlebar, text="✕",
            fg="#555555", bg="#141414",
            relief="flat", font=("Consolas", 11),
            activebackground="#141414", activeforeground="#ff5f57",
            command=self.hide, cursor="hand2", bd=0
        )
        self.close_btn.pack(side="right", padx=4)

        # divider
        tk.Frame(self.root, bg="#222222", height=1).pack(fill="x")

        # --- Messages area ---
        self.msg_frame = tk.Frame(self.root, bg="#0f0f0f")
        self.msg_frame.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(self.msg_frame, bg="#0f0f0f", highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.msg_frame, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        # scrollbar hidden but functional
        self.canvas.bind("<Enter>", self._bind_mousewheel)
        self.canvas.bind("<Leave>", self._unbind_mousewheel)

        self.messages_inner = tk.Frame(self.canvas, bg="#0f0f0f")
        self.canvas_window = self.canvas.create_window((0, 0), window=self.messages_inner, anchor="nw")

        self.messages_inner.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        # --- Input area ---
        tk.Frame(self.root, bg="#222222", height=1).pack(fill="x")

        self.input_area = tk.Frame(self.root, bg="#141414", pady=8)
        self.input_area.pack(fill="x", padx=12)

        self.input_box = tk.Entry(
            self.input_area,
            fg="#cccccc", bg="#1e1e1e",
            font=("Consolas", 11),
            relief="flat",
            insertbackground="#00e87a",
            bd=0
        )
        self.input_box.pack(side="left", fill="x", expand=True, ipady=7, padx=(0, 8))
        self.input_box.insert(0, "Ask Odin...")
        self.input_box.config(fg="#444444")
        self.input_box.bind("<FocusIn>", self._clear_placeholder)
        self.input_box.bind("<FocusOut>", self._restore_placeholder)
        self.input_box.bind("<Return>", self._on_submit)

        self.send_btn = tk.Button(
            self.input_area, text="↑",
            fg="#0a0a0a", bg="#00e87a",
            font=("Consolas", 13, "bold"),
            relief="flat", bd=0,
            activebackground="#00cc6a",
            cursor="hand2",
            width=3,
            command=lambda: self._on_submit(None)
        )
        self.send_btn.pack(side="right", ipady=4)

        tk.Frame(self.root, bg="#141414", height=8).pack(fill="x")

        # drag
        for w in [self.titlebar, self.brand, self.status_label]:
            w.bind("<ButtonPress-1>", self._start_move)
            w.bind("<B1-Motion>", self._do_move)

        # add welcome message
        self.add_message("Hey. I'm watching your screen.\nAsk me anything about what's on it.", sender="odin")

    def _on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _bind_mousewheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbind_mousewheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")

    def _clear_placeholder(self, event):
        if self.input_box.get() == "Ask Odin...":
            self.input_box.delete(0, tk.END)
            self.input_box.config(fg="#cccccc")

    def _restore_placeholder(self, event):
        if self.input_box.get() == "":
            self.input_box.insert(0, "Ask Odin...")
            self.input_box.config(fg="#444444")

    def add_message(self, text, sender="odin"):
        bubble_color = "#1a1a1a" if sender == "odin" else "#00e87a"
        text_color = "#d4d4d4" if sender == "odin" else "#0a0a0a"
        anchor = "w" if sender == "odin" else "e"
        sender_text = "ODIN" if sender == "odin" else "you"
        sender_color = "#00e87a" if sender == "odin" else "#666666"
        padx = (10, 40) if sender == "odin" else (40, 10)

        row = tk.Frame(self.messages_inner, bg="#0f0f0f")
        row.pack(fill="x", pady=(4, 0), padx=8)

        sender_label = tk.Label(
            row, text=sender_text,
            fg=sender_color, bg="#0f0f0f",
            font=("Consolas", 8)
        )
        sender_label.pack(anchor=anchor, padx=padx[0] if sender == "odin" else padx[1])

        bubble = tk.Label(
            row, text=text,
            fg=text_color, bg=bubble_color,
            font=("Consolas", 10),
            wraplength=240,
            justify="left" if sender == "odin" else "right",
            padx=12, pady=8
        )
        bubble.pack(anchor=anchor, padx=padx[0] if sender == "odin" else padx[1], pady=(2, 6))

        self.root.after(50, lambda: self.canvas.yview_moveto(1.0))

    def set_thinking(self):
        self.status_label.config(text="thinking...")
        self.add_message("...", sender="odin")

    def update_last_message(self, text):
        self.status_label.config(text="watching")
        # remove last bubble and replace
        frames = self.messages_inner.winfo_children()
        if frames:
            frames[-1].destroy()
        self.add_message(text, sender="odin")

    def show(self):
        self.visible = True
        self.root.deiconify()
        self.root.lift()
        self.root.after(100, lambda: self.input_box.focus_set())

    def hide(self):
        self.visible = False
        self.root.withdraw()

    def toggle(self):
        if self.visible:
            self.hide()
        else:
            self.show()

    def _start_move(self, event):
        self.x = event.x
        self.y = event.y

    def _do_move(self, event):
        dx = event.x - self.x
        dy = event.y - self.y
        x = self.root.winfo_x() + dx
        y = self.root.winfo_y() + dy
        self.root.geometry(f"+{x}+{y}")

    def _on_submit(self, event):
        question = self.input_box.get().strip()
        if not question or question == "Ask Odin...":
            return
        self.input_box.delete(0, tk.END)
        self.input_box.config(fg="#444444")
        self.input_box.insert(0, "Ask Odin...")
        self.add_message(question, sender="user")
        self.set_thinking()
        threading.Thread(target=self._process, args=(question,), daemon=True).start()

    def _process(self, question):
        image_path = capture_screen()
        ask_gemini(image_path, question)

    def run(self):
        self.root.mainloop()


def capture_screen():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"capture_{timestamp}.png"
    screenshot = pyautogui.screenshot()
    screenshot.save(filename)
    return filename

def ask_gemini(image_path, question):
    image = PIL.Image.open(image_path)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[question, image]
    )
    overlay.update_last_message(response.text)
    print(f"Odin: {response.text}")

def background_capture():
    while True:
        try:
            image_path = capture_screen()
            image = PIL.Image.open(image_path)
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=["Describe what is happening on this screen in 2-3 sentences. Be concise.", image]
            )
            save_memory(response.text)
            os.remove(image_path)
        except Exception as e:
            print(f"[memory error] {e}")
        time.sleep(30)
overlay = OdinOverlay()

print("Odin is watching. Press Ctrl+Space to open/close. Press Ctrl+Q to quit.")
keyboard.add_hotkey('ctrl+space', overlay.toggle)
keyboard.add_hotkey('ctrl+q', lambda: os._exit(0))

threading.Thread(target=background_capture, daemon=True).start()

overlay.run()