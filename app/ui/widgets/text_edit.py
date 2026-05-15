from PyQt5.QtWidgets import QTextEdit


class StyledTextEdit(QTextEdit):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)

    def text(self):
        return self.toPlainText()

    def set_text(self, text):
        self.setPlainText(text)
