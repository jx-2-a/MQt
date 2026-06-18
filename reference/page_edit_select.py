from class_child_window import BaseChildWindow
import sys
from PyQt5.QtWidgets import QApplication, QVBoxLayout
from item_down_but import ButtonBar
from tool_global_registry import remove_register
from item_select_add import EditableComboBox
from json_manager import JsonManager
content_data = JsonManager("_internal/jsons/content_data.json")


class EditTextWindow_add(BaseChildWindow):
    def __init__(self, title="文本编辑", callback=None, parent=None, content=None,
                 width=600, height=300,duixiang = None):
        super().__init__(parent, title=title, width=width, height=height)
        self.parent = parent
        if parent:
            parent.mask.show_mask()
        self.callback = callback

        self.content_layout.addStretch()
        # 使用 EditableComboBox 替代 QTextEdit
        self.text_edit = EditableComboBox("选择内容:", parent=self)
        self.content_layout.addWidget(self.text_edit)
        self.content_layout.addStretch()
        self.duixiang = duixiang
        self.content = content
        if self.duixiang:
            self.load()
        # 创建按钮区
        self.create_buttons(self.content_layout)

        # 置顶拖拽区域
        self.resize_handle.raise_()
        self.show()
    def load(self):
        content =  content_data.get(self.duixiang,[])
        self.text_edit.set_items(content)
        if self.content:
            self.text_edit.set_current_text(self.content)
    def create_buttons(self, layout):
        btn_bar = ButtonBar(
            ["编辑", "确定", "取消"],
            [self.on_edit, self.on_ok, self.on_cancel],
            side="right", ratio=0.4, parent=self
        )
        layout.addWidget(btn_bar)

    def on_edit(self):
        """开启编辑"""
        # EditableComboBox 默认就是可编辑的，这里可以选中焦点
        self.text_edit.widget.setFocus()

    def on_ok(self):
        """保存并关闭"""
        items = self.text_edit.get_all_items()
        self.on_save(items)
        current = self.text_edit.get_value()
        self._close_window()
        if self.callback:
            self.callback(current)
    def on_save(self,values):
        content_data.set(self.duixiang,values)
    def on_cancel(self):
        """取消编辑并关闭"""
        self._close_window()

    def _close_window(self):
        print(6868)
        self.close()
        remove_register("child_window", self)
        if self.parent:
            self.parent.mask.close_mask()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # 初始内容可以是列表形式
    win = EditTextWindow(content=["苹果", "香蕉", "橙子"])
    sys.exit(app.exec_())
