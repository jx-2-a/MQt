from class_child_window import BaseChildWindow
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QDialog, QSplitter,QSpacerItem, QTreeWidget,
    QLabel, QPushButton, QListWidget, QStackedWidget, QMainWindow, QScrollArea, QSizePolicy, QTreeWidgetItem
)
from PyQt5.QtCore import Qt, QPoint, QPropertyAnimation, QObject, QEvent
from PyQt5.QtGui import QPixmap
from item_down_but import ButtonBar
from item_input import AutoExpandInput
from item_label import StyledLabel
from item_select import LabeledComboBox
from ietm_check import AutoCheckBox
from tool_global_registry import register, registry,remove_register
from tools import Tool
from json_manager import JsonManager
config = JsonManager("_internal/jsons/setting.json")

class tipWindow(BaseChildWindow):
    def __init__(self, parent=None,content="", width=600, height=200):
        super().__init__(parent, title="提示", width=width, height=height)
        self.parent = parent
        parent.mask.show_mask()

        self.add_centered_content(self.content_layout,content)

        self.creat_oac_but(self.content_layout)
        # 置顶拖拽区域
        self.resize_handle.raise_()
        self.show()
    def creat_oac_but(self,layout):
        btn_bar = ButtonBar(["确定"],[self.on_ok], side="right", ratio=0.5, parent=self)
        layout.addWidget(btn_bar)

    def add_centered_content(self,parent_layout, content):
        """
        在 parent_layout 中添加一个“壳子”，包含水平居中的内容和底部伸缩
        :param parent_layout: 外层垂直布局（self.content_layout）
        :param content: 显示内容的文本
        """
        # 外层壳子，垂直布局，主动扩张
        shell = QWidget()
        shell_lay = QVBoxLayout(shell)
        shell_lay.setContentsMargins(20, 20, 20, 20)
        shell_lay.setSpacing(0)

        # 中间内容水平居中
        con = QWidget()
        con_lay = QHBoxLayout(con)
        con_lay.setContentsMargins(0, 0, 0, 0)
        con_lay.setSpacing(0)

        con_lay.addStretch()
        item = StyledLabel(content)
        con_lay.addWidget(item)
        con_lay.addStretch()

        shell_lay.addWidget(con)
        shell_lay.addStretch()  # 底部伸缩，把内容顶上去

        # 添加到父布局
        parent_layout.addWidget(shell)
    def on_ok(self):
        self.close()
        remove_register("child_window", self)
        self.parent.mask.close_mask()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = tipWindow()

    sys.exit(app.exec_())