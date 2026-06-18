from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem
from app.core.style_engine import props_to_qss

DATA_ROLE = Qt.UserRole


class StyledTreeWidget(QTreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHeaderLabel("树")
        self.setRootIsDecorated(True)
        self._strip_header_bg()

    def _strip_header_bg(self):
        """移除 QHeaderView 所有默认背景层（Widget→Palette→Viewport），使半透明 QSS 背景能穿透到 QTreeWidget。"""
        header = self.header()
        # 1. 关闭控件级调色板填充
        header.setAutoFillBackground(False)
        # 2. 关掉视口层的默认白色背景（QAbstractScrollArea 内嵌 viewport）
        vp = header.viewport()
        if vp:
            vp.setAutoFillBackground(False)
            vp.setAttribute(Qt.WA_TranslucentBackground, True)
        # 3. 把调色板基色全部置透明，盖掉原生样式里的默认 Button/Window 白色
        pal = header.palette()
        pal.setColor(QPalette.Base, QColor(0, 0, 0, 0))
        pal.setColor(QPalette.Window, QColor(0, 0, 0, 0))
        pal.setColor(QPalette.Button, QColor(0, 0, 0, 0))
        header.setPalette(pal)

    def apply_style(self, style_props=None):
        self.setStyleSheet(props_to_qss(style_props) if style_props else "")

    def set_header_visible(self, visible):
        self.setHeaderHidden(not visible)

    def clear_tree(self):
        self.clear()

    def add_top_level(self, text, data=None):
        item = QTreeWidgetItem([text])
        if data is not None:
            item.setData(0, DATA_ROLE, data)
        self.addTopLevelItem(item)
        return item

    def add_child(self, parent_item, text, data=None):
        item = QTreeWidgetItem([text])
        if data is not None:
            item.setData(0, DATA_ROLE, data)
        parent_item.addChild(item)
        return item

    def current_data(self):
        item = self.currentItem()
        if item:
            return item.data(0, DATA_ROLE)
        return None

    def current_text(self):
        item = self.currentItem()
        if item:
            return item.text(0)
        return ""
