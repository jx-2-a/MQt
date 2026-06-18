from PyQt5.QtWidgets import QWidget, QLabel, QFrame, QHBoxLayout, QSizePolicy
from PyQt5.QtCore import Qt
from tool_config_style_binder import ConfigStyleBinder

class TextLineWidget(QWidget):
    """左边文字，右边横线填满"""

    def __init__(self, text: str = "", parent=None):
        super().__init__(parent)
        self.nature = "fenge"
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 20, 0)
        layout.setSpacing(20)

        self.label = QLabel(text)
        self.label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        StyledLabel_STYLE = """
                        QLabel {
                            font-family: {{font-family:宋体}}, sans-serif;
                            color: rgba{{label_color:(255,255,255,255)}};
                            font-size: {{label_font_size:24}}px; 
                        }"""

        ConfigStyleBinder.bind("TextLineWidget", self, StyledLabel_STYLE)

        self.line = QFrame()
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)
        self.line.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.line.setFixedHeight(1)  # 线条高度

        layout.addWidget(self.label)
        layout.addWidget(self.line)
        self.setLineStyle("solid", "gray", 3)  # 实线，黑色，粗2px

    def get_value(self):
        return None

    def setLineStyle(self, style: str = "solid", color: str = "gray", width: int = 1):
        """
        设置横线样式
        :param style: 线型 ('solid', 'dashed', 'dotted', 'double')
        :param color: 颜色 (任意CSS颜色: 'red', '#FF0000', 'rgb(100,100,100)' 等)
        :param width: 线宽 (像素)
        """
        style_map = {
            "solid": "solid",
            "dashed": "dashed",
            "dotted": "dotted",
            "double": "double"
        }
        css = f"border-top: {width}px {style_map.get(style,'solid')} {color};"
        self.line.setStyleSheet(css)