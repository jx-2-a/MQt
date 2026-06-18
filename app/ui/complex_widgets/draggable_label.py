from PyQt5.QtWidgets import QLabel, QHBoxLayout, QSizePolicy
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QPoint, pyqtSignal
from ..widgets.composite import CompositeWidget
from ..widgets.image import _resolve_path


# ── 样式属性 → QSS 属性名映射 ──────────────────────
_STYLE_ATTR_MAP = {
    "font_family":     "font-family",
    "font_size":       "font-size",
    "font_weight":     "font-weight",
    "font_style":      "font-style",
    "color":           "color",
    "background_color": "background-color",
    "border":          "border",
    "border_radius":   "border-radius",
    "border_top":      "border-top",
    "border_right":    "border-right",
    "border_bottom":   "border-bottom",
    "border_left":     "border-left",
    "padding":         "padding",
    "margin":          "margin",
    "min_width":       "min-width",
    "max_width":       "max-width",
    "min_height":      "min-height",
    "max_height":      "max-height",
    "width":           "width",
    "height":          "height",
}


def _style_to_qss(style_dict):
    """样式 dict → QSS 声明块（不含选择器花括号）。"""
    if not style_dict:
        return ""
    parts = []
    for key, qss_key in _STYLE_ATTR_MAP.items():
        val = style_dict.get(key)
        if val:
            parts.append(f"    {qss_key}: {val};")
    return "\n".join(parts)


# ── 默认模板（Python 硬编码 — 稳定性基线）───────────

DEFAULT_TEMPLATE = {
    "icon": {
        "src": "", "width": 24, "height": 24, "visible": False,
        "style": {
            "background_color": "transparent",
            "border_radius": "2px",
        },
    },
    "text": {
        "content": "", "visible": True,
        "style": {
            "font_family":  "Microsoft YaHei",
            "font_size":    "14px",
            "color":        "#cccccc",
            "font_weight":  "normal",
        },
    },
    "button": {"enabled": False},
    "drag":   {"enabled": True},
    "style": {
        "background_color": "#2d2d30",
        "border":           "1px solid #3e3e42",
        "border_radius":    "6px",
        "padding":          "4px 8px",
        "margin":           "2px",
    },
}


