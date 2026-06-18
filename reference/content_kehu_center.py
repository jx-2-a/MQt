from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QApplication
)
from PyQt5.QtCore import Qt,QTimer
from item_excel import TableWidget
import sys
from json_manager import JsonManager
import traceback
from tool_config_style_binder import ConfigStyleBinder
from page_heards_set import heards_Window
from tool_global_registry import register, registry,update_register,add_register
from tools import Tool
from item_search_bar import SearchBar
from page_kehu import UserDetailWindow
config = JsonManager("_internal/jsons/setting.json")
content_data = JsonManager("_internal/jsons/content_data.json")

def excepthook(exc_type, exc_value, exc_tb):
    traceback.print_exception(exc_type, exc_value, exc_tb)
sys.excepthook = excepthook
class MyTableWidget(TableWidget):
    def __init__(self, headers,parent=None, allow_add_row=True):
        super().__init__(headers, parent, allow_add_row)
        self.last_gaoliang = None
    def bind_funcation(self,row,i):
        for n, cell in enumerate(row.cells):
            cell.mousePressEvent = lambda e,b=cell, r=i,c=n: self.on_row_clicked(b,r,c)
            cell.mouseDoubleClickEvent = lambda e, b=cell, r=i, c=n: self.on_row_double_clicked(b, r, c)
    def on_row_clicked(self,button,row,col):
        if row>1:
            if self.last_gaoliang is not None:
                self.rows[self.last_gaoliang].set_highlight(False)
                self.last_gaoliang = row-1
                self.rows[row-1].set_highlight()
            else:
                self.last_gaoliang = row - 1
                self.rows[row-1].set_highlight()

    def on_row_double_clicked(self, button, row, col):
        def callback(text):
            self.parent.search_field.setCurrentText("姓名")
            self.parent.search_field.setText(text)
            self.parent.on_search_text_changed(text)

        if registry["current_page_id"] == "gtm7ebNbBO":
            user_id = self.parent.filtered_id[row - 2]
            tip = add_register("child_window", UserDetailWindow(parent=registry["main_window"]
                                                             , callback=callback, title=f"用户详细信息", user_data=user_id, new_mode=False))
            tip.exec_()
class kc(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        STYLE = """
                    background-color: rgba{{1_6_1_settings/02:(20,20,20,100)}};
                    border: 0px;
                    border-radius: 0px;
                                        """
        ConfigStyleBinder.bind("(Style)-ea_style-(color)", self, STYLE)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.filtered_id = []
        self.filtered_users = []

        #创建搜索框
        self.creat_search_bar()

        # 创建下方表格
        self.creat_excel()

        QTimer.singleShot(0, lambda: self.on_search_text_changed())
    def creat_search_bar(self):
        columns =["姓名","称号","微信","备注","车牌", "电话"]
        button_text = "新建客户信息"

        self.search_field = SearchBar(columns,button_text=button_text)
        self.search_field.on_text_changed(self.on_search_text_changed)
        self.search_field.on_new_clicked(self.on_new_kehu)
        self.layout.addWidget(self.search_field)
    def creat_excel(self):
        self.headers = ["姓名","称号","微信","备注","车牌", "电话"]

        self.table = MyTableWidget(self.headers, allow_add_row=False,parent=self)
        self.layout.addWidget(self.table)

    def on_search_text_changed(self, text=""):
        """根据搜索栏内容和选择字段过滤用户"""
        def transform(rows):
            users = []
            self.filtered_id = []
            for r in rows:
                plate_str = "/".join(r.get("plates", [])) if r.get("plates") else ""
                phone_str = "/".join(r.get("phones", [])) if r.get("phones") else ""

                users.append({
                    "name": r.get("name", ""),
                    "title": r.get("title", ""),
                    "wechat":r.get("wechat", ""),
                    "note": r.get("note", ""),
                    "plate": plate_str,
                    "phone": phone_str
                })
                self.filtered_id.append(r.get("id", ""))
            return users

        text = text.strip().lower()
        field_map = {"姓名": "name", "称号": "title", "微信": "wechat", "备注": "note", "车牌": "plate", "电话": "phone"}
        field_key = field_map.get(self.search_field.currentText(), "name")
        if text:
            self.filtered_users = transform(registry["data_libary"].search_customers_by_field(field_key, text))
        else:
            self.filtered_users = transform(registry["data_libary"].get_customers_random(50))
        self.update_table(self.filtered_users)

    def update_table(self, users_list):
        """刷新表格显示"""
        self.table.clear()
        self.table.last_gaoliang = None
        self.table.on_add_new_row(self.headers)
        for u in users_list:
            row_values = [u.get("name", ""), u.get("title", ""), u.get("wechat", ""), u.get("note", ""), u.get("plate", ""), u.get("phone", "")]
            self.table.on_add_new_row(row_values)


    def on_new_kehu(self):
        def callback(text):
            self.search_field.setCurrentText("姓名")
            self.search_field.setText(text)
            self.on_search_text_changed(text)


        tip = add_register("child_window", UserDetailWindow(parent=registry["main_window"]
                                                            , title=f"添加新用户", callback=callback, new_mode=True))
        tip.exec_()


    def save_all(self):
        pass