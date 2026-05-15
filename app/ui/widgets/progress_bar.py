from PyQt5.QtWidgets import QProgressBar


class StyledProgressBar(QProgressBar):
    def __init__(self, parent=None):
        super().__init__(parent)

    def value(self):
        return super().value()

    def set_value(self, val):
        self.setValue(val)

    def set_range(self, min_val, max_val):
        self.setRange(min_val, max_val)
