from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSplitter
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPainter, QColor, QPainterPath
from app.core.style_engine import props_to_qss, parse_color

# Box 控件支持的 QSS 属性（背景色和圆角由 paintEvent 直绘处理，支持 rgba 半透明）
_BOX_QSS_KEYS = {"border"}


class StyledBox(QWidget):
    """布局容器 — 通过 QPainter paintEvent 绘制背景（支持 rgba 半透明），
    QSS 仅处理边框和内距。
    """

    def __init__(self, orientation="v", parent=None, spacing=0, margins=(0, 0, 0, 0)):
        super().__init__(parent)
        self._orientation = orientation
        self._bg_color = None       # QColor or None
        self._border_radius = 0     # px
        self.setAttribute(Qt.WA_StyledBackground, False)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAutoFillBackground(False)
        layout = QVBoxLayout() if orientation == "v" else QHBoxLayout()
        layout.setContentsMargins(*margins)
        layout.setSpacing(spacing)
        self.setLayout(layout)
        self._layout = layout

    def add_widget(self, widget, stretch=0):
        self._layout.addWidget(widget, stretch)

    def remove_widget(self, widget):
        self._layout.removeWidget(widget)

    def orientation(self):
        return self._orientation

    def paintEvent(self, event):
        """QPainter 直绘背景，正确合成 rgba 半透明通道。"""
        if not self._bg_color:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        if self._border_radius > 0:
            path = QPainterPath()
            path.addRoundedRect(QRectF(self.rect()), self._border_radius, self._border_radius)
            painter.fillPath(path, self._bg_color)
        else:
            painter.fillRect(self.rect(), self._bg_color)
        painter.end()

    def apply_style(self, style_props=None):
        """分离背景色/圆角给 paintEvent，其余盒模型属性走 QSS。"""
        bg_value = None
        radius = 0
        qss_props = {}

        if style_props:
            for k, v in style_props.items():
                if k == "background_color":
                    bg_value = v
                elif k == "border_radius":
                    try:
                        radius = int(str(v).replace("px", "").strip())
                    except ValueError:
                        radius = 0
                else:
                    qss_props[k] = v

        self._bg_color = parse_color(bg_value) if bg_value else None
        self._border_radius = radius

        qss = props_to_qss(qss_props, _BOX_QSS_KEYS) if qss_props else ""
        self.setStyleSheet(qss)
        self.update()


class StyledSplitter(QSplitter):
    def __init__(self, orientation=Qt.Horizontal, parent=None):
        super().__init__(orientation, parent)

    def add_widget(self, widget):
        self.addWidget(widget)

    def apply_style(self, style_props=None):
        self.setStyleSheet(props_to_qss(style_props) if style_props else "")
