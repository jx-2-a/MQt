from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QDialog,
    QLabel, QPushButton,QApplication
)
from PyQt5.QtCore import Qt, QPoint, QPropertyAnimation,QRectF
from PyQt5.QtGui import QPainter, QPixmap, QPainterPath, QRegion, QColor
from tool_global_registry import register, registry,remove_register
from json_manager import JsonManager
from tools import Tool
from tool_mask import MaskWidget
from tool_resize_handle import ResizeHandle
config = JsonManager("_internal/jsons/setting.json")
class CustomTitleBar(QWidget):
    def __init__(self, parent=None, title="窗口", icon_path="_internal/use_resource/photo/tubiao.png"):
        super().__init__(parent)
        self.parent = parent
        self.setFixedHeight(64)
        self.setStyleSheet("""
                    background-color: rgba(20, 35, 39, 255);
                """)
        self.setAttribute(Qt.WA_StyledBackground, True)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10,10)
        layout.setSpacing(0)

        if icon_path:
            icon_label = QLabel()
            pix = QPixmap(icon_path)
            icon_label.setPixmap(pix.scaled(44, 44, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            layout.addWidget(icon_label)
        font_h = int(44*0.6)
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
                    font-family: 宋体, sans-serif; /* 字体 */
                    font-size: {font_h}px; 
                    font-weight: bold;
                    color: rgba(255,255,255,255);""")
        layout.addWidget(title_label)
        layout.addStretch()#"(201,79,79,255)"

        self.exite = Tool.add_image_button(layout, icon_path="_internal/use_resource/white_button/close.png",callback=self.on_close)
        self._drag_active = False


    def on_close(self):
        if self.parent:
            self.parent.close()
            remove_register("child_window",self.parent)
            self.parent.parent.mask.close_mask()

    def mousePressEvent(self, event):
        def _in_titlebar(pos):
            return pos.y() <= 64
        if event.button() == Qt.LeftButton and _in_titlebar(event.pos()):
            self._drag_active = True
            self._drag_start_pos = event.globalPos() - self.parent.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if self._drag_active:
            self.parent.move(event.globalPos() - self._drag_start_pos)

    def mouseReleaseEvent(self, event):
        self._drag_active = False
class BaseChildWindow(QDialog):
    """自定义子窗口基类，支持自定义标题栏、拖动、抖动"""
    def __init__(self, parent=None, title="子窗口", icon_path="_internal/use_resource/photo/tubiao.png", width=600, height=400):
        super().__init__(parent)
        # self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMinimumSize(width, height)
        self.border_width = 6  # 边缘宽度，用于检测拖动缩放
        self.radius = 8
        self.setStyleSheet(f"""
                            background-color: rgba(60, 35, 39, 255);
                            border-radius: 0px;
                            """)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # 自定义标题栏
        self.title_bar = CustomTitleBar(self, title=title, icon_path=icon_path)
        self.main_layout.addWidget(self.title_bar)

        # 内容区容器，子类可向 self.content_layout 添加控件
        self.content_layout = QVBoxLayout()
        self.main_layout.addLayout(self.content_layout)
        self.center_on_screen()
        # 创建右下角拖动控件

        self.resize_handle = ResizeHandle(self,name=title, size=10)
        self.mask = MaskWidget(self)

        # -------------------- 添加这一段 --------------------

    def keyPressEvent(self, event):
        # 如果按下回车或回车数字键
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            # 阻止回车触发默认按钮或关闭窗口
            event.ignore()
        else:
            # 其他按键保持默认行为
            super().keyPressEvent(event)
    def center_on_screen(self):
        """窗口居中"""
        screen = QApplication.desktop().screenGeometry()
        size = self.geometry()
        x = (screen.width() - size.width()) // 2
        y = (screen.height() - size.height()) // 2
        self.move(x, y)

    def shake_window(self):
        """窗口左右抖动动画"""
        anim = QPropertyAnimation(self, b"pos", self)
        start_pos = self.pos()
        anim.setDuration(300)
        anim.setKeyValueAt(0, start_pos)
        anim.setKeyValueAt(0.2, start_pos + QPoint(3, 0))
        anim.setKeyValueAt(0.4, start_pos - QPoint(3, 0))
        anim.setKeyValueAt(0.6, start_pos + QPoint(3, 0))
        anim.setKeyValueAt(0.8, start_pos - QPoint(3, 0))
        anim.setKeyValueAt(1, start_pos)
        anim.start(QPropertyAnimation.DeleteWhenStopped)
    def resizeEvent(self, event):
        super().resizeEvent(event)
        # 圆角蒙版
        path = QPainterPath()
        path.addRoundedRect(QRectF(0, 0, self.width(), self.height()), self.radius, self.radius)
        self.setMask(QRegion(path.toFillPolygon().toPolygon()))

        # 保证 handle 永远在右下角，避开圆角裁剪
        self.resize_handle.update_position()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QColor(30, 35, 39, 255))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), self.radius, self.radius)