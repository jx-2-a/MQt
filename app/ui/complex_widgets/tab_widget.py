"""CachedTabWidget — 带缓存机制的标签页控件。

Tab 头由 DraggableLabel 组成，支持自由拖拽和拖出（tear-off）。
页面通过工厂函数延迟构建，首次切换时创建并缓存，后续切换直接复用。

复合控件结构:
    header_row — 上方的 tab 栏（QWidget + HBoxLayout）
    content    — 下方的页面区（QStackedWidget）
两者均支持独立设置 height、border 等样式属性。
"""
from PyQt5.QtWidgets import QWidget, QStackedWidget, QHBoxLayout, QVBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal, QPoint
from app.core.style_engine import props_to_qss
from .draggable_label import DraggableLabel

_DESELECTED_STYLE = {
    "background_color": "#2d2d30",
    "border": "1px solid #3e3e42",
    "border_radius": "6px 6px 0px 0px",
    "border_bottom": "1px solid #3e3e42",
    "padding": "4px 12px",
    "margin": "1px 1px 0px 1px",
    "color": "#999999",
}
_SELECTED_STYLE = {
    "background_color": "#1e1e1e",
    "border": "1px solid #3e3e42",
    "border_radius": "6px 6px 0px 0px",
    "border_bottom": "2px solid #0e639c",
    "padding": "4px 12px",
    "margin": "1px 1px 0px 1px",
    "color": "#ffffff",
}


