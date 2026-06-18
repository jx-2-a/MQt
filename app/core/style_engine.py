"""样式引擎：四级级联解析 → QSS 生成 → 动态应用。支持子控件选择器。"""
import json
import os
import re
import hashlib

from PyQt5.QtGui import QColor, QPainter
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt

_STYLES_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "styles.json")

# 内部类型名 → 真实 Qt 类名（子控件 ::pane ::section ::handle 等必须挂载到 Qt 类名上）
_QT_CLASS_FOR = {
    "VBox": "QWidget", "HBox": "QWidget", "Form": "QWidget", "Spacer": "QWidget",
    "HSplitter": "QSplitter", "VSplitter": "QSplitter",
    "TabWidget": "QWidget",
    "TreeView": "QTreeWidget", "ToolBar": "QToolBar",
    "Label": "QLabel", "Image": "QLabel",
    "Button": "QPushButton", "ComboBox": "QComboBox",
    "TextEdit": "QTextEdit", "LineEdit": "QLineEdit",
    "CheckBox": "QCheckBox", "SpinBox": "QSpinBox", "DoubleSpinBox": "QDoubleSpinBox",
    "GroupBox": "QGroupBox", "Slider": "QSlider", "ProgressBar": "QProgressBar",
    "DraggableLabel": "QWidget",
}


def color_to_qss(qcolor):
    """QColor → QSS 字符串，含透明度时返回 rgba() 格式，否则 #rrggbb。"""
    if qcolor.alpha() == 255:
        return qcolor.name()
    return f"rgba({qcolor.red()}, {qcolor.green()}, {qcolor.blue()}, {qcolor.alphaF():.2g})"


def parse_color(value):
    """解析颜色字符串 → QColor，兼容 #rgb/#rrggbb/#aarrggbb/rgba()/命名色。"""
    if not value:
        return None
    c = QColor(value)
    if c.isValid():
        return c
    import re
    m = re.match(r'rgba?\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*([\d.]+)\s*)?\)', value)
    if m:
        r, g, b = int(m.group(1)), int(m.group(2)), int(m.group(3))
        a = m.group(4)
        alpha = max(0, min(255, round(float(a) * 255))) if a else 255
        return QColor(r, g, b, alpha)
    return None

class ColorSwatch(QWidget):
    """颜色预览块 — paintEvent 直绘，绕过 QSS 渲染层，正确显示 rgba 半透明。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._color = None
        self.setFixedSize(36, 36)
        self.setAttribute(Qt.WA_StyledBackground, False)

    def set_color(self, color):
        self._color = color
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        w, h = self.width(), self.height()
        cell = w // 4
        for row in range(4):
            for col in range(4):
                c = QColor("#ffffff") if (row + col) % 2 == 0 else QColor("#cccccc")
                painter.fillRect(col * cell, row * cell, cell, cell, c)
        if self._color:
            painter.fillRect(0, 0, w, h, self._color)
        painter.setPen(QColor("#555555"))
        painter.drawRect(0, 0, w - 1, h - 1)
        painter.end()


# ── 属性 → QSS 映射（供各控件 apply_style 引用）────────────────
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


_HEX8 = re.compile(r'^#[0-9a-fA-F]{8}$')


def _sanitize_value(key, val):
    """对 QSS 属性值做修正：font_family 加引号、#AARRGGBB → rgba()。"""
    val_str = str(val)
    # Qt 5 QSS 不支持 #AARRGGBB，必须转为 rgba()
    if key in ("background_color", "color", "border", "border_top", "border_right",
               "border_bottom", "border_left", "selection_background_color",
               "selection_color"):
        if _HEX8.match(val_str):
            c = QColor(val_str)
            if c.isValid():
                return f"rgba({c.red()}, {c.green()}, {c.blue()}, {c.alphaF():.2g})"
    if key == "font_family" and " " in val_str and not val_str.startswith('"'):
        return f'"{val_str}"'
    return val_str


