"""Icon manager — native icon generation UI (Ctrl+Shift+I)."""
import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton,
    QLineEdit, QSpinBox, QScrollArea, QGridLayout, QGroupBox,
    QMessageBox,
)
from PyQt5.QtGui import QPixmap, QIcon, QColor
from PyQt5.QtCore import Qt

from app.assets.icon_generator import IconGenerator, AVAILABLE_ICONS
from app.controllers.color_picker import ColorPicker


STYLE = """
QWidget {
    background-color: #1e1e1e;
    color: #cccccc;
    font-size: 13px;
}
QGroupBox {
    border: 1px solid #3e3e42;
    border-radius: 6px;
    margin-top: 12px;
    padding-top: 16px;
    font-weight: bold;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    color: #007acc;
}
QComboBox, QSpinBox, QLineEdit {
    background: #2d2d30;
    border: 1px solid #3e3e42;
    border-radius: 4px;
    padding: 4px 8px;
    color: #cccccc;
}
QComboBox::drop-down { border: none; }
QComboBox QAbstractItemView {
    background: #2d2d30;
    selection-background-color: #094771;
}
QPushButton {
    background: #0e639c;
    border: none;
    border-radius: 4px;
    padding: 6px 16px;
    color: white;
    font-weight: bold;
}
QPushButton:hover { background: #1177bb; }
QPushButton#save_btn { background: #2d2d30; border: 1px solid #3e3e42; }
QPushButton#save_btn:hover { background: #3e3e42; }
QLabel#preview_label { border: 1px dashed #3e3e42; border-radius: 4px; }
"""


class IconController(QWidget):
    """Native icon generation tool."""

    def __init__(self, parent=None):
        super().__init__(parent, Qt.Window)
        self.setWindowTitle("icon manager - ctrl+shift+i")
        self.resize(720, 520)
        self.setStyleSheet(STYLE)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)

        # ---- top controls ----
        top = QHBoxLayout()
        top.setSpacing(10)

        top.addWidget(QLabel("icon:"))
        self._icon_combo = QComboBox()
        self._icon_combo.addItems(AVAILABLE_ICONS)
        self._icon_combo.currentTextChanged.connect(self._on_change)
        top.addWidget(self._icon_combo)

        top.addWidget(QLabel("color:"))
        self._color_edit = QLineEdit("#cccccc")
        self._color_edit.setMaximumWidth(80)
        self._color_edit.textChanged.connect(self._on_change)
        top.addWidget(self._color_edit)

        self._pick_btn = QPushButton("...")
        self._pick_btn.setMaximumWidth(36)
        self._pick_btn.clicked.connect(self._pick_color)
        top.addWidget(self._pick_btn)

        top.addWidget(QLabel("size:"))
        self._size_spin = QSpinBox()
        self._size_spin.setRange(12, 256)
        self._size_spin.setValue(32)
        self._size_spin.valueChanged.connect(self._on_change)
        top.addWidget(self._size_spin)

        top.addStretch()

        self._save_btn = QPushButton("save png")
        self._save_btn.setObjectName("save_btn")
        self._save_btn.clicked.connect(self._save)
        top.addWidget(self._save_btn)

        layout.addLayout(top)

        # ---- preview area ----
        group = QGroupBox("preview")
        group_layout = QVBoxLayout(group)

        self._preview = QLabel()
        self._preview.setObjectName("preview_label")
        self._preview.setAlignment(Qt.AlignCenter)
        self._preview.setMinimumHeight(200)
        group_layout.addWidget(self._preview)

        self._info = QLabel()
        self._info.setStyleSheet("color: #888; font-size: 12px;")
        self._info.setAlignment(Qt.AlignCenter)
        group_layout.addWidget(self._info)

        layout.addWidget(group)

        # ---- gallery ----
        gallery_group = QGroupBox("all icons (click to select)")
        gallery_layout = QVBoxLayout(gallery_group)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; }")

        gallery_widget = QWidget()
        self._gallery_grid = QGridLayout(gallery_widget)
        self._gallery_grid.setSpacing(6)

        scroll.setWidget(gallery_widget)
        gallery_layout.addWidget(scroll)
        layout.addWidget(gallery_group)

        self._build_gallery()
        self._on_change()

    # ---- events ----

    def _on_change(self):
        name = self._icon_combo.currentText()
        color = self._color_edit.text().strip() or "#cccccc"
        size = self._size_spin.value()
        try:
            pm = IconGenerator.pixmap(name, color, size)
            self._preview.setPixmap(pm)
            self._preview.setFixedSize(pm.size())
            color_hex = color.lstrip("#")
            self._info.setText(
                f"icons/{name}_{color_hex}.png  ({size}x{size})"
            )
        except Exception as e:
            self._info.setText(f"error: {e}")

    def _pick_color(self):
        cur = self._color_edit.text().strip() or "#cccccc"
        init = QColor(cur)
        dlg = ColorPicker(init, self)
        if dlg.exec_() == ColorPicker.Accepted:
            color = dlg.selected_color()
            self._color_edit.setText(color.name(QColor.HexArgb))

    def _save(self):
        name = self._icon_combo.currentText()
        color = self._color_edit.text().strip() or "#cccccc"
        size = self._size_spin.value()
        try:
            path = IconGenerator.save(name, color, size)
            QMessageBox.information(self, "saved", f"{os.path.basename(path)}\n{path}")
        except Exception as e:
            QMessageBox.warning(self, "error", str(e))

    def _build_gallery(self):
        for i, name in enumerate(AVAILABLE_ICONS):
            btn = QPushButton()
            btn.setIcon(QIcon(IconGenerator.pixmap(name, "#cccccc", 24)))
            btn.setIconSize(btn.iconSize())
            btn.setToolTip(name)
            btn.setFixedSize(40, 40)
            btn.setStyleSheet("QPushButton { background: #2d2d30; border: 1px solid #3e3e42; border-radius: 4px; } QPushButton:hover { background: #3e3e42; border-color: #007acc; }")
            btn.clicked.connect(lambda checked, n=name: self._select_icon(n))
            row, col = divmod(i, 10)
            self._gallery_grid.addWidget(btn, row, col)

    def _select_icon(self, name):
        self._icon_combo.setCurrentText(name)
