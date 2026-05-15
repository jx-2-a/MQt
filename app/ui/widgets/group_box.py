from PyQt5.QtWidgets import QGroupBox, QVBoxLayout


class StyledGroupBox(QGroupBox):
    def __init__(self, title="", parent=None):
        super().__init__(title, parent)
        layout = QVBoxLayout()
        layout.setContentsMargins(4, 4, 4, 4)
        self.setLayout(layout)

    def add_widget(self, widget):
        self.layout().addWidget(widget)

    def remove_widget(self, widget):
        self.layout().removeWidget(widget)

    def set_title(self, title):
        self.setTitle(title)
