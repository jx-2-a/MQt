from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSplitter
from PyQt5.QtCore import Qt


class StyledBox(QWidget):
    def __init__(self, orientation="v", parent=None):
        super().__init__(parent)
        self._orientation = orientation
        self.setAttribute(Qt.WA_StyledBackground, True)
        layout = QVBoxLayout() if orientation == "v" else QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        self._layout = layout

    def add_widget(self, widget):
        self._layout.addWidget(widget)

    def remove_widget(self, widget):
        self._layout.removeWidget(widget)

    def orientation(self):
        return self._orientation


class StyledSplitter(QSplitter):
    def __init__(self, orientation=Qt.Horizontal, parent=None):
        super().__init__(orientation, parent)

    def add_widget(self, widget):
        self.addWidget(widget)
