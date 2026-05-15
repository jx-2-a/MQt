from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem

DATA_ROLE = Qt.UserRole


class StyledTreeWidget(QTreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHeaderLabel("树")
        self.setRootIsDecorated(True)

    def clear_tree(self):
        self.clear()

    def add_top_level(self, text, data=None):
        item = QTreeWidgetItem([text])
        if data is not None:
            item.setData(0, DATA_ROLE, data)
        self.addTopLevelItem(item)
        return item

    def add_child(self, parent_item, text, data=None):
        item = QTreeWidgetItem([text])
        if data is not None:
            item.setData(0, DATA_ROLE, data)
        parent_item.addChild(item)
        return item

    def current_data(self):
        item = self.currentItem()
        if item:
            return item.data(0, DATA_ROLE)
        return None

    def current_text(self):
        item = self.currentItem()
        if item:
            return item.text(0)
        return ""
