import hashlib
from PyQt5.QtCore import Qt, QEvent, QObject
from PyQt5.QtWidgets import QPushButton, QWidget, QApplication
from app.ui.widgets import (
    StyledBox, StyledSplitter, StyledToolBar, StyledLabel, StyledTreeWidget, StyledForm,
    StyledButton, StyledComboBox, StyledTextEdit, StyledLineEdit, StyledCheckBox,
    StyledSpinBox, StyledDoubleSpinBox, CachedTabWidget, StyledGroupBox,
    StyledSlider, StyledProgressBar, StyledSpacer, StyledImage,
    FormRow, FormContainer,
)
from app.ui.complex_widgets import DraggableLabel

# 鼠标/事件过滤器事件
_MOUSE_EVENTS = {"enter", "leave", "click", "double_click", "hover", "drag", "right_click"}

# 信号级事件：event_key → {widget_type → signal_name}
_SIGNAL_MAP = {
    "changed": {
        "ComboBox": "currentIndexChanged",
        "TextEdit": "textChanged",
        "LineEdit": "textChanged",
        "SpinBox": "valueChanged",
        "DoubleSpinBox": "valueChanged",
        "Slider": "valueChanged",
        "CheckBox": "toggled",
    },
    "clicked": {"Button": "clicked"},
    "toggled": {"Button": "toggled", "CheckBox": "toggled"},
    "return_pressed": {"LineEdit": "returnPressed"},
    "tab_changed": {"TabWidget": "currentChanged"},
    "item_activated": {"ComboBox": "activated"},
}


def _find_widget_in_window(window, name):
    """在窗口中按 objectName 查找控件。"""
    if not window or not name:
        return None
    for child in window.findChildren(QWidget):
        if child.objectName() == name:
            return child
    return None


def _make_exec_scope(widget):
    """构建 exec 执行环境，提供 find_widget 等辅助函数。"""
    win = widget.window()
    return {
        "widget": widget,
        "self": widget,
        "find_widget": lambda name: _find_widget_in_window(win, name),
        "window": win,
        "app": QApplication.instance(),
        "Qt": Qt,
    }


class _EventHandler(QObject):
    """事件过滤器：根据节点 events 配置绑定交互行为。"""
    def __init__(self, widget, events):
        super().__init__(widget)
        self._widget = widget
        self._events = events or {}
        self._drag_pos = None

    def eventFilter(self, obj, event):
        if obj is not self._widget:
            return super().eventFilter(obj, event)
        t = event.type()

        # drag: 左键拖动（移动窗口）
        if "drag" in self._events:
            if t == QEvent.MouseButtonPress and event.button() == Qt.LeftButton:
                self._drag_pos = event.globalPos()
                code = self._events["drag"]
                if code:
                    try:
                        exec(code, _make_exec_scope(obj))
                    except Exception as e:
                        print(f"[EventHandler] {code!r} -> {e}")
                return True
            elif t == QEvent.MouseMove and self._drag_pos is not None:
                if not (event.buttons() & Qt.LeftButton):
                    self._drag_pos = None  # 左键已释放但 release 被模态对话框吃掉
                    return False
                delta = event.globalPos() - self._drag_pos
                self._widget.window().move(self._widget.window().pos() + delta)
                self._drag_pos = event.globalPos()
                return True
            elif t == QEvent.MouseButtonRelease and event.button() == Qt.LeftButton:
                self._drag_pos = None

        code = None
        if t == QEvent.Enter and "enter" in self._events:
            code = self._events["enter"]
        elif t == QEvent.Leave and "leave" in self._events:
            code = self._events["leave"]
        elif t == QEvent.MouseButtonPress:
            if event.button() == Qt.RightButton and "right_click" in self._events:
                code = self._events["right_click"]
            elif "click" in self._events:
                self._drag_pos = None  # click 与 drag 互斥，避免模态对话框吃掉 release 事件
                code = self._events["click"]
        elif t == QEvent.MouseButtonDblClick and "double_click" in self._events:
            code = self._events["double_click"]
        elif t == QEvent.HoverEnter and "hover" in self._events:
            code = self._events["hover"]
        if code:
            try:
                exec(code, _make_exec_scope(obj))
            except Exception as e:
                print(f"[EventHandler] {code!r} -> {e}")
        return super().eventFilter(obj, event)


