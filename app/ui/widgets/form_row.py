from PyQt5.QtWidgets import QWidget, QHBoxLayout, QSizePolicy
from PyQt5.QtCore import Qt
from app.core.style_engine import props_to_qss


class FormRow(QWidget):
    """水平行容器 — 横向排列控件，自动尾部弹簧。"""

    def __init__(self, spacing=40, parent=None):
        super().__init__(parent)
        self._widgets = []
        self.setAttribute(Qt.WA_StyledBackground, True)

        self._h_layout = QHBoxLayout(self)
        self._h_layout.setContentsMargins(0, 0, 0, 0)
        self._h_layout.setSpacing(spacing)

    def apply_style(self, style_props=None):
        self.setStyleSheet(props_to_qss(style_props) if style_props else "")

    def add_widget(self, widget):
        c = self._h_layout.count()
        if c > 0:
            self._h_layout.insertWidget(c - 1, widget)
        else:
            self._h_layout.addWidget(widget)
        self._widgets.append(widget)

    def add_stretch(self):
        self._h_layout.addStretch(1)

    def clear(self):
        while self._h_layout.count():
            item = self._h_layout.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)
                w.deleteLater()
        self._widgets.clear()
