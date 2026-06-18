# row_list_widget.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal

class RowItem(QWidget):
    """一行：左边是文本，右边是删除按钮（默认隐藏）"""
    clicked = pyqtSignal(object)  # 发射自己被点击的信号
    deleted = pyqtSignal(object)  # 发射自己被删除的信号

    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.text = text

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # 左边的 label
        self.label = QLabel(text, self)
        self.label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        layout.addWidget(self.label, 1)

        # 右边的删除按钮（默认隐藏）
        self.delete_btn = QPushButton("x", self)
        self.delete_btn.setFixedWidth(30)
        self.delete_btn.hide()
        self.delete_btn.clicked.connect(self.on_delete)
        layout.addWidget(self.delete_btn, 0)

        # 点击 label 触发显示按钮
        self.label.mousePressEvent = self.on_click

    def on_click(self, event):
        """点击 label"""
        self.clicked.emit(self)

    def on_delete(self):
        """删除按钮点击"""
        self.deleted.emit(self)


class RowListWidget(QWidget):
    """管理多行，支持添加、删除，回调返回当前数组"""
    def __init__(self, items=None, callback=None, parent=None):
        super().__init__(parent)
        self.callback = callback
        self.items = []

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        if items:
            for text in items:
                self.add_item(text)

    def add_item(self, text):
        row = RowItem(text, self)
        row.clicked.connect(self.on_item_clicked)
        row.deleted.connect(self.on_item_deleted)
        self.layout.addWidget(row)
        self.items.append(row)

    def on_item_clicked(self, item):
        """点击时只显示当前项的按钮"""
        for row in self.items:
            row.delete_btn.hide()
        item.delete_btn.show()

    def on_item_deleted(self, item):
        """删除一行"""
        self.items.remove(item)
        item.setParent(None)  # 移除控件
        self.update_callback()

    def update_callback(self):
        """回调当前的数组"""
        if self.callback:
            self.callback([row.text for row in self.items])
