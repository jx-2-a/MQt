from PyQt5.QtWidgets import QCheckBox


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
