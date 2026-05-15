import hashlib
from PyQt5.QtCore import Qt, QEvent, QObject
from PyQt5.QtWidgets import QPushButton, QWidget, QApplication
from app.ui.widgets import (
    StyledBox, StyledSplitter, StyledToolBar, StyledLabel, StyledTreeWidget, StyledForm,
    StyledButton, StyledComboBox, StyledTextEdit, StyledLineEdit, StyledCheckBox,
    StyledSpinBox, StyledDoubleSpinBox, StyledTabWidget, StyledGroupBox,
    StyledSlider, StyledProgressBar, StyledSpacer,
)

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

    def eventFilter(self, obj, event):
        if obj is not self._widget:
            return super().eventFilter(obj, event)
        t = event.type()
        code = None
        if t == QEvent.Enter and "enter" in self._events:
            code = self._events["enter"]
        elif t == QEvent.Leave and "leave" in self._events:
            code = self._events["leave"]
        elif t == QEvent.MouseButtonPress:
            if event.button() == Qt.RightButton and "right_click" in self._events:
                code = self._events["right_click"]
            elif "click" in self._events:
                code = self._events["click"]
        elif t == QEvent.MouseButtonDblClick and "double_click" in self._events:
            code = self._events["double_click"]
        elif t == QEvent.HoverEnter and "hover" in self._events:
            code = self._events["hover"]
        elif t == QEvent.DragEnter and "drag" in self._events:
            code = self._events["drag"]
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
    """生成稳定的控件标识符：有名用名，无名用 path hash。"""
    name = node.get("name", "")
    if name:
        return name
    raw = f"{path}|{node.get('type', '')}|{node.get('label', '')}"
    return "w" + hashlib.md5(raw.encode()).hexdigest()[:7]


# ── 控件构建器 ─────────────────────────────────────────────────────

def _build_box(node, orientation, _path="0"):
    box = StyledBox(orientation)
    box.setObjectName(_node_id(node, _path))
    for i, child in enumerate(node.get("children", [])):
        w = build(child, f"{_path}/{i}")
        if w:
            box.add_widget(w)
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
    return label


def _build_treeview(node, _path="0"):
    tree = StyledTreeWidget()
    tree.setObjectName(_node_id(node, _path))
    tree.setHeaderLabel(node.get("label", "树"))
    return tree


def _build_form(node, _path="0"):
    form = StyledForm()
    form.setObjectName(_node_id(node, _path))
    return form


def _build_button(node, _path="0"):
    btn = StyledButton(node.get("label", ""))
    btn.setObjectName(_node_id(node, _path))
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
    tw = StyledTabWidget()
    tw.setObjectName(_node_id(node, _path))
    for i, child in enumerate(node.get("children", [])):
        page = build(child, f"{_path}/{i}")
        if page:
            tw.add_tab(page, child.get("label", "Tab"))
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
}

WIDGET_TYPE_OPTIONS = sorted(BUILDERS.keys())


def build(node, _path="0"):
    node_type = node.get("type", "")
    builder = BUILDERS.get(node_type)
    if builder is None:
        return None
    widget = builder(node, _path)
    if widget:
        widget.setProperty("layout_type", node_type)
        _bind_events(widget, node)
    return widget


def apply_to_window(window, node):
    root = build(node, "0")
    if root:
        window.setCentralWidget(root)
