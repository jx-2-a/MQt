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
from page_set_select_way import pssw
from page_kehu import UserDetailWindow
from page_show_quxian import psqWindow
config = JsonManager("_internal/jsons/setting.json")
content_data = JsonManager("_internal/jsons/content_data.json")

def excepthook(exc_type, exc_value, exc_tb):
    traceback.print_exception(exc_type, exc_value, exc_tb)
sys.excepthook = excepthook
class MyTableWidget(TableWidget):
    def __init__(self, headers,parent=None, allow_add_row=True,textt ="商品" ):
        super().__init__(headers, parent, allow_add_row)
        self.parent = parent
        self.last_gaoliang = None
        self.textt = textt
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
        if self.textt == "商品":
            tip = add_register("child_window", psqWindow(parent=registry["main_window"],
                        id=self.parent.filtered_users[row-2]["shopper_id"],
                        title=f"{self.parent.filtered_users[row-2]['shopper_name']}统计"))
            tip.exec_()
        elif self.textt == "道具":
            tip = add_register("child_window", psqWindow(parent=registry["main_window"],
                                                         id=self.parent.filtered_users[row - 2]["shopper_id"],
                                                         title=f"{self.parent.filtered_users[row - 2]['shopper_name']}统计"))
            tip.exec_()
class psad(QWidget):
    def __init__(self, parent=None,textt = ""):
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
        self.textt = textt
        self.text = ""
        #创建搜索框
        self.creat_search_bar()
        # 创建下方表格
        self.creat_excel()
        QTimer.singleShot(0, lambda: self.on_search_text_changed())
    def creat_search_bar(self):
        if self.textt == "账单":
            self.name = "psad_"+"账单"
            columns = ["客户","支付方式", "日期", "服务内容", "备注"]
        elif self.textt == "保修卡":
            self.name = "psad_" + "保修卡"
            columns = ["保修内容", "产品序列", "保修有效时长", "日期", "当前状态"]
        elif self.textt == "商品":
            self.name = "psad_" + "商品"
            columns = [
                "日期",
                "商品名称",
                "型号",
                "简称",
                "分类",
                "价格",
                "来源",
                "备注"]
        elif self.textt == "道具":
            self.name = "psad_" + "道具"
            columns = [
                        "日期",
                        "道具名称",
                        "简称",
                        "分类",
                        "价格",
                        "来源",
                        "用途",
                        "备注"]
        data = content_data.get(self.name)
        self.limit = data["limit"]
        self.data = data["data"]
        self.desc = data["desc"]
        self.order_by = data["order_by"]
        button_text = "设置展示范围"
        self.search_field = SearchBar(columns,button_text=button_text)
        self.search_field.on_text_changed(self.on_search_text_changed)
        self.search_field.on_new_clicked(self.on_new_kehu)
        self.layout.addWidget(self.search_field)
    def creat_excel(self):
        if self.textt == "账单":
            self.headers = ["序号",
                            "日期",
                            "客户",
                            "服务内容",
                            "收费",
                            "成本",
                            "利润",
                            "支付方式",
                            "备注"]
        elif self.textt == "保修卡":
            self.headers = ["序号",
                            "日期",
                            "客户",
                            "保修内容",
                            "产品序号",
                            "保修起始日期",
                            "保修有效时长",
                            "保修终止日期",
                            "当前状态",
                            "备注"]
        elif self.textt == "商品":
            self.headers = ["序号",
                            "日期",
                            "商品名称",
                            "型号",
                            "简称",
                            "分类",
                            "价格",
                            "来源",
                            "备注"
                            ]
        elif self.textt == "道具":
            self.headers = ["序号",
                            "日期",
                            "道具名称",
                            "简称",
                            "分类",
                            "价格",
                            "来源",
                            "用途",
                            "备注"]
        self.table = MyTableWidget(self.headers, allow_add_row=False,parent=self,textt=self.textt)
        self.layout.addWidget(self.table)

    def on_search_text_changed(self, text=""):
        """根据搜索栏内容和选择字段过滤用户"""
        def zhaun(text):
            if text == "顺序":
                return False
            else:
                return True
        self.text = text.strip().lower()


        if self.textt == "账单":
            field_map = {"客户":"customer_name","支付方式": "payment_method", "日期": "date",
                         "服务内容": "service", "备注": "note","收费":"fee","成本":"cost","利润":"profit"}
            field_key = field_map.get(self.search_field.currentText(), "payment_method")
            order_by = field_map.get(self.order_by, "date")
            filtered_users = registry["data_libary"].get_billings(order_by = order_by,desc = zhaun(self.desc),
                                                                  field_key = field_key, text = self.text,limit=int(self.limit),
                                                                  date_str =self.data)
        elif self.textt == "保修卡":
            field_map = {"客户":"customer_name","保修内容": "product", "产品序列": "product_id", "保修有效时长": "long", "日期": "date",
                         "当前状态": "state", "保修起始日期": "start", "保修终止日期": "end"}
            field_key = field_map.get(self.search_field.currentText(), "product_id")
            order_by = field_map.get(self.order_by, "date")
            filtered_users = registry["data_libary"].get_warranty_card(order_by=order_by, desc=zhaun(self.desc),
                                                                  field_key=field_key, text=self.text, limit=int(self.limit),
                                                                  date_str =self.data)
        elif self.textt == "商品":
            field_map = {"日期": "date", "商品名称": "shopper_name","型号":"xinghao", "简称": "shopper_jia_name",
                         "分类": "fenlei", "价格": "jiage", "来源": "laiyuan", "备注": "note"}
            field_key = field_map.get(self.search_field.currentText(), "shopper_name")
            order_by = field_map.get(self.order_by, "date")
            filtered_users = registry["data_libary"].get_shoppingss(order_by=order_by, desc=zhaun(self.desc),
                                                                  field_key=field_key, text=self.text, limit=int(self.limit),
                                                                  date_str =self.data)
        elif self.textt == "道具":
            field_map = {"日期": "date", "道具名称": "shopper_name", "简称": "shopper_jia_name",
                         "分类": "fenlei", "价格": "jiage", "来源": "laiyuan","用途":"how_use", "备注": "note"}
            field_key = field_map.get(self.search_field.currentText(), "shopper_name")
            order_by = field_map.get(self.order_by, "date")
            filtered_users = registry["data_libary"].get_daojus(order_by=order_by, desc=zhaun(self.desc),
                                                                  field_key=field_key, text=self.text, limit=int(self.limit),
                                                                  date_str =self.data)
        self.update_table(filtered_users)
        self.filtered_users = filtered_users

    def update_table(self, users_list):
        """刷新表格显示"""
        self.table.clear()
        if self.textt == "账单":
            self.upup(users_list)
        elif self.textt == "保修卡":
            self.downdown(users_list)
        elif self.textt == "商品":
            self.leftleft(users_list)
        elif self.textt == "道具":
            self.rightright(users_list)
    def rightright(self,needed_data):
        self.table.on_add_new_row(self.headers)
        for i, u in enumerate(needed_data):
            row_values = [
                str(i + 1),
                str(u.get("date", "")),
                str(u.get("shopper_name", "")),
                str(u.get("shopper_jia_name", "")),
                str(u.get("fenlei", "")),
                str(u.get("jiage", "")),
                str(u.get("laiyuan", "")),
                str(u.get("how_use", "")),
                str(u.get("note", ""))
            ]
            self.table.on_add_new_row(row_values)
    def leftleft(self,needed_data):
        self.table.on_add_new_row(self.headers)

        for i, u in enumerate(needed_data):
            row_values = [
                str(i + 1),
                str(u.get("date", "")),
                str(u.get("shopper_name", "")),
                str(u.get("xinghao", "")),
                str(u.get("shopper_jia_name", "")),
                str(u.get("fenlei", "")),
                str(u.get("jiage", "")),
                str(u.get("laiyuan", "")),
                str(u.get("note", ""))
            ]
            self.table.on_add_new_row(row_values)
    def upup(self,needed_data):
        self.table.on_add_new_row(self.headers)

        for i, u in enumerate(needed_data):
            row_values = [
                str(i + 1),
                str(u.get("date", "")),
                str(u.get("customer_name", "")),
                str(u.get("service", "")),
                str(u.get("fee", "")),
                str(u.get("cost", "")),
                str(u.get("profit", "")),
                str(u.get("payment_method", "")),
                str(u.get("note", "")),
            ]
            self.table.on_add_new_row(row_values)
    def downdown(self,needed_data):
        self.table.on_add_new_row(self.headers)
        for i, u in enumerate(needed_data):
            row_values = [
                str(i + 1),
                str(u.get("date", "")),
                str(u.get("customer_name", "")),
                str(u.get("product", "")),
                str(u.get("product_id", "")),
                str(u.get("start", "")),
                str(u.get("long", "")),
                str(u.get("end", "")),
                str(u.get("state", "")),
                str(u.get("note", "")),
            ]
            self.table.on_add_new_row(row_values)
    def on_new_kehu(self):
        def callback(data):
            self.limit = data["limit"]
            self.data = data["data"]
            self.desc = data["desc"]
            self.order_by = data["order_by"]
            self.on_search_text_changed(self.text)
        tip = add_register("child_window", pssw(parent=registry["main_window"]
                                                         , title=f"编辑数据筛选", callback=callback, name=self.name))
        tip.exec_()
    def save_all(self):
        pass