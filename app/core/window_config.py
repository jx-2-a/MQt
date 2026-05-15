import json
import os

CONFIG_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "config")
SETTINGS_PATH = os.path.join(CONFIG_DIR, "settings.json")


def _resolve_path():
    return os.path.abspath(SETTINGS_PATH)


def load_config():
    with open(_resolve_path(), "r", encoding="utf-8") as f:
        return json.load(f)


def save_config(data):
    with open(_resolve_path(), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def get_window_config(key):
    data = load_config()
    return data.get(key, {})


def update_window_config(key, geometry=None, opacity=None, frameless=None, title=None, background_color=None, layout=None):
    data = load_config()
    if key not in data:
        data[key] = {}
    section = data[key]
    if geometry is not None:
        section["geometry"] = geometry
    if opacity is not None:
        section["opacity"] = opacity
    if frameless is not None:
        section["frameless"] = frameless
    if title is not None:
        section["title"] = title
    if background_color is not None:
        section["background_color"] = background_color
    if layout is not None:
        section["layout"] = layout
    save_config(data)
