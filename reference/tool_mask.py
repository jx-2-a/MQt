from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt

class MaskWidget(QWidget):
    def __init__(self, parent=None, color="rgba(0,0,0,80)"):
        """
        :param parent: 父窗口
        :param color: 遮罩颜色（带透明度），默认半透明黑色
        """
        super().__init__(parent)
        self.setGeometry(parent.rect() if parent else self.rect())
        self.setStyleSheet(f"background: {color};")
        self.hide()

        # 遮罩要拦截鼠标事件，避免点击穿透
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)

    def show_mask(self):
        if self.parent():
            self.setGeometry(self.parent().rect())
        self.show()

    def close_mask(self):
        self.hide()
