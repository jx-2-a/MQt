from class_child_window import BaseChildWindow
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
)
from PyQt5.QtCore import Qt
from item_down_but import ButtonBar
from tool_global_registry import remove_register
from PyQt5.QtGui import QFont
import re

class ColorSlider(QWidget):
    """单个颜色通道控件（带标签 + 滑块 + 数值显示）"""
    def __init__(self, name, color,dul=127, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        self.setStyleSheet("font-size: 24px; color: rgb(255,255,255,255);")

        self.label = QLabel(name)

        from PyQt5.QtWidgets import QSlider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 255)
        self.slider.setValue(dul)

        self.value_label = QLabel(str(self.slider.value()))
        self.value_label.setAlignment(Qt.AlignCenter)
        # 锁定宽度，宽度按最大值计算
        max_value = 255
        width = self.value_label.fontMetrics().boundingRect(str(max_value)).width() + 10  # +10 给点空隙
        self.value_label.setFixedWidth(width)

        layout.addWidget(self.label)
        layout.addWidget(self.slider, 1)
        layout.addWidget(self.value_label)

        self.slider.valueChanged.connect(self.update_value)

    def update_value(self, v):
        self.value_label.setText(str(v))

    def value(self):
        return self.slider.value()


class ColorPickerWindow(BaseChildWindow):
    """颜色选择窗口，带渐变滑块"""
    def __init__(self, parent=None,callback=None,color=None, width=600, height=400):
        super().__init__(parent, title="选择颜色", width=width, height=height)
        self.parent = parent
        if parent:
            parent.mask.show_mask()
        self.callback = callback
        result = self.parse_rgb(color)

        # ---------- 上方颜色预览 ----------
        preview_shell = QWidget()
        preview_shell_lay = QHBoxLayout(preview_shell)
        preview_shell_lay.setContentsMargins(40, 20, 40, 20)
        preview_shell_lay.setSpacing(0)

        self.color_preview = QFrame()
        self.color_preview.setMinimumHeight(80)
        self.color_preview.setStyleSheet("background: rgb(127,127,127); border-radius: 8px;")
        preview_shell_lay.addWidget(self.color_preview)

        self.content_layout.addWidget(preview_shell)

        # ---------- 中间滑块 ----------
        def add_color_slider(slider_widget):
            shell = QWidget()
            lay = QHBoxLayout(shell)
            lay.setContentsMargins(40, 0, 40, 0)
            lay.setSpacing(0)
            lay.addWidget(slider_widget)
            self.content_layout.addWidget(shell)

        self.r_slider = ColorSlider("R", "red",dul=result[0])
        self.g_slider = ColorSlider("G", "green",dul=result[1])
        self.b_slider = ColorSlider("B", "blue",dul=result[2])
        self.a_slider = ColorSlider("A", "gray", dul=result[3])

        add_color_slider(self.r_slider)
        add_color_slider(self.g_slider)
        add_color_slider(self.b_slider)
        add_color_slider(self.a_slider)

        # ---------- 信号绑定 ----------
        self.r_slider.slider.valueChanged.connect(self.update_color)
        self.g_slider.slider.valueChanged.connect(self.update_color)
        self.b_slider.slider.valueChanged.connect(self.update_color)
        self.a_slider.slider.valueChanged.connect(self.update_color)

        # ---------- 底部确认按钮 ----------
        self.creat_ok_button(self.content_layout)

        # ---------- 初始化显示 ----------
        self.update_color()

        # 置顶拖拽区域
        self.resize_handle.raise_()
        self.show()

    def parse_rgb(self,s: str):
        """解析形如 '(r,g,b)' 的字符串，返回 r,g,b 三个整数（0~255），不合法用127替代"""
        result = []
        # 匹配所有数字
        nums = re.findall(r'\d+', s)
        for i in range(4):
            try:
                val = int(nums[i])
                if 0 <= val <= 255:
                    result.append(val)
                else:
                    result.append(127)
            except IndexError:  # 数字不足
                result.append(127)
        return tuple(result)
    def update_color(self):
        """更新颜色预览 & 滑块渐变"""
        r, g, b, a = self.r_slider.value(), self.g_slider.value(), self.b_slider.value(),self.a_slider.value()
        # 更新颜色预览
        self.color_preview.setStyleSheet(f"""
            background: rgba({r},{g},{b},{a/255});
            border-radius: 8px;
        """)
        # 更新滑块渐变
        self.update_slider_gradient()

    def update_slider_gradient(self):
        """根据当前 RGB 值更新每个滑块的渐变"""
        r, g, b, a = self.r_slider.value(), self.g_slider.value(), self.b_slider.value(),self.a_slider.value()

        # R 滑块渐变
        self.r_slider.slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                height: 8px;
                border-radius: 4px;
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgb(0, {g}, {b}),
                    stop:1 rgb(255, {g}, {b})
                );
            }}
            QSlider::handle:horizontal {{
                background: rgb({255-r},{g},{b});
                border: 0px solid #666;
                width: 14px;
                margin: -4px 0;
                border-radius: 7px;
            }}
        """)

        # G 滑块渐变
        self.g_slider.slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                height: 8px;
                border-radius: 4px;
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgb({r}, 0, {b}),
                    stop:1 rgb({r}, 255, {b})
                );
            }}
            QSlider::handle:horizontal {{
                background: rgb({r},{255-g},{b});
                border: 0px solid #666;
                width: 14px;
                margin: -4px 0;
                border-radius: 7px;
            }}
        """)

        # B 滑块渐变
        self.b_slider.slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                height: 8px;
                border-radius: 4px;
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgb({r}, {g}, 0),
                    stop:1 rgb({r}, {g}, 255)
                );
            }}
            QSlider::handle:horizontal {{
                background: rgb({r},{g},{255-b});
                border: 0px solid #666;
                width: 14px;
                margin: -4px 0;
                border-radius: 7px;
            }}
        """)
        # A 滑块渐变
        self.a_slider.slider.setStyleSheet(f"""
                    QSlider::groove:horizontal {{
                        height: 8px;
                        border-radius: 4px;
                        background: qlineargradient(
                            x1:0, y1:0, x2:1, y2:0,
                            stop:0 rgba({r},{g},{b},0),
                            stop:1 rgba({r},{g},{b},255)
                        );
                    }}
                    QSlider::handle:horizontal {{
                        background: rgba({255-r},{255-g},{255-b},{a/255});
                        border: 0px solid #666;
                        width: 14px;
                        margin: -4px 0;
                        border-radius: 7px;
                    }}
                """)

    def color(self):
        return self.r_slider.value(), self.g_slider.value(), self.b_slider.value(), self.a_slider.value()

    def creat_ok_button(self, layout):
        btn_bar = ButtonBar(["确定"], [self.on_ok], side="right", ratio=0.5, parent=self)
        layout.addWidget(btn_bar)

    def on_ok(self):
        print("选中的颜色：", self.color())
        self.close()
        remove_register("child_window", self)
        if self.parent:
            self.parent.mask.close_mask()
        if self.callback:
            self.callback(str(self.color()))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = ColorPickerWindow()
    sys.exit(app.exec_())
