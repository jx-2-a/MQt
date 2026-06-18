from PyQt5.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QSizePolicy
from PyQt5.QtCore import Qt
from app.core.style_engine import props_to_qss
from .form_row import FormRow


class FormContainer(QWidget):
    """垂直滚动表单容器 — 管理多行 FormRow，内容超出自动滚动。"""

    def __init__(self, row_spacing=20, margin=0, parent=None):
        super().__init__(parent)
        self._rows = []
        self._current_row = None
        self._row_spacing = row_spacing
        self.setAttribute(Qt.WA_StyledBackground, True)

        self._scroll = QScrollArea(self)
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self._scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self._content = QWidget()
        self._scroll.setWidget(self._content)

        self._v_layout = QVBoxLayout(self._content)
        self._v_layout.setContentsMargins(margin, margin, margin, margin)
        self._v_layout.setSpacing(row_spacing)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self._scroll)

    def apply_style(self, style_props=None):
        self.setStyleSheet(props_to_qss(style_props) if style_props else "")

    def add_widget(self, widget, new_row=False):
        """添加控件到当前行，或创建新行后再添加。"""
        if not new_row and self._current_row:
            self._current_row.add_widget(widget)
            return self._current_row

        self._current_row = FormRow(spacing=self._row_spacing, parent=self._content)
        self._rows.append(self._current_row)
        self._v_layout.addWidget(self._current_row)
        self._current_row.add_widget(widget)
        return self._current_row

    def add_row(self):
        """创建空行并返回。"""
        self._current_row = FormRow(spacing=self._row_spacing, parent=self._content)
        self._rows.append(self._current_row)
        self._v_layout.addWidget(self._current_row)
        return self._current_row

    def add_stretch(self):
        self._v_layout.addStretch()

    def clear(self):
        while self._v_layout.count():
            item = self._v_layout.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)
                w.deleteLater()
        self._rows.clear()
        self._current_row = None
