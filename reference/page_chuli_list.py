# item_edit_text_window.py
from PyQt5.QtWidgets import QApplication
import sys
from class_child_window import BaseChildWindow
from item_down_but import ButtonBar
from tool_global_registry import remove_register
from item_list_change import RowListWidget


class chuli_listtWindow(BaseChildWindow):
    def __init__(self, title="文本编辑", callback=None, parent=None, content=None, width=600, height=300):
        super().__init__(parent, title=title, width=width, height=height)
        self.parent = parent
        if parent:
            parent.mask.show_mask()
        self.callback = callback
        self.content = content
        # 主体：RowListWidget
        self.row_list = RowListWidget(content or [], callback=self.on_items_changed)
        self.content_layout.addWidget(self.row_list)
        self.content_layout.addStretch()
        # 按钮区
        self.create_buttons(self.content_layout)

        # 置顶拖拽
        self.resize_handle.raise_()
        self.show()

    def create_buttons(self, layout):
        btn_bar = ButtonBar(
            ["确定", "取消"],
            [self.on_ok, self.on_cancel],
            side="right", ratio=0.4, parent=self
        )
        layout.addWidget(btn_bar)

    def on_items_changed(self, items):
        """当列表变化时触发"""
        self.content = items

    def on_ok(self):
        """确定"""
        self.close()
        remove_register("child_window", self)
        if self.parent:
            self.parent.mask.close_mask()
        if self.callback:
            self.callback(self.content)

    def on_cancel(self):
        """取消"""
        self.close()
        remove_register("child_window", self)
        if self.parent:
            self.parent.mask.close_mask()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = chuli_listtWindow(content=["第一行", "第二行", "第三行"], callback=print)
    sys.exit(app.exec_())
