from PyQt5.QtWidgets import (
    QWidget, QLineEdit, QComboBox, QVBoxLayout, QHBoxLayout, QApplication
)
from PyQt5.QtCore import Qt,QTimer
import sys
from item_excel import TableWidget
from item_down_but import ButtonBar
from tool_global_registry import remove_register,register, registry,update_register,add_register
from class_child_window import BaseChildWindow
from item_search_bar import SearchBar

import traceback
import sys

def excepthook(exc_type, exc_value, exc_tb):
    traceback.print_exception(exc_type, exc_value, exc_tb)

sys.excepthook = excepthook
class MyTableWidget(TableWidget):
    def __init__(self, headers,parent=None, allow_add_row=True):
        super().__init__(headers, parent, allow_add_row)
        self.last_gaoliang = None
        self.selected_row_index = -1
    def bind_funcation(self,row,i):
        for n, cell in enumerate(row.cells):
            cell.mousePressEvent = lambda e,b=cell, r=i,c=n: self.on_row_clicked(b,r,c)
    def on_row_clicked(self,button,row,col):
        if self.last_gaoliang is not None:
            self.rows[self.last_gaoliang].set_highlight(False)
            self.last_gaoliang = row-1
            self.rows[row-1].set_highlight()
        else:
            self.last_gaoliang = row - 1
            self.rows[row-1].set_highlight()
        self.selected_row_index = row-1


class kehudata_Window(BaseChildWindow):
    def __init__(self,title, parent=None,id="", width=1200, height=600,baoxiu = False):
        """
        :param users: 用户数据列表，每个用户是 dict，如 {"name": ..., "plate": ..., "phone": ...}
        :param callback: 点击行时回调，参数为选中用户 dict
        """
        super().__init__(parent, title=title, width=width, height=height)
        self.parent = parent
        self.id = id
        if parent:
            parent.mask.show_mask()
        self.baoxiu = baoxiu
        # 🔹 搜索栏
        if not self.baoxiu:
            search = ["支付方式","日期", "服务内容","备注"]
        else:
            search = ["产品","产品序列", "保修时长","日期","当前状态"]
        self.search_field =SearchBar(search,button_text="")
        self.search_field.on_text_changed(self.on_search_text_changed)
        self.content_layout.addWidget(self.search_field)
        if not self.baoxiu:
            self.headers = ["序号",
                            "日期",
                            "客户",
                            "服务内容",
                            "收费",
                            "成本",
                            "利润",
                            "支付方式",
                            "备注"]
        else:
            self.headers =["序号",
                            "日期",
                            "客户",
                            "保修内容",
                            "产品序号",
                            "保修起始日期",
                            "保修有效时长",
                            "保修终止日期",
                            "当前状态",
                            "备注"]

        self.table = MyTableWidget(self.headers, allow_add_row=False)
        self.content_layout.addWidget(self.table)

        # 创建按钮区
        self.create_buttons(self.content_layout)

        #初始化内容

        QTimer.singleShot(0, lambda:  self.on_search_text_changed())

        # 置顶拖拽区域
        self.resize_handle.raise_()
        self.show()
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

    def create_buttons(self, layout):
        btn_bar = ButtonBar(
            ["关闭"],
            [ self.on_cancel],
            side="right", ratio=0.6, parent=self
        )
        layout.addWidget(btn_bar)
    def on_search_text_changed(self, text=""):
        """根据搜索栏内容和选择字段过滤用户"""
        text = text.strip().lower()

        if not self.baoxiu:
            field_map = {"支付方式":"payment_method","日期":"date", "服务内容": "service","备注": "note"}
            field_key = field_map.get(self.search_field.currentText(), "payment_method")

            if text:
                filtered_users = registry["data_libary"].search_billings_by_customer_field(self.id,field_key,text)
            else:
                filtered_users = registry["data_libary"].get_billings_by_customer_id(self.id)
        else:
            field_map = {"产品": "product", "产品序列": "product_id", "保修时长": "long", "日期": "date","当前状态":"state"}
            field_key = field_map.get(self.search_field.currentText(), "payment_method")
            if text:
                filtered_users = registry["data_libary"].search_warranty_card_by_customer_field(self.id,field_key,text)
            else:
                filtered_users = registry["data_libary"].get_warranty_card_by_customer_id(self.id)
        self.update_table(filtered_users)
    def update_table(self, users_list):
        """刷新表格显示"""
        self.table.clear()
        if not self.baoxiu:
            self.upup(users_list)
        else:
            self.downdown(users_list)
    def on_cancel(self):
        self.close()
        remove_register("child_window", self)
        if self.parent:
            self.parent.mask.close_mask()



# 测试
if __name__ == "__main__":
    app = QApplication(sys.argv)
    users = [
        {"name": "张三", "plate": "粤A12345", "phone": "13800138000"},
        {"name": "李四", "plate": "粤B54321", "phone": "13900139000"},
        {"name": "王五", "plate": "粤C67890", "phone": "13700137000"},
    ]

    def callback(user):
        print("选中用户:", user)

    w = UserSearchWindow(title="7", callback=callback)
    w.show()
    sys.exit(app.exec_())
