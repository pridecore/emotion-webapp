import os
import json

DATA_FOLDER = "data"
FILENAME = "pending_confirmations.json"

def get_file_path():
    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)
    return os.path.join(DATA_FOLDER, FILENAME)

def load_pending_confirmations():
    file_path = os.path.join("data", "pending_confirmations.json")
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data
            else:
                return {}
    return {}

def save_pending_confirmations(data):
    path = get_file_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)