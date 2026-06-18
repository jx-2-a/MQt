from PyQt5.QtWidgets import QWidget, QLabel, QComboBox, QHBoxLayout, QSizePolicy
from PyQt5.QtGui import QFontMetrics
from tool_config_style_binder import ConfigStyleBinder

class LabeledComboBox(QWidget):
    def __init__(self, text: str, items=None, parent=None):
        super().__init__(parent)
        self.nature = "select"
        # self.min_width = 0  # 默认最小宽度
        self.label = QLabel(text)
        self.combo = QComboBox()
        self.setStyleSheet("""
                    QLabel {
                        font-size: 24px;
                        color: rgba(255,255,255,255);
                    }
                    QComboBox {
                        font-size: 24px;
                        padding: 4px 8px;
                        border: 1px solid #aaa;
                        border-radius: 4px;
                        background: rgba(30,30,25,105);
                        color: rgba(240,240,240,255);
                        min-width: 120px;
                    }
                    QComboBox::drop-down {
                        subcontrol-origin: padding;
                        subcontrol-position: top right;
                        width: 20px;
                        border-left: 1px solid #aaa;
                    }
                    QComboBox::down-arrow {
                        image: url(:/icons/arrow-down.png);  /* 可以替换为自定义图标 */
                        width: 10px;
                        height: 10px;
                        
                    }
                    QComboBox QAbstractItemView {
                        border: 1px solid #aaa;
                        background:rgba(20,20,25,205);
                        color: rgba(240,240,240,255);
                        selection-background-color: rgba(30,30,35,105);
                        selection-color: rgba(255,255,255,255);
                    }
                """)
        # 设置大小策略：水平方向可扩展，垂直固定
        self.combo.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        # self.combo.setMinimumWidth(self.min_width)

        # 如果传入初始选项
        if items:
            self.combo.addItems(items)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(40, 0, 0, 0)
        layout.addWidget(self.label)
        layout.addWidget(self.combo)  # 占据剩余空间

        # 自动设置最小宽度
        self.update_min_width()

        # 信号：当选择项变化时，更新宽度
        self.combo.currentIndexChanged.connect(self.update_min_width)
    def set_items(self,items):
        self.combo.addItems(items)
        self.update_min_width()


    def set_dtext(self,dtext):
        self.combo.setCurrentText(dtext)
        self.update_min_width()  # 初始化调整
    def update_min_width(self):
        """根据内容自动调整最小宽度"""
        fm = QFontMetrics(self.combo.font())
        max_width = 0
        for i in range(self.combo.count()):
            text_width = fm.width(self.combo.itemText(i))
            max_width = max(max_width, text_width)

        # 加上内边距和箭头的宽度
        max_width +=fm.height() // 2
        print(max_width)
        self.combo.setMinimumWidth(max_width)

    @property
    def widget(self):
        """返回选择框本体，便于外部操作"""
        return self.combo

    @property
    def min_width(self):
        """返回当前最小宽度"""
        return self.combo.minimumWidth()

    def get_value(self):
        """获取当前选中内容"""
        return self.combo.currentText()
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication, QVBoxLayout, QWidget
    import sys

    app = QApplication(sys.argv)
    win = QWidget()
    layout = QVBoxLayout(win)

    box = LabeledComboBox("选sssss 项：", ["苹果", "香蕉", "橙sss子"])
    # box.set_min_width(150)
    layout.addWidget(box)

    print(box.get_value)  # 获取当前输入内容
    print(box.min_width)  # 获取程序计算出的最小宽度

    win.show()
    sys.exit(app.exec_())