def props_to_qss(props, allowed_keys=None):
    """将样式属性 dict 转为 QSS 字符串（裸声明，无选择器）。

    allowed_keys: 可选的白名单集合，只输出这些 key 对应的 QSS。
    供各控件 apply_style() 调用。
    """
    if not props:
        return ""
    parts = []
    for key, qss_key in _ATTR_MAP.items():
        if allowed_keys is not None and key not in allowed_keys:
            continue
        val = props.get(key)
        if val:
            val = _sanitize_value(key, val)
            parts.append(f"{qss_key}: {val};")
    return "\n".join(parts)


# ── 控件子控件样式架构 ──────────────────────────────────────
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
        "#header_row": ["background_color", "border", "border_top", "border_right",
                        "border_bottom", "border_left", "border_radius",
                        "padding", "margin", "height", "min_height", "max_height"],
        "#content": ["background_color", "border", "border_top", "border_right",
                     "border_bottom", "border_left", "border_radius",
                     "padding", "margin", "height", "min_height", "max_height"],
    },
    "TreeView": {
        "_self": [],
        "::item": ["background_color", "color", "padding", "border", "border_radius", "height"],
        "::item:selected": ["background_color", "color", "border", "border_radius"],
        "::item:hover": ["background_color", "color", "border", "border_radius"],
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
        "::handle:horizontal": ["background_color", "border", "border_radius", "width", "margin"],
    },
    "VSplitter": {
        "_self": [],
        "::handle:vertical": ["background_color", "border", "border_radius", "height", "margin"],
    },

    # ── 无子控件的类型 ──
    "VBox": {"_self": ["background_color", "border", "border_radius"]},
    "HBox": {"_self": ["background_color", "border", "border_radius"]},
    "Spacer": {"_self": ["min_width", "min_height", "max_width", "max_height"]},
    "Image": {"_self": []},
    "DraggableLabel": {
        "_self": ["background_color", "border", "border_radius", "padding", "margin",
                  "font_family", "font_size", "color", "font_weight"],
        "#icon": ["background_color", "border_radius", "width", "height"],
        "#text": ["font_family", "font_size", "color", "font_weight", "font_style"],
    },
    "ToolBar": {
        "_self": [],
        "QToolButton": ["background_color", "color", "border", "border_radius", "padding",
                        "margin", "font_size", "font_weight", "min_width", "min_height"],
        "QToolButton:hover": ["background_color", "color", "border"],
        "QToolButton:pressed": ["background_color", "color"],
        "QToolButton:checked": ["background_color", "color", "border"],
    },
    "Label": {"_self": ["font_family", "font_size", "font_weight", "font_style", "color", "background_color"]},
    "Form": {"_self": []},
    "Button": {
        "_self": ["font_family", "font_size", "font_weight", "color",
                  "background_color", "border", "border_radius", "padding",
                  "width", "height", "min_width", "max_width", "min_height", "max_height"],
        "&:hover": ["background_color", "color", "border"],
        "&:pressed": ["background_color", "color", "border"],
    },
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
# VBox/HBox 是纯布局容器，只需盒模型属性
TYPE_PROPERTIES["VBox"] = ["background_color", "border", "border_radius"]
TYPE_PROPERTIES["HBox"] = ["background_color", "border", "border_radius"]
TYPE_PROPERTIES["Label"] = [
    "font_family", "font_size", "font_weight", "font_style",
    "color", "background_color",
    "border", "border_radius", "border_top", "border_right",
    "border_bottom", "border_left",
    "padding", "margin",
    "width", "height", "min_width", "max_width", "min_height", "max_height",
]

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
    has_sub_keys = any(k == "_self" or "::" in k or k.startswith("&") for k in d.keys())
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


