import json
import os
from datetime import datetime

MEMORY_FILE = "memory.json"

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return []
    with open(MEMORY_FILE, "r") as f:
        return json.load(f)

def save_memory(content):
    memory = load_memory()
    entry = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "content": content
    }
    memory.append(entry)
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)
    print(f"[memory saved] {entry['time']}: {content[:60]}...")