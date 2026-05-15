from PyQt5.QtWidgets import QToolBar, QAction


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
