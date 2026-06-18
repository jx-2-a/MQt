from PyQt5.QtWidgets import (
    QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QScrollArea,
    QInputDialog, QApplication, QLabel, QSizePolicy
)
from PyQt5.QtCore import Qt
import sys
import traceback
from json_manager import JsonManager

config = JsonManager("_internal/jsons/setting.json")
from tools import Tool
from page_edit import EditTextWindow
from tool_config_style_binder import ConfigStyleBinder
from tool_global_registry import register, registry, update_register, add_register


def excepthook(exc_type, exc_value, exc_tb):
    traceback.print_exception(exc_type, exc_value, exc_tb)


sys.excepthook = excepthook


class EditableLabel(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.set_style()
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        # 🔑 设置文本水平、垂直居中
        self.setAlignment(Qt.AlignCenter)

    def set_style(self):
        self.setStyleSheet(f"""
                            QLabel {{
                                background: rgba{config.get_set("1_6_1_settings/29")};
                                border: 0px;
                                border-radius: {config.get_set("1_6_1_settings/30")}px;
                                padding: {config.get_set("1_6_1_settings/31")}px {config.get_set("1_6_1_settings/32")}px;

                                font-family: '{config.get_set("1_6_1_settings/33")}', sans-serif;
                                font-size: {config.get_set("1_6_1_settings/35")}px;
                                font-weight: {Tool.get_font_weight("1_6_1_settings/34")};
                                color: rgba{config.get_set("1_6_1_settings/37")};  
                            }}
                            QLabel:hover {{
                                    border-radius: {config.get_set("1_6_1_settings/30")}px;
                                    background: rgba{config.get_set("1_6_1_settings/38")};
                            }}
                        """)


class RowWidget(QWidget):
    def __init__(self, values, col_widths, edit_callback=None, is_header=False, parent=None, this_row=0):
        """
        :param values: 当前行的文本列表
        :param col_widths: 每一列的宽度列表
        :param edit_callback: 双击编辑时调用的函数 (btn, col, is_header)
        :param is_header: 是否是表头行
        :param parent: 父级窗口
        """
        super().__init__(parent)
        self.now_rows = this_row
        self.values = values
        self.col_widths = col_widths
        self.is_header = is_header
        self.edit_callback = edit_callback

        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(f"""
                                            background-color: rgba(0,0,0,0);
                                            border: 0px;
                                            border-radius: 0 px;
                                        """)
        self.h_layout = QHBoxLayout(self)
        self.h_layout.setContentsMargins(0, 0, 0, 0)
        self.h_layout.setSpacing(int(config.get_set("1_6_1_settings/28")))

        self.cells = []  # 存储所有 EditableLabel
        self._build_row()

    def _build_row(self):
        """根据 values 和 col_widths 生成一行"""
        # from editable_label import EditableLabel  # 你定义的 EditableLabel 类

        for i, value in enumerate(self.values):
            cell = EditableLabel(value, self)
            # cell.setFixedWidth(self.col_widths[i])  # 保持该列宽度一致

            # 双击事件绑定到 edit_callback
            if self.edit_callback:
                cell.mouseDoubleClickEvent = lambda e, b=cell, col=i, row=self.now_rows: self.edit_callback(b, col, row, self.is_header)

            self.h_layout.addWidget(cell)
            self.cells.append(cell)
        # self.h_layout.addStretch()

    def update_values(self, values):
        """更新这一行的内容"""
        self.values = values
        for i, text in enumerate(values):
            if i < len(self.cells):
                self.cells[i].setText(text)

    def get_values(self):
        """获取当前行所有单元格文本"""
        return [cell.text() for cell in self.cells]

    def set_highlight(self, highlight=True):
        print("高亮")

    def fixwidth(self, col, new_width):
        self.cells[col].setMinimumWidth(new_width)


class BaseTableWidget(QWidget):
    def __init__(self, headers, parent=None, allow_add_row=False):
        """
        :param headers: 表头列表
        :param allow_add_row: 是否显示 "+ 添加新行" 占位行
        """
        super().__init__(parent)
        self.setStyleSheet("background-color: transparent; border: 0px; border-radius: 0px;")

        self.headers = headers
        self.rows = []
        self.col_widths = [100] * len(headers)
        self.allow_add_row = allow_add_row

        # 主布局 + 滚动区域
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.content_widget = QWidget()
        self.v_layout = QVBoxLayout(self.content_widget)
        self.v_layout.setAlignment(Qt.AlignTop)
        side1 = int(config.get_set("1_6_1_settings/24"))
        side2 = int(config.get_set("1_6_1_settings/25"))
        self.v_layout.setContentsMargins(side1, side2, side1, side2)
        self.v_layout.setSpacing(int(config.get_set("1_6_1_settings/26")))
        self.scroll_area.setWidget(self.content_widget)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.scroll_area)

        # 添加标题行
        # self.add_row(headers, is_header=True)

        # 可选占位行
        if self.allow_add_row:
            self.add_placeholder_row()

        # 样式刷新绑定
        ConfigStyleBinder.bind_function(
            "(Function)-reflash_all_cell_style-(color)", self.reflash_all_cell_style
        )
    def reflash_all_cell_style(self):
        for row in self.rows:
            for cell in row.cells:
                cell.set_style()
        if self.allow_add_row and hasattr(self, "placeholder_btn"):
            self.placeholder_btn.set_style()

    def clear(self):
        """清空表格内容，但保留标题行"""
        for row in self.rows:
            self.v_layout.removeWidget(row)
            row.deleteLater()
        self.rows.clear()

        if self.allow_add_row and hasattr(self, "placeholder_btn"):
            self.v_layout.removeWidget(self.placeholder_btn)
            self.placeholder_btn.deleteLater()
            self.placeholder_btn = None
            self.add_placeholder_row()

    def add_row(self, values, is_header=False):
        """添加普通行，子类可以重载 edit_callback"""
        row = RowWidget(values, self.col_widths, edit_callback=self.edit_cell, is_header=is_header, this_row=len(self.rows))
        self.v_layout.insertWidget(len(self.rows), row)
        self.rows.append(row)

    def add_placeholder_row(self):
        """添加占位行（+ 添加新行），可在子类中覆盖或禁用"""
        self.placeholder_btn = EditableLabel("+ 添加新行")
        self.placeholder_btn.mouseDoubleClickEvent = lambda e: self.on_add_new_row()
        self.v_layout.addWidget(self.placeholder_btn, alignment=Qt.AlignTop)

    def on_add_new_row(self):
        """默认添加空白行，可在子类覆盖实现不同行为"""
        values = [" " if h != "序号" else str(len(self.rows)) for h in self.headers]
        self.add_row(values)

    def edit_cell(self, button, col, row, is_header=False):
        """默认双击编辑单元格，可在子类覆盖"""

        def callback_edit(text):
            button.setText(text)
            self.adjust_min_width(button, text, col)

        if row > 0:
            tip = add_register(
                "child_window",
                EditTextWindow(
                    parent=registry["main_window"],
                    title=f"编辑-第{row}行-{self.headers[col]}项",
                    callback=callback_edit,
                    content=button.text()
                )
            )
            tip.exec_()

    def adjust_min_width(self, widget, text, col):
        """根据内容调整输入框最小宽度"""
        fm = widget.fontMetrics()
        text_width = fm.horizontalAdvance(text)
        padding = fm.height()
        new_width = max(text_width + padding, 180)
        if new_width > self.col_widths[col]:
            self.col_widths[col] = new_width
            for row in self.rows:
                row.fixwidth(col, new_width)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    headers = ["日期", "收入", "成本", "利润", "备注"]
    w = TableWidget(headers)
    w.setWindowTitle("商铺记账表格 Demo")
    w.resize(800, 400)
    w.show()
    sys.exit(app.exec_())
