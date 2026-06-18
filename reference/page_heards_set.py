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
config = JsonManager("_internal/jsons/content_data.json")
import traceback
import sys
import copy
def excepthook(exc_type, exc_value, exc_tb):
    traceback.print_exception(exc_type, exc_value, exc_tb)
sys.excepthook = excepthook
class RowWidget(QWidget):
    """
    一行控件容器
    - 记录行属性
    - 横向排列控件
    - 提供方法计算总宽度
    """
    def __init__(self, parent=None,widge = None):
        super().__init__(parent)
        self.parent = parent
        self.widgets = []           # 存储这一行的控件

        self.h_layout = QHBoxLayout(self)
        self.h_layout.setContentsMargins(0, 0, 0, 0)
        self.h_layout.setSpacing(40)

        if widge and widge.nature != "fenge":
            self.add_stretch()


    def add_widget(self, widget):
        count = self.h_layout.count()
        if count<1:
            count = 1
        # stretch 通常在最后，所以插入到倒数第 1 个位置
        self.h_layout.insertWidget(count - 1, widget)
        self.widgets.append(widget)
    def add_stretch(self):
        self.h_layout.addStretch(1)
class VerticalContainer(QWidget):
    """
    大控件容器：
    - 使用竖向布局
    - 用于放置每行控件
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        self.rows = []
        self.current_row = None
        # 外层滚动区域
        self.scroll = QScrollArea(self)
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # 内容控件
        self.content = QWidget()
        self.scroll.setWidget(self.content)

        # 竖向布局，用于放置每行控件
        self.v_layout = QVBoxLayout(self.content)
        self.v_layout.setContentsMargins(0, 0, 0, 0)
        self.v_layout.setSpacing(20)

        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.scroll)
    def creat_new_row(self,widget):
        self.current_row = RowWidget(self,widget)
        self.rows.append(self.current_row)
        self.v_layout.addWidget(self.current_row)
    def add_widget(self,widget,new_row = False):
        if not new_row and self.current_row:
            self.current_row.add_widget(widget)
        else:
            # if self.current_row:
            #     self.current_row.add_stretch()
            self.creat_new_row(widget)
            self.current_row.add_widget(widget)
    def add_stretch(self):
        self.v_layout.addStretch()

    def clear_child(self):
        while self.v_layout.count():
            item = self.v_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()
            else:
                # 不是 widget，而是 QSpacerItem（比如 addStretch）
                del item
class heards_Window(BaseChildWindow):
    def __init__(self, parent=None,title="", width=600, height=200,content="?",callback=None):
        super().__init__(parent, title=title, width=width, height=height)
        self.parent = parent
        if parent:
            parent.mask.show_mask()
        self.settings_all = {}
        self.changed_key = []
        self.changed_relect = []
        self.path = registry["current_page_id"]+"_heards"+content
        self.had = config.deep_check(self.path)
        if self.had:
            self.settings = config.get(self.path)
        else:
            self.settings = copy.deepcopy(config.get("moren_heards"))
        # 右侧容器（你的自定义容器）
        self.Container = VerticalContainer()
        self.Container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.content_layout.addWidget(self.Container)

        self.creat_page(self.path)

        self.create_buttons(self.content_layout)
        # 置顶拖拽区域
        self.resize_handle.raise_()
        self.show()

    def creat_page(self,key=""):
        for sid, setting in self.settings.items():
            # print(key + "/" + sid, setting)
            self.create_setting_item(key + "/" + sid, setting)
        self.Container.add_stretch()
    def create_setting_item(self, prefix, setting):
        stype = setting.get("type")
        relect = setting.get("relect")
        key = prefix # 唯一键
        if stype == "select":
            item = LabeledComboBox(setting.get("label"))
            options = setting.get("options", [])
            item.set_items(options)
            default = setting.get("default")
            if default in options:
                item.set_dtext(default)
        elif stype == "text":
            item = AutoExpandInput(setting.get("label"))
            default = setting.get("default")
            item.set_dtext(default)
        elif stype == "text_b":
            item = InputWithButton(setting.get("label"),parent=self)
            default = setting.get("default")
            item.set_value(default,relect)
        elif stype == "zhushi":
            item = StyledLabel(setting.get("default"))
            default = None
        elif stype == "fenge":
            item = TextLineWidget(setting.get("default"))
            default = None
        elif stype == "check":
            item = AutoCheckBox(setting.get("label"))
            default = setting.get("default")
            if isinstance(default, str):
                default = Tool.to_bool(default)
            item.set_dtext(default)

        self.Container.add_widget(item, setting.get("state"))
        self.settings_all[key] = {
            "item":item,
            "default":default,
            "relect": relect
        }

    def create_buttons(self, layout):
        btn_bar = ButtonBar(
            ["确定", "取消"],
            [self.on_ok, self.on_cancel],
            side="right", ratio=0.4, parent=self
        )
        layout.addWidget(btn_bar)
    def save_data(self):
        changes = {
            key: info["item"].get_value()
            for key, info in self.settings_all.items()
            if info["item"].get_value() != info["default"]
        }
        if changes:
            # 记录变化的 relect
            self.changed_relect.extend(info["relect"] for key, info in self.settings_all.items() if key in changes)
            self.changed_key.extend(key for key, info in self.settings_all.items() if key in changes)
        if self.had:
            # 一次性写入 config
            config.update_set(changes)  # 假设 config 支持批量更新
        else:
            config.set(self.path,self.settings)
            config.update_set(changes)
    def on_ok(self):
        """选择当前行用户"""
        self.save_data()
        self.close()
        remove_register("child_window", self)
        if self.parent:
            self.parent.mask.close_mask()

    def on_cancel(self):
        self.close()
        remove_register("child_window", self)
        if self.parent:
            self.parent.mask.close_mask()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    register("5IbCZ8Z5ZN", name="current_page_id")
    win = heards_Window()

    sys.exit(app.exec_())