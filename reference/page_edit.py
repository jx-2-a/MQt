from class_child_window import BaseChildWindow
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit
)
from PyQt5.QtCore import Qt
from item_down_but import ButtonBar
from tool_global_registry import remove_register


class EditTextWindow(BaseChildWindow):
    def __init__(self,title="文本编辑",callback=None, parent=None, content="", width=600, height=300):
        super().__init__(parent, title=title, width=width, height=height)
        self.parent = parent
        if parent:
            parent.mask.show_mask()
        self.callback = callback

        # 文本编辑框（初始为只读）
        self.text_edit = QTextEdit(content, self)
        # 🔑 设置样式：边距 + 圆角 + 背景色
        self.text_edit.setStyleSheet("""
                    QTextEdit {
                        padding: 10px;
                        border: 0px;
                        border-radius: 0px;
                        background-color: rgba(0,0,0,0);
                        font-size: 24px;
                        line-height: 2em;
                        color: rgba(255,255,255,255)
                    }
                """)
        if content and content != " ":
            self.text_edit.setReadOnly(True)
        else:
            self.text_edit.setReadOnly(False)
            self.text_edit.setFocus()
        self.content_layout.addWidget(self.text_edit)

        # 创建按钮区
        self.create_buttons(self.content_layout)

        # 置顶拖拽区域
        self.resize_handle.raise_()
        self.show()

    def create_buttons(self, layout):
        btn_bar = ButtonBar(
            ["编辑", "确定", "取消"],
            [self.on_edit, self.on_ok, self.on_cancel],
            side="right", ratio=0.4, parent=self
        )
        layout.addWidget(btn_bar)

    def on_edit(self):
        """开启编辑"""
        self.text_edit.setReadOnly(False)
        self.text_edit.setFocus()

    def on_ok(self):
        """保存并关闭"""
        text = self.text_edit.toPlainText()
        self.close()
        remove_register("child_window", self)
        if self.parent:
            self.parent.mask.close_mask()
        if self.callback:
            self.callback(text)

    def on_cancel(self):
        """取消编辑并关闭"""
        self.close()
        remove_register("child_window", self)
        if self.parent:
            self.parent.mask.close_mask()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = EditTextWindow(content="")
    sys.exit(app.exec_())
