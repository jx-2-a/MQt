from PyQt5.QtWidgets import QGroupBox, QVBoxLayout
from app.core.style_engine import props_to_qss


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

    def apply_style(self, style_props=None):
        self.setStyleSheet(props_to_qss(style_props) if style_props else "")
