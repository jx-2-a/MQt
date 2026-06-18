from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QHBoxLayout, QSizePolicy
from PyQt5.QtCore import Qt,QTimer
from tool_config_style_binder import ConfigStyleBinder

class AutoExpandInput(QWidget):
    def __init__(self, text: str = "text:", parent=None):
        super().__init__(parent)
        self.nature = "input"
        # self.min_width = 100  # 默认最小宽度
        self.label = QLabel(text)
        self.input = QLineEdit()
        LABEL_INPUT_STYLE = """
        QLabel {
            font-family: {{font-family:宋体}}, sans-serif;
            color: rgba{{label_color:(255,255,255,255)}};
            font-size: {{label_font_size:24}}px; 
        }

        QLineEdit {
            background-color: rgba{{input_bg_color:(30,30,30,255)}};
            border: {{input_border_width:1}}px solid rgba{{input_border_color:(150,150,150,255)}};
            border-radius: {{input_radius:8}}px;
            
            font-family: {{font-family:宋体}}, sans-serif;
            font-size: {{input_font_size:24}}px;
            color: rgba{{label_color:(255,255,255,255)}};
            
            padding: {{input_padding_shangxia:2}}px  {{input_padding_zuoyou:5}}px;
        }
        """
        ConfigStyleBinder.bind("item_input",self, LABEL_INPUT_STYLE)
        self.input.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)

        # 自动调整输入框最小宽度
        self.input.textChanged.connect(self.adjust_min_width)

        # 布局
        layout = QHBoxLayout(self)
        layout.setContentsMargins(40, 0, 0, 0)
        layout.addWidget(self.label)
        layout.addWidget(self.input)
        # layout.addStretch()



    def adjust_min_width(self):
        """根据内容调整输入框最小宽度"""
        fm = self.input.fontMetrics()
        text = self.input.text() or " "
        text_width = fm.horizontalAdvance(text)

        # 使用字体高度近似 padding（更随字体变化）
        padding = fm.height() // 2

        # 也可以根据 QStyle 取真实的 padding（更精确）
        # option = QStyleOptionFrame()
        # self.input.initStyleOption(option)
        # padding = self.input.style().pixelMetric(QStyle.PM_DefaultFrameWidth, option, self.input)

        self.input.setMinimumWidth(text_width + padding)

    def get_value(self):
        """获取当前输入内容"""
        return self.input.text()
    def set_dtext(self,dtext):
        self.input.setText(dtext)  # 设置默认值
        QTimer.singleShot(0, self.adjust_min_width)
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication, QVBoxLayout, QWidget
    import sys

    app = QApplication(sys.argv)
    win = QWidget()
    layout = QVBoxLayout(win)

    field = AutoExpandInput("姓hgh名:")
    layout.addWidget(field)

    btn_field = AutoExpandInput("备注:")
    layout.addWidget(btn_field)

    win.show()
    sys.exit(app.exec_())
