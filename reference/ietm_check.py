from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QCheckBox

class AutoCheckBox(QWidget):
    def __init__(self, text="", parent=None):
        super().__init__(parent)
        self.nature = "check"
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(40, 0, 0, 0)

        # self.label = QLabel("选项:")
        self.checkbox = QCheckBox(text)
        self.checkbox.setStyleSheet("""
                    QCheckBox {
                        font-size: 24px;
                        color: rgba(255,255,255,255);
                    }
                    QCheckBox::indicator {
                        width: 24px;
                        height: 24px;
                    }
                """)
        # self.layout.addWidget(self.label)
        self.layout.addWidget(self.checkbox)

        # 自动最小宽度：根据文字长度设置
        self._min_width = self.sizeHint().width()
        self.setMinimumWidth(self._min_width)
    def set_dtext(self,dtext):
        self.checkbox.setChecked(dtext)  # 默认勾选
    @property
    def control(self):
        """返回复选框控件本身"""
        return self.checkbox

    @property
    def min_width(self):
        """返回该控件的最小宽度"""
        return self._min_width

    def get_value(self):
        """获取当前勾选状态"""
        return self.checkbox.isChecked()
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication, QVBoxLayout, QWidget
    import sys

    app = QApplication(sys.argv)
    win = QWidget()
    layout = QVBoxLayout(win)

    checkbox_widget = AutoCheckBox("是否启用功能")
    layout.addWidget(checkbox_widget)

    print("当前状态:", checkbox_widget.value)
    print("最小宽度:", checkbox_widget.min_width)
    # layout.addWidget(btn_field)

    win.show()
    sys.exit(app.exec_())


