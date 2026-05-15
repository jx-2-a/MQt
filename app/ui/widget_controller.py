"""
WidgetController — 布局树编辑器

功能:
- 从 layout.json 选择/新建/删除布局
- 树形展示布局节点（类型 | 名称 | 标签）
- 属性编辑：选中节点 → 修改类型/名称/标签
- 事件绑定：enter/leave/click/double_click/hover/drag
- 节点操作：添加子节点、删除、上移、下移
- 独立布局：创建不关联窗口的布局，可通过 apply_layout() 加载
- 页面切换：选择目标窗口 → 应用布局 → 即时切换
"""
import json
import os
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QToolBar,
    QTreeWidget, QTreeWidgetItem, QComboBox, QLineEdit, QPushButton,
    QLabel, QFormLayout, QSplitter, QMessageBox, QHeaderView, QGroupBox,
    QListWidget, QListWidgetItem, QScrollArea,
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor

from app.core.layout_loader import load_layout
from app.core.layout_engine import apply_to_window, WIDGET_TYPE_OPTIONS
from app.core.window_config import load_config, save_config
from app.core.action_registry import get_event_types_for_type
from app.ui.event_editor import EventEditor, _event_label

DATA_ROLE = Qt.UserRole
LAYOUT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "config")
LAYOUT_PATH = os.path.join(LAYOUT_DIR, "layout.json")


def _load_all_layouts():
    with open(os.path.abspath(LAYOUT_PATH), "r", encoding="utf-8") as f:
        return json.load(f)


