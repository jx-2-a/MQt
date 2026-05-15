from PyQt5.QtWidgets import QWidget, QFormLayout, QLineEdit, QLabel, QComboBox


class StyledForm(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._layout = QFormLayout()
        self.setLayout(self._layout)
        self._fields = {}

    def add_field(self, label, widget=None):
        if widget is None:
            widget = QLineEdit()
        self._layout.addRow(label, widget)
        self._fields[label] = widget
        return widget

    def add_combo(self, label, items=None):
        combo = QComboBox()
        if items:
            combo.addItems(items)
        self._layout.addRow(label, combo)
        self._fields[label] = combo
        return combo

    def field(self, label):
        return self._fields.get(label)

    def set_field_value(self, label, value):
        w = self._fields.get(label)
        if w is None:
            return
        if isinstance(w, QLineEdit):
            w.setText(str(value))
        elif isinstance(w, QComboBox):
            w.setCurrentText(str(value))

    def field_value(self, label):
        w = self._fields.get(label)
        if w is None:
            return None
        if isinstance(w, QLineEdit):
            return w.text()
        elif isinstance(w, QComboBox):
            return w.currentText()
        return None

    def clear_fields(self):
        while self._layout.rowCount() > 0:
            self._layout.removeRow(0)
        self._fields.clear()
