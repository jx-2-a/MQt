from PyQt5.QtWidgets import QTextEdit
from app.core.style_engine import props_to_qss


class StyledTextEdit(QTextEdit):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)

    def text(self):
        return self.toPlainText()

    def set_text(self, text):
        self.setPlainText(text)

    def apply_style(self, style_props=None):
        self.setStyleSheet(props_to_qss(style_props) if style_props else "")