def resolve_style(name, widget_type, window_key, flat=True, _styles=None):
    """四级级联合并：global → types[type] → windows[key] → widgets[name]。
    返回规范 dict-of-dicts: {"_self": {...}, "::pane": {...}, ...}
    flat=True 时仅返回 _self 属性 dict（向后兼容）。
    """
    styles = _styles if _styles is not None else load_styles()
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
        elif sub_key.startswith("&"):
            # &:hover / &:pressed — 控件自身的伪类
            selector = f"{base_selector}{sub_key[1:]}"
        elif sub_key.startswith("::"):
            # ::item / ::handle → 挂到纯 Qt 类名上（QTreeWidget::item）
            cls_name = base_selector.split("#")[0].split("[")[0].strip()
            selector = f"{cls_name}{sub_key}" if cls_name else f"{base_selector}{sub_key}"
        elif "::" in sub_key:
            # QHeaderView::section — 已包含类名的子控件选择器，直接使用
            selector = sub_key
        else:
            # 后代子控件选择器（QToolButton, #tab_close_btn 等）
            selector = f"{base_selector} {sub_key}"

        parts = []
        for key, qss_key in _ATTR_MAP.items():
            val = props.get(key)
            if val:
                val = _sanitize_value(key, val)
                parts.append(f"    {qss_key}: {val};")
        if not parts:
            continue
        blocks.append(f"{selector} {{\n" + "\n".join(parts) + "\n}")
    return "\n".join(blocks)


def generate_widget_id(node_type, node_name, node_label, path):
    """生成控件标识符：优先使用 node['id']（稳定不变）。外部分调用时传入完整 node dict。"""
    if isinstance(node_type, dict):
        node = node_type
        nid = node.get("id", "")
        if nid:
            return nid
        node_name = node.get("name", "")
        node_label = node.get("label", "")
        if node_name:
            return node_name
        path = "0"
        node_type = node.get("type", "")
        raw = f"{path}|{node_type}|{node_label}"
        return "w" + hashlib.md5(raw.encode()).hexdigest()[:7]
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
    wid = generate_widget_id(node, node.get("name", ""), node.get("label", ""), path)
    result.append((wid, ntype))
    for i, child in enumerate(node.get("children", [])):
        _collect_recursive(child, f"{path}/{i}", result)


def _per_widget_qss(merged, widget_type, object_name=None, skip_self=False):
    """为单个控件生成 setStyleSheet 用的 QSS 字符串。

    _self 属性 → 裸声明（无选择器，直接作用于控件本身）
    ::xxx 子控件 → 带 Qt 类选择器（如 QSlider::handle {...}）
    &:xxx 伪类 → #objectName:xxx（控件自身的状态伪类）
    其他 key → 后代子控件选择器（如 QToolButton:hover）
    布局容器无显式背景色 → 自动补 transparent
    按控件类型 schema 过滤属性，不相关的不写入 QSS
    """
    if not merged:
        return ""
    cls = _QT_CLASS_FOR.get(widget_type, "QWidget")
    allowed = set(TYPE_PROPERTIES.get(widget_type, []))
    blocks = []

    if not skip_self:
        # _self → 裸声明（只输出该类型允许的属性）
        self_props = merged.get("_self", {})
        _BOX_TYPES = {"VBox", "HBox", "Form", "Spacer"}
        if widget_type in _BOX_TYPES:
            self_props = {k: v for k, v in self_props.items() if k != "background_color"}
        if self_props:
            parts = []
            for key, qss_key in _ATTR_MAP.items():
                if key not in allowed:
                    continue
                val = self_props.get(key)
                if val:
                    val = _sanitize_value(key, val)
                    parts.append(f"{qss_key}: {val};")
            if parts:
                blocks.append("\n".join(parts))

    # 子控件 / 伪类 → 带选择器
    for sub_key, props in merged.items():
        if sub_key == "_self" or not props:
            continue
        if sub_key.startswith("&"):
            # &:hover / &:pressed — 控件自身的伪类
            pseudo = sub_key[1:]  # 去掉 & 前缀
            if object_name:
                selector = f"{cls}#{object_name}{pseudo}"
            else:
                selector = f"{cls}{pseudo}"
        elif sub_key.startswith("::"):
            selector = f"{cls}{sub_key}"
        else:
            selector = sub_key
        parts = []
        for key, qss_key in _ATTR_MAP.items():
            val = props.get(key)
            if val:
                val = _sanitize_value(key, val)
                parts.append(f"    {qss_key}: {val};")
        if parts:
            blocks.append(f"{selector} {{\n" + "\n".join(parts) + "\n}")

    return "\n".join(blocks)


