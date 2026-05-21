import pyautogui
import keyboard
from datetime import datetime

def start_odin():
    print("Odin is watching...")

def get_current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def capture_screen():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"capture_{timestamp}.png"
    screenshot = pyautogui.screenshot()
    screenshot.save(filename)
    print(f"Screen captured: {filename}")
    return filename

print("Press 's' to capture screen. Press 'q' to quit.")
start_odin()

keyboard.add_hotkey('s', capture_screen)
keyboard.wait('q')