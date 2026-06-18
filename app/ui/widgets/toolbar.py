from PyQt5.QtWidgets import QToolBar, QAction
from app.core.style_engine import props_to_qss


class StyledToolBar(QToolBar):
    def __init__(self, title="", parent=None):
        super().__init__(title, parent)
        self.setMovable(False)

    def add_action(self, label, callback=None):
        action = QAction(label, self)
        if callback:
            action.triggered.connect(callback)
        self.addAction(action)
        return action

    def apply_style(self, style_props=None):
        self.setStyleSheet(props_to_qss(style_props) if style_props else "")