def subcontrol_display_name(sub_key, widget_type=None):
    """将子控件 key 转为用户可读的显示名。
    _self   → Qt 类名（如 QPushButton）
    &:hover → 悬停 (:hover)
    ::handle → 把手 (::handle)
    """
    if sub_key == "_self":
        return _QT_CLASS_FOR.get(widget_type, "QWidget") if widget_type else "自身"
    if sub_key.startswith("&"):
        pseudo = sub_key[1:]
        labels = {
            ":hover": "悬停 (:hover)",
            ":pressed": "按下 (:pressed)",
            ":checked": "选中 (:checked)",
            ":disabled": "禁用 (:disabled)",
            ":focus": "聚焦 (:focus)",
        }
        return labels.get(pseudo, f"状态 {pseudo}")
    if sub_key.startswith("::"):
        labels = {
            "::handle:horizontal": "把手 (::handle:horizontal)",
            "::handle:vertical": "把手 (::handle:vertical)",
            "::groove:horizontal": "滑槽 (::groove:horizontal)",
            "::groove:vertical": "滑槽 (::groove:vertical)",
            "::sub-page:horizontal": "已填充 (::sub-page:horizontal)",
            "::sub-page:vertical": "已填充 (::sub-page:vertical)",
            "::up-button": "上箭头 (::up-button)",
            "::down-button": "下箭头 (::down-button)",
            "::drop-down": "下拉箭头 (::drop-down)",
            "::indicator": "指示器 (::indicator)",
            "::indicator:checked": "指示器-选中 (::indicator:checked)",
            "::title": "标题 (::title)",
            "::item": "项 (::item)",
            "::item:selected": "项-选中 (::item:selected)",
            "::item:hover": "项-悬停 (::item:hover)",
            "::branch": "展开分支 (::branch)",
            "::chunk": "进度块 (::chunk)",
        }
        return labels.get(sub_key, f"子控件 {sub_key}")
    return sub_key


def cascade_apply_styles(root_widget, styles=None):
    """收集所有命名控件的样式，统一应用到根控件。

    Qt 的关键约束：伪类选择器（:hover, :pressed）只有在父级样式表中才能
    正确匹配子控件。直接设置在控件自身的 setStyleSheet() 中无效。
    因此：
      1. apply_style() 仅用于副作用（圆角遮罩、容器背景色缓存等）
      2. 所有 QSS（含 _self 和伪类/子控件选择器）统一汇集到 root_widget
    """
    from PyQt5.QtWidgets import QWidget

    styles = styles if styles is not None else load_styles()

    # 收集所有命名控件（含 root 自身）
    widgets = []
    lt = root_widget.property("layout_type")
    if lt and root_widget.objectName():
        widgets.append(root_widget)
    for child in root_widget.findChildren(QWidget):
        if child.objectName() and child.property("layout_type"):
            widgets.append(child)

    all_qss_blocks = []
    for w in widgets:
        name = w.objectName()
        lt = w.property("layout_type")
        merged_full = resolve_style(name, lt, None, flat=False, _styles=styles)
        self_props = merged_full.get("_self", {}) if merged_full else {}

        # apply_style 处理副作用（圆角遮罩等）
        if hasattr(w, "apply_style"):
            w.apply_style(self_props if self_props else None)

        # 清除控件自有的样式表，让根样式表规则可以级联匹配
        w.setStyleSheet("")

        # 生成带完整选择器的 QSS（含 _self 和伪类/子控件）
        # ::handle:* 子控件由 _apply_splitter_handle_styles 直接应用
        # QHeaderView::section 由 _apply_header_section_styles 直接应用
        # 不在此处输出，避免冲突。
        if merged_full:
            cls = _QT_CLASS_FOR.get(lt, "QWidget")
            if lt in ("HSplitter", "VSplitter"):
                merged_full = {k: v for k, v in merged_full.items()
                               if not k.startswith("::handle")}
            if lt == "TreeView":
                merged_full = {k: v for k, v in merged_full.items()
                               if k != "QHeaderView::section"}
            qss = style_to_qss(merged_full, f"{cls}#{name}")
            if qss:
                all_qss_blocks.append(qss)

    # 所有 QSS 统一设置到根控件，确保伪类选择器生效
    if all_qss_blocks:
        root_widget.setStyleSheet("\n".join(all_qss_blocks))

    # 确保内部子控件启用 QSS 背景
    from app.core.layout_engine import _propagate_styled_bg
    _propagate_styled_bg(root_widget)

    # Splitter 把手 + 表头 section + 透明穿透
    _apply_splitter_handle_styles(root_widget.window(), None, styles)
    _apply_header_section_styles(root_widget, styles)
    _apply_transparency_hints(root_widget.window(), None, styles)


