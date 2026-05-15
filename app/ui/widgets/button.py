from PyQt5.QtWidgets import QPushButton


class StyledButton(QPushButton):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)

    def text(self):
        return super().text()

    def set_text(self, text):
        self.setText(text)
