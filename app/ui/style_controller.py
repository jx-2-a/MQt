"""样式控制器 — 可视编辑 styles.json，四级级联：全局→类型→窗口→控件实例。"""
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QComboBox, QPushButton, QTreeWidget, QTreeWidgetItem, QLabel,
    QLineEdit, QGroupBox, QColorDialog, QMessageBox,
    QSplitter, QScrollArea, QFrame,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from app.core.window_config import load_config
from app.core.layout_loader import load_all_layouts
from app.core.layout_engine import WIDGET_TYPE_OPTIONS
from app.core.style_engine import (
    load_styles, save_styles, apply_to_widget,
    generate_widget_id,
    TYPE_PROPERTIES, PROPERTY_GROUPS,
    SUB_CONTROLS_OF, WIDGET_STYLE_SCHEMA, _normalize_style_dict,
)


STYLE = """
/* ═══════════════════════════════════════════════════════════════
   StyleController — VSCode Dark+ 完整样式
   每个控件类型都显式设定全部关键属性，杜绝继承泄露
   ═══════════════════════════════════════════════════════════════ */

/* ── 顶层窗口 ── */
QMainWindow {
    background-color: #1e1e1e;
    color: #cccccc;
}

/* ── QWidget 基类 ── */
QWidget {
    font-size: 13px;
    color: #cccccc;
    background-color: #1e1e1e;
}

/* ── 标签 ── */
QLabel {
    color: #cccccc;
    font-size: 13px;
    background-color: transparent;
    border: none;
    padding: 0px;
}
QLabel#inherited_hint {
    color: #858585;
    font-size: 12px;
    font-style: italic;
    padding: 2px 4px;
    background-color: transparent;
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

/* ── 树视图 ── */
QTreeWidget {
    background-color: #252526;
    color: #cccccc;
    border: none;
    font-size: 13px;
    outline: none;
    alternate-background-color: #2d2d2d;
}
QTreeWidget::item {
    padding: 3px 6px;
    color: #cccccc;
    border: none;
    background-color: transparent;
}
QTreeWidget::item:selected {
    background-color: #094771;
    color: #ffffff;
}
QTreeWidget::item:hover {
    background-color: #2a2d2e;
}
QTreeWidget::branch {
    background-color: transparent;
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
QPushButton#color_btn {
    min-width: 28px;
    max-width: 28px;
    padding: 2px;
    font-size: 14px;
    background-color: #3c3c3c;
    border: 1px solid #3c3c3c;
    color: #cccccc;
}
QPushButton#color_btn:hover {
    background-color: #4a4a4a;
    border-color: #007acc;
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

/* ── 滚动区域 ── */
QScrollArea {
    background-color: transparent;
    border: none;
}
QScrollArea QWidget#qt_scrollarea_viewport {
    background-color: #1e1e1e;
}
QScrollBar:vertical {
    background-color: #1e1e1e;
    width: 12px;
    border: none;
}
QScrollBar::handle:vertical {
    background-color: #424242;
    min-height: 30px;
    border: none;
}
QScrollBar::handle:vertical:hover { background-color: #4f4f4f; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; border: none; }
QScrollBar:horizontal {
    background-color: #1e1e1e;
    height: 12px;
    border: none;
}
QScrollBar::handle:horizontal {
    background-color: #424242;
    min-width: 30px;
    border: none;
}
QScrollBar::handle:horizontal:hover { background-color: #4f4f4f; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0px; border: none; }

/* ── 框架（颜色预览） ── */
QFrame {
    background-color: transparent;
    border: none;
    color: #cccccc;
}
QFrame#color_preview {
    border: 1px solid #555555;
    min-width: 22px;
    max-width: 22px;
    min-height: 22px;
    max-height: 22px;
}

/* ── 复选框 ── */
QCheckBox {
    spacing: 6px;
    color: #cccccc;
    font-size: 13px;
    background-color: transparent;
}
QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 1px solid #555555;
    background-color: #3c3c3c;
}

/* ── 消息框 ── */
QMessageBox {
    background-color: #1e1e1e;
    color: #cccccc;
}
QMessageBox QLabel {
    color: #cccccc;
    background-color: transparent;
}
QMessageBox QPushButton {
    background-color: #0e639c;
    color: #ffffff;
    border: 1px solid #0e639c;
    padding: 5px 16px;
}

/* ── 颜色对话框 ── */
QColorDialog {
    background-color: #1e1e1e;
}
"""