def apply_to_widget(window, window_key, _styles=None):
    """对窗口内所有控件递归应用样式（cascade_apply_styles 封装）。"""
    cw = window.centralWidget()
    if cw is not None:
        cascade_apply_styles(cw, _styles)


def _apply_splitter_handle_styles(window, window_key, styles):
    """将 splitter 把手样式直接应用到 QSplitterHandle 控件。

    Qt 的 ::handle 伪元素选择器需要类型级选择器（如 QSplitter::handle），
    而我们的类型名（HSplitter/VSplitter）不是真实 Qt 类名，ID 选择器
    （#id::handle）也不可靠。直接在 QSplitterHandle 上 setStyleSheet 最稳妥。

    QSplitterHandle 的粗细由 QSplitter.handleWidth() 控制，QSS width/height
    不一定能覆盖，因此同时调用 setHandleWidth()。

    关键：root_widget.setStyleSheet() 会触发全局 re-polish，导致 QSplitter
    把 handleWidth 重置为样式默认值。因此 setHandleWidth 必须在所有
    QSS 处理完毕后延迟执行（QTimer.singleShot(0, ...)）。
    """
    from PyQt5.QtWidgets import QSplitter, QSplitterHandle
    from PyQt5.QtCore import Qt as QtCore, QTimer

    for splitter in window.findChildren(QSplitter):
        name = splitter.objectName()
        lt = splitter.property("layout_type") or "VSplitter"
        merged = resolve_style(name, lt, window_key, flat=False, _styles=styles)
        if not merged:
            continue

        # 根据 splitter 朝向确定对应的 handle 子控件 key
        # Qt QSS: :horizontal/:vertical 指 splitter 本身的朝向，不是把手形状
        if splitter.orientation() == QtCore.Horizontal:
            handle_key = "::handle:horizontal"
            size_key = "width"
        else:
            handle_key = "::handle:vertical"
            size_key = "height"

        handle_props = merged.get(handle_key, {})
        if not handle_props:
            continue

        # QSS 仅负责颜色/边框等视觉效果，不含 width/height
        visual_props = {k: v for k, v in handle_props.items() if k not in ("width", "height")}
        qss = style_to_qss({"_self": visual_props}, "QSplitterHandle")
        if qss:
            for i in range(splitter.count()):
                handle = splitter.handle(i)
                if isinstance(handle, QSplitterHandle):
                    handle.setStyleSheet(qss)
                    handle.setAttribute(QtCore.WA_StyledBackground, True)

        # 把手粗细 = setHandleWidth + 固定尺寸，双保险对抗 QSS re-polish 重置
        size_val = handle_props.get(size_key, "")
        if size_val:
            val = int(re.sub(r"[^\d.]", "", str(size_val)) or 0)
            actual_val = val
            splitter.setHandleWidth(actual_val)
            # 直接固定 QSplitterHandle 的对应尺寸
            for i in range(splitter.count()):
                h = splitter.handle(i)
                if isinstance(h, QSplitterHandle):
                    if splitter.orientation() == QtCore.Horizontal:
                        h.setFixedWidth(actual_val)
                    else:
                        h.setFixedHeight(actual_val)
            # 延迟再设，覆盖 QSS re-polish 的副作用
            def _defer(s=splitter, v=actual_val, sk=size_key):
                try:
                    s.setHandleWidth(v)
                    for i in range(s.count()):
                        h = s.handle(i)
                        if isinstance(h, QSplitterHandle):
                            if sk == "width":
                                h.setFixedWidth(v)
                            else:
                                h.setFixedHeight(v)
                except RuntimeError:
                    pass  # widget 已销毁
            QTimer.singleShot(0, _defer)


