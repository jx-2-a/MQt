"""样式引擎：四级级联解析 → QSS 生成 → 动态应用。支持子控件选择器。"""
import json
import os
import hashlib

_STYLES_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "config", "styles.json")

# 属性 → QSS 属性名映射
_ATTR_MAP = {
    "font_family": "font-family",
    "font_size": "font-size",
    "font_weight": "font-weight",
    "font_style": "font-style",
    "color": "color",
    "background_color": "background-color",
    "border": "border",
    "border_radius": "border-radius",
    "border_top": "border-top",
    "border_right": "border-right",
    "border_bottom": "border-bottom",
    "border_left": "border-left",
    "padding": "padding",
    "margin": "margin",
    "min_width": "min-width",
    "max_width": "max-width",
    "min_height": "min-height",
    "max_height": "max-height",
    "width": "width",
    "height": "height",
    # 子控件专用属性
    "selection_background_color": "selection-background-color",
    "selection_color": "selection-color",
    "outline": "outline",
    "text_align": "text-align",
    "subcontrol_origin": "subcontrol-origin",
    "subcontrol_position": "subcontrol-position",
    "spacing": "spacing",
}

# ── 子控件样式架构 ──────────────────────────────────────────
# 每个控件类型的 schema 为 dict: {"_self": [...], "::sub": [...], "QXxx::yy": [...]}
# _self 是控件本身的属性（即原来的 20 个通用属性）
# 子控件 key 以 :: 开头的是伪元素，否则是后代子控件选择器

_COMMON_SELF = [
    "font_family", "font_size", "font_weight", "font_style",
    "color", "background_color",
    "border", "border_radius", "border_top", "border_right",
    "border_bottom", "border_left",
    "padding", "margin",
    "width", "height", "min_width", "max_width", "min_height", "max_height",
]

WIDGET_STYLE_SCHEMA = {
    "common": {"_self": _COMMON_SELF},

    # ── 含子控件的类型 ──
    "TabWidget": {
        "_self": [],
        "::pane": ["background_color", "border", "border_radius", "padding", "margin",
                   "border_top", "border_right", "border_bottom", "border_left"],
        "QTabBar::tab": ["background_color", "color", "font_weight", "font_size", "padding",
                         "border", "border_radius", "margin", "min_width", "min_height",
                         "border_bottom", "border_top", "border_left", "border_right"],
        "QTabBar::tab:selected": ["background_color", "color", "font_weight", "border", "border_bottom"],
        "QTabBar::tab:hover": ["background_color", "color"],
    },
    "TreeView": {
        "_self": [],
        "::item": ["background_color", "color", "padding", "border", "height"],
        "::item:selected": ["background_color", "color"],
        "::item:hover": ["background_color"],
        "::branch": ["background_color"],
        "QHeaderView::section": ["background_color", "color", "border", "border_right",
                                  "border_bottom", "padding", "font_size", "font_weight"],
    },
    "Slider": {
        "_self": [],
        "::groove:horizontal": ["background_color", "border", "border_radius", "height"],
        "::groove:vertical": ["background_color", "border", "border_radius", "width"],
        "::handle:horizontal": ["background_color", "border", "border_radius", "width", "margin"],
        "::handle:vertical": ["background_color", "border", "border_radius", "height", "margin"],
        "::sub-page:horizontal": ["background_color", "border_radius"],
        "::sub-page:vertical": ["background_color", "border_radius"],
    },
    "ProgressBar": {
        "_self": ["text_align"],
        "::chunk": ["background_color", "border", "border_radius", "width"],
    },
    "ComboBox": {
        "_self": [],
        "::drop-down": ["border", "width", "background_color", "padding", "margin"],
        "QAbstractItemView::item": ["background_color", "color", "selection_background_color",
                                     "selection_color", "border", "outline", "padding"],
        "QAbstractItemView::item:selected": ["background_color", "color"],
    },
    "SpinBox": {
        "_self": [],
        "::up-button": ["background_color", "border", "border_radius", "width", "height", "padding"],
        "::down-button": ["background_color", "border", "border_radius", "width", "height", "padding"],
    },
    "DoubleSpinBox": {
        "_self": [],
        "::up-button": ["background_color", "border", "border_radius", "width", "height", "padding"],
        "::down-button": ["background_color", "border", "border_radius", "width", "height", "padding"],
    },
    "CheckBox": {
        "_self": ["spacing"],
        "::indicator": ["width", "height", "border", "border_radius", "background_color"],
        "::indicator:checked": ["background_color", "border"],
    },
    "GroupBox": {
        "_self": [],
        "::title": ["subcontrol_origin", "subcontrol_position", "padding", "color", "background_color"],
    },
    "HSplitter": {
        "_self": [],
        "::handle:horizontal": ["background_color", "width"],
        "::handle:vertical": ["background_color", "height"],
    },
    "VSplitter": {
        "_self": [],
        "::handle:horizontal": ["background_color", "width"],
        "::handle:vertical": ["background_color", "height"],
    },

    # ── 无子控件的类型 ──
    "VBox": {"_self": []},
    "HBox": {"_self": []},
    "Spacer": {"_self": ["min_width", "min_height", "max_width", "max_height"]},
    "ToolBar": {
        "_self": [],
        "QToolButton": ["background_color", "color", "border", "border_radius", "padding",
                        "margin", "font_size", "font_weight", "min_width", "min_height"],
        "QToolButton:hover": ["background_color", "color", "border"],
        "QToolButton:pressed": ["background_color", "color"],
        "QToolButton:checked": ["background_color", "color", "border"],
    },
    "Label": {"_self": []},
    "Form": {"_self": []},
    "Button": {"_self": []},
    "TextEdit": {"_self": []},
    "LineEdit": {"_self": []},
}