def _connect_signal(widget, widget_type, event_key, code):
    """根据事件类型连接 Qt 信号。返回 True 表示成功连接。"""
    type_map = _SIGNAL_MAP.get(event_key, {})
    signal_name = type_map.get(widget_type)
    if signal_name is None:
        return False

    def handler(*args):
        scope = _make_exec_scope(widget)
        if args:
            scope["value"] = args[0]
        try:
            exec(code, scope)
        except Exception as e:
            print(f"[SignalEvent] {code!r} -> {e}")

    signal = getattr(widget, signal_name, None)
    if signal is not None:
        signal.connect(handler)
        return True
    return False


def _bind_events(widget, node):
    """为 widget 绑定事件：鼠标事件 → eventFilter，信号事件 → connect。"""
    events = node.get("events")
    if not events:
        return

    widget_type = node.get("type", "")

    # 鼠标事件 → eventFilter
    mouse_events = {k: v for k, v in events.items() if k in _MOUSE_EVENTS}
    if mouse_events:
        widget.setAttribute(Qt.WA_Hover, True)
        widget.setMouseTracking(True)
        widget.installEventFilter(_EventHandler(widget, mouse_events))

    # 信号事件 → connect
    for event_key, code in events.items():
        if event_key not in _MOUSE_EVENTS:
            if not _connect_signal(widget, widget_type, event_key, code):
                print(f"[BindEvents] Cannot connect '{event_key}' for {widget_type}")


def _node_id(node, path):
    """生成稳定的控件标识符：id > name > path hash。id 一旦生成永不改变。"""
    nid = node.get("id", "")
    if nid:
        return nid
    name = node.get("name", "")
    if name:
        return name
    raw = f"{path}|{node.get('type', '')}|{node.get('label', '')}"
    return "w" + hashlib.md5(raw.encode()).hexdigest()[:7]


# ── 控件构建器 ─────────────────────────────────────────────────────

def _build_box(node, orientation, _path="0"):
    spacing = node.get("spacing", 0)
    margins = tuple(node.get("margins", (0, 0, 0, 0)))
    box = StyledBox(orientation, spacing=spacing, margins=margins)
    box.setObjectName(_node_id(node, _path))
    for i, child in enumerate(node.get("children", [])):
        w = build(child, f"{_path}/{i}")
        if w:
            box.add_widget(w, int(child.get("stretch", 0)))
    return box


def _build_splitter(node, orientation, _path="0"):
    splitter = StyledSplitter(orientation)
    splitter.setObjectName(_node_id(node, _path))
    stretches = []
    for i, child in enumerate(node.get("children", [])):
        w = build(child, f"{_path}/{i}")
        if w:
            splitter.add_widget(w)
            stretches.append(int(child.get("stretch", 0)))
    if any(s > 0 for s in stretches):
        for i, s in enumerate(stretches):
            splitter.setStretchFactor(i, s)
        # 同步设初始比例 — setSizes 只认比例，不认绝对值
        base = 100 * max(stretches)
        sizes = [int(base * s / sum(stretches)) for s in stretches]
        splitter.setSizes(sizes)
    return splitter


def _build_toolbar(node, _path="0"):
    tb = StyledToolBar()
    tb.setObjectName(_node_id(node, _path))
    for i, child in enumerate(node.get("children", [])):
        if child.get("type") == "Action":
            tb.add_action(child.get("label", ""))
    return tb


def _build_label(node, _path="0"):
    label = StyledLabel(node.get("label", ""))
    label.setObjectName(_node_id(node, _path))
    icon = node.get("icon", "")
    if icon:
        w = node.get("icon_width", 0)
        h = node.get("icon_height", 0)
        label.set_icon(icon, w, h)
    return label


