from PyQt5.QtWidgets import QWidget, QHBoxLayout, QComboBox, QLineEdit, QPushButton
from PyQt5.QtCore import pyqtSignal,Qt
from item_select import LabeledComboBox

class SearchBar(QWidget):
    def __init__(self, columns, parent=None,button_text=""):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 40, 0)
        self.layout.setSpacing(30)

        self.columns = columns
        self.button_text = button_text

        # 列选择框
        self.creat_combo()
        # 搜索输入框
        self.creat_lineEdit()
        if self.button_text:
            # 新建按钮
            self.creat_newButton()

    def creat_combo(self):
        self.combo_qw = LabeledComboBox(text="")
        self.combo_qw.set_items(self.columns)
        self.combo = self.combo_qw.combo

        # 设置宽度
        # self.combo.setFixedWidth(150)  # 宽一点，例如 150px，可根据需要调整

        # # 设置样式（文字居中）
        # self.combo.setStyleSheet("""
        #     QComboBox {
        #         background-color: rgba(60, 35, 39, 255);
        #         color: rgba(255,255,255,255)
        #         text-align: center;        /* 这个对齐在 QComboBox 不生效 */
        #     }
        #     QComboBox QAbstractItemView {
        #         text-align: center;        /* 下拉菜单里的文字居中 */
        #     }
        # """)

        # 让当前文本居中（需要代理）
        self.combo.setEditable(True)
        self.combo.lineEdit().setAlignment(Qt.AlignCenter)
        self.combo.lineEdit().setReadOnly(True)  # 不允许编辑，只是用来居中显示

        self.layout.addWidget(self.combo_qw)

    def creat_lineEdit(self):
        self.lineEdit = QLineEdit()
        self.lineEdit.setPlaceholderText("输入搜索内容...")
        self.layout.addWidget(self.lineEdit)

    def creat_newButton(self):
        self.newButton = QPushButton(self.button_text)
        # self.newButton.setFixedWidth(100)  # 设置宽度
        # self.newButton.setFixedHeight(30)  # 高度可选

        # 设置样式
        self.newButton.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;   /* 按钮背景色 */
                color: white;                /* 文字颜色 */
                border-radius: 8px;          /* 圆角 */
                padding: 5px 10px;           /* 内边距 */
                font-size: 14px;             /* 字体大小 */
            }
            QPushButton:hover {
                background-color: #45a049;   /* 悬停颜色 */
            }
            QPushButton:pressed {
                background-color: #3e8e41;   /* 点击时颜色 */
            }
        """)

        self.layout.addWidget(self.newButton)


    def on_text_changed(self, hanshu):
        """输入框内容改变时触发"""
        self.lineEdit.textChanged.connect(hanshu)
    def on_new_clicked(self,hanshu):
        """新建按钮被触发时逻辑"""
        if self.button_text:
            self.newButton.clicked.connect(hanshu)
    def setCurrentText(self,text):
        self.combo.setCurrentText(text)
    def setText(self,text):
        self.lineEdit.setText(text)
    def currentText(self):
        return self.combo.currentText()