def _save_all_layouts(data):
    with open(os.path.abspath(LAYOUT_PATH), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


STYLE = """
/* ═══════════════════════════════════════════════════════════════
   WidgetController — VSCode Dark+ 完整样式
   每个控件类型都显式设定全部关键属性，杜绝继承泄露
   ═══════════════════════════════════════════════════════════════ */

/* ── 顶层窗口 ── */
QMainWindow {
    background-color: #1e1e1e;
    color: #cccccc;
}

/* ── QWidget 基类（只设字体/颜色，不设背景，由子类各自覆盖） ── */
QWidget {
    font-size: 13px;
    color: #cccccc;
    background-color: #1e1e1e;
}

/* ── 标签：透明背景，不遮挡父容器 ── */
QLabel {
    color: #cccccc;
    font-size: 13px;
    background-color: transparent;
    border: none;
    padding: 0px;
}

/* ── 结构层 ── */
QWidget#topbar {
    background-color: #252526;
    border: none;
    border-bottom: 1px solid #3c3c3c;
}
QWidget#topbar QLabel {
    background-color: transparent;
    color: #cccccc;
}
QWidget#statusbar {
    background-color: #007acc;
    border: none;
    border-top: 1px solid #007acc;
}
QLabel#panel_header {
    background-color: #252526;
    color: #8a8a8a;
    font-size: 11px;
    font-weight: bold;
    padding: 5px 10px;
    border: none;
    border-bottom: 1px solid #3c3c3c;
}
QLabel#status_lbl {
    color: #ffffff;
    font-size: 12px;
    background-color: transparent;
    border: none;
}

/* ── 工具栏 ── */
QToolBar {
    background-color: #252526;
    border: none;
    border-bottom: 1px solid #3c3c3c;
    spacing: 2px;
    padding: 2px 6px;
}
QToolBar QToolButton {
    background-color: #3c3c3c;
    color: #cccccc;
    border: 1px solid #3c3c3c;
    padding: 4px 10px;
    font-size: 12px;
}
QToolBar QToolButton:hover {
    background-color: #4a4a4a;
    border-color: #007acc;
}
QToolBar QToolButton:pressed {
    background-color: #333333;
}

/* ── 树视图 ── */
QTreeWidget {
    background-color: #252526;
    color: #cccccc;
    border: none;
    font-size: 13px;
    alternate-background-color: #2d2d2d;
    outline: none;
}
QTreeWidget::item {
    padding: 3px 4px;
    background-color: transparent;
    color: #cccccc;
    border: none;
}
QTreeWidget::item:selected {
    background-color: #094771;
    color: #ffffff;
}
QTreeWidget::item:hover {
    background-color: #2a2d2e;
}
QHeaderView {
    background-color: #252526;
    border: none;
}
QHeaderView::section {
    background-color: #252526;
    color: #cccccc;
    border: none;
    border-right: 1px solid #3c3c3c;
    border-bottom: 1px solid #3c3c3c;
    padding: 4px 8px;
    font-size: 12px;
    font-weight: bold;
}

/* ── 输入框 ── */
QLineEdit {
    background-color: #3c3c3c;
    color: #cccccc;
    border: 1px solid #3c3c3c;
    padding: 4px 8px;
    font-size: 13px;
}
QLineEdit:focus {
    border-color: #007acc;
    background-color: #3c3c3c;
}
QLineEdit:disabled {
    background-color: #2d2d2d;
    color: #858585;
}

/* ── 下拉框 ── */
QComboBox {
    background-color: #3c3c3c;
    color: #cccccc;
    border: 1px solid #3c3c3c;
    padding: 4px 8px;
    font-size: 13px;
}
QComboBox:hover {
    border-color: #007acc;
}
QComboBox:focus {
    border-color: #007acc;
}
QComboBox::drop-down {
    border: none;
    width: 20px;
    background-color: transparent;
}
QComboBox QAbstractItemView {
    background-color: #252526;
    color: #cccccc;
    selection-background-color: #094771;
    border: 1px solid #3c3c3c;
    outline: none;
}

/* ── 按钮 ── */
QPushButton {
    background-color: #0e639c;
    color: #ffffff;
    border: 1px solid #0e639c;
    padding: 4px 14px;
    font-size: 13px;
}
QPushButton:hover {
    background-color: #1177bb;
    border-color: #1177bb;
}
QPushButton:pressed {
    background-color: #094771;
    border-color: #094771;
}
QPushButton:disabled {
    background-color: #2d2d2d;
    color: #858585;
    border-color: #3c3c3c;
}

/* ── 分组框 ── */
QGroupBox {
    color: #cccccc;
    border: 1px solid #3c3c3c;
    margin-top: 8px;
    padding-top: 14px;
    font-size: 12px;
    font-weight: bold;
    background-color: transparent;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 4px;
    color: #cccccc;
    background-color: transparent;
}

/* ── 分割器 ── */
QSplitter {
    background-color: #1e1e1e;
}
QSplitter::handle {
    background-color: #3c3c3c;
}
QSplitter::handle:horizontal { width: 1px; }
QSplitter::handle:vertical { height: 1px; }

/* ── 滚动区域（QMessageBox 等可能用到） ── */
QScrollArea {
    background-color: transparent;
    border: none;
}
QScrollBar:vertical {
    background-color: #1e1e1e;
    width: 12px;
}
QScrollBar::handle:vertical {
    background-color: #424242;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover { background-color: #4f4f4f; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
QScrollBar:horizontal {
    background-color: #1e1e1e;
    height: 12px;
}
QScrollBar::handle:horizontal {
    background-color: #424242;
    min-width: 30px;
}
QScrollBar::handle:horizontal:hover { background-color: #4f4f4f; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0px; }

/* ── 消息框 ── */
QMessageBox {
    background-color: #1e1e1e;
    color: #cccccc;
}
QMessageBox QLabel {
    color: #cccccc;
    background-color: transparent;
    font-size: 13px;
}
QMessageBox QPushButton {
    background-color: #0e639c;
    color: #ffffff;
    border: 1px solid #0e639c;
    padding: 5px 16px;
    font-size: 13px;
}
"""


def _new_node(typ="VBox", name="", label=""):
    node = {"type": typ, "name": name, "label": label}
    if typ in ("VBox", "HBox", "HSplitter", "VSplitter", "ToolBar",
               "TabWidget", "GroupBox", "Form"):
        node["children"] = []
    return node


class WidgetController(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(   parent)
        self.setWindowTitle("布局控制器")
        self.resize(1100, 720)

        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), QColor("#1e1e1e"))
        self.setPalette(p)

        self._all_layouts = {}
        self._current_layout_name = None
        self._node_items = {}   # id(node) → QTreeWidgetItem
        self._item_nodes = {}   # id(item) → node
        self._target_window = None
        self._current_node = None
        self._current_events = {}
        self._layout_widgets = []  # [(name, type), ...] 用于事件编辑器的控件引用

        self._build_ui()
        self._load_layout_list()
        self.setStyleSheet(STYLE)

    # ── UI 构建 ──────────────────────────────────────────────

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ── 顶部栏 ──
        topbar = QWidget()
        topbar.setObjectName("topbar")
        top_bar = QHBoxLayout(topbar)
        top_bar.setContentsMargins(10, 5, 10, 5)
        top_bar.setSpacing(8)
        top_bar.addWidget(QLabel("当前布局:"))
        self._layout_combo = QComboBox()
        self._layout_combo.setMinimumWidth(180)
        self._layout_combo.currentTextChanged.connect(self._on_layout_selected)
        top_bar.addWidget(self._layout_combo)
        top_bar.addSpacing(12)
        top_bar.addWidget(QLabel("目标窗口:"))
        self._window_combo = QComboBox()
        self._window_combo.setMinimumWidth(160)
        self._window_combo.currentTextChanged.connect(self._on_window_selected)
        top_bar.addWidget(self._window_combo)
        self._apply_btn = QPushButton("应用到窗口")
        self._apply_btn.clicked.connect(self._apply_layout_to_window)
        top_bar.addWidget(self._apply_btn)
        top_bar.addStretch()
        root_layout.addWidget(topbar)

        # ── 工具栏 ──
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setObjectName("actionbar")
        self._act_new = toolbar.addAction("新建布局")
        self._act_new.triggered.connect(self._new_layout)
        toolbar.addSeparator()
        self._act_add = toolbar.addAction("+ 子节点")
        self._act_add.triggered.connect(self._add_child_node)
        self._act_del = toolbar.addAction("− 删除")
        self._act_del.triggered.connect(self._delete_node)
        toolbar.addSeparator()
        self._act_up = toolbar.addAction("↑ 上移")
        self._act_up.triggered.connect(self._move_node_up)
        self._act_down = toolbar.addAction("↓ 下移")
        self._act_down.triggered.connect(self._move_node_down)
        toolbar.addSeparator()
        self._act_rename = toolbar.addAction("重命名")
        self._act_rename.triggered.connect(self._rename_layout)
        self._act_del_layout = toolbar.addAction("删除布局")
        self._act_del_layout.triggered.connect(self._delete_layout)
        self._act_refresh = toolbar.addAction("刷新")
        self._act_refresh.triggered.connect(self._refresh)
        root_layout.addWidget(toolbar)

        # ── 主体：树 + 属性面板 ──
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(1)

        # 左侧面板
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)
        left_header = QLabel("布局节点树")
        left_header.setObjectName("panel_header")
        left_layout.addWidget(left_header)
        self._tree = QTreeWidget()
        self._tree.setHeaderLabels(["类型", "名称", "标签"])
        self._tree.setAlternatingRowColors(True)
        self._tree.setRootIsDecorated(True)
        self._tree.header().setStretchLastSection(True)
        self._tree.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self._tree.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self._tree.setMinimumWidth(400)
        self._tree.currentItemChanged.connect(self._on_tree_selection)
        left_layout.addWidget(self._tree)
        splitter.addWidget(left_panel)

        # 右侧面板
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        right_header = QLabel("节点属性")
        right_header.setObjectName("panel_header")
        right_layout.addWidget(right_header)

        form_widget = QWidget()
        form_widget.setObjectName("prop_form")
        self._form_layout = QFormLayout(form_widget)
        self._form_layout.setContentsMargins(10, 8, 10, 8)
        self._form_layout.setSpacing(6)
        self._type_combo = QComboBox()
        self._type_combo.addItems(WIDGET_TYPE_OPTIONS)
        self._form_layout.addRow("类型:", self._type_combo)
        self._name_edit = QLineEdit()
        self._name_edit.setPlaceholderText("节点名称（唯一标识）")
        self._form_layout.addRow("名称:", self._name_edit)
        self._label_edit = QLineEdit()
        self._label_edit.setPlaceholderText("显示文本")
        self._form_layout.addRow("标签:", self._label_edit)
        from PyQt5.QtWidgets import QSpinBox
        self._stretch_spin = QSpinBox()
        self._stretch_spin.setRange(0, 999)
        self._stretch_spin.setToolTip("Splitter 子节点伸缩比例，0=不伸缩")
        self._form_layout.addRow("伸缩:", self._stretch_spin)
        right_layout.addWidget(form_widget)

        # 事件绑定
        events_group = QGroupBox("事件绑定")
        events_out = QVBoxLayout(events_group)
        events_out.setContentsMargins(10, 12, 10, 8)
        events_out.setSpacing(4)

        # 事件列表（显示已绑定的事件）
        self._event_list = QListWidget()
        self._event_list.setMaximumHeight(160)
        self._event_list.setAlternatingRowColors(True)
        self._event_list.itemDoubleClicked.connect(self._edit_selected_event)
        self._event_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self._event_list.customContextMenuRequested.connect(self._on_event_list_menu)
        events_out.addWidget(self._event_list)

        # 添加事件按钮
        add_event_btn = QPushButton("+ 添加事件")
        add_event_btn.clicked.connect(self._add_event)
        events_out.addWidget(add_event_btn)

        right_layout.addWidget(events_group)
        right_layout.addStretch()

        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(10, 6, 10, 6)
        self._save_props_btn = QPushButton("保存属性")
        self._save_props_btn.clicked.connect(self._save_node_properties)
        btn_row.addStretch()
        btn_row.addWidget(self._save_props_btn)
        right_layout.addLayout(btn_row)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)
        root_layout.addWidget(splitter, 1)

        # ── 状态栏 ──
        statusbar = QWidget()
        statusbar.setObjectName("statusbar")
        statusbar.setFixedHeight(26)
        sb_layout = QHBoxLayout(statusbar)
        sb_layout.setContentsMargins(10, 0, 10, 0)
        self._status = QLabel("就绪")
        self._status.setObjectName("status_lbl")
        sb_layout.addWidget(self._status)
        root_layout.addWidget(statusbar)

    # ── 布局列表 ─────────────────────────────────────────────

    def _load_layout_list(self):
        self._all_layouts = _load_all_layouts()
        current = self._layout_combo.currentText()
        self._layout_combo.blockSignals(True)
        self._layout_combo.clear()
        for name in sorted(self._all_layouts.keys()):
            self._layout_combo.addItem(name)
        if current and current in self._all_layouts:
            self._layout_combo.setCurrentText(current)
        elif self._all_layouts:
            self._layout_combo.setCurrentIndex(0)
        self._layout_combo.blockSignals(False)

        # 刷新窗口列表
        self._refresh_window_list()

        if self._all_layouts:
            name = self._layout_combo.currentText()
            if name:
                self._on_layout_selected(name)

    def _refresh_window_list(self):
        self._window_combo.blockSignals(True)
        self._window_combo.clear()
        cfg = load_config()
        for key in sorted(cfg.keys()):
            if key == "widget_controller":
                continue
            title = cfg[key].get("title", key)
            self._window_combo.addItem(f"{title} ({key})", key)
        self._window_combo.blockSignals(False)

    # ── 布局选择 ─────────────────────────────────────────────

    def _on_layout_selected(self, name):
        if not name:
            return
        self._current_layout_name = name
        node = self._all_layouts.get(name)
        if node:
            self._populate_tree(node)

    def _on_window_selected(self, _text):
        key = self._window_combo.currentData()
        if key:
            self._target_window = self._find_window_by_key(key)

    def _find_window_by_key(self, key):
        from PyQt5.QtWidgets import QApplication
        for w in QApplication.topLevelWidgets():
            if hasattr(w, "_config_key") and w._config_key == key:
                return w
        return None

    # ── 树填充 ───────────────────────────────────────────────

    def _populate_tree(self, root_node):
        self._tree.blockSignals(True)
        self._tree.clear()
        self._node_items.clear()
        self._item_nodes.clear()
        if root_node:
            self._add_tree_node(None, root_node)
            self._tree.expandAll()
        self._tree.blockSignals(False)

    def _add_tree_node(self, parent_item, node):
        typ = node.get("type", "")
        name = node.get("name", "")
        label = node.get("label", "")
        item = QTreeWidgetItem([typ, name, str(label)])
        item.setData(0, DATA_ROLE, id(node))
        self._node_items[id(node)] = item
        self._item_nodes[id(item)] = node

        if parent_item is None:
            self._tree.addTopLevelItem(item)
        else:
            parent_item.addChild(item)

        for child in node.get("children", []):
            self._add_tree_node(item, child)

        return item

    # ── 树选择 → 属性表单 ───────────────────────────────────

    def _on_tree_selection(self, current, _previous):
        if not current:
            return
        node = self._item_nodes.get(id(current))
        if node is None:
            return
        self._current_node = node
        self._type_combo.blockSignals(True)
        self._type_combo.setCurrentText(node.get("type", ""))
        self._type_combo.blockSignals(False)
        self._name_edit.setText(node.get("name", ""))
        self._label_edit.setText(str(node.get("label", "")))
        self._stretch_spin.setValue(int(node.get("stretch", 0)))

        # 加载事件列表
        self._current_events = dict(node.get("events", {}))
        self._refresh_event_list()

        # 更新布局控件列表（用于事件编辑器的 widget_ref 参数）
        self._layout_widgets = self._collect_layout_widgets(self._current_layout_name)

    # ── 保存属性 ─────────────────────────────────────────────

    def _save_node_properties(self):
        item = self._tree.currentItem()
        if not item:
            self._set_status("未选中节点")
            return
        node = self._item_nodes.get(id(item))
        if node is None:
            return

        new_type = self._type_combo.currentText()
        new_name = self._name_edit.text().strip()
        new_label = self._label_edit.text()
        new_stretch = self._stretch_spin.value()

        old_type = node.get("type", "")
        node["type"] = new_type
        node["name"] = new_name
        node["label"] = new_label
        if new_stretch > 0:
            node["stretch"] = new_stretch
        else:
            node.pop("stretch", None)

        # 保存事件绑定（从事件列表收集）
        if self._current_events:
            node["events"] = dict(self._current_events)
        else:
            node.pop("events", None)

        # 容器类型需要有 children
        container_types = ("VBox", "HBox", "HSplitter", "VSplitter", "ToolBar",
                           "TabWidget", "GroupBox", "Form")
        if new_type in container_types and "children" not in node:
            node["children"] = []
        elif new_type not in container_types and old_type in container_types:
            node.pop("children", None)

        type_changed = old_type != new_type
        was_container = old_type in container_types
        is_container = new_type in container_types

        if type_changed and (was_container != is_container):
            # 容器↔叶子：必须重建树项（children 结构变化）
            self._persist_and_reload(item, node)
        else:
            # 仅名称/标签变化 or 同是容器/叶子：原地更新 + 保存
            _save_all_layouts(self._all_layouts)
            item.setText(0, new_type)
            item.setText(1, new_name)
            item.setText(2, new_label)
            self._node_items[id(node)] = item
            self._item_nodes[id(item)] = node

        self._set_status(f"已保存: {new_name or new_type}")

    # ── 节点操作 ─────────────────────────────────────────────

    def _add_child_node(self):
        item = self._tree.currentItem()
        if not item:
            self._set_status("请先选中父节点")
            return
        parent_node = self._item_nodes.get(id(item))
        if parent_node is None:
            return
        if "children" not in parent_node:
            self._set_status("选中的节点不是容器，无法添加子节点")
            return

        child = _new_node("Label", "", "新节点")
        parent_node["children"].append(child)
        self._persist_and_save()

        new_item = self._add_tree_node(item, child)
        self._tree.expandItem(item)
        self._tree.setCurrentItem(new_item)
        self._set_status("已添加子节点")

    def _delete_node(self):
        item = self._tree.currentItem()
        if not item:
            self._set_status("请先选中要删除的节点")
            return
        node = self._item_nodes.get(id(item))
        if node is None:
            return

        parent_item = item.parent()
        if parent_item is None:
            # 根节点不能直接删除，而是要删除整个布局
            reply = QMessageBox.question(
                self, "确认", f"确定删除布局 '{self._current_layout_name}' 吗？",
                QMessageBox.Yes | QMessageBox.No,
            )
            if reply != QMessageBox.Yes:
                return
            self._delete_layout()
            return

        parent_node = self._item_nodes.get(id(parent_item))
        if parent_node and "children" in parent_node:
            parent_node["children"].remove(node)

        self._persist_and_save()
        parent_item.removeChild(item)
        self._node_items.pop(id(node), None)
        self._item_nodes.pop(id(item), None)
        self._set_status("已删除节点")

    def _move_node_up(self):
        self._move_node(-1)

    def _move_node_down(self):
        self._move_node(1)

    def _move_node(self, direction):
        item = self._tree.currentItem()
        if not item:
            self._set_status("请先选中节点")
            return
        node = self._item_nodes.get(id(item))
        if node is None:
            return

        parent_item = item.parent()
        if parent_item is None:
            self._set_status("根节点不能移动")
            return

        parent_node = self._item_nodes.get(id(parent_item))
        children = parent_node.get("children", [])
        idx = children.index(node) if node in children else -1
        if idx < 0:
            return

        new_idx = idx + direction
        if new_idx < 0 or new_idx >= len(children):
            self._set_status("已到边界")
            return

        children[idx], children[new_idx] = children[new_idx], children[idx]
        self._persist_and_save()

        # 重建整棵子树 — 收集→重排
        self._tree.blockSignals(True)
        old_items = {}
        for i in range(parent_item.childCount()):
            ci = parent_item.child(0)
            node_of_ci = self._item_nodes.get(id(ci))
            old_items[id(node_of_ci) if node_of_ci is not None else None] = ci
            parent_item.takeChild(0)
        for child_node in children:
            ci = old_items.get(id(child_node))
            if ci:
                parent_item.addChild(ci)
            else:
                self._add_tree_node(parent_item, child_node)
        self._tree.setCurrentItem(item)
        self._tree.blockSignals(False)
        self._set_status("已移动节点")

    # ── 布局级操作 ───────────────────────────────────────────

    def _new_layout(self):
        name = "new_layout"
        base = name
        i = 1
        while name in self._all_layouts:
            name = f"{base}_{i}"
            i += 1
        self._all_layouts[name] = _new_node("VBox", "root", "")
        _save_all_layouts(self._all_layouts)
        self._load_layout_list()
        self._layout_combo.setCurrentText(name)
        self._set_status(f"已创建布局: {name}")

    def _rename_layout(self):
        name = self._current_layout_name
        if not name:
            self._set_status("没有选中的布局")
            return
        from PyQt5.QtWidgets import QInputDialog
        new_name, ok = QInputDialog.getText(
            self, "重命名布局", "新名称:", QLineEdit.Normal, name)
        if not ok or not new_name.strip():
            return
        new_name = new_name.strip()
        if new_name == name:
            return
        if new_name in self._all_layouts:
            QMessageBox.warning(self, "名称冲突", f"布局 '{new_name}' 已存在")
            return
        # 重命名 key
        self._all_layouts[new_name] = self._all_layouts.pop(name)
        _save_all_layouts(self._all_layouts)
        # 更新 settings.json 中引用此布局的窗口
        cfg = load_config()
        updated = False
        for k, v in cfg.items():
            if isinstance(v, dict) and v.get("layout") == name:
                cfg[k]["layout"] = new_name
                updated = True
        if updated:
            save_config(cfg)
        self._current_layout_name = new_name
        self._load_layout_list()
        self._layout_combo.setCurrentText(new_name)
        self._set_status(f"已重命名为: {new_name}")

    def _delete_layout(self):
        name = self._current_layout_name
        if not name:
            return
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除布局 '{name}' 吗？\n\n此操作会永久删除该布局及其所有节点，不可撤销。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return
        if name in self._all_layouts:
            del self._all_layouts[name]
            _save_all_layouts(self._all_layouts)
        self._load_layout_list()
        self._set_status(f"已删除布局: {name}")

    def _refresh(self):
        self._load_layout_list()
        self._set_status("已刷新")

    # ── 应用到窗口（页面切换） ───────────────────────────────

    def _apply_layout_to_window(self):
        if not self._current_layout_name:
            self._set_status("没有选中的布局")
            return

        node = self._all_layouts.get(self._current_layout_name)
        if not node:
            self._set_status("布局数据为空")
            return

        key = self._window_combo.currentData()
        if not key:
            self._set_status("没有选择目标窗口")
            return

        window = self._find_window_by_key(key)
        if window is None:
            from app.core.window_factory import open_sub_window
            from PyQt5.QtWidgets import QApplication
            main_win = None
            for w in QApplication.topLevelWidgets():
                if hasattr(w, '_config_key') and w._config_key == 'main' and hasattr(w, 'open_sub_window'):
                    main_win = w
                    break
            window = open_sub_window(main_win, config_key=key)
            if window is None:
                self._set_status(f"找不到窗口: {key}")
                return

        apply_to_window(window, node)

        # 更新 settings.json 使关联持久化
        cfg = load_config()
        if key in cfg:
            cfg[key]["layout"] = self._current_layout_name
            save_config(cfg)

        self._refresh_window_list()
        self._set_status(f"已应用 '{self._current_layout_name}' → '{key}'")

    # ── 事件编辑 ─────────────────────────────────────────────

    def _refresh_event_list(self):
        """根据 _current_events 重建事件列表显示。"""
        self._event_list.clear()
        for evt_key, code in self._current_events.items():
            summary = code[:60] + ("..." if len(code) > 60 else "")
            label = _event_label(evt_key)
            item = QListWidgetItem(f"{label}  →  {summary}")
            item.setData(Qt.UserRole, evt_key)
            item.setToolTip(code)
            # 添加删除按钮通过右键菜单
            self._event_list.addItem(item)

    def _add_event(self):
        """添加新事件：打开 EventEditor 对话框。"""
        if self._current_node is None:
            self._set_status("请先选中一个节点")
            return
        widget_type = self._current_node.get("type", "")
        code, evt_key, ok = EventEditor.edit_event(
            self, widget_type, self._layout_widgets)
        if not ok or not code:
            return
        self._current_events[evt_key] = code
        self._refresh_event_list()
        self._set_status(f"已添加事件: {_event_label(evt_key)}")

    def _edit_selected_event(self, _item=None):
        """双击编辑已有事件。"""
        item = self._event_list.currentItem()
        if not item:
            return
        evt_key = item.data(Qt.UserRole)
        old_code = self._current_events.get(evt_key, "")
        widget_type = self._current_node.get("type", "") if self._current_node else ""
        code, new_evt_key, ok = EventEditor.edit_event(
            self, widget_type, self._layout_widgets, evt_key, old_code)
        if ok and code:
            if new_evt_key != evt_key:
                del self._current_events[evt_key]
            self._current_events[new_evt_key] = code
            self._refresh_event_list()
            self._set_status(f"已更新事件: {_event_label(new_evt_key)}")

    def _on_event_list_menu(self, pos):
        """右键菜单：编辑/删除事件。"""
        item = self._event_list.itemAt(pos)
        if not item:
            return
        from PyQt5.QtWidgets import QMenu, QAction
        menu = QMenu(self)
        edit_act = QAction("编辑事件", menu)
        edit_act.triggered.connect(lambda: self._edit_selected_event())
        menu.addAction(edit_act)
        del_act = QAction("删除事件", menu)
        del_act.triggered.connect(self._delete_event)
        menu.addAction(del_act)
        menu.exec_(self._event_list.mapToGlobal(pos))

    def _delete_event(self):
        """删除选中的事件绑定。"""
        item = self._event_list.currentItem()
        if not item:
            self._set_status("请先在事件列表中选中要删除的事件")
            return
        evt_key = item.data(Qt.UserRole)
        if evt_key in self._current_events:
            del self._current_events[evt_key]
        self._refresh_event_list()
        self._set_status(f"已删除事件: {_event_label(evt_key)}")

    def _collect_layout_widgets(self, layout_name):
        """收集布局中所有具名控件: [(name, type), ...]。"""
        result = []
        layout_root = self._all_layouts.get(layout_name)
        if layout_root is None:
            return result

        def _walk(node):
            t = node.get("type", "")
            n = node.get("name", "")
            if n:
                result.append((n, t))
            for child in node.get("children", []):
                _walk(child)

        _walk(layout_root)
        return result

    # ── 持久化 ───────────────────────────────────────────────

    def _persist_and_save(self):
        _save_all_layouts(self._all_layouts)

    def _persist_and_reload(self, tree_item, updated_node):
        # 如果从容器变成叶子，丢弃 children
        container_types = ("VBox", "HBox", "HSplitter", "VSplitter", "ToolBar",
                           "TabWidget", "GroupBox", "Form")
        if updated_node.get("type") not in container_types:
            updated_node.pop("children", None)
        _save_all_layouts(self._all_layouts)
        # 重建子树以反映类型变化（如容器↔叶子）
        parent_item = tree_item.parent()
        if parent_item:
            parent_item.removeChild(tree_item)
            new_item = self._add_tree_node(parent_item, updated_node)
            self._tree.setCurrentItem(new_item)
        else:
            self._populate_tree(updated_node)

    def _set_status(self, msg):
        self._status.setText(msg)
        QTimer.singleShot(4000, lambda: self._status.setText("就绪"))

    # ── 公开 API ─────────────────────────────────────────────

    @staticmethod
    def apply_layout(name, window=None):
        """
        将命名布局应用到指定窗口（无窗口则创建新独立窗口）。
        可在任意位置直接调用，实现"脱离窗口的独立布局加载"。
        """
        node = load_layout(name)
        if node is None:
            raise ValueError(f"布局 '{name}' 不存在")

        if window is None:
            from app.ui.config_window import ConfigWindow
            # 在 settings.json 中注册临时配置
            cfg = load_config()
            temp_key = f"_layout_{name}"
            if temp_key not in cfg:
                cfg[temp_key] = {
                    "title": name,
                    "geometry": {"x": 200, "y": 200, "width": 800, "height": 600},
                    "opacity": 1.0,
                    "frameless": False,
                    "background_color": "#f0f0f0",
                    "layout": name,
                }
                save_config(cfg)
            window = ConfigWindow(temp_key)
            window.setWindowTitle(name)

        apply_to_window(window, node)
        window.show()
        window.raise_()
        return window

    @staticmethod
    def switch_page(window, layout_name):
        """
        切换窗口页面（即时切换布局）。
        用法: WidgetController.switch_page(my_window, "demo")
        """
        node = load_layout(layout_name)
        if node is None:
            raise ValueError(f"布局 '{layout_name}' 不存在")
        apply_to_window(window, node)
        if hasattr(window, "_config_key"):
            from app.core.window_config import update_window_config
            cfg = load_config()
            key = window._config_key
            if key in cfg:
                cfg[key]["layout"] = layout_name
                save_config(cfg)
