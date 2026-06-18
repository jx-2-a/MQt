from PyQt5.QtWidgets import (QWidget, QLabel, QLineEdit,
                             QHBoxLayout, QSizePolicy, QPushButton, QFileDialog)
from PyQt5.QtCore import Qt,QTimer
from tool_config_style_binder import ConfigStyleBinder
from page_select_color import ColorPickerWindow
from tool_global_registry import register, registry,add_register,remove_register

class PathSelector(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.relect = None
        self.setAttribute(Qt.WA_StyledBackground, True)

        # 输入框
        self.line_edit = QLineEdit()
        self.line_edit.setPlaceholderText("点击…选取内容")
        # 自动调整输入框最小宽度
        self.line_edit.textChanged.connect(self.adjust_min_width)

        # 按钮
        self.browse_button = QPushButton("…")
        self.browse_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)



        # 水平布局
        layout = QHBoxLayout(self)
        layout.setContentsMargins(1, 1, 1, 1)  # 贴合
        layout.setSpacing(0)  # 无间距
        layout.addWidget(self.line_edit,1)
        layout.addWidget(self.browse_button)

        self.setLayout(layout)
    def adjust_min_width(self):
        """根据内容调整输入框最小宽度"""
        fm = self.line_edit.fontMetrics()
        text = self.line_edit.text() or " "
        text_width = fm.horizontalAdvance(text)

        # 使用字体高度近似 padding（更随字体变化）
        padding = fm.height()//2

        # 也可以根据 QStyle 取真实的 padding（更精确）
        # option = QStyleOptionFrame()
        # self.input.initStyleOption(option)
        # padding = self.input.style().pixelMetric(QStyle.PM_DefaultFrameWidth, option, self.input)

        self.line_edit.setMinimumWidth(text_width + padding)
    def set_value(self, value: str,relect:str):
        """设置输入内容"""
        self.line_edit.setText(value)
        self.relect = relect
        self.browse_button.clicked.connect(self.chuli)
        QTimer.singleShot(0,self.adjust_min_width)
    def chuli(self):
        def callback_color(color):
            self.new_setText(color)
        if "color" in self.relect:
            tip = add_register("child_window", ColorPickerWindow(parent=self.parent,color=self.line_edit.text(),callback = callback_color ))
            tip.exec_()
        elif "path" in self.relect:
            def open_folder_dialog():
                file, _  = QFileDialog.getOpenFileName(
                    self,
                    "选择图片",
                    "D:\\",  # 初始目录（可以改成你需要的路径）
                    "图片文件 (*.png *.jpg *.bmp);;所有文件 (*.*)"
                )
                if file:
                    self.new_setText(file)
            open_folder_dialog()
    def new_setText(self,text):
        self.line_edit.setText(text)
class InputWithButton(QWidget):
    def __init__(self, text: str = "text:", button_text: str = "...", parent=None):
        super().__init__(parent)
        self.nature = "input_with_button"
        self.parent = parent
        # 左侧标签
        self.label = QLabel(text)

        # 输入框
        self.input_b = PathSelector(parent=self.parent)
        LABEL_INPUT_STYLE = """
                QWidget {
                    background-color: rgba(30,30,30,255);
                    border: 1px solid rgba(150,150,150,255);
                    border-radius: 8px;
                }
                QLabel {
                    background-color: rgba(30,30,30,0);
                    border: 0px solid rgba(150,150,150,255);
                    
                    font-family: {{font-family:宋体}}, sans-serif;
                    color: rgba{{label_color:(255,255,255,255)}};
                    font-size: {{label_font_size:24}}px; 
                }
                QLineEdit {
                    background-color: rgba{{input_bg_color:(30,30,30,0)}};
                    border: {{input_border_width:0}}px solid rgba{{input_border_color:(150,150,150,255)}};
                    border-radius: {{input_radius:8}}px;

                    font-family: {{font-family:宋体}}, sans-serif;
                    font-size: {{input_font_size:24}}px;
                    color: rgba{{label_color:(255,255,255,255)}};

                    padding: {{input_padding_shangxia:2}}px  {{input_padding_zuoyou:5}}px;
                }

                QPushButton {
                    background-color: rgba{{button_bg_color:(60,60,60,0)}};
                    border: {{button_border_width:0}}px solid rgba{{button_border_color:(150,150,150,255)}};
                    border-radius: {{button_radius:8}}px;

                    font-family: {{font-family:宋体}}, sans-serif;
                    font-size: {{button_font_size:24}}px;
                    color: rgba{{button_color:(255,255,255,255)}};

                    padding: 0px 5px;
                }
                QPushButton:hover {
                    background-color: rgba{{button_hover_bg:(100,100,100,255)}};
                }
                """
        ConfigStyleBinder.bind("item_input_button", self, LABEL_INPUT_STYLE)

        # 布局
        layout = QHBoxLayout(self)
        layout.setContentsMargins(40, 0, 0, 0)
        layout.setSpacing(6)
        layout.addWidget(self.label)
        layout.addWidget(self.input_b, 1)

    def get_value(self):
        """获取当前输入内容"""
        return self.input_b.line_edit.text()

    def set_value(self, value: str,relect:str):
        """设置输入内容"""
        self.input_b.set_value(value,relect)

    def set_button_callback(self, callback):
        """绑定按钮点击回调"""
        self.button.clicked.connect(callback)


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication, QVBoxLayout, QWidget
    import sys

    app = QApplication(sys.argv)
    win = QWidget()
    layout = QVBoxLayout(win)

    field = InputWithButton("路径:")
    field.set_button_callback(lambda: print("点击了按钮, 当前输入:", field.get_value()))
    layout.addWidget(field)

    field2 = InputWithButton("备注:", "选择")
    layout.addWidget(field2)

    win.show()
    sys.exit(app.exec_())
