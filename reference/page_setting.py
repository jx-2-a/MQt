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
from item_textline import TextLineWidget
from ietm_check import AutoCheckBox
from item_input_but import InputWithButton
from tool_global_registry import register, registry,add_register,remove_register
from tools import Tool
from json_manager import JsonManager
config = JsonManager("_internal/jsons/setting.json")
from page_tip import tipWindow
from tool_config_style_binder import ConfigStyleBinder
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


class SettingsWindow(BaseChildWindow):
    def __init__(self, parent=None, width=400, height=300):
        super().__init__(parent, title="设置窗口", width=width, height=height)
        self.parent = parent
        parent.mask.show_mask()
        self.current_key = None
        self.settings_all ={}
        self.changed_relect = []
        self.changed_key = []
        # 主竖直布局（包含内容区和按钮区）
        main_layout = self.content_layout

        # ======================
        # 中间区域：使用 QSplitter
        # ======================
        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(False)  # 防止被收缩成 0
        splitter.setHandleWidth(6)

        # 左侧分类列表
        self.creat_category_list()


        # 右侧容器（你的自定义容器）
        self.Container = VerticalContainer()
        self.Container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        splitter.addWidget(self.category_list)
        splitter.addWidget(self.Container)
        splitter.setStretchFactor(0, 0)  # 左侧不拉伸
        splitter.setStretchFactor(1, 3)  # 右侧优先拉伸

        # 将 splitter 放入主布局
        main_layout.addWidget(splitter, 1)

        # 传递选中文本
        # self.category_list.currentItemChanged.connect(
        #     lambda current, prev: self.update_content(current.text() if current else None)
        # )

        self.creat_oac_but(main_layout)

        # 置顶拖拽区域
        self.resize_handle.raise_()
        self.mask.raise_()
        self.show()

    def creat_category_list(self):
        self.category_list = QTreeWidget()
        self.category_list.setHeaderHidden(True)
        self.category_list.itemClicked.connect(self.update_content)

        self.category_list.setStyleSheet("""
            QTreeWidget {
                background: rgba(33, 35, 39, 255);
                border: none;
                color: rgba(250, 250, 250, 255);
                font-size: 20px;
            }
            QTreeWidget::item {
                padding: 10px 8px;
            }
            QTreeWidget::item:selected {
                background: #0078d7;
                color: white;
                border-radius: 4px;
            }
            QTreeWidget::item:hover {
                background: rgba(40, 60, 60, 255);
            }
        """)
        self.create_pages()
    def create_pages(self,parent=None,new_i = "1"):
        if config.check(f"set_{new_i}"):
            for i,cat in enumerate(config.get(f"set_{new_i}")):
                item = QTreeWidgetItem([cat])
                next_i = new_i +"_"+str(i+1)
                item.setData(0, Qt.UserRole, next_i)
                is_par = self.create_pages(item,next_i)

                if parent:
                    parent.addChild(item)
                else:
                    self.category_list.addTopLevelItem(item)
            return True
        else:
            return False

    def update_content(self, item, column):
        if item.childCount() == 0:
            key = item.data(0, Qt.UserRole)
            full_key = key + "_settings"
            self.Container.clear_child()
            self.settings_all = {}
            self.changed_key = []
            self.current_key = full_key
            # 创建新页面并添加
            self.creat_page(full_key)
    def creat_page(self,key):
        if config.check(key):
            for sid, setting in config.get(key).items():
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
    def create_button_row(self,parent_layout, buttons, style=""):
        """
        创建一个带空隙的按钮行
        :param parent_layout: 要添加到的父布局
        :param buttons: 按钮文本列表，例如 ["确定", "应用", "取消"]
        :param style: 按钮的样式表，可选
        :return: dict {按钮文本: QPushButton对象}
        """
        layout = QHBoxLayout()
        btn_dict = {}

        layout.addStretch()  # 左边空白

        for i, text in enumerate(buttons):
            btn = QPushButton(text)
            if style:
                btn.setStyleSheet(style)
            layout.addWidget(btn)
            btn_dict[text] = btn
            if i != len(buttons) - 1:
                layout.addStretch()  # 中间空白

        layout.addStretch()  # 右边空白
        parent_layout.addLayout(layout)

        return btn_dict
    def creat_oac_but(self,layout):
        btn_bar = ButtonBar(["确定", "应用", "取消"],[self.on_ok,self.on_apply,self.on_cancel], side="right", ratio=0.5, parent=self)
        layout.addWidget(btn_bar)
    def on_ok(self):
        self.save_data()
        self.close()
        remove_register("child_window", self)
        self.parent.mask.close_mask()



    def on_apply(self):
        self.save_data()
    def on_cancel(self):
        self.close()
        remove_register("child_window", self)
        self.parent.mask.close_mask()
    def reflash_settings_all(self):
        for item in self.changed_key:
            default = config.get_set(item)
            print(item)
            self.settings_all[item]["default"] = default
    def save_data(self):
        if self.current_key:
            changes = {
                key: info["item"].get_value()
                for key, info in self.settings_all.items()
                if info["item"].get_value() != info["default"]
            }

            if changes:
                # 一次性写入 config
                config.update_set(changes)  # 假设 config 支持批量更新
                # 记录变化的 relect
                self.changed_relect.extend(info["relect"] for key, info in self.settings_all.items() if key in changes)
                self.changed_key.extend(key for key, info in self.settings_all.items() if key in changes)
        if self.changed_relect:
            self.shuaxin()
            self.changed_relect = []
            self.reflash_settings_all()
    def shuaxin(self):
        def handle_empty_case():
            tip = add_register("child_window",tipWindow(self,"修改对象中有需要重启生效者，请重新启动！"))
            tip.exec_()
        unique_relects = set(self.changed_relect)  # 自动去重

        if "" in unique_relects:
            # 如果有空字符串，只执行一次逻辑
            handle_empty_case()
        else:
            # 否则，对每个去重后的值逐一处理
            for r in unique_relects:
                print(r)
                if "(Style)" in r:
                    ConfigStyleBinder.refresh(r)
                elif "(Function)" in r:
                    ConfigStyleBinder.call_function(r)




