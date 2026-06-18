from PyQt5.QtWidgets import QCheckBox
from app.core.style_engine import props_to_qss


class StyledCheckBox(QCheckBox):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)

    def is_checked(self):
        return self.isChecked()

    def set_checked(self, checked):
        self.setChecked(checked)

    def text(self):
        return super().text()

    def set_text(self, text):
        self.setText(text)

    def apply_style(self, style_props=None):
        self.setStyleSheet(props_to_qss(style_props) if style_props else "")
