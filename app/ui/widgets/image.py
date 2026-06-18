import os
from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from app.core.style_engine import props_to_qss
from app.assets import resources


def _resolve_path(src):
    if not src:
        return None
    if os.path.isabs(src) and os.path.exists(src):
        return src
    # 先尝试 app/assets/ 下的公开资源
    try:
        p = resources.path(src)
        if os.path.exists(p):
            return p
    except Exception:
        pass
    if os.path.exists(src):
        return os.path.abspath(src)
    return None


class StyledImage(QLabel):
    def __init__(self, src="", scale="contain", width=0, height=0, parent=None):
        super().__init__(parent)
        self._src = src
        self._scale = scale
        self._orig_pixmap = None
        self.setAttribute(Qt.WA_StyledBackground, True)
        if src:
            self.set_src(src)
        if width or height:
            w = width or height
            h = height or width
            self.setFixedSize(w, h)

    def apply_style(self, style_props=None):
        self.setStyleSheet(props_to_qss(style_props) if style_props else "")

    def set_src(self, src):
        self._src = src
        path = _resolve_path(src)
        if path:
            self._orig_pixmap = QPixmap(path)
            self._apply_pixmap()

    def _apply_pixmap(self):
        if self._orig_pixmap is None or self._orig_pixmap.isNull():
            return
        pw, ph = self._orig_pixmap.width(), self._orig_pixmap.height()
        fw = self.width() if self.width() > 0 else pw
        fh = self.height() if self.height() > 0 else ph
        if fw <= 0 or fh <= 0:
            return
        if self._scale == "contain":
            scaled = self._orig_pixmap.scaled(fw, fh, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        elif self._scale == "stretch":
            scaled = self._orig_pixmap.scaled(fw, fh, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        elif self._scale == "crop":
            expanded = self._orig_pixmap.scaled(fw, fh, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            x = (expanded.width() - fw) // 2
            y = (expanded.height() - fh) // 2
            scaled = expanded.copy(x, y, fw, fh)
        else:
            scaled = self._orig_pixmap
        self.setPixmap(scaled)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._apply_pixmap()