def _apply_header_section_styles(root_widget, styles):
    """将 QHeaderView::section QSS 直接应用到 QHeaderView 控件。

    Qt5 的 QSS 引擎对后代+子控件组合选择器（QTreeWidget#id QHeaderView::section）
    匹配不可靠，必须把 ::section 样式直接设到 QHeaderView 自身才能稳定生效。
    """
    from PyQt5.QtWidgets import QHeaderView, QTreeWidget

    styles = styles if styles is not None else load_styles()
    types_cfg = styles.get("types", {})

    for tree in root_widget.findChildren(QTreeWidget):
        name = tree.objectName()
        if not name:
            continue

        # 按 resolve_style 的级联规则收集 QHeaderView::section 样式
        merged = resolve_style(name, "TreeView", None, flat=False, _styles=styles)
        section_props = merged.get("QHeaderView::section", {})
        if not section_props:
            continue

        qss = style_to_qss({"QHeaderView::section": section_props}, "QHeaderView")
        if qss:
            header = tree.header()
            header.setStyleSheet(qss)
            header.setAttribute(Qt.WA_StyledBackground, True)


def _apply_transparency_hints(window, window_key, styles):
    """仅对背景透明或半透明的控件设置 WA_TranslucentBackground。

    该属性让 Qt 不填充控件默认背景，使父控件/背景层的内容可穿透显示。
    """
    from PyQt5.QtWidgets import QWidget
    from PyQt5.QtCore import Qt
    import re

    _transparent_rgx = re.compile(r"^rgba\([^)]+\)$")

    def _is_transparent(bg):
        if not bg:
            return False
        return bg == "transparent" or bg == "none" or bool(_transparent_rgx.match(bg))

    _BOX_TYPES = {"VBox", "HBox", "Form", "Spacer"}

    for child in window.findChildren(QWidget):
        lt = child.property("layout_type")
        if not lt:
            continue

        # VBox/HBox 使用 paintEvent 直绘背景，必须始终启用半透明穿透
        if lt in _BOX_TYPES:
            child.setAttribute(Qt.WA_TranslucentBackground, True)
            continue

        name = child.objectName()
        merged = resolve_style(name, lt, window_key, flat=True, _styles=styles)
        bg = merged.get("background_color", "")
        if not bg:
            continue

        if _is_transparent(bg):
            child.setAttribute(Qt.WA_TranslucentBackground, True)
            # QAbstractScrollArea（TextEdit 等）的 viewport 需额外启用透明
            from PyQt5.QtWidgets import QAbstractScrollArea
            if isinstance(child, QAbstractScrollArea):
                vp = child.viewport()
                if vp:
                    vp.setAttribute(Qt.WA_StyledBackground, True)
                    vp.setAttribute(Qt.WA_TranslucentBackground, True)
                    vp.setAutoFillBackground(False)
        else:
            child.setAttribute(Qt.WA_TranslucentBackground, False)


def update_live(window, window_key, _styles=None):
    apply_to_widget(window, window_key, _styles)
