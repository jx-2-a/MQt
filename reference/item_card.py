from PyQt5.QtWidgets import (QWidget, QLabel, QSpacerItem, QVBoxLayout,
                             QHBoxLayout, QFrame, QSizePolicy, QFrame)
from PyQt5.QtCore import Qt, QTimer, QDateTime
from json_manager import JsonManager
config = JsonManager("_internal/jsons/setting.json")
from tools import Tool
class CardContainer(QWidget):
    def __init__(self, cards=None, spacing=20):
        super().__init__()
        self.setStyleSheet("""
                                    background-color: rgba(0, 0, 0, 0);
                                    border: 0px;
                                    border-radius: 0px;
                                """)
        self.layout = QHBoxLayout()
        self.layout.setSpacing(spacing)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        # 左占位
        self.left_spacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.layout.addItem(self.left_spacer)

        # 卡片
        self.cards = []
        if cards:
            for card in cards:
                self.addCard(card)

        # 右占位
        self.right_spacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.layout.addItem(self.right_spacer)

    def addCard(self, card):
        card.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.layout.insertWidget(self.layout.count()-1, card)
        self.cards.append(card)

    def clearCards(self):
        for card in self.cards:
            self.layout.removeWidget(card)
            card.deleteLater()
        self.cards.clear()
class SummaryCard(QFrame):
    def __init__(self, title="", value="0", min_width=300):
        super().__init__()
        # 卡片样式
        self.setFrameShape(QFrame.StyledPanel)

        # 设置最小宽度
        self.setMinimumWidth(min_width)
        # 主布局
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)

        # 内容行（左对齐）
        self.title_label = QLabel(title)

        self.title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        layout.addWidget(self.title_label)

        # 值行（右对齐）
        self.value_label = QLabel(str(value))
        self.value_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        layout.addWidget(self.value_label)
        self.set_SummaryCard_style()
        self.setLayout(layout)

    def set_SummaryCard_style(self):
        self.setStyleSheet(f"""
                        border-radius: {config.get_set("1_6_1_settings/05")}px;
                        border: 0px;
                        padding: {config.get_set("1_6_1_settings/07")}px {config.get_set("1_6_1_settings/06")}px;
                        background-color: rgba{config.get_set("1_6_1_settings/04")};
                """)
        self.title_label.setStyleSheet(f"""
                        background-color: transparent;
                        border: 0px;
                        
                        font-family: '{config.get_set("1_6_1_settings/09")}', sans-serif;
                        font-size:{config.get_set("1_6_1_settings/10")}px; 
                        font-weight:{Tool.get_font_weight("1_6_1_settings/11")};
                        color: rgba{config.get_set("1_6_1_settings/12")};  
                        border: 0px;
                        """)
        self.value_label.setStyleSheet(f"""
                        background-color: transparent;
                        border: 0px;
                        
                        font-family: '{config.get_set("1_6_1_settings/14")}', sans-serif;
                        font-size:{config.get_set("1_6_1_settings/15")}px; 
                        font-weight:{Tool.get_font_weight("1_6_1_settings/16")};
                        color: rgba{config.get_set("1_6_1_settings/17")};  
                        border: 0px;
                         """)

    def setTitle(self, title):
        self.title_label.setText(title)

    def setValue(self, value):
        self.value_label.setText(str(value))

    def mouseDoubleClickEvent(self, event):
        # 这里写你的逻辑
        super().mouseDoubleClickEvent(event)
# -------------------- 测试 --------------------
if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    card1 = SummaryCard("今日收入次数", 5)
    card2 = SummaryCard("今日收入总额", "1200.50")
    # card3 = SummaryCard("今日成本", "400")
    # card4 = SummaryCard("今日利润", "800.50")

    container = CardContainer([card1, card2])
    container.resize(700, 150)
    container.show()

    sys.exit(app.exec_())
