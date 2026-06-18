from PyQt5.QtWidgets import (
    QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QScrollArea,
    QInputDialog, QApplication, QLabel ,QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal
from json_manager import JsonManager
config = JsonManager("_internal/jsons/setting.json")
from tools import Tool
from tool_config_style_binder import ConfigStyleBinder
import traceback
import sys

def excepthook(exc_type, exc_value, exc_tb):
    traceback.print_exception(exc_type, exc_value, exc_tb)

sys.excepthook = excepthook

class EditableLabel(QLabel):
    textChanged = pyqtSignal(str,int)
    def __init__(self, text, parent=None,col = None):
        super().__init__(text, parent)
        self.col = col
        self.set_style()
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
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

    def setText(self, text: str):
        old_text = self.text()
        super().setText(text)
        if text != old_text:  # 避免重复触发
            self.textChanged.emit(text,self.col)
class RowWidget(QWidget):
    def __init__(self, values, col_widths, is_header=False, parent=None,this_row = 0):
        """
        :param values: 当前行的文本列表
        :param col_widths: 每一列的宽度列表
        :param edit_callback: 双击编辑时调用的函数 (btn, col, is_header)
        :param is_header: 是否是表头行
        :param parent: 父级窗口
        """
        super().__init__(parent)
        self.now_rows = this_row
        self.jilu_id = {
            "customer_id":"",
            "shopper_id": ""
        }
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.values = values
        self.col_widths = col_widths
        self.is_header = is_header
        self.setStyleSheet(f"""
                                            background-color: transparent;
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
        for i, value in enumerate(self.values):
            cell = EditableLabel(value, self,col=i)
            self.h_layout.addWidget(cell)
            self.cells.append(cell)

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
        """设置整行高亮"""
        if highlight:
            self.setStyleSheet("""
                background-color: rgba(20,20,20,0.8);
                border: 0px;
                border-radius: 8px;
            """)
        else:
            self.setStyleSheet("""
                background-color: transparent;
                border: 0px;
                border-radius: 8px;
            """)

    def fixwidth(self, col, new_width):
        self.cells[col].setMinimumWidth(new_width)
class TableWidget(QWidget):
    def __init__(self, headers, parent=None,allow_add_row=False):
        super().__init__(parent)
        self.parent = parent
        self.setStyleSheet(f"""
                                    background-color: transparent;
                                    border: 0px;
                                    border-radius: 0 px;
                                """)
        self.allow_add_row = allow_add_row

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.headers = headers
        self.rows = []   # 存储所有行
        self.col_widths = [100] * len(headers)  # 每列的固定宽度

        # 主布局 + 滚动区域
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        STYLE ="""
            /* 垂直滚动条 */
            QScrollBar:vertical {
                width: {{1_6_1_settings/19:12}}px;
                background: transparent;
                margin: 0px 0px 0px 0px;
                border-radius:  {{1_6_1_settings/20:6}}px;
            }
            QScrollBar::handle:vertical {
                background: rgba{{1_6_1_settings/21:(150,150,150,120)}};
                border-radius:  {{1_6_1_settings/20:12}}px;
                min-height: 0px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba{{1_6_1_settings/22:(180,180,180,180)}};
            }
            QScrollBar::sub-line:vertical,
            QScrollBar::add-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: none;
            }
    
            /* 横向滚动条 */
            QScrollBar:horizontal {
                height: {{1_6_1_settings/19:12}}px;
                background: transparent;
                border-radius: {{1_6_1_settings/20:6}}px;
            }
            QScrollBar::handle:horizontal {
                background: rgba{{1_6_1_settings/21:12}};
                border-radius: {{1_6_1_settings/20:12}}px;
                min-width: 0px;
            }
            QScrollBar::handle:horizontal:hover {
                background: rgba{{1_6_1_settings/22:12}};
            }
            QScrollBar::sub-line:horizontal,
            QScrollBar::add-line:horizontal {
                width: 0px;
            }
            QScrollBar::add-page:horizontal,
            QScrollBar::sub-page:horizontal {
                background: none;
            }
        """
        ConfigStyleBinder.bind("(Style)-item_eccel_QScrollBar-(color)", self.scroll_area, STYLE)

        self.content_widget = QWidget()
        self.v_layout = QVBoxLayout(self.content_widget)
        self.v_layout.setAlignment(Qt.AlignTop)
        side1 = int(config.get_set("1_6_1_settings/24"))
        side2 = int(config.get_set("1_6_1_settings/25"))
        self.v_layout.setContentsMargins(side1, side2, side1, side2)
        self.v_layout.setSpacing(int(config.get_set("1_6_1_settings/26")))

        self.scroll_area.setWidget(self.content_widget)

        main_layout.addWidget(self.scroll_area)

        if self.allow_add_row:
            self.add_placeholder_row()
        ConfigStyleBinder.bind_function("(Function)-reflash_all_cell_style-(color)", self.reflash_all_cell_style)
    def reflash_all_cell_style(self):
        for row in self.rows:
            for cell in row.cells:
                cell.set_style()
        self.placeholder_btn.set_style()
    def get_row_text(self,row):
        """获取单行的文本,更新记录中此行内容"""
        pass
    def bind_funcation(self,row,i):
        """
        给按键绑定函数，在子类中覆盖
        row::行id
        i::该行为第几行
        """
        pass
    def add_to_jilu(self):
        """
        向值记录数组中添加空占位数据
        """
        pass
    def clear(self):
        """清空表格内容，但保留标题行"""
        # 移除所有行 widget
        for row in self.rows:
            self.v_layout.removeWidget(row)
            row.deleteLater()
        self.rows.clear()

        # 移除占位按钮
        if hasattr(self, "placeholder_btn") and self.placeholder_btn:
            self.v_layout.removeWidget(self.placeholder_btn)
            self.placeholder_btn.deleteLater()
            self.placeholder_btn = None
        if self.allow_add_row:
            # 重新添加占位行
            self.add_placeholder_row()
    def add_row(self, values, is_header=False):
        row = RowWidget(values, self.col_widths, is_header=False,this_row = len(self.rows))
        self.v_layout.insertWidget(len(self.rows), row)
        self.rows.append(row)
        self.bind_funcation(row,len(self.rows))
        return row

    def add_placeholder_row(self):
        self.placeholder_btn = EditableLabel("+ 添加新行")
        self.placeholder_btn.mouseDoubleClickEvent = lambda e: self.on_add_new_row(values=[])
        # self.placeholder_btn.clicked.connect(self.on_add_new_row)
        self.v_layout.addWidget(self.placeholder_btn, alignment=Qt.AlignTop)
    def on_add_new_row(self,values = []):
        if not values:
            for item in self.headers:
                if item == "序号":
                    values.append(str(len(self.rows)))
                else:
                    values.append(" ")
            row = self.add_row(values)
            self.add_to_jilu()
            self.get_row_text(self.rows[len(self.rows)-1])
        else:
            row = self.add_row(values)
        for i, text in enumerate(values):
            row.cells[i].setText(text)
            self.adjust_min_width(row.cells[i], text, i)
    def adjust_min_width(self,widget,text,col):
        """根据内容调整输入框最小宽度"""
        fm = widget.fontMetrics()
        text_width = fm.horizontalAdvance(text)
        padding = fm.height()
        new_width = max(text_width + padding, 180)
        if self.col_widths:
            if new_width > self.col_widths[col]:
                self.col_widths[col] = new_width
                # 同步更新这一列的所有按钮宽度
                for row in self.rows:
                    row.fixwidth(col,new_width)
            else:
                widget.setMinimumWidth(self.col_widths[col])



if __name__ == "__main__":
    app = QApplication(sys.argv)
    headers = ["日期", "收入", "成本", "利润", "备注"]
    w = TableWidget(headers)
    w.setWindowTitle("商铺记账表格 Demo")
    w.resize(800, 400)
    w.show()
    sys.exit(app.exec_())
