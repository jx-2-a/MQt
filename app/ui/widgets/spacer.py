from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QSizePolicy
from app.core.style_engine import props_to_qss


class StyledSpacer(QWidget):
    """弹性占位控件 — 撑开同行/同列控件。"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)

    def apply_style(self, style_props=None):
        qss = props_to_qss(style_props) if style_props else ""
        if "background" not in qss and "background-color" not in qss:
            qss = qss + "\nbackground: transparent;" if qss else "background: transparent;"
        self.setStyleSheet(qss)