FONT_FAMILIES = [
    "Microsoft YaHei", "SimSun", "SimHei", "KaiTi", "FangSong",
    "Arial", "Helvetica", "Times New Roman", "Consolas", "Courier New",
    "Verdana", "Georgia", "Tahoma", "Segoe UI", "monospace",
]
FONT_WEIGHTS = ["normal", "bold", "100", "200", "300", "400", "500", "600", "700", "800", "900"]
FONT_STYLES = ["normal", "italic"]

_ATTR_LABELS = {
    "font_family": "字体族", "font_size": "字号", "font_weight": "粗细", "font_style": "样式",
    "color": "文字颜色", "background_color": "背景颜色",
    "border": "四周边框", "border_top": "上边框", "border_right": "右边框",
    "border_bottom": "下边框", "border_left": "左边框", "border_radius": "圆角",
    "width": "宽度", "height": "高度",
    "min_width": "最小宽度", "max_width": "最大宽度",
    "min_height": "最小高度", "max_height": "最大高度",
    "padding": "内边距", "margin": "外边距",
    "selection_background_color": "选中背景色", "selection_color": "选中文字色",
    "outline": "轮廓", "text_align": "文字对齐",
    "subcontrol_origin": "子控件原点", "subcontrol_position": "子控件位置",
    "spacing": "间距",
    "left": "左边距偏移",
}


