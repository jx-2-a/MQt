from PyQt5.QtWidgets import QComboBox


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
