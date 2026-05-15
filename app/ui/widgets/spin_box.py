from PyQt5.QtWidgets import QSpinBox, QDoubleSpinBox


class StyledSpinBox(QSpinBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRange(0, 9999)

    def value(self):
        return super().value()

    def set_value(self, val):
        self.setValue(val)

    def set_range(self, min_val, max_val):
        self.setRange(min_val, max_val)


class StyledDoubleSpinBox(QDoubleSpinBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRange(0.0, 9999.0)
        self.setDecimals(2)

    def value(self):
        return super().value()

    def set_value(self, val):
        self.setValue(val)

    def set_range(self, min_val, max_val):
        self.setRange(min_val, max_val)
