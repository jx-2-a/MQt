from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QSizePolicy

class ButtonBar(QWidget):
    """
    可复用的按钮条
    - buttons: 按钮文本列表
    - side: "left" 或 "right"，决定按钮放左边还是右边
    - ratio: 左侧区域占总宽度比例，右侧自动
    """
    def __init__(self, buttons,connects, side="right", ratio=0.8, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 左右两块布局
        self.left_layout = QHBoxLayout()
        self.left_layout.setContentsMargins(20, 5, 20, 5)
        self.left_layout.setSpacing(12)

        self.right_layout = QHBoxLayout()
        self.right_layout.setContentsMargins(20, 5, 20, 5)
        self.right_layout.setSpacing(12)

        # 左右 widget 占位
        left_widget = QWidget(self)
        left_widget.setLayout(self.left_layout)
        right_widget = QWidget(self)
        right_widget.setLayout(self.right_layout)

        layout.addWidget(left_widget)
        layout.addWidget(right_widget)

        # 设置左右占比
        layout.setStretch(0, int(ratio * 100))
        layout.setStretch(1, 100 - int(ratio * 100))

        # 创建按钮
        self.button_widgets = []
        for i,text in enumerate(buttons):
            btn = QPushButton(text, self)
            self.button_widgets.append(btn)
            if side == "left":
                self.left_layout.addWidget(btn)
            else:
                self.right_layout.addWidget(btn)
            btn.clicked.connect(connects[i])

        # 样式统一
        btn_style = """
            QPushButton {
                padding: 6px 10px;
                border-radius: 6px;
                background-color: #3498db;
                color: white;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """
        for b in self.button_widgets:
            b.setStyleSheet(btn_style)
