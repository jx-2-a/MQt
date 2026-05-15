from PyQt5.QtWidgets import QTabWidget, QWidget


class StyledTabWidget(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

    def add_tab(self, widget, title="Tab"):
        self.addTab(widget, title)

    def remove_tab(self, index):
        self.removeTab(index)

    def tab_count(self):
        return self.count()