# 子控件列表查询表
SUB_CONTROLS_OF = {}
for _tname, _sc_defs in WIDGET_STYLE_SCHEMA.items():
    if _tname != "common":
        SUB_CONTROLS_OF[_tname] = list(_sc_defs.keys())


def _build_type_props():
    common_self = WIDGET_STYLE_SCHEMA.get("common", {}).get("_self", [])
    result = {}
    for tname, sc_defs in WIDGET_STYLE_SCHEMA.items():
        if tname == "common":
            continue
        result[tname] = common_self + sc_defs.get("_self", [])
    return result


TYPE_PROPERTIES = _build_type_props()

# 属性分组（供 UI 按组展示）
PROPERTY_GROUPS = [
    ("字体", ["font_family", "font_size", "font_weight", "font_style"]),
    ("颜色与背景", ["color", "background_color", "selection_color", "selection_background_color"]),
    ("边框", ["border", "border_top", "border_right", "border_bottom", "border_left", "border_radius", "outline"]),
    ("尺寸", ["width", "height", "min_width", "max_width", "min_height", "max_height"]),
    ("间距", ["padding", "margin", "spacing"]),
    ("布局", ["text_align", "subcontrol_origin", "subcontrol_position"]),
]


def _normalize_style_dict(d):
    """将旧格式 {prop: val} 或新格式 {'_self': {...}, '::sub': {...}} 统一为规范形式。"""
    if not d:
        return {}
    has_sub_keys = any(k == "_self" or "::" in k for k in d.keys())
    if has_sub_keys:
        return d
    return {"_self": d}


