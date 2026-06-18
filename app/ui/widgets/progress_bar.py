from PyQt5.QtWidgets import QProgressBar
from app.core.style_engine import props_to_qss


class StyledProgressBar(QProgressBar):
    def __init__(self, parent=None):
        super().__init__(parent)

    def value(self):
        return super().value()

    def set_value(self, val):
        self.setValue(val)

    def set_range(self, min_val, max_val):
        self.setRange(min_val, max_val)

    def apply_style(self, style_props=None):
        self.setStyleSheet(props_to_qss(style_props) if style_props else "")
