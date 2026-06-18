import json
import os

LAYOUT_DIR = os.path.join(os.path.dirname(__file__), "..", "config")
LAYOUT_PATH = os.path.join(LAYOUT_DIR, "layout.json")


def _resolve_path():
    return os.path.abspath(LAYOUT_PATH)


def load_layout(name):
    with open(_resolve_path(), "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get(name)


def load_all_layouts():
    path = _resolve_path()
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_layout(name, node):
    path = _resolve_path()
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    data[name] = node
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