class DraggableLabel(CompositeWidget):
    """可拖拽复合标签 — 图标/文本/按钮可同时启用，硬编码默认样式 + 模板覆盖。

    样式优先级（低→高）:
        1. Python DEFAULT_TEMPLATE（硬编码，永不丢失）
        2. 构造时传入的 template 参数
        3. set_template() / update_template() 运行时更新

    每个样式层的 property 粒度合并，非全量替换。

    槽位:
        icon  — QLabel，图标区
        text  — QLabel，文本区

    信号:
        clicked — button.enabled=True 时，鼠标在控件范围内释放触发
    """

    clicked = pyqtSignal()

    def __init__(self, template=None, parent=None):
        self._drag_pos = None
        self._template = None
        super().__init__(parent)
        self.setProperty("_dl_root", True)  # 自引用选择器锚点
        self.set_template(template or {})

    # ── 内部布局 ─────────────────────────────────────

    def _build_layout(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        icon_label = QLabel()
        icon_label.setScaledContents(True)
        self._register_slot("icon", icon_label)
        layout.addWidget(icon_label)

        text_label = QLabel()
        text_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self._register_slot("text", text_label)
        layout.addWidget(text_label)

        layout.addStretch()

    # ── 模板系统 ─────────────────────────────────────

    def set_template(self, template):
        """应用完整模板 — 与 DEFAULT_TEMPLATE 合并，传入值覆盖默认值。"""
        self._template = {
            "icon":   _deep_merge(DEFAULT_TEMPLATE["icon"],   (template or {}).get("icon", {})),
            "text":   _deep_merge(DEFAULT_TEMPLATE["text"],   (template or {}).get("text", {})),
            "button": _deep_merge(DEFAULT_TEMPLATE["button"], (template or {}).get("button", {})),
            "drag":   _deep_merge(DEFAULT_TEMPLATE["drag"],   (template or {}).get("drag", {})),
            "style":  _deep_merge(DEFAULT_TEMPLATE["style"],  (template or {}).get("style", {})),
        }
        self._apply_template()

    def template(self):
        """返回当前模板深拷贝。"""
        return _deep_copy_template(self._template)

    def update_template(self, partial):
        """合并更新 — 只改传入的部分，其余保持。"""
        for section in ("icon", "text", "button", "drag", "style"):
            if section in partial:
                if section in ("button", "drag", "style"):
                    self._template[section].update(partial[section])
                else:
                    values = partial[section]
                    if "style" in values:
                        self._template[section]["style"].update(values.pop("style"))
                    self._template[section].update(values)
        self._apply_template()

    def _apply_template(self):
        t = self._template

        # ── 控件自身样式 ──
        qss = _style_to_qss(t.get("style", {}))
        if qss:
            self.setStyleSheet(f"QWidget[_dl_root=\"true\"] {{\n{qss}\n}}")
        else:
            self.setStyleSheet("")

        # ── 图标槽位 ──
        icon_cfg = t["icon"]
        self._apply_slot_style("icon", icon_cfg.get("style", {}))
        if icon_cfg.get("visible") and icon_cfg.get("src"):
            self._set_icon_internal(icon_cfg["src"], icon_cfg.get("width", 24), icon_cfg.get("height", 24))
        self.slot("icon").setVisible(bool(icon_cfg.get("visible") and icon_cfg.get("src")))

        # ── 文本槽位 ──
        text_cfg = t["text"]
        self._apply_slot_style("text", text_cfg.get("style", {}))
        if text_cfg.get("visible"):
            self.slot("text").setText(text_cfg.get("content", ""))
        self.slot("text").setVisible(bool(text_cfg.get("visible")))

        # ── 拖拽光标 ──
        drag_enabled = t.get("drag", {}).get("enabled", True)
        self.setCursor(Qt.OpenHandCursor if drag_enabled else Qt.ArrowCursor)

    def _apply_slot_style(self, slot_name, style_dict):
        """将样式 dict 转为 QSS 并应用到单个槽位。"""
        qss = _style_to_qss(style_dict)
        slot_widget = self.slot(slot_name)
        if qss:
            slot_widget.setStyleSheet(f"QLabel {{\n{qss}\n}}")
        else:
            slot_widget.setStyleSheet("")

    # ── 便捷 API ─────────────────────────────────────

    def set_text(self, text):
        self.update_template({"text": {"content": text, "visible": bool(text)}})

    def text(self):
        return self.slot("text").text()

    def set_icon(self, src, width=24, height=24):
        self.update_template({"icon": {"src": src, "width": width, "height": height, "visible": bool(src)}})

    def _set_icon_internal(self, src, width, height):
        path = _resolve_path(src)
        if path:
            pix = QPixmap(path).scaled(width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.slot("icon").setPixmap(pix)
            self.slot("icon").setFixedSize(width, height)

    def set_button_enabled(self, enabled):
        self.update_template({"button": {"enabled": enabled}})

    def is_button_enabled(self):
        return self._template.get("button", {}).get("enabled", False)

    def set_drag_enabled(self, enabled):
        self.update_template({"drag": {"enabled": enabled}})

    def is_drag_enabled(self):
        return self._template.get("drag", {}).get("enabled", True)

    # ── 拖拽事件 ─────────────────────────────────────

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self._template.get("drag", {}).get("enabled", True):
            self._drag_pos = event.globalPos() - self.window().frameGeometry().topLeft()
            self.setCursor(Qt.ClosedHandCursor)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._template.get("drag", {}).get("enabled", True) and self._drag_pos is not None:
            parent = self.parentWidget()
            if parent:
                local_pos = parent.mapFromGlobal(event.globalPos())
                ref_pos = parent.mapFromGlobal(
                    self._drag_pos + self.window().frameGeometry().topLeft()
                )
                target = self.mapToParent(self.pos()) + (local_pos - ref_pos)
                r = parent.rect()
                target.setX(max(0, min(target.x(), r.width() - self.width())))
                target.setY(max(0, min(target.y(), r.height() - self.height())))
            else:
                target = event.globalPos() - self._drag_pos
            self.move(target)
            self._drag_pos = event.globalPos() - self.window().frameGeometry().topLeft()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = None
            if self._template.get("drag", {}).get("enabled", True):
                self.setCursor(Qt.OpenHandCursor)
            if self._template.get("button", {}).get("enabled") and self.rect().contains(event.pos()):
                self.clicked.emit()
        super().mouseReleaseEvent(event)


# ── 工具函数 ───────────────────────────────────────

def _deep_merge(base, override):
    """递归合并两个 dict — override 中的 style 子 dict 也做深度合并。"""
    result = dict(base)
    for k, v in override.items():
        if k == "style" and isinstance(v, dict) and isinstance(result.get(k), dict):
            result[k] = {**result[k], **v}
        elif isinstance(v, dict) and isinstance(result.get(k), dict):
            result[k] = {**result[k], **v}
        else:
            result[k] = v
    return result


def _deep_copy_template(t):
    """深拷贝模板的全部 section。"""
    return {
        "icon":   dict(t["icon"]),
        "text":   dict(t["text"]),
        "button": dict(t["button"]),
        "drag":   dict(t["drag"]),
        "style":  dict(t.get("style", {})),
    }