class CachedTabWidget(QWidget):
    """带缓存机制的标签页控件。

    槽位:
        header_row — HBoxLayout 容器，内部是 DraggableLabel tab 头
        content   — QStackedWidget，页面缓存在此切换

    信号:
        currentChanged(int)          — tab 切换
        tabTearOff(int, QPoint)      — tab 被拖出 header 区域 (index, globalPos)
    """

    currentChanged = pyqtSignal(int)
    tabTearOff = pyqtSignal(int, QPoint)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setAutoFillBackground(False)

        self._factories = []       # List[dict]  child_node 原始数据
        self._factory_paths = []   # List[str]   每个 child 的 path
        self._cache = {}           # Dict[int, QWidget]  已构建的页面
        self._headers = []         # List[DraggableLabel]
        self._current_idx = -1
        self._tear_threshold = 40  # 拖出 header 多少像素触发 tear-off

        self._build_layout()

    def _build_layout(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── tab 头行 ──
        self._header_row = QWidget()
        self._header_row.setObjectName("header_row")
        self._header_row.setAttribute(Qt.WA_StyledBackground, True)
        self._header_row.setAutoFillBackground(False)
        self._header_layout = QHBoxLayout(self._header_row)
        self._header_layout.setContentsMargins(0, 0, 0, 0)
        self._header_layout.setSpacing(0)
        self._header_layout.addStretch()
        layout.addWidget(self._header_row)

        # ── 内容区 ──
        self._stack = QStackedWidget()
        self._stack.setObjectName("content")
        self._stack.setAttribute(Qt.WA_StyledBackground, True)
        self._stack.setAutoFillBackground(False)
        layout.addWidget(self._stack, 1)

    # ── public API ─────────────────────────────────────────

    def add_tab(self, widget, title="Tab", icon=None):
        """直接添加已构建的页面（向后兼容旧 API）。"""
        idx = len(self._factories)
        # 制造一个虚拟 factory，缓存直接存放预构建 widget
        self._factories.append({"_prebuilt": True})
        self._factory_paths.append("0")
        self._cache[idx] = widget
        self._stack.addWidget(widget)

        template = {
            "text": {"content": title, "visible": True},
            "button": {"enabled": True},
            "drag": {"enabled": True},
            "style": dict(_DESELECTED_STYLE),
        }
        if icon:
            template["icon"] = {"src": icon, "width": 16, "height": 16, "visible": True}
        header = DraggableLabel(template=template)
        header.setObjectName(f"tab_header_{idx}")
        header.clicked.connect(self._make_selector(idx))
        header.setProperty("tab_index", idx)
        self._patch_drag(header, idx)
        self._headers.append(header)
        self._header_layout.insertWidget(self._header_layout.count() - 1, header)

        if len(self._headers) == 1:
            self.setCurrentIndex(0)
        return idx

    def add_tab_factory(self, child_node, path, label=""):
        """存入工厂信息，创建 DraggableLabel 头。页面在首次切换时才构建。"""
        idx = len(self._factories)
        self._factories.append(child_node)
        self._factory_paths.append(path)

        # 构建 tab 头的默认模板
        template = {
            "text": {"content": label or "Tab", "visible": True},
            "button": {"enabled": True},
            "drag": {"enabled": True},
            "style": dict(_DESELECTED_STYLE),
        }
        header = DraggableLabel(template=template)
        header.setObjectName(f"tab_header_{idx}")
        header.clicked.connect(self._make_selector(idx))
        header.setProperty("tab_index", idx)

        # 重写 drag 行为：允许拖出 header_row 外部 → 触发 tear-off
        self._patch_drag(header, idx)

        self._headers.append(header)
        self._header_layout.insertWidget(self._header_layout.count() - 1, header)

        if len(self._headers) == 1:
            self.setCurrentIndex(0)
        return idx

    def setCurrentIndex(self, idx):
        if idx < 0 or idx >= len(self._factories):
            return
        if idx == self._current_idx:
            return

        # 取消旧 tab 选中态
        if self._current_idx >= 0 and self._current_idx < len(self._headers):
            self._headers[self._current_idx].update_template(
                {"style": dict(_DESELECTED_STYLE)})

        # 第一次访问：构建页面并缓存
        if idx not in self._cache:
            from app.core.layout_engine import build
            page = build(self._factories[idx], self._factory_paths[idx])
            if page:
                self._stack.addWidget(page)
                self._cache[idx] = page

        # 设置新 tab 选中态
        self._headers[idx].update_template({"style": dict(_SELECTED_STYLE)})
        if idx in self._cache:
            self._stack.setCurrentWidget(self._cache[idx])
        self._current_idx = idx
        self.currentChanged.emit(idx)

    def remove_tab(self, idx):
        if not (0 <= idx < len(self._factories)):
            return

        # 清理 header
        h = self._headers.pop(idx)
        self._header_layout.removeWidget(h)
        h.deleteLater()

        # 清理 factory
        self._factories.pop(idx)
        self._factory_paths.pop(idx)

        # 清理缓存
        if idx in self._cache:
            w = self._cache.pop(idx)
            self._stack.removeWidget(w)
            w.deleteLater()

        # 重新映射缓存索引
        new_cache = {}
        for old_idx, widget in self._cache.items():
            new_idx = old_idx if old_idx < idx else old_idx - 1
            new_cache[new_idx] = widget
        self._cache = new_cache

        # 重绑 header 点击
        for i, h in enumerate(self._headers):
            self._rebind_header(h, i)

        # 切换选中
        if idx <= self._current_idx:
            if self._headers:
                self.setCurrentIndex(min(idx, len(self._headers) - 1))
            else:
                self._current_idx = -1

    def count(self):
        return len(self._factories)

    def tab_count(self):
        return len(self._factories)

    def currentIndex(self):
        return self._current_idx

    def widget(self, index):
        """获取已缓存的页面（可能为 None 如果尚未构建）。"""
        return self._cache.get(index)

    def header_at(self, index):
        if 0 <= index < len(self._headers):
            return self._headers[index]
        return None

    # ── style ──────────────────────────────────────────────

    def apply_style(self, style_props=None):
        """应用样式到自身及内部槽位（header_row / content）。"""
        self.setStyleSheet(props_to_qss(style_props) if style_props else "")
        # 槽位样式由 cascade_apply_styles 的根 QSS 级联覆盖，此处仅做基础清理
        self._header_row.setStyleSheet("")
        self._stack.setStyleSheet("")

    # ── internal ───────────────────────────────────────────

    def _make_selector(self, idx):
        def handler():
            self.setCurrentIndex(idx)
        return handler

    def _rebind_header(self, header, idx):
        try:
            header.clicked.disconnect()
        except TypeError:
            pass
        header.clicked.connect(self._make_selector(idx))
        header.setObjectName(f"tab_header_{idx}")
        header.setProperty("tab_index", idx)

    def _patch_drag(self, header, idx):
        """替换 DraggableLabel 的 drag 行为：允许拖出 header 区域，触发 tear-off。"""
        orig_mouse_move = header.mouseMoveEvent

        def patched_move(event):
            if not header._drag_pos:
                return orig_mouse_move(event)
            # 检查是否拖出了 header_row 的下边界
            local_in_header = self._header_row.mapFromGlobal(event.globalPos())
            if local_in_header.y() > self._header_row.height() + self._tear_threshold:
                # 触发 tear-off，tab 头归位
                header._drag_pos = None
                header.setCursor(Qt.OpenHandCursor)
                self.tabTearOff.emit(idx, event.globalPos())
                return
            orig_mouse_move(event)

        header.mouseMoveEvent = patched_move
