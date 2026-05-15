from PyQt5.QtWidgets import QLabel


class StyledLabel(QLabel):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)

    def set_text(self, text):
        self.setText(text)
