"""
EventEditor — 事件编辑器对话框。

从动作注册表生成可选动作列表，用户选择动作 + 填写参数，
自动生成 Python 代码用于事件绑定。

用法：
    code, ok = EventEditor.edit_event(parent, widget_type, layout_widgets, event_key, current_code="")
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem,
    QComboBox, QLineEdit, QSpinBox, QDoubleSpinBox, QCheckBox, QPushButton,
    QLabel, QFormLayout, QWidget, QSplitter, QGroupBox, QMessageBox,
    QHeaderView,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

from app.core.action_registry import (
    get_actions, get_categories, generate_code, try_parse_code,
    get_widget_actions, get_event_types_for_type, ALL_EVENT_TYPES,
)


class EventEditor(QDialog):
    """事件编辑器对话框 — 选择动作 + 填写参数 → 生成代码。"""

    def __init__(self, parent=None, widget_type="", layout_widgets=None,
                 event_key="click", current_code=""):
        super().__init__(parent)
        self._widget_type = widget_type
        self._layout_widgets = layout_widgets or []
        self._event_key = event_key
        self._current_action = None
        self._param_widgets = {}    # param_name → edit widget
        self._result_code = ""

        self.setWindowTitle("事件编辑器")
        self.resize(820, 540)
        self.setMinimumSize(680, 420)

        self._build_ui()
        self._load_actions()
        self.setStyleSheet(_STYLE)

        # 如果有已有代码，尝试解析回动作选择
        if current_code:
            self._try_restore(current_code)

        # 初始化预览
        self._update_preview()

    # ── 公开 API ──────────────────────────────────────────────

    def get_result_code(self):
        return self._result_code

    def get_event_key(self):
        return self._event_key

    @staticmethod
    def edit_event(parent=None, widget_type="", layout_widgets=None,
                   event_key="click", current_code=""):
        """静态方法：打开对话框并返回 (code, event_key, ok)。"""
        dlg = EventEditor(parent, widget_type, layout_widgets,
                          event_key, current_code)
        ok = dlg.exec_() == QDialog.Accepted
        return (dlg.get_result_code(), dlg.get_event_key(), ok)

    # ── UI 构建 ───────────────────────────────────────────────

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(8)

        # ── 顶部：事件类型选择 ──
        top = QHBoxLayout()
        top.addWidget(QLabel("事件类型:"))
        self._event_combo = QComboBox()
        self._event_combo.setMinimumWidth(160)
        available = get_event_types_for_type(self._widget_type)
        for et in available:
            self._event_combo.addItem(_event_label(et), et)
        if self._event_key in available:
            self._event_combo.setCurrentIndex(available.index(self._event_key))
        self._event_combo.currentIndexChanged.connect(self._on_event_changed)
        top.addWidget(self._event_combo)
        top.addStretch()
        self._header_label = QLabel("")
        top.addWidget(self._header_label)
        root.addLayout(top)

        # ── 主体：动作列表 + 参数表单 ──
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(1)

        # 左侧：动作列表
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(4)

        self._search_edit = QLineEdit()
        self._search_edit.setPlaceholderText("搜索动作...")
        self._search_edit.textChanged.connect(self._on_search)
        left_layout.addWidget(self._search_edit)

        self._action_tree = QTreeWidget()
        self._action_tree.setHeaderHidden(True)
        self._action_tree.setRootIsDecorated(True)
        self._action_tree.setIndentation(16)
        self._action_tree.currentItemChanged.connect(self._on_action_selected)
        left_layout.addWidget(self._action_tree)

        splitter.addWidget(left)

        # 右侧：参数表单
        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(8, 0, 0, 0)
        right_layout.setSpacing(8)

        param_header = QLabel("参数设置")
        param_header.setObjectName("section_header")
        right_layout.addWidget(param_header)

        self._desc_label = QLabel("")
        self._desc_label.setWordWrap(True)
        self._desc_label.setObjectName("desc_label")
        right_layout.addWidget(self._desc_label)

        self._param_widget_container = QWidget()
        self._param_form = QFormLayout(self._param_widget_container)
        self._param_form.setContentsMargins(0, 4, 0, 0)
        self._param_form.setSpacing(6)
        right_layout.addWidget(self._param_widget_container)
        right_layout.addStretch()

        splitter.addWidget(right)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 3)
        root.addWidget(splitter, 1)

        # ── 底部：代码预览 ──
        preview_group = QGroupBox("生成代码")
        preview_layout = QVBoxLayout(preview_group)
        self._preview_label = QLabel("")
        self._preview_label.setWordWrap(True)
        self._preview_label.setObjectName("preview_label")
        self._preview_label.setMinimumHeight(36)
        self._preview_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        preview_layout.addWidget(self._preview_label)
        root.addWidget(preview_group)

        # ── 按钮行 ──
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        test_btn = QPushButton("测试执行")
        test_btn.setObjectName("test_btn")
        test_btn.clicked.connect(self._test_run)
        btn_row.addWidget(test_btn)
        ok_btn = QPushButton("确定")
        ok_btn.clicked.connect(self._accept)
        btn_row.addWidget(ok_btn)
        cancel_btn = QPushButton("取消")
        cancel_btn.setObjectName("cancel_btn")
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)
        root.addLayout(btn_row)

    # ── 动作列表 ──────────────────────────────────────────────

    def _load_actions(self):
        self._action_tree.clear()
        self._all_action_items = []
        categories = get_categories()
        for cat in categories:
            cat_item = QTreeWidgetItem([cat])
            cat_item.setFlags(cat_item.flags() & ~Qt.ItemIsSelectable)
            cat_item.setData(0, Qt.UserRole, None)  # 标记为分组
            cat_item.setExpanded(True)
            self._action_tree.addTopLevelItem(cat_item)

            actions = get_actions(category=cat)
            # 控件专用分类只显示当前控件类型的动作
            if cat == "控件专用":
                widget_actions = get_widget_actions(self._widget_type)
                actions = [a for a in actions if a in widget_actions]

            for action in actions:
                item = QTreeWidgetItem([f"  {action.name}"])
                item.setData(0, Qt.UserRole, action)
                item.setToolTip(0, action.description)
                cat_item.addChild(item)
                self._all_action_items.append((item, action))

            # 隐藏空分类
            if cat_item.childCount() == 0:
                self._action_tree.takeTopLevelItem(
                    self._action_tree.indexOfTopLevelItem(cat_item))

        if self._action_tree.topLevelItemCount() > 0:
            # 展开第一个分类并选中第一个动作
            first_cat = self._action_tree.topLevelItem(0)
            if first_cat.childCount() > 0:
                first_action = first_cat.child(0)
                self._action_tree.setCurrentItem(first_action)

    def _on_search(self, text):
        t = text.strip().lower()
        for i in range(self._action_tree.topLevelItemCount()):
            cat_item = self._action_tree.topLevelItem(i)
            visible_children = 0
            for j in range(cat_item.childCount()):
                child = cat_item.child(j)
                action = child.data(0, Qt.UserRole)
                if not t or t in action.name.lower() or t in action.description.lower():
                    child.setHidden(False)
                    visible_children += 1
                else:
                    child.setHidden(True)
            cat_item.setHidden(visible_children == 0)

    def _on_action_selected(self, current, _previous):
        if not current:
            return
        action = current.data(0, Qt.UserRole)
        if action is None or not hasattr(action, 'id'):
            return
        self._current_action = action
        self._desc_label.setText(action.description)
        self._build_param_form(action)
        self._update_preview()

    # ── 参数表单 ──────────────────────────────────────────────

    def _build_param_form(self, action):
        # 清除旧表单
        while self._param_form.rowCount() > 0:
            self._param_form.removeRow(0)
        self._param_widgets.clear()

        for param in action.params:
            if param.param_type == "widget_ref":
                widget = QComboBox()
                for name, wtype in self._layout_widgets:
                    if name:
                        widget.addItem(f"{name} ({wtype})", name)
                if self._layout_widgets:
                    widget.insertSeparator(0)
                    widget.insertItem(0, "（触发源）", "{source}")
                    widget.setCurrentIndex(0)
                widget.setMinimumWidth(160)
            elif param.param_type == "choice":
                widget = QComboBox()
                for val, label in (param.options or []):
                    widget.addItem(label, val)
                widget.setMinimumWidth(160)
            elif param.param_type == "number":
                widget = QSpinBox()
                widget.setRange(-999999, 999999)
                widget.setMinimumWidth(100)
                try:
                    widget.setValue(int(param.default) if param.default else 0)
                except ValueError:
                    widget.setValue(0)
            elif param.param_type == "bool":
                widget = QCheckBox()
                widget.setChecked(param.default.lower() in ("true", "1", "yes"))
            else:  # string
                widget = QLineEdit()
                widget.setPlaceholderText(param.label)
                widget.setText(param.default)
                widget.setMinimumWidth(160)

            widget.setObjectName(f"param_{param.name}")
            widget.setToolTip(param.label)
            # 参数变化时实时更新预览
            if hasattr(widget, 'currentIndexChanged'):
                widget.currentIndexChanged.connect(self._update_preview)
            elif hasattr(widget, 'textChanged'):
                widget.textChanged.connect(self._update_preview)
            elif hasattr(widget, 'valueChanged'):
                widget.valueChanged.connect(self._update_preview)
            elif hasattr(widget, 'toggled'):
                widget.toggled.connect(self._update_preview)

            self._param_form.addRow(param.label + ":", widget)
            self._param_widgets[param.name] = widget

    # ── 代码生成 ──────────────────────────────────────────────

    def _get_params(self):
        """从参数表单收集当前参数值。"""
        if not self._current_action:
            return {}
        params = {}
        for param in self._current_action.params:
            w = self._param_widgets.get(param.name)
            if w is None:
                params[param.name] = param.default
            elif isinstance(w, QComboBox):
                params[param.name] = w.currentData() or w.currentText()
            elif isinstance(w, QSpinBox):
                params[param.name] = str(w.value())
            elif isinstance(w, QDoubleSpinBox):
                params[param.name] = str(w.value())
            elif isinstance(w, QCheckBox):
                params[param.name] = str(w.isChecked())
            elif isinstance(w, QLineEdit):
                val = w.text()
                # 对字符串值做引号内的单引号转义
                safe_val = val.replace("\\", "\\\\").replace("'", "\\'")
                params[param.name] = safe_val
            else:
                params[param.name] = param.default
        return params

    def _update_preview(self):
        if self._current_action is None:
            self._preview_label.setText("")
            return
        params = self._get_params()
        # 模板中用 {source} 隐式引用触发源控件，注入 widget.objectName()
        if "{source}" in self._current_action.code_template:
            params.setdefault("source", "widget.objectName()")
        # widget_ref 参数若选"触发源"，同样替换
        for k, v in list(params.items()):
            if v == "{source}":
                params[k] = "widget.objectName()" if "find_widget" in self._current_action.code_template else "widget"
        try:
            code = self._current_action.code_template.format(**params)
            self._preview_label.setText(code)
        except Exception:
            self._preview_label.setText("（参数不完整）")

    # ── 事件类型 ──────────────────────────────────────────────

    def _on_event_changed(self, _idx):
        self._event_key = self._event_combo.currentData()

    # ── 恢复已有代码 ──────────────────────────────────────────

    def _try_restore(self, code):
        """尝试将已有代码反向匹配到注册动作。"""
        result = try_parse_code(code)
        if result is None:
            self._header_label.setText("（未识别的自定义代码，可重新选择动作覆盖）")
            return
        action_id, params = result
        # 在树中找到对应动作并选中
        for i in range(self._action_tree.topLevelItemCount()):
            cat_item = self._action_tree.topLevelItem(i)
            for j in range(cat_item.childCount()):
                child = cat_item.child(j)
                action = child.data(0, Qt.UserRole)
                if action and hasattr(action, 'id') and action.id == action_id:
                    self._action_tree.setCurrentItem(child)
                    # 回填参数
                    for pname, pval in params.items():
                        w = self._param_widgets.get(pname)
                        if w is None:
                            continue
                        if isinstance(w, QComboBox):
                            idx = w.findData(pval)
                            if idx >= 0:
                                w.setCurrentIndex(idx)
                        elif isinstance(w, QLineEdit):
                            w.setText(pval)
                        elif isinstance(w, QSpinBox):
                            try:
                                w.setValue(int(pval))
                            except ValueError:
                                pass
                    self._header_label.setText(f"（已识别: {action.name}）")
                    return

    # ── 测试执行 ──────────────────────────────────────────────

    def _test_run(self):
        code = self._preview_label.text()
        if not code:
            return
        # 测试执行：在无 widget 的环境中尝试运行
        try:
            exec(code, {"widget": None, "find_widget": lambda n: None, "window": None, "app": None})
            QMessageBox.information(self, "测试结果", "代码语法正确，可以绑定。")
        except Exception as e:
            QMessageBox.warning(self, "测试结果", f"执行出错:\n{e}")

    def _accept(self):
        code = self._preview_label.text()
        if not code or code == "（参数不完整）":
            QMessageBox.warning(self, "提示", "请先选择一个动作并填写参数。")
            return
        # 验证代码语法可执行
        try:
            compile(code, "<event>", "exec")
        except SyntaxError as e:
            QMessageBox.warning(self, "代码错误", f"生成的代码有语法错误:\n{e}")
            return
        self._result_code = code
        self.accept()


# ── 事件类型中文标签 ────────────────────────────────────────────

_EVENT_LABELS = {
    "click": "点击 (鼠标)",
    "double_click": "双击",
    "right_click": "右键点击",
    "enter": "鼠标进入",
    "leave": "鼠标离开",
    "hover": "悬停",
    "drag": "拖入",
    "changed": "值变更",
    "clicked": "点击 (信号)",
    "toggled": "切换状态",
    "return_pressed": "回车键",
    "tab_changed": "标签页切换",
    "item_activated": "项目激活",
}


def _event_label(key):
    return _EVENT_LABELS.get(key, key)


# ── 暗色样式 ──────────────────────────────────────────────────

_STYLE = """
QDialog {
    background-color: #1e1e1e;
    color: #cccccc;
}
QLabel {
    color: #cccccc;
    background-color: transparent;
    font-size: 13px;
}
QLabel#section_header {
    font-size: 12px;
    font-weight: bold;
    color: #8a8a8a;
    padding: 4px 0;
}
QLabel#desc_label {
    color: #8a8a8a;
    font-size: 12px;
    padding: 4px 0;
    min-height: 20px;
}
QTreeWidget {
    background-color: #252526;
    color: #cccccc;
    border: 1px solid #3c3c3c;
    font-size: 13px;
}
QTreeWidget::item {
    padding: 3px 4px;
    background-color: transparent;
    color: #cccccc;
}
QTreeWidget::item:selected {
    background-color: #094771;
    color: #ffffff;
}
QTreeWidget::item:hover {
    background-color: #2a2d2e;
}
QLineEdit {
    background-color: #3c3c3c;
    color: #cccccc;
    border: 1px solid #3c3c3c;
    padding: 4px 8px;
    font-size: 13px;
}
QLineEdit:focus {
    border-color: #007acc;
}
QComboBox {
    background-color: #3c3c3c;
    color: #cccccc;
    border: 1px solid #3c3c3c;
    padding: 4px 8px;
    font-size: 13px;
}
QComboBox:hover { border-color: #007acc; }
QComboBox::drop-down { border: none; width: 20px; }
QComboBox QAbstractItemView {
    background-color: #252526;
    color: #cccccc;
    selection-background-color: #094771;
    border: 1px solid #3c3c3c;
    outline: none;
}
QSpinBox, QDoubleSpinBox {
    background-color: #3c3c3c;
    color: #cccccc;
    border: 1px solid #3c3c3c;
    padding: 4px 8px;
    font-size: 13px;
}
QSpinBox:focus, QDoubleSpinBox:focus { border-color: #007acc; }
QCheckBox {
    color: #cccccc;
    background-color: transparent;
    font-size: 13px;
}
QGroupBox {
    color: #cccccc;
    border: 1px solid #3c3c3c;
    margin-top: 8px;
    padding-top: 14px;
    font-size: 12px;
    font-weight: bold;
    background-color: #1e1e1e;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 4px;
    color: #cccccc;
}
QLabel#preview_label {
    background-color: #252526;
    color: #6a9955;
    font-family: "Consolas", "Courier New", monospace;
    font-size: 13px;
    padding: 8px;
    border: 1px solid #3c3c3c;
}
QPushButton {
    background-color: #0e639c;
    color: #ffffff;
    border: 1px solid #0e639c;
    padding: 6px 16px;
    font-size: 13px;
}
QPushButton:hover { background-color: #1177bb; }
QPushButton:pressed { background-color: #094771; }
QPushButton#cancel_btn {
    background-color: #3c3c3c;
    border-color: #3c3c3c;
    color: #cccccc;
}
QPushButton#cancel_btn:hover { background-color: #4a4a4a; }
QPushButton#test_btn {
    background-color: #3c3c3c;
    border-color: #3c3c3c;
    color: #cccccc;
}
QPushButton#test_btn:hover { background-color: #4a4a4a; }
QSplitter { background-color: #1e1e1e; }
QSplitter::handle { background-color: #3c3c3c; }
QSplitter::handle:horizontal { width: 1px; }
"""
