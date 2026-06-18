from class_child_window import BaseChildWindow
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit
)
from PyQt5.QtCore import Qt
from item_down_but import ButtonBar
from tool_global_registry import remove_register
from item_inpu_add import MultiListField
from item_label import StyledLabel
from json_manager import JsonManager
from item_select import LabeledComboBox
content_data = JsonManager("_internal/jsons/content_data.json")


class pssw(BaseChildWindow):
    def __init__(self,title="文本编辑",name="",callback=None, parent=None, content="", width=600, height=300):
        super().__init__(parent, title=title, width=width, height=height)
        self.parent = parent
        if parent:
            parent.mask.show_mask()
        self.callback = callback
        self.name = name
        self.user_data = content_data.get(self.name)

        # 核心UI
        self._create_user_fields()
        self.content_layout.addStretch()

        # 创建按钮区
        self.create_buttons(self.content_layout)

        # 置顶拖拽区域
        self.resize_handle.raise_()
        self.show()
    def _create_user_fields(self):
        # 内部表单布局
        self.form_layout = QVBoxLayout()
        self.form_layout.setSpacing(10)
        # 普通模式，允许加号
        self.input_data = MultiListField("设定日期:", [self.user_data.get("data", "")], allow_add=False)
        self.input_note1 = StyledLabel("注意格式: YYYY-MM-DD ")
        self.input_name = MultiListField("展示数量:",[self.user_data.get("limit", "")], allow_add=False)
        self.input_title = LabeledComboBox("排列顺序:",items=["顺序","倒序"])
        self.input_title.set_dtext(self.user_data.get("desc", ""))
        self.input_wechat = MultiListField("指定序列:",[ self.user_data.get("order_by", "")], allow_add=False)
        self.input_note2 = StyledLabel("必须保存列中为时间，或者数字")

        self.form_layout.addWidget(self.input_data)
        self.form_layout.addWidget(self.input_note1)
        self.form_layout.addWidget(self.input_name)
        self.form_layout.addWidget(self.input_title)
        self.form_layout.addWidget(self.input_wechat)
        self.form_layout.addWidget(self.input_note2)

        # --- 包装壳子 ---
        wrapper = QWidget()
        wrapper.setLayout(self.form_layout)

        outer_layout = QHBoxLayout()
        outer_layout.addStretch()  # 顶部留空
        outer_layout.addWidget(wrapper)  # 水平居中

        outer_layout.addStretch()  # 底部留空

        # 放到 content_layout 里
        self.content_layout.addLayout(outer_layout)

        self._set_editable(False)
    def create_buttons(self, layout):
        btn_bar = ButtonBar(
            ["编辑", "确定", "取消"],
            [self.on_edit, self.on_ok, self.on_cancel],
            side="right", ratio=0.4, parent=self
        )
        layout.addWidget(btn_bar)

    def _set_editable(self, editable: bool):
        self.input_data.setEnabled(editable)
        self.input_name.setEnabled(editable)
        self.input_title.setEnabled(editable)
        self.input_wechat.setEnabled(editable)

    def on_edit(self):
        self._set_editable(True)

    def on_ok(self):
        """保存并关闭"""
        data = {
            "data":self.input_data.get_value(),
            "limit": self.input_name.get_value(),
            "desc": self.input_title.get_value(),
            "order_by": self.input_wechat.get_value()
        }
        for i in data:
            self.user_data[i] = data[i]
        content_data.set(self.name,self.user_data)
        if self.callback:
            # new_mode 走新增逻辑，查看模式走更新逻辑都可用同一回调
            self.callback(data)
        self.close()
        remove_register("child_window", self)
        if self.parent:
            self.parent.mask.close_mask()

    def on_cancel(self):
        """取消编辑并关闭"""
        self.close()
        remove_register("child_window", self)
        if self.parent:
            self.parent.mask.close_mask()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = pssw(content="t",name="psad_账单")
    sys.exit(app.exec_())
