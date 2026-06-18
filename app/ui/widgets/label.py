from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QPixmap, QBitmap, QPainter
from PyQt5.QtCore import Qt
from .image import _resolve_path
from app.core.style_engine import props_to_qss


class StyledLabel(QLabel):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self._border_radius = 0
        self.setAttribute(Qt.WA_StyledBackground, True)

    def set_text(self, text):
        self.setText(text)

    def set_icon(self, src, width=0, height=0):
        path = _resolve_path(src)
        if path:
            pix = QPixmap(path)
            if width and height:
                pix = pix.scaled(width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.setPixmap(pix)

    def apply_style(self, style_props=None):
        qss = props_to_qss(style_props) if style_props else ""
        self.setStyleSheet(qss)

        radius = 0
        if style_props:
            val = style_props.get("border_radius", "0")
            try:
                radius = int(str(val).replace("px", "").strip())
            except ValueError:
                radius = 0
        self._border_radius = radius
        self._apply_rounded_mask()

    def _apply_rounded_mask(self):
        r = self._border_radius
        if r <= 0 or self.width() <= 0 or self.height() <= 0:
            self.clearMask()
            return
        bitmap = QBitmap(self.size())
        bitmap.fill(Qt.color0)
        p = QPainter(bitmap)
        p.setRenderHint(QPainter.Antialiasing)
        p.setBrush(Qt.color1)
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(self.rect(), r, r)
        p.end()
        self.setMask(bitmap)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._apply_rounded_mask()