def _build_treeview(node, _path="0"):
    tree = StyledTreeWidget()
    tree.setObjectName(_node_id(node, _path))
    tree.setHeaderLabel(node.get("label", "树"))
    if node.get("header_hidden", False):
        tree.setHeaderHidden(True)
    return tree


def _build_form(node, _path="0"):
    form = StyledForm()
    form.setObjectName(_node_id(node, _path))
    return form


def _build_button(node, _path="0"):
    btn = StyledButton(node.get("label", ""))
    btn.setObjectName(_node_id(node, _path))
    icon = node.get("icon", "")
    icon_toggled = node.get("icon_toggled", "")
    w = node.get("icon_width", 0)
    h = node.get("icon_height", 0)
    if icon and icon_toggled:
        btn.set_toggle_icons(icon, icon_toggled, w, h)
    elif icon:
        btn.set_icon(icon, w, h)
    return btn


def _build_combobox(node, _path="0"):
    cb = StyledComboBox()
    cb.setObjectName(_node_id(node, _path))
    items = node.get("items", [])
    if items:
        cb.add_items(items)
    return cb


def _build_textedit(node, _path="0"):
    te = StyledTextEdit(node.get("label", ""))
    te.setObjectName(_node_id(node, _path))
    return te


def _build_lineedit(node, _path="0"):
    le = StyledLineEdit(node.get("label", ""))
    le.setObjectName(_node_id(node, _path))
    return le


def _build_checkbox(node, _path="0"):
    cb = StyledCheckBox(node.get("label", ""))
    cb.setObjectName(_node_id(node, _path))
    return cb


def _build_spinbox(node, _path="0"):
    sb = StyledSpinBox()
    sb.setObjectName(_node_id(node, _path))
    return sb


def _build_doublespinbox(node, _path="0"):
    dsb = StyledDoubleSpinBox()
    dsb.setObjectName(_node_id(node, _path))
    return dsb


def _build_tabwidget(node, _path="0"):
    tw = CachedTabWidget()
    tw.setObjectName(_node_id(node, _path))
    return tw


def _build_groupbox(node, _path="0"):
    gb = StyledGroupBox(node.get("label", ""))
    gb.setObjectName(_node_id(node, _path))
    for i, child in enumerate(node.get("children", [])):
        w = build(child, f"{_path}/{i}")
        if w:
            gb.add_widget(w)
    return gb


def _build_slider(node, _path="0"):
    sl = StyledSlider()
    sl.setObjectName(_node_id(node, _path))
    return sl


def _build_progressbar(node, _path="0"):
    pb = StyledProgressBar()
    pb.setObjectName(_node_id(node, _path))
    return pb


def _build_spacer(node, _path="0"):
    sp = StyledSpacer()
    sp.setObjectName(_node_id(node, _path))
    return sp


def _build_image(node, _path="0"):
    img = StyledImage(
        src=node.get("src", ""),
        scale=node.get("scale", "contain"),
        width=node.get("width", 0),
        height=node.get("height", 0),
    )
    img.setObjectName(_node_id(node, _path))
    return img


def _build_draggable_label(node, _path="0"):
    template = node.get("template", None)
    if template is None:
        # 从传统字段合成模板
        template = {
            "icon": {
                "src": node.get("icon", ""),
                "width": node.get("icon_width", 24),
                "height": node.get("icon_height", 24),
                "visible": bool(node.get("icon", "")),
            },
            "text": {
                "content": node.get("label", ""),
                "visible": True,
            },
            "button": {
                "enabled": node.get("button_enabled", False),
            },
            "drag": {
                "enabled": node.get("drag_enabled", True),
            },
        }
    lbl = DraggableLabel(template=template)
    lbl.setObjectName(_node_id(node, _path))
    return lbl


def _build_form_row(node, _path="0"):
    row = FormRow(spacing=node.get("spacing", 40))
    row.setObjectName(_node_id(node, _path))
    for i, child in enumerate(node.get("children", [])):
        w = build(child, f"{_path}/{i}")
        if w:
            row.add_widget(w)
    return row


