from PyQt5.QtWidgets import QSlider
from PyQt5.QtCore import Qt
from app.core.style_engine import props_to_qss


class StyledSlider(QSlider):
    def __init__(self, orientation=Qt.Horizontal, parent=None):
        super().__init__(orientation, parent)

    def value(self):
        return super().value()

    def set_value(self, val):
        self.setValue(val)

    def set_range(self, min_val, max_val):
        self.setRange(min_val, max_val)

    def apply_style(self, style_props=None):
        self.setStyleSheet(props_to_qss(style_props) if style_props else "")
