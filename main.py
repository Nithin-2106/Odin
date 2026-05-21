import pyautogui
import keyboard
import PIL.Image
import os
from datetime import datetime
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

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

def ask_gemini(image_path, question):
    image = PIL.Image.open(image_path)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[question, image]
    )
    print(f"Odin: {response.text}")

def capture_and_ask():
    image_path = capture_screen()
    question = input("Ask Odin: ")
    ask_gemini(image_path, question)

start_odin()
print("Press 's' to capture and ask. Press 'q' to quit.")

keyboard.add_hotkey('s', capture_and_ask)
keyboard.wait('q')