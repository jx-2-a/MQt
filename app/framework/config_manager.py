"""配置管理器 — 统一管理 config/ 目录下所有 JSON 配置文件的读写。

合并了原 window_config.py 和 layout_loader.py，参考 reference/json_manager.py 的路径语义设计。
"""
import json
import os

_CONFIG_DIR = os.path.join(os.path.dirname(__file__), "..", "config")

SETTINGS_PATH = os.path.join(_CONFIG_DIR, "settings.json")
LAYOUT_PATH = os.path.join(_CONFIG_DIR, "layout.json")
STYLES_PATH = os.path.join(_CONFIG_DIR, "styles.json")


def _config_dir():
    return os.path.abspath(_CONFIG_DIR)


# ── settings.json ─────────────────────────────────────────────

def load_config():
    with open(os.path.abspath(SETTINGS_PATH), "r", encoding="utf-8") as f:
        return json.load(f)


def save_config(data):
    with open(os.path.abspath(SETTINGS_PATH), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def get_window_config(key):
    data = load_config()
    return data.get(key, {})


def update_window_config(key, geometry=None, opacity=None, frameless=None, title=None,
                         background_image=None, background_image_scale=None,
                         border_radius=None, layout=None):
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
        section["title"] = title if title else None
    if background_image is not None:
        section["background_image"] = background_image if background_image else None
    if background_image_scale is not None:
        section["background_image_scale"] = background_image_scale if background_image_scale else None
    if border_radius is not None:
        section["border_radius"] = border_radius if border_radius else None
    if layout is not None:
        section["layout"] = layout if layout else None
    # 清除空值键
    section = {k: v for k, v in section.items() if v is not None}
    data[key] = section
    save_config(data)


# ── layout.json ───────────────────────────────────────────────

def load_layout(name):
    with open(os.path.abspath(LAYOUT_PATH), "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get(name)


def load_all_layouts():
    path = os.path.abspath(LAYOUT_PATH)
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_layout(name, node):
    path = os.path.abspath(LAYOUT_PATH)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    data[name] = node
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


# ── styles.json ───────────────────────────────────────────────

def load_styles():
    path = os.path.abspath(STYLES_PATH)
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_styles(data):
    path = os.path.abspath(STYLES_PATH)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