class StyleController(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(   parent)
        self.setWindowTitle("样式控制器")
        self.setAttribute(Qt.WA_DeleteOnClose, False)
        self.resize(1200, 760)

        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), QColor("#1e1e1e"))
        self.setPalette(p)
        self._styles = load_styles()
        self._current_path = None
        self._current_widget_type = None
        self._current_subcontrol = "_self"
        self._prop_widgets = {}
        self._color_previews = {}
        self._building = False
        self._target_windows = self._scan_windows()
        self._layouts = load_all_layouts()
        self._selected_layout = None
        self._build_ui()
        self._populate_layout_combo()
        self._populate_tree()
        self.setStyleSheet(STYLE)

    # ── 扫描 ──────────────────────────────────────────────────────
    def _scan_windows(self):
        windows = {}
        cfg = load_config()
        for key in cfg:
            if key != "widget_controller":
                windows[key] = cfg[key].get("title", key)
        from PyQt5.QtWidgets import QApplication
        for w in QApplication.topLevelWidgets():
            if isinstance(w, QMainWindow) and hasattr(w, "_config_key"):
                key = w._config_key
                if key not in windows:
                    windows[key] = w.windowTitle() or key
        return windows

    def _get_target_window(self):
        key = self._target_combo.currentData()
        if not key:
            return None
        from PyQt5.QtWidgets import QApplication
        for w in QApplication.topLevelWidgets():
            if isinstance(w, QMainWindow) and hasattr(w, "_config_key") and w._config_key == key:
                return w
        return None

    # ── UI 构建 ───────────────────────────────────────────────────
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── 顶部栏 ──
        topbar = QWidget()
        topbar.setObjectName("topbar")
        top = QHBoxLayout(topbar)
        top.setContentsMargins(10, 5, 10, 5)
        top.setSpacing(8)
        top.addWidget(QLabel("目标窗口:"))
        self._target_combo = QComboBox()
        self._target_combo.setMinimumWidth(140)
        for key, title in self._target_windows.items():
            self._target_combo.addItem(f"{title} [{key}]", key)
        self._target_combo.setCurrentIndex(0)
        top.addWidget(self._target_combo)
        top.addWidget(QLabel("布局:"))
        self._layout_combo = QComboBox()
        self._layout_combo.setMinimumWidth(160)
        self._layout_combo.currentIndexChanged.connect(self._on_layout_changed)
        top.addWidget(self._layout_combo)
        refresh_btn = QPushButton("刷新")
        refresh_btn.setToolTip("重新加载布局和样式")
        refresh_btn.clicked.connect(self._refresh)
        top.addWidget(refresh_btn)
        top.addStretch()
        apply_btn = QPushButton("应用")
        apply_btn.setObjectName("apply_btn")
        apply_btn.clicked.connect(self._apply_styles)
        top.addWidget(apply_btn)
        root.addWidget(topbar)

        # ── 主体 ──
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(1)

        # 左侧面板
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)
        left_header = QLabel("样式层级")
        left_header.setObjectName("panel_header")
        left_layout.addWidget(left_header)
        self._tree = QTreeWidget()
        self._tree.setHeaderLabels(["层级", "预览"])
        self._tree.setColumnWidth(0, 280)
        self._tree.setRootIsDecorated(True)
        self._tree.setExpandsOnDoubleClick(True)
        self._tree.currentItemChanged.connect(self._on_tree_selection)
        left_layout.addWidget(self._tree)
        splitter.addWidget(left_panel)

        # 右侧面板
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        right_header = QLabel("属性编辑")
        right_header.setObjectName("panel_header")
        right_layout.addWidget(right_header)
        self._prop_scroll = QScrollArea()
        self._prop_scroll.setWidgetResizable(True)
        self._prop_container = QWidget()
        self._prop_layout = QVBoxLayout(self._prop_container)
        self._prop_layout.setContentsMargins(8, 6, 8, 6)
        self._prop_layout.setSpacing(6)
        self._prop_scroll.setWidget(self._prop_container)
        right_layout.addWidget(self._prop_scroll)
        splitter.addWidget(right_panel)
        splitter.setSizes([350, 850])
        root.addWidget(splitter, 1)

        # ── 状态栏 ──
        statusbar = QWidget()
        statusbar.setObjectName("statusbar")
        statusbar.setFixedHeight(26)
        sb_layout = QHBoxLayout(statusbar)
        sb_layout.setContentsMargins(10, 0, 10, 0)
        self._status = QLabel("就绪")
        self._status.setObjectName("status_lbl")
        sb_layout.addWidget(self._status)
        root.addWidget(statusbar)

    # ── 布局选择 ──────────────────────────────────────────────────
    def _populate_layout_combo(self):
        self._layout_combo.blockSignals(True)
        self._layout_combo.clear()
        self._layout_combo.addItem("（不显示布局控件）", None)
        self._layouts = load_all_layouts()
        for lname in sorted(self._layouts.keys()):
            self._layout_combo.addItem(lname, lname)
        self._layout_combo.blockSignals(False)

    def _on_layout_changed(self, index):
        self._selected_layout = self._layout_combo.currentData()
        self._current_path = None
        self._current_widget_type = None
        self._current_subcontrol = "_self"
        self._clear_prop_panel()
        self._populate_tree()
        # 应用布局到目标窗口
        if self._selected_layout:
            win = self._get_target_window()
            if win:
                from app.core.layout_loader import load_layout
                from app.core.layout_engine import apply_to_window
                node = load_layout(self._selected_layout)
                if node:
                    apply_to_window(win, node)
                    from app.core.window_config import update_window_config
                    update_window_config(self._target_combo.currentData() or "main", layout=self._selected_layout)
                    self._status.setText(f"已切换到布局 [{self._selected_layout}] → 窗口 [{self._target_combo.currentData()}]")

    # ── 树构建 ────────────────────────────────────────────────────
    def _populate_tree(self):
        self._tree.clear()
        self._styles = load_styles()

        # 0. 布局控件（仅在选择了布局时显示）
        if self._selected_layout and self._selected_layout in self._layouts:
            lnode = self._layouts[self._selected_layout]
            layout_root = QTreeWidgetItem(self._tree,
                [f"布局控件 [{self._selected_layout}]", lnode.get("type", "")])
            layout_root.setData(0, Qt.UserRole, ("_section",))
            font = layout_root.font(0)
            font.setBold(True)
            layout_root.setFont(0, font)
            self._build_widget_tree(lnode, layout_root, "0")
            self._tree.addTopLevelItem(layout_root)

        # 1. 全局基础样式
        preview = self._preview_dict(self._styles.get("global", {}))
        global_item = QTreeWidgetItem(self._tree, ["全局基础样式", preview])
        global_item.setData(0, Qt.UserRole, ("global",))
        font = global_item.font(0)
        font.setBold(True)
        global_item.setFont(0, font)

        # 2. 控件类型样式
        types_root = QTreeWidgetItem(self._tree, ["控件类型样式", ""])
        types_root.setData(0, Qt.UserRole, ("_section",))
        font = types_root.font(0)
        font.setBold(True)
        types_root.setFont(0, font)

        types_styles = self._styles.get("types", {})
        for tname in WIDGET_TYPE_OPTIONS:
            preview = self._preview_dict(types_styles.get(tname, {}))
            child = QTreeWidgetItem(types_root, [tname, preview])
            child.setData(0, Qt.UserRole, ("types", tname))

        # 3. 窗口样式
        win_root = QTreeWidgetItem(self._tree, ["窗口样式", ""])
        win_root.setData(0, Qt.UserRole, ("_section",))
        font = win_root.font(0)
        font.setBold(True)
        win_root.setFont(0, font)

        win_styles = self._styles.get("windows", {})
        for key in self._target_windows:
            preview = self._preview_dict(win_styles.get(key, {}))
            child = QTreeWidgetItem(win_root, [key, preview])
            child.setData(0, Qt.UserRole, ("windows", key))

        self._tree.expandAll()

    def _build_widget_tree(self, node, parent_item, path):
        """递归构建布局控件树，每个节点显示名称(类型) + 样式预览。"""
        ntype = node.get("type", "")
        if not ntype:
            return
        wid = generate_widget_id(ntype, node.get("name", ""), node.get("label", ""), path)
        wstyle = self._styles.get("widgets", {}).get(wid, {})
        preview = self._preview_dict(wstyle)
        label = node.get("label", "")
        display = f"{wid}  ({ntype})" if not label else f"{wid}  [{label}]  ({ntype})"

        item = QTreeWidgetItem(parent_item, [display, preview])
        item.setData(0, Qt.UserRole, ("widget", wid, ntype))

        for i, child in enumerate(node.get("children", [])):
            self._build_widget_tree(child, item, f"{path}/{i}")

    def _preview_dict(self, d):
        if not d:
            return ""
        d = _normalize_style_dict(d)
        self_props = d.get("_self", {})
        parts = []
        if "color" in self_props:
            parts.append(f"color:{self_props['color']}")
        if "background_color" in self_props:
            parts.append(f"bg:{self_props['background_color']}")
        if "font_size" in self_props:
            parts.append(self_props["font_size"])
        if "font_weight" in self_props:
            parts.append(self_props["font_weight"])
        result = ", ".join(parts[:3])
        other_count = len(d) - (1 if "_self" in d else 0)
        if other_count > 0:
            result += f"  [+{other_count}]"
        return result

    # ── 树选择 ────────────────────────────────────────────────────
    def _on_tree_selection(self, current, previous):
        if not current:
            return
        path = current.data(0, Qt.UserRole)
        if not path or path[0] == "_section":
            self._current_path = None
            self._current_widget_type = None
            self._clear_prop_panel()
            return

        self._current_path = path
        self._current_subcontrol = "_self"
        if path[0] == "types":
            self._current_widget_type = path[1]
        elif path[0] == "widget":
            self._current_widget_type = path[2]
        else:
            self._current_widget_type = None

        style_dict = self._get_style_at_path(path)
        inherited = self._get_inherited(path)
        self._build_prop_panel(style_dict, inherited)
        self._status.setText(f"编辑 → {self._path_label(path)}")

    # ── 路径 → 样式存取 ───────────────────────────────────────────
    def _get_style_at_path(self, path):
        """返回规范化的 style dict（含 _self 和子控件 key）。"""
        raw = {}
        if path[0] == "global":
            raw = self._styles.get("global", {})
        elif path[0] == "types":
            raw = self._styles.get("types", {}).get(path[1], {})
        elif path[0] == "windows":
            raw = self._styles.get("windows", {}).get(path[1], {})
        elif path[0] == "widget":
            raw = self._styles.get("widgets", {}).get(path[1], {})
        return _normalize_style_dict(raw)

    def _set_style_at_path(self, path, subcontrol_props, subcontrol=None):
        """将 subcontrol_props 写入 path 处样式 dict 的 subcontrol key 中。"""
        subcontrol = subcontrol or self._current_subcontrol
        # 读取现有完整 dict
        full = _normalize_style_dict(self._get_style_at_path_raw(path))
        # 清理传入的属性
        clean = {k: v for k, v in subcontrol_props.items() if v and v.strip()}
        if clean:
            full[subcontrol] = clean
        elif subcontrol in full:
            del full[subcontrol]
        # 如果只剩空的 _self，视为空 dict
        if list(full.keys()) == ["_self"] and not full["_self"]:
            full = {}
        self._set_style_at_path_raw(path, full)

    def _get_style_at_path_raw(self, path):
        """返回原始 dict（未经 normalize），供 _set_style_at_path 读写。"""
        if path[0] == "global":
            return self._styles.get("global", {})
        elif path[0] == "types":
            return self._styles.get("types", {}).get(path[1], {})
        elif path[0] == "windows":
            return self._styles.get("windows", {}).get(path[1], {})
        elif path[0] == "widget":
            return self._styles.get("widgets", {}).get(path[1], {})
        return {}

    def _set_style_at_path_raw(self, path, full):
        """将规范化 full dict 写回 self._styles。"""
        if path[0] == "global":
            self._styles["global"] = full
        elif path[0] == "types":
            self._styles.setdefault("types", {})
            if full:
                self._styles["types"][path[1]] = full
            elif path[1] in self._styles["types"]:
                del self._styles["types"][path[1]]
        elif path[0] == "windows":
            self._styles.setdefault("windows", {})
            if full:
                self._styles["windows"][path[1]] = full
            elif path[1] in self._styles["windows"]:
                del self._styles["windows"][path[1]]
        elif path[0] == "widget":
            self._styles.setdefault("widgets", {})
            if full:
                self._styles["widgets"][path[1]] = full
            elif path[1] in self._styles["widgets"]:
                del self._styles["widgets"][path[1]]

    def _get_inherited(self, path, subcontrol=None):
        """返回当前 subcontrol 从上级级联继承的合并属性。"""
        subcontrol = subcontrol or self._current_subcontrol
        styles = self._styles
        if path[0] == "widget":
            merged = {}
            g = _normalize_style_dict(styles.get("global", {}))
            merged.update(g.get(subcontrol, {}))
            wtype = path[2] if len(path) > 2 else None
            if wtype:
                t = _normalize_style_dict(styles.get("types", {}).get(wtype, {}))
                merged.update(t.get(subcontrol, {}))
            win_key = self._target_combo.currentData()
            if win_key:
                w = _normalize_style_dict(styles.get("windows", {}).get(win_key, {}))
                merged.update(w.get(subcontrol, {}))
            return merged
        elif path[0] == "types":
            g = _normalize_style_dict(styles.get("global", {}))
            return dict(g.get(subcontrol, {}))
        elif path[0] == "windows":
            g = _normalize_style_dict(styles.get("global", {}))
            return dict(g.get(subcontrol, {}))
        elif path[0] == "global":
            return {}
        return {}

    # ── 动态属性面板 ──────────────────────────────────────────────
    def _clear_prop_panel(self):
        while self._prop_layout.count():
            item = self._prop_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())
        self._prop_widgets.clear()
        self._color_previews.clear()

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())

    def _build_prop_panel(self, style_dict, inherited):
        self._clear_prop_panel()
        self._prop_widgets = {}
        self._color_previews = {}
        layout = self._prop_layout

        # ── 子控件选择器 ──
        sub_controls = SUB_CONTROLS_OF.get(self._current_widget_type, ["_self"]) if self._current_widget_type else ["_self"]
        if len(sub_controls) > 1:
            sc_row = QHBoxLayout()
            sc_row.setSpacing(6)
            sc_row.addWidget(QLabel("控件内样式列表:"))
            sc_combo = QComboBox()
            sc_combo.addItems(sub_controls)
            idx = sub_controls.index(self._current_subcontrol) if self._current_subcontrol in sub_controls else 0
            sc_combo.setCurrentIndex(idx)
            sc_combo.currentIndexChanged.connect(lambda i: self._on_subcontrol_changed(sub_controls[i]))
            sc_row.addWidget(sc_combo)
            sc_row.addStretch()
            sc_wrapper = QWidget()
            sc_wrapper.setLayout(sc_row)
            layout.addWidget(sc_wrapper)

        # ── 确定当前子控件支持的属性列表 ──
        if self._current_widget_type:
            sc_schema = WIDGET_STYLE_SCHEMA.get(self._current_widget_type, {"_self": []})
            if self._current_subcontrol == "_self":
                prop_keys = TYPE_PROPERTIES.get(self._current_widget_type, [])
            else:
                prop_keys = list(sc_schema.get(self._current_subcontrol, []))
        else:
            prop_keys = TYPE_PROPERTIES.get("VBox", [])

        for group_name, keys in PROPERTY_GROUPS:
            relevant = [k for k in keys if k in prop_keys]
            if not relevant:
                continue
            group = QGroupBox(group_name)
            form = QFormLayout()
            form.setSpacing(4)

            for key in relevant:
                inh_val = inherited.get(key, "")
                inh_text = f" ↑{inh_val}" if inh_val else ""

                if key == "font_family":
                    self._add_combo_field(form, key, _ATTR_LABELS[key], FONT_FAMILIES, inh_text)
                elif key == "font_weight":
                    self._add_combo_field(form, key, _ATTR_LABELS[key], FONT_WEIGHTS, inh_text)
                elif key == "font_style":
                    self._add_combo_field(form, key, _ATTR_LABELS[key], FONT_STYLES, inh_text)
                elif key in ("color", "background_color"):
                    self._add_color_field(form, key, _ATTR_LABELS[key], inh_text)
                else:
                    self._add_text_field(form, key, _ATTR_LABELS[key], inh_text)

            group.setLayout(form)
            layout.addWidget(group)

        hint = QLabel("空属性自动从上级继承，填写值则覆盖上级")
        hint.setObjectName("inherited_hint")
        layout.addWidget(hint)

        btn_row = QHBoxLayout()
        btn_row.addStretch()

        delete_btn = QPushButton("删除此级样式")
        delete_btn.clicked.connect(self._clear_current)
        btn_row.addWidget(delete_btn)

        save_btn = QPushButton("保存")
        save_btn.setObjectName("save_btn")
        save_btn.clicked.connect(self._save_current)
        btn_row.addWidget(save_btn)
        layout.addLayout(btn_row)
        layout.addStretch()

        # 填充当前值（从当前子控件 key 读取）
        self._building = True
        sub_style = style_dict.get(self._current_subcontrol, {})
        for key, widget in self._prop_widgets.items():
            val = sub_style.get(key, "")
            if isinstance(widget, QComboBox):
                if val:
                    idx = widget.findText(val)
                    if idx >= 0:
                        widget.setCurrentIndex(idx)
                    else:
                        widget.setCurrentIndex(0)
                else:
                    widget.setCurrentIndex(0)
            else:
                widget.blockSignals(True)
                widget.setText(val)
                widget.blockSignals(False)
            if key in self._color_previews:
                self._update_color_preview(key, val)
        self._building = False

    def _add_text_field(self, form, key, label, inh_text):
        row = QHBoxLayout()
        row.setSpacing(4)
        edit = QLineEdit()
        edit.setPlaceholderText(inh_text if inh_text else "继承自上级…")
        edit.textChanged.connect(lambda v, k=key: self._on_prop_changed(k, v))
        self._prop_widgets[key] = edit
        row.addWidget(edit)
        wrapper = QWidget()
        wrapper.setLayout(row)
        form.addRow(QLabel(label), wrapper)

    def _add_combo_field(self, form, key, label, items, inh_text):
        row = QHBoxLayout()
        row.setSpacing(4)
        combo = QComboBox()
        combo.addItem(f"（继承）" + (f" {inh_text}" if inh_text else ""), "")
        combo.addItems(items)
        combo.currentTextChanged.connect(
            lambda v, k=key: self._on_prop_changed(k, v if not v.startswith("（继承）") else ""))
        self._prop_widgets[key] = combo
        row.addWidget(combo)
        wrapper = QWidget()
        wrapper.setLayout(row)
        form.addRow(QLabel(label), wrapper)

    def _add_color_field(self, form, key, label, inh_text):
        row = QHBoxLayout()
        row.setSpacing(4)
        edit = QLineEdit()
        edit.setPlaceholderText(inh_text if inh_text else "#rrggbb")
        edit.textChanged.connect(lambda v, k=key: self._on_prop_changed(k, v))
        self._prop_widgets[key] = edit

        preview = QFrame()
        preview.setObjectName("color_preview")
        preview.setFrameShape(QFrame.Box)
        self._color_previews[key] = preview

        btn = QPushButton("…")
        btn.setObjectName("color_btn")
        btn.setToolTip("拾取颜色")
        btn.clicked.connect(lambda checked, k=key, e=edit, p=preview: self._pick_color(k, e, p))

        row.addWidget(edit)
        row.addWidget(preview)
        row.addWidget(btn)
        wrapper = QWidget()
        wrapper.setLayout(row)
        form.addRow(QLabel(label), wrapper)

    def _pick_color(self, key, edit, preview):
        cur = edit.text().strip()
        init_color = QColor(cur) if cur and QColor(cur).isValid() else QColor(Qt.white)
        color = QColorDialog.getColor(init_color, self, "选择颜色")
        if color.isValid():
            edit.setText(color.name())
            self._update_color_preview(key, color.name())

    def _update_color_preview(self, key, value):
        preview = self._color_previews.get(key)
        if not preview:
            return
        if value and QColor(value).isValid():
            preview.setStyleSheet(f"background-color: {value};")
        else:
            preview.setStyleSheet("")

    def _on_subcontrol_changed(self, subcontrol):
        """用户切换子控件下拉，重建属性面板。"""
        self._current_subcontrol = subcontrol
        if not self._current_path:
            return
        style_dict = self._get_style_at_path(self._current_path)
        inherited = self._get_inherited(self._current_path, subcontrol)
        self._build_prop_panel(style_dict, inherited)

    # ── 属性变更 ──────────────────────────────────────────────────
    def _on_prop_changed(self, key, value):
        pass  # 属性变更不自动预览，用户点击"应用"手动触发

    def _read_fields(self):
        result = {}
        for key, widget in self._prop_widgets.items():
            if isinstance(widget, QComboBox):
                val = widget.currentText().strip()
                if val and not val.startswith("（继承）"):
                    result[key] = val
            else:
                val = widget.text().strip()
                if val:
                    result[key] = val
        return result

    # ── 保存 / 清除 / 应用 ───────────────────────────────────────
    def _commit_fields(self):
        """将当前表单值写入 self._styles 并持久化到 styles.json，返回旧 path 供恢复选中。"""
        if not self._current_path:
            return None
        style_dict = self._read_fields()
        self._set_style_at_path(self._current_path, style_dict, self._current_subcontrol)
        save_styles(self._styles)
        return self._current_path

    def _save_current(self):
        if not self._current_path:
            self._status.setText("请先在左侧树中选择样式节点")
            return
        saved_path = self._commit_fields()
        if saved_path is None:
            return
        self._populate_tree()
        self._select_path(saved_path)
        self._status.setText(f"已保存 → {self._path_label(saved_path)}")
        self._do_apply()

    def _clear_current(self):
        if not self._current_path:
            return
        sc_label = self._current_subcontrol if self._current_subcontrol != "_self" else "自身样式"
        reply = QMessageBox.question(self, "确认",
                                     f"删除 {self._path_label(self._current_path)} 的 [{sc_label}] 样式？",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
        # 清除当前子控件
        full = _normalize_style_dict(self._get_style_at_path_raw(self._current_path))
        if self._current_subcontrol in full:
            del full[self._current_subcontrol]
        if list(full.keys()) == ["_self"] and not full["_self"]:
            full = {}
        self._set_style_at_path_raw(self._current_path, full)
        save_styles(self._styles)
        self._populate_tree()
        self._clear_prop_panel()
        self._current_path = None
        self._current_widget_type = None
        self._status.setText("已删除样式")

    def _apply_styles(self):
        """点击'应用'按钮：先提交表单到内存+磁盘，再应用到窗口。"""
        self._commit_fields()
        self._do_apply()

    def _do_apply(self):
        win = self._get_target_window()
        if not win:
            self._status.setText("未找到目标窗口")
            return
        try:
            apply_to_widget(win, self._target_combo.currentData() or "main", self._styles)
            self._status.setText("样式已应用到目标窗口")
        except Exception as e:
            self._status.setText(f"❌ 应用失败: {e}")

    # ── 辅助 ──────────────────────────────────────────────────────
    def _path_label(self, path):
        if path[0] == "global":
            return "全局基础样式"
        if path[0] == "types":
            return f"控件类型样式 → {path[1]}"
        if path[0] == "windows":
            return f"窗口样式 → {path[1]}"
        if path[0] == "widget":
            wtype = path[2] if len(path) > 2 else ""
            return f"控件实例 → {path[1]} ({wtype})"
        return " → ".join(path)

    def _select_path(self, target_path):
        """在树中查找并选中匹配路径的项。"""
        for i in range(self._tree.topLevelItemCount()):
            root = self._tree.topLevelItem(i)
            if self._match_item(root, target_path):
                return
            for j in range(root.childCount()):
                if self._match_item(root.child(j), target_path):
                    return
                for k in range(root.child(j).childCount()):
                    if self._match_item(root.child(j).child(k), target_path):
                        return
                    for m in range(root.child(j).child(k).childCount()):
                        if self._match_item(root.child(j).child(k).child(m), target_path):
                            return

    def _match_item(self, item, target_path):
        data = item.data(0, Qt.UserRole)
        if data and tuple(data) == target_path:
            self._tree.setCurrentItem(item)
            return True
        return False

    def _refresh(self):
        self._target_windows = self._scan_windows()
        current_key = self._target_combo.currentData()
        self._target_combo.blockSignals(True)
        self._target_combo.clear()
        for key, title in self._target_windows.items():
            self._target_combo.addItem(f"{title} [{key}]", key)
        idx = self._target_combo.findData(current_key)
        if idx >= 0:
            self._target_combo.setCurrentIndex(idx)
        self._target_combo.blockSignals(False)
        self._styles = load_styles()
        self._populate_layout_combo()
        self._populate_tree()
        self._clear_prop_panel()
        self._current_path = None
        self._current_widget_type = None
        self._current_subcontrol = "_self"
        self._status.setText("已刷新")

    # ── 公开 API ──────────────────────────────────────────────────
    @staticmethod
    def apply_styles(window_key):
        cfg = load_config()
        if window_key in cfg:
            from PyQt5.QtWidgets import QApplication
            for w in QApplication.topLevelWidgets():
                if isinstance(w, QMainWindow) and hasattr(w, "_config_key") and w._config_key == window_key:
                    apply_to_widget(w, window_key)
                    return

    @staticmethod
    def update_window(window):
        key = getattr(window, "_config_key", "main")
        apply_to_widget(window, key)
