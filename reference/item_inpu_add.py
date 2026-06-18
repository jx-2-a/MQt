from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QAction, QLineEdit
)
from item_input import AutoExpandInput


class MultiListField(QWidget):
    """
    多行输入控件：
    - 左侧有标签（仅第一行显示标签，后续行留空位）
    - 仅最底部一行右侧显示 “+” 按钮（嵌入到输入框内，可配置启用/禁用）
    - 支持数组输入/输出
    """
    def __init__(self, label_text: str, values=None, allow_add: bool = True, parent=None):
        super().__init__(parent)
        self.label_text = label_text
        self.allow_add = allow_add
        self.rows = []  # {"input": AutoExpandInput, "action": QAction|None}

        self.main = QVBoxLayout(self)
        self.main.setContentsMargins(0, 0, 0, 0)
        self.main.setSpacing(8)

        if not values:
            values = [""]

        for i, v in enumerate(values):
            # 只有最后一行并且 allow_add=True 时才有 "+"
            self._add_row(v, add_button=(i == len(values) - 1 and self.allow_add))

    def _add_row(self, default_text: str, add_button: bool):
        # 统一标签宽度：取第一行标签宽度
        label_text = self.label_text if len(self.rows) == 0 else ""
        inp = AutoExpandInput(label_text)

        # 给标签一个固定宽度，让所有行对齐
        if len(self.rows) == 0:
            self._label_width = inp.label.sizeHint().width()
        inp.label.setFixedWidth(getattr(self, "_label_width", 0))

        inp.set_dtext(default_text)

        action = None
        if add_button and self.allow_add:
            action = QAction("+", inp.input)
            inp.input.addAction(action, QLineEdit.TrailingPosition)
            action.triggered.connect(self.add_empty_row)

        self.rows.append({"input": inp, "action": action})
        self.main.addWidget(inp)

    def add_empty_row(self):
        if not self.allow_add:
            return  # 禁止加行时直接返回

        # 当前底部行必须非空才能新增
        if self.rows and self.rows[-1]["input"].get_value().strip() == "":
            return

        # 移除旧行的 "+" action
        if self.rows and self.rows[-1]["action"] is not None:
            last = self.rows[-1]
            last["input"].input.removeAction(last["action"])
            last["action"] = None

        # 新增一行空行，添加 "+" action
        self._add_row("", add_button=True)

    def get_values(self):
        """只保留非空行，如果多余空行，保留最后一行空行"""
        vals = []
        empty_rows = []

        for r in self.rows:
            text = r["input"].get_value().strip()
            if text:
                vals.append(text)
            else:
                empty_rows.append(r)

        # 如果最后一行是空的，可以保留（用户可能还要填），但其他空行丢掉
        if empty_rows:
            last_empty = empty_rows[-1]
            vals.append(last_empty["input"].get_value().strip())  # 空字符串

        return [v for v in vals if v]
    def get_value(self):
        r = self.rows[0]
        text = r["input"].get_value().strip()
        return text
    def set_editable(self, editable: bool):
        for r in self.rows:
            r["input"].setEnabled(editable)
            if r["action"]:
                r["action"].setEnabled(editable)
