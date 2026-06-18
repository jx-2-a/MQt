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
from page_kehu import UserDetailWindow
import traceback
from page_tip import tipWindow
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


class UserSearchWindow(BaseChildWindow):
    def __init__(self,title, callback=None,content=" ", parent=None, width=1200, height=600):
        """
        :param users: 用户数据列表，每个用户是 dict，如 {"name": ..., "plate": ..., "phone": ...}
        :param callback: 点击行时回调，参数为选中用户 dict
        """
        super().__init__(parent, title=title, width=width, height=height)
        self.parent = parent
        if parent:
            parent.mask.show_mask()
        self.callback = callback
        self.filtered_users = []
        self.filtered_id = []
        # 🔹 搜索栏
        self.search_field =SearchBar(["姓名", "车牌", "电话"],button_text="新建客户信息")
        self.search_field.on_text_changed(self.on_search_text_changed)
        self.search_field.on_new_clicked(self.on_new_kehu)
        self.content_layout.addWidget(self.search_field)

        # 🔹 用户列表表格
        self.headers = ["姓名", "车牌", "电话"]
        self.table = MyTableWidget(self.headers, allow_add_row=False)
        self.content_layout.addWidget(self.table)

        # 创建按钮区
        self.create_buttons(self.content_layout)

        #初始化内容
        self.chushi(content)
        QTimer.singleShot(0, lambda:  self.on_search_text_changed(content))

        # 置顶拖拽区域
        self.resize_handle.raise_()
        self.show()

    def get_keu_infor(self):
        rows = registry["data_libary"].get_customers_random(50)
        self.users = []

        for r in rows:
            plate_str = "/".join(r.get("plates", [])) if r.get("plates") else ""
            phone_str = "/".join(r.get("phones", [])) if r.get("phones") else ""

            self.users.append({
                "name": r.get("name", ""),
                "plate": plate_str,
                "phone": phone_str
            })
    def chushi(self,content):
        if content.strip():
            self.search_field.setCurrentText("姓名")
            self.search_field.setText(content)
    def create_buttons(self, layout):
        btn_bar = ButtonBar(
            ["确定", "取消"],
            [self.on_ok, self.on_cancel],
            side="right", ratio=0.6, parent=self
        )
        layout.addWidget(btn_bar)
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
                    "plate": plate_str,
                    "phone": phone_str
                })
                self.filtered_id.append(r.get("id", ""))
            return users

        text = text.strip().lower()
        field_map = {"姓名": "name", "车牌": "plate", "电话": "phone"}
        field_key = field_map.get(self.search_field.currentText(), "name")
        if text:
            self.filtered_users = transform(registry["data_libary"].search_customers_by_field(field_key,text))
        else:
            self.filtered_users = transform(registry["data_libary"].get_customers_random(50))
        self.update_table(self.filtered_users)
    def update_table(self, users_list):
        """刷新表格显示"""
        self.table.clear()
        for u in users_list:
            row_values = [u.get("name",""), u.get("plate",""), u.get("phone","")]
            self.table.on_add_new_row(row_values)
    def tip(self,text):
        tip = add_register("child_window", tipWindow(registry["main_window"], text))
        tip.exec_()
    def on_ok(self):
        if self.table.selected_row_index  ==-1:
            self.tip("没有进行选择！")
            return
        """选择当前行用户"""
        if 0 <= self.table.selected_row_index < len(self.filtered_users):
            user = self.filtered_users[self.table.selected_row_index]
        else:
            user = {"name":""}
        self.callback([user["name"],self.filtered_id[self.table.selected_row_index],"customer_id"],True)
        self.close()
        remove_register("child_window", self)
        if self.parent:
            self.parent.mask.close_mask()
    def on_cancel(self):
        self.close()
        remove_register("child_window", self)
        if self.parent:
            self.parent.mask.close_mask()
    def on_new_kehu(self):
        def callback(text):
            self.search_field.setCurrentText("姓名")
            self.search_field.setText(text)
            self.on_search_text_changed(text)

        tip = add_register("child_window", UserDetailWindow(parent=self
                                                         , title=f"添加新用户", callback=callback, new_mode=True))
        tip.exec_()


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
