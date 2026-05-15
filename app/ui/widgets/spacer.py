from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QSizePolicy


class StyledSpacer(QWidget):
    """弹性占位控件 — 撑开同行/同列控件。"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setStyleSheet("background: transparent;")
