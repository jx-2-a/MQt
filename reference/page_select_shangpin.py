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
from page_shangpin import spDetailWindow
import traceback
import sys
from page_tip import tipWindow
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


class spSearchWindow(BaseChildWindow):
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
        if registry["current_page_id"] == "9eDvzcwp2o":
            self.mm = "商品"
            self.search_field = SearchBar([
                "商品名称",
                "日期",
                "型号",
                "简称",
                "分类",
                "价格",
                "来源",
                "备注"], button_text="新建商品信息")
            self.headers = ["日期",
                "商品名称",
                "型号",
                "简称",
                "分类",
                "价格",
                "来源",
                "备注"]
        elif registry["current_page_id"] == "o9GjUsU6V3":
            self.mm = "道具"
            self.search_field = SearchBar([
                        "道具名称",
                        "日期",
                        "简称",
                        "分类",
                        "价格",
                        "来源",
                        "用途",
                        "备注"], button_text="新建道具信息")
            self.headers = ["日期",
                        "道具名称",
                        "简称",
                        "分类",
                        "价格",
                        "来源",
                        "用途",
                        "备注"]
        else:
            self.mm = "商品"
            self.search_field = SearchBar([
               "商品名称",
                "日期",
               "型号",
               "简称",
               "分类",
               "价格",
               "来源",
               "备注"])
            self.headers = ["日期",
                            "商品名称",
                            "型号",
                            "简称",
                            "分类",
                            "价格",
                            "来源",
                            "备注"]

        self.search_field.on_text_changed(self.on_search_text_changed)
        self.search_field.on_new_clicked(self.on_new_kehu)
        self.content_layout.addWidget(self.search_field)

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
        if registry["current_page_id"] == "9eDvzcwp2o":
            if content.strip():
                self.search_field.setCurrentText("商品名称")

        elif registry["current_page_id"] == "o9GjUsU6V3":
            if content.strip():
                self.search_field.setCurrentText("道具名称")

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
            self.filtered_users = rows
            users = []
            self.filtered_id = []

            for i, u in enumerate(rows):
                users.append([
                    str(u.get("date", "")),
                    str(u.get("shopper_name", "")),
                    str(u.get("xinghao", "")),
                    str(u.get("shopper_jia_name", "")),
                    str(u.get("fenlei", "")),
                    str(u.get("jiage", "")),
                    str(u.get("laiyuan", "")),
                    str(u.get("note", ""))
                ])
                self.filtered_id.append(u.get("shopper_id", ""))
            return users
        def transform2(rows):
            self.filtered_users = rows
            users = []
            self.filtered_id = []

            for i, u in enumerate(rows):
                users.append([
                    str(u.get("date", "")),
                    str(u.get("shopper_name", "")),
                    str(u.get("xinghao", "")),
                    str(u.get("shopper_jia_name", "")),
                    str(u.get("fenlei", "")),
                    str(u.get("jiage", "")),
                    str(u.get("laiyuan", "")),
                    str(u.get("note", ""))
                ])
                self.filtered_id.append(u.get("shopper_id", ""))
            return users
        if registry["current_page_id"] == "9eDvzcwp2o":
            text = text.strip().lower()
            field_map = { "商品名称": "shopper_name","日期": "date", "型号": "xinghao", "简称": "shopper_jia_name",
                         "分类": "fenlei", "价格": "jiage", "来源": "laiyuan", "备注": "note"}
            field_key = field_map.get(self.search_field.currentText(), "shopper_name")
            filtered_users = transform(registry["data_libary"].get_latest_per_shopper_shoppingss(field_key,text))
        elif registry["current_page_id"] == "o9GjUsU6V3":
            text = text.strip().lower()
            field_map = {"商品名称": "shopper_name", "日期": "date", "用途": "how_use", "简称": "shopper_jia_name",
                         "分类": "fenlei", "价格": "jiage", "来源": "laiyuan", "备注": "note"}
            field_key = field_map.get(self.search_field.currentText(), "shopper_name")
            filtered_users = transform(registry["data_libary"].get_latest_per_daoju_shoppingss(field_key, text))
        else:
            text = text.strip().lower()
            field_map = {"商品名称": "shopper_name","日期": "date",  "型号": "xinghao", "简称": "shopper_jia_name",
                         "分类": "fenlei", "价格": "jiage", "来源": "laiyuan", "备注": "note"}
            field_key = field_map.get(self.search_field.currentText(), "shopper_name")
            filtered_users = transform(registry["data_libary"].get_latest_per_shopper_shoppingss(field_key, text))
        self.update_table(filtered_users)
    def update_table(self, users_list):
        """刷新表格显示"""
        self.table.clear()
        for u in users_list:
            self.table.on_add_new_row(u)
    def tip(self,text):
        tip = add_register("child_window", tipWindow(registry["main_window"], text))
        tip.exec_()
    def on_ok(self):
        """选择当前行用户"""
        if self.table.selected_row_index  ==-1:
            self.tip("没有进行选择！")
            return
        if 0 <= self.table.selected_row_index < len(self.filtered_users):
            user = self.filtered_users[self.table.selected_row_index]
        self.callback([user["shopper_name"],self.filtered_id[self.table.selected_row_index]],True,all_data=user)
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
            self.callback([text["shopper_name"], text["shopper_id"],"shopper_id"], True)
            self.close()
            remove_register("child_window", self)
            if self.parent:
                self.parent.mask.close_mask()
                self.parent.raise_()
                self.parent.activateWindow()

        tip = add_register("child_window", spDetailWindow(parent=self
                                                         , title=f"添加新{self.mm}", callback=callback, new_mode=True))
        tip.exec_()


# 测试
if __name__ == "__main__":
    app = QApplication(sys.argv)
    register("9eDvzcwp2o","current_page_id")
    print(registry["current_page_id"])
    def callback(user):
        print("选中用户:", user)

    w = spSearchWindow(title="7", callback=callback)
    w.show()
    sys.exit(app.exec_())
