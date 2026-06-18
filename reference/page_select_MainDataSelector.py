from class_child_window import BaseChildWindow
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout
)
from item_down_but import ButtonBar
from tool_global_registry import remove_register
from item_inpu_add import MultiListField
from item_label import StyledLabel
from json_manager import JsonManager
from item_select import LabeledComboBox

# 读取存储的数据
main_data_json = JsonManager("_internal/jsons/content_data.json")


class MainDataSelector(BaseChildWindow):
    """
    主数据选择窗口
    用于配置和选择主数据源，比如客户表、订单表、账单表等
    """
    def __init__(self, title="主数据选择", name="", callback=None,add=[], parent=None, width=600, height=320):
        super().__init__(parent, title=title, width=width, height=height)
        self.parent = parent
        if parent:
            parent.mask.show_mask()
        self.callback = callback
        self.name = name
        self.add =add
        self.user_data = main_data_json.get(self.name, {})  # 取对应配置
        if self.add:
            item = ["kuadu","danwei","chidu"]
            for i in item:
                print(add[1][i])
                self.user_data[i] = add[1][i]
        # 核心 UI
        self._create_fields()
        self.content_layout.addStretch()

        # 底部按钮区
        self.create_buttons(self.content_layout)

        # 置顶拖拽区域
        self.resize_handle.raise_()
        self.show()

    def _create_fields(self):
        """创建内部表单"""
        self.form_layout = QVBoxLayout()
        self.form_layout.setSpacing(10)

        self.kuadu = MultiListField(
            "跨度:", [self.user_data.get("kuadu", "")], allow_add=False
        )
        self.danwei = LabeledComboBox(
            "单位:", items=["年", "月", "周", "日"]
        )
        self.danwei.set_dtext(self.user_data.get("danwei", ""))
        self.mouwei_n = MultiListField(
            "结束年-月-日:", [self.user_data.get("mouwei_n", "")], allow_add=False
        )
        self.chidu = LabeledComboBox(
            "尺度:",  items=["年", "月", "周", "日"]
        )
        self.chidu.set_dtext(self.user_data.get("chidu", ""))
        # 数据源选择（例如客户表、账单表）
        self.mobiao = LabeledComboBox(
            "数据列:",
            items=["收费", "成本", "利润","客户","服务内容","支付方式"]
        )
        self.mobiao.set_dtext(self.user_data.get("mobiao", ""))
        # 附加说明
        self.input_note = StyledLabel("注意格式: YYYY-MM-DD ")

        # 添加控件
        self.form_layout.addWidget(self.kuadu)
        self.form_layout.addWidget(self.danwei)
        self.form_layout.addWidget(self.mouwei_n)
        self.form_layout.addWidget(self.input_note)
        self.form_layout.addWidget(self.chidu)
        self.form_layout.addWidget(self.mobiao)

        if self.add:
            self.input_note2 = StyledLabel("在增加线条情况下，不可编辑跨度、单位、尺度")
            self.form_layout.addWidget(self.input_note2)

        # --- 包装 ---
        wrapper = QWidget()
        wrapper.setLayout(self.form_layout)

        outer_layout = QHBoxLayout()
        outer_layout.addStretch()
        outer_layout.addWidget(wrapper)
        outer_layout.addStretch()

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
        if self.add and editable:
            pass
        else:
            self.kuadu.setEnabled(editable)
            self.danwei.setEnabled(editable)
            self.chidu.setEnabled(editable)
        self.mouwei_n.setEnabled(editable)
        self.mobiao.setEnabled(editable)

    def on_edit(self):
        self._set_editable(True)

    def on_ok(self):
        """保存并关闭"""
        data = {
            "kuadu": self.kuadu.get_value(),
            "danwei": self.danwei.get_value(),
            "mouwei_n": self.mouwei_n.get_value(),
            "chidu": self.chidu.get_value(),
            "mobiao": self.mobiao.get_value()
        }
        for k in data:
            self.user_data[k] = data[k]
        print(self.name, self.user_data)
        main_data_json.set(self.name, self.user_data)

        if self.callback:
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
    win = MainDataSelector(name="chart_page_main")
    sys.exit(app.exec_())
