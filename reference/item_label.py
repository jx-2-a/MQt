from PyQt5.QtWidgets import QWidget,QLabel, QHBoxLayout, QSizePolicy
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from tool_config_style_binder import ConfigStyleBinder

class StyledLabel(QWidget):
    def __init__(self, text: str = "", parent=None,pos=None,next=False):
        super().__init__(parent)
        self.nature = "zhushi"
        self.label = QLabel(text)
        # 自动换行
        if next:
            self.label.setWordWrap(True)
        if pos == "center":
            self.label.setAlignment(Qt.AlignCenter)  # 水平 + 垂直居中
        StyledLabel_STYLE = """
                QLabel {
                    font-family: {{font-family:宋体}}, sans-serif;
                    color: rgba{{label_color:(255,255,255,255)}};
                    font-size: {{label_font_size:24}}px; 
                }"""

        ConfigStyleBinder.bind("item_label", self, StyledLabel_STYLE)
        # 设置大小策略：最小优先，必要时扩展
        self.label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        # 布局
        layout = QHBoxLayout(self)
        layout.setContentsMargins(40, 0, 0, 0)
        layout.addWidget(self.label)
        # layout.addStretch()
    def get_value(self):
        return None
