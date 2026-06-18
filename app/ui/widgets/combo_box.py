from PyQt5.QtWidgets import QComboBox
from app.core.style_engine import props_to_qss


class StyledComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)

    def current_text(self):
        return self.currentText()

    def set_current_text(self, text):
        self.setCurrentText(text)

    def items(self):
        return [self.itemText(i) for i in range(self.count())]

    def add_items(self, items):
        self.addItems(items)

    def clear_items(self):
        self.clear()

    def apply_style(self, style_props=None):
        self.setStyleSheet(props_to_qss(style_props) if style_props else "")