def load_styles():
    if not os.path.exists(_STYLES_PATH):
        return {"global": {}, "types": {}, "windows": {}, "widgets": {}}
    with open(_STYLES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_styles(data):
    os.makedirs(os.path.dirname(_STYLES_PATH), exist_ok=True)
    with open(_STYLES_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def resolve_style(name, widget_type, window_key, flat=True):
    """四级级联合并：global → types[type] → windows[key] → widgets[name]。
    返回规范 dict-of-dicts: {"_self": {...}, "::pane": {...}, ...}
    flat=True 时仅返回 _self 属性 dict（向后兼容）。
    """
    styles = load_styles()
    sources = [
        _normalize_style_dict(styles.get("global", {})),
    ]
    if widget_type:
        sources.append(_normalize_style_dict(
            styles.get("types", {}).get(widget_type, {})
        ))
    if window_key:
        sources.append(_normalize_style_dict(
            styles.get("windows", {}).get(window_key, {})
        ))
    if name:
        sources.append(_normalize_style_dict(
            styles.get("widgets", {}).get(name, {})
        ))

    # 按 sub-control key 逐级合并
    merged = {}
    all_sub_keys = set()
    for src in sources:
        all_sub_keys.update(src.keys())

    for sub_key in sorted(all_sub_keys):
        sub_merged = {}
        for src in sources:
            sub_merged.update(src.get(sub_key, {}))
        if sub_merged:
            merged[sub_key] = sub_merged

    if flat:
        return merged.get("_self", {})
    return merged


def style_to_qss(style_dict, base_selector):
    """将规范 sub-control dict 转为 QSS 字符串。
    也接受 flat dict（向后兼容），自动包装为 {"_self": {...}}。
    """
    if not style_dict:
        return ""
    style_dict = _normalize_style_dict(style_dict)
    blocks = []
    for sub_key, props in style_dict.items():
        if not props:
            continue
        # 构造选择器
        if sub_key == "_self":
            selector = base_selector
        elif sub_key.startswith("::"):
            selector = f"{base_selector}{sub_key}"
        else:
            selector = f"{base_selector} {sub_key}"

        parts = []
        for key, qss_key in _ATTR_MAP.items():
            val = props.get(key)
            if val:
                parts.append(f"    {qss_key}: {val};")
        if not parts:
            continue
        blocks.append(f"{selector} {{\n" + "\n".join(parts) + "\n}")
    return "\n".join(blocks)


def generate_widget_id(node_type, node_name, node_label, path):
    if node_name:
        return node_name
    raw = f"{path}|{node_type}|{node_label}"
    return "w" + hashlib.md5(raw.encode()).hexdigest()[:7]


def collect_layout_widgets(root_node):
    result = []
    _collect_recursive(root_node, "0", result)
    return result


def _collect_recursive(node, path, result):
    ntype = node.get("type", "")
    if not ntype:
        return
    wid = generate_widget_id(ntype, node.get("name", ""), node.get("label", ""), path)
    result.append((wid, ntype))
    for i, child in enumerate(node.get("children", [])):
        _collect_recursive(child, f"{path}/{i}", result)


def apply_to_widget(window, window_key, _styles=None):
    """生成组合 QSS 并一次性应用到窗口。
    三阶段：
    1. 全局 * + 子控件
    2. 类型级裸选择器（仅子控件，不含 _self）
    3. 控件级 #id + 完整级联
    """
    from PyQt5.QtWidgets import QWidget

    styles = _styles if _styles is not None else load_styles()
    qss_blocks = []

    # 1. 全局样式
    global_style = _normalize_style_dict(styles.get("global", {}))
    if global_style:
        qss_blocks.append(style_to_qss(global_style, "*"))

    # 2. 窗口级样式
    win_style = _normalize_style_dict(styles.get("windows", {}).get(window_key, {}))
    if win_style:
        qss_blocks.append(style_to_qss(win_style, "QMainWindow"))

    # 3. 类型级子控件选择器（不带 #id，影响所有该类型控件）
    types_styles = styles.get("types", {})
    for tname, raw in types_styles.items():
        sc_dict = _normalize_style_dict(raw)
        sub_only = {k: v for k, v in sc_dict.items() if k != "_self"}
        if sub_only:
            qss_blocks.append(style_to_qss(sub_only, tname))

    # 4. 控件级 #id 选择器（完整级联：global+type+window+widget）
    processed = set()
    for child in window.findChildren(QWidget):
        name = child.objectName()
        if not name or name in processed:
            continue
        processed.add(name)
        lt = child.property("layout_type") or type(child).__name__
        merged = resolve_style(name, lt, window_key, flat=False)
        if merged:
            qss = style_to_qss(merged, f"#{name}")
            if qss:
                qss_blocks.append(qss)

    # 5. 补充 styles.json 中有但窗口树中未出现的控件实例
    widget_styles = styles.get("widgets", {})
    for name in widget_styles:
        if name not in processed:
            merged = resolve_style(name, None, window_key, flat=False)
            qss = style_to_qss(merged, f"#{name}")
            if qss:
                qss_blocks.append(qss)

    combined = "\n".join(qss_blocks)
    window.setStyleSheet(combined)


def update_live(window, window_key, _styles=None):
    apply_to_widget(window, window_key, _styles)
