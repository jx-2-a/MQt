from class_child_window import BaseChildWindow
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem,QLineEdit, QAction
)
from page_tip import tipWindow
from PyQt5.QtCore import Qt
import sys
from tools import Tool
from item_down_but import ButtonBar
from item_input import AutoExpandInput
from tool_global_registry import remove_register
from item_inpu_add import MultiListField
import traceback
from tool_global_registry import remove_register,register, registry,update_register,add_register

from page_show_kehudate import kehudata_Window
def excepthook(exc_type, exc_value, exc_tb):
    traceback.print_exception(exc_type, exc_value, exc_tb)
sys.excepthook = excepthook
class spDetailWindow(BaseChildWindow):
    def __init__(self, user_data=None, records=None, title="用户详情",
                 parent=None, width=400, height=520, callback=None, new_mode=None):
        """
        编辑内容：【客户姓名，个性称号，电话号码（多个），车牌号码（多个）,微信号,备注】
        内容按键：【查询消费记录】（仅查看模式显示）
        底部按键：【编辑信息，确定，取消】（新建模式无“编辑信息”）
        规则：
          1) 窗口既可新建也可查看；新建模式不显示内容按键与“编辑信息”，所有输入默认可编辑；
             查看模式默认禁用编辑，可点“编辑信息”启用。
          2) 单字段用 AutoExpandInput；多字段用 MultiListField（竖直多行，最下行右侧有“+”）。
          3) 电话、车牌支持数组输入输出。
        """
        super().__init__(parent, title=title, width=width, height=height)
        self.parent = parent
        if parent:
            parent.mask.show_mask()

        self.callback = callback
        if user_data :
            self.user_id = user_data
            self.user_data = registry["data_libary"].get_shoppingss_by_shopper_id(user_data)
        else:
            self.user_data ={
                "shopper_id":Tool.generate_random_string(20),
                "shopper_name": ""
            }
        self.records = records or []

        # 自动判断模式：未传则按是否有数据来判定
        if new_mode is None:
            new_mode = not bool(self.user_data)
        self.new_mode = new_mode

        # 核心UI
        self._create_user_fields()
        self.content_layout.addStretch()
        # 底部按钮区
        self._create_buttons(self.content_layout)

        self.resize_handle.raise_()
        self.show()

    # ---------- UI 构建 ----------
    def _create_user_fields(self):
        # 内部表单布局
        self.form_layout = QVBoxLayout()
        self.form_layout.setSpacing(10)
        self.bianhao = self.user_data.get("shopper_id", "")
        self.mingcheng = self.user_data.get("shopper_name","")
        # 单字段
        # 普通模式，允许加号
        self.bianhao_input = MultiListField("编号",[self.bianhao], allow_add=False)
        self.mingcheng_input = MultiListField("名称", [self.mingcheng], allow_add=False)

        self.form_layout.addWidget(self.bianhao_input)
        self.form_layout.addWidget(self.mingcheng_input)

        if not self.new_mode:
            self._create_record_button(self.form_layout)

        # --- 包装壳子 ---
        wrapper = QWidget()
        wrapper.setLayout(self.form_layout)

        outer_layout = QHBoxLayout()
        outer_layout.addStretch()  # 顶部留空
        outer_layout.addWidget(wrapper)  # 水平居中
        # “查询消费记录”按钮（仅查看模式显示）

        outer_layout.addStretch()  # 底部留空

        # 放到 content_layout 里
        self.content_layout.addLayout(outer_layout)

        # 查看模式默认禁用编辑
        if not self.new_mode:
            self._set_editable(False)

    def _on_query_baoxiu_records(self):
        """简单地把 records 作为只读表格展示/切换。无记录时不创建。"""
        tip = add_register("child_window", kehudata_Window(parent=self
                                                            , title=f"{self.name} 保修记录", id=self.id,baoxiu = True))
        tip.exec_()
    def _create_record_button(self,outer_layout):
        self.btn_record = QPushButton("查询消费记录")
        self.btn_record.setFixedHeight(30)
        self.btn_record.clicked.connect(self._on_query_records)
        outer_layout.addWidget(self.btn_record)

    def _create_buttons(self, layout):
        labels = ["确定", "取消"]
        funcs = [self._on_ok, self._on_cancel]

        if not self.new_mode:
            labels.insert(0, "编辑信息")
            funcs.insert(0, self._on_edit)

        btn_bar = ButtonBar(labels, funcs, side="right", ratio=0.4, parent=self)
        layout.addWidget(btn_bar)

    # ---------- 行为 ----------
    def _set_editable(self, editable: bool):
        self.input_name.setEnabled(editable)
        self.input_title.setEnabled(editable)
        self.input_wechat.setEnabled(editable)
        self.input_note.setEnabled(editable)
        self.multi_phone.set_editable(editable)
        self.multi_plate.set_editable(editable)

    def _on_edit(self):
        self._set_editable(True)

    def _on_ok(self):
        """采集数据并回传：phones/plates 一定是数组"""
        data = {
            "shopper_id": self.bianhao_input.get_value(),
            "shopper_name": self.mingcheng_input.get_value()
        }
        shopper_name = data["shopper_name"].strip()

        if self.callback and shopper_name:
            # new_mode 走新增逻辑，查看模式走更新逻辑都可用同一回调
            self.callback(data)
            self._close_self()
        else:
            self.tip("输入名称无效！")
    def tip(self, text):
        tip = add_register("child_window", tipWindow(self, text))
        tip.exec_()
    def _on_cancel(self):
        self._close_self()

    def _on_query_records(self):
        """简单地把 records 作为只读表格展示/切换。无记录时不创建。"""
        tip = add_register("child_window", kehudata_Window(parent=self
                                                            , title=f"{self.name} 消费记录", id=self.id))
        tip.exec_()


    def _close_self(self):
        self.close()
        remove_register("child_window", self)
        if self.parent:
            self.parent.mask.close_mask()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 查看模式示例
    user = {
        "name": "张三",
        "title": "老客户",
        "wechat": "wx123",
        "note": "VIP",
        "phones": ["123456789", "987654321"],
        "plates": ["粤A12345", "粤B54321"]
    }
    records = [
        {"year": 2025, "month": 8, "day": 28, "amount": 100, "note": "测试1"},
        {"year": 2025, "month": 8, "day": 27, "amount": 200, "note": "测试2"},
    ]
    win = UserDetailWindow(user_data=user, records=records, new_mode=False)

    # 新建模式示例
    # win = UserDetailWindow(new_mode=True)

    sys.exit(app.exec_())