def _build_form_container(node, _path="0"):
    fc = FormContainer(
        row_spacing=node.get("row_spacing", 20),
        margin=node.get("margin", 0),
    )
    fc.setObjectName(_node_id(node, _path))
    for i, child in enumerate(node.get("children", [])):
        w = build(child, f"{_path}/{i}")
        if w:
            fc.add_widget(w)
    return fc


BUILDERS = {
    "VBox": lambda n, p="0": _build_box(n, "v", p),
    "HBox": lambda n, p="0": _build_box(n, "h", p),
    "HSplitter": lambda n, p="0": _build_splitter(n, Qt.Horizontal, p),
    "VSplitter": lambda n, p="0": _build_splitter(n, Qt.Vertical, p),
    "ToolBar": _build_toolbar,
    "Label": _build_label,
    "TreeView": _build_treeview,
    "Form": _build_form,
    "Button": _build_button,
    "ComboBox": _build_combobox,
    "TextEdit": _build_textedit,
    "LineEdit": _build_lineedit,
    "CheckBox": _build_checkbox,
    "SpinBox": _build_spinbox,
    "DoubleSpinBox": _build_doublespinbox,
    "TabWidget": _build_tabwidget,
    "GroupBox": _build_groupbox,
    "Slider": _build_slider,
    "ProgressBar": _build_progressbar,
    "Spacer": _build_spacer,
    "Image": _build_image,
    "DraggableLabel": _build_draggable_label,
    "FormRow": _build_form_row,
    "FormContainer": _build_form_container,
}

# 容器类型：子控件可穿透的背景，让 QLabel 背景层可见
_CONTAINER_TYPES = {"VBox", "HBox", "HSplitter", "VSplitter", "GroupBox", "ToolBar", "Form", "FormRow", "FormContainer"}

WIDGET_TYPE_OPTIONS = sorted(BUILDERS.keys())


def build(node, _path="0"):
    node_type = node.get("type", "")
    builder = BUILDERS.get(node_type)
    if builder is None:
        return None
    widget = builder(node, _path)
    if widget:
        widget.setProperty("layout_type", node_type)
        # Box 类型使用 paintEvent 直绘背景（支持 rgba），不能启用 QSS 背景
        if node_type not in ("VBox", "HBox", "Form", "Spacer"):
            widget.setAttribute(Qt.WA_StyledBackground, True)
        widget.setAutoFillBackground(False)
        _bind_events(widget, node)
    return widget


def apply_to_window(window, node):
    root = build(node, "0")
    if root:
        window.setCentralWidget(root)
        _propagate_styled_bg(root)
        # 递归应用样式到所有控件
        from app.core.style_engine import cascade_apply_styles
        cascade_apply_styles(root)
        # 重建背景层（centralWidget 被替换后旧的 __bg_layer__ 已销毁）
        from app.windows.base_window import BaseWindow
        if isinstance(window, BaseWindow):
            window.ensure_background()


def _propagate_styled_bg(widget):
    """确保 Qt 内部子控件使用 QSS 渲染背景。

    WA_StyledBackground 让 QTabBar、QHeaderView、QScrollBar 等内部控件
    通过 QSS 渲染背景（而非调色板），使子控件选择器（::tab、::section 等）
    正确生效。QStackedWidget 额外禁用自动填充，否则调色板底色会遮挡
    容器半透明背景。

    注意：不对内部控件设置 WA_TranslucentBackground——它们不需要穿透到
    窗口背景层，只需在其父容器已渲染的内容上正常绘制即可。
    """
    from PyQt5.QtWidgets import QStackedWidget, QHeaderView
    for child in widget.findChildren(QWidget):
        child.setAttribute(Qt.WA_StyledBackground, True)
        if isinstance(child, (QStackedWidget, QHeaderView)):
            child.setAutoFillBackground(False)
        if isinstance(child, QHeaderView):
            vp = child.viewport()
            if vp:
                vp.setAutoFillBackground(False)
