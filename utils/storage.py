import json
import os

DATA_FILE = "data/user_count.json"

def load_counts():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)
    
def save_counts(counts):
    with open(DATA_FILE, "w") as f:
        json.dump(counts, f, indent=4)