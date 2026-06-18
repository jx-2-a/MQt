"""窗口状态控制器 — 编辑 settings.json 中的窗口属性，实时应用到目标窗口。

通过 BaseWindow 公开 API 操作窗口，不直接操作窗口内部。
"""
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QComboBox, QPushButton, QLabel, QLineEdit, QSpinBox,
    QDoubleSpinBox, QCheckBox, QGroupBox,
    QFileDialog,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

from app.framework.config_manager import load_config, save_config, update_window_config, load_all_layouts, load_layout
from app.core.layout_engine import apply_to_window
from app.core.style_engine import apply_to_widget
from app.windows.base_window import BaseWindow


STYLE = """
QMainWindow {
    background-color: #1e1e1e;
    color: #cccccc;
}
QWidget {
    font-size: 15px;
    color: #cccccc;
    background-color: #1e1e1e;
}
QLabel {
    color: #cccccc;
    font-size: 15px;
    background-color: transparent;
    border: none;
    padding: 0px;
}
QWidget#topbar {
    background-color: #252526;
    border: none;
    border-bottom: 1px solid #3c3c3c;
}
QWidget#topbar QLabel {
    background-color: transparent;
    color: #cccccc;
}
QWidget#statusbar {
    background-color: #007acc;
    border: none;
    border-top: 1px solid #007acc;
}
QLabel#status_lbl {
    color: #ffffff;
    font-size: 13px;
    background-color: transparent;
    border: none;
}
QLabel#section_header {
    color: #8a8a8a;
    font-size: 13px;
    font-weight: bold;
    padding: 5px 10px;
}
QLineEdit, QSpinBox, QDoubleSpinBox {
    background-color: #3c3c3c;
    color: #cccccc;
    border: 1px solid #3c3c3c;
    padding: 5px 10px;
    font-size: 15px;
}
QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {
    border-color: #007acc;
}
QComboBox {
    background-color: #3c3c3c;
    color: #cccccc;
    border: 1px solid #3c3c3c;
    padding: 5px 10px;
    font-size: 15px;
}
QComboBox:hover { border-color: #007acc; }
QComboBox::drop-down { border: none; width: 22px; background-color: transparent; }
QComboBox QAbstractItemView {
    background-color: #252526;
    color: #cccccc;
    selection-background-color: #007acc;
    border: 1px solid #3c3c3c;
    outline: none;
    font-size: 15px;
}
QPushButton {
    background-color: #0e639c;
    color: #ffffff;
    border: 1px solid #0e639c;
    padding: 6px 18px;
    font-size: 15px;
}
QPushButton:hover { background-color: #1177bb; }
QPushButton:pressed { background-color: #094771; }
QPushButton#color_btn {
    min-width: 32px; max-width: 32px; padding: 3px;
    font-size: 16px; background-color: #3c3c3c; border: 1px solid #3c3c3c;
    color: #cccccc;
}
QPushButton#color_btn:hover { background-color: #4a4a4a; border-color: #007acc; }
QCheckBox {
    spacing: 8px;
    color: #cccccc;
    font-size: 15px;
    background-color: transparent;
}
QCheckBox::indicator {
    width: 18px; height: 18px;
    border: 1px solid #555555;
    background-color: #3c3c3c;
}
QCheckBox::indicator:checked {
    background-color: #007acc;
    border-color: #007acc;
}
QGroupBox {
    color: #cccccc;
    border: 1px solid #3c3c3c;
    margin-top: 10px;
    padding-top: 16px;
    font-size: 13px;
    font-weight: bold;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px;
    color: #cccccc;
    background-color: transparent;
}
QSpinBox { min-width: 90px; }
QDoubleSpinBox { min-width: 90px; }
"""


class WindowStateController(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("窗口状态控制器")
        self.setAttribute(Qt.WA_DeleteOnClose, False)
        self.resize(520, 620)

        p = self.palette()
        p.setColor(self.backgroundRole(), QColor("#1e1e1e"))
        self.setPalette(p)

        self._windows = {}
        self._layouts = {}
        self._build_ui()
        self._refresh()
        self.setStyleSheet(STYLE)

    def _scan_windows(self):
        windows = {}
        cfg = load_config()
        for key in cfg:
            if key == "widget_controller":
                continue
            windows[key] = cfg[key]
        return windows

    def _get_target_window(self):
        key = self._window_combo.currentData()
        if not key:
            return None
        from PyQt5.QtWidgets import QApplication
        for w in QApplication.topLevelWidgets():
            if isinstance(w, BaseWindow) and w.config_key == key:
                return w
        return None

    # ── UI ─────────────────────────────────────────────────────────

    def _build_ui(self):
        central = QWidget()
        central.setAttribute(Qt.WA_StyledBackground, True)
        central.setAutoFillBackground(False)
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        topbar = QWidget()
        topbar.setAttribute(Qt.WA_StyledBackground, True)
        topbar.setAutoFillBackground(False)
        topbar.setObjectName("topbar")
        top = QHBoxLayout(topbar)
        top.setContentsMargins(10, 6, 10, 6)
        top.setSpacing(10)
        top.addWidget(QLabel("目标窗口:"))
        self._window_combo = QComboBox()
        self._window_combo.setMinimumWidth(220)
        self._window_combo.currentIndexChanged.connect(self._on_window_selected)
        top.addWidget(self._window_combo)
        top.addStretch()
        refresh_btn = QPushButton("刷新")
        refresh_btn.clicked.connect(self._refresh)
        top.addWidget(refresh_btn)
        root.addWidget(topbar)

        section = QLabel("窗口属性")
        section.setObjectName("section_header")
        root.addWidget(section)

        form_widget = QWidget()
        form_widget.setAttribute(Qt.WA_StyledBackground, True)
        form_widget.setAutoFillBackground(False)
        self._form = QFormLayout(form_widget)
        self._form.setContentsMargins(14, 10, 14, 10)
        self._form.setSpacing(8)

        self._title_edit = QLineEdit()
        self._form.addRow("标题:", self._title_edit)

        geo_group = QGroupBox("窗口位置与大小")
        geo_layout = QFormLayout(geo_group)
        geo_layout.setSpacing(6)

        geo_row = QHBoxLayout()
        geo_row.setSpacing(6)
        self._x_spin = QSpinBox()
        self._x_spin.setRange(-9999, 9999)
        self._y_spin = QSpinBox()
        self._y_spin.setRange(-9999, 9999)
        geo_row.addWidget(QLabel("X:"))
        geo_row.addWidget(self._x_spin)
        geo_row.addWidget(QLabel("Y:"))
        geo_row.addWidget(self._y_spin)
        geo_layout.addRow("位置:", geo_row)

        size_row = QHBoxLayout()
        size_row.setSpacing(6)
        self._w_spin = QSpinBox()
        self._w_spin.setRange(100, 9999)
        self._h_spin = QSpinBox()
        self._h_spin.setRange(100, 9999)
        size_row.addWidget(QLabel("宽:"))
        size_row.addWidget(self._w_spin)
        size_row.addWidget(QLabel("高:"))
        size_row.addWidget(self._h_spin)
        geo_layout.addRow("大小:", size_row)
        self._form.addRow(geo_group)

        appear_group = QGroupBox("外观")
        appear_layout = QFormLayout(appear_group)
        appear_layout.setSpacing(6)

        opacity_row = QHBoxLayout()
        opacity_row.setSpacing(6)
        self._opacity_spin = QDoubleSpinBox()
        self._opacity_spin.setRange(0.1, 1.0)
        self._opacity_spin.setSingleStep(0.05)
        self._opacity_spin.setValue(1.0)
        opacity_row.addWidget(self._opacity_spin)
        appear_layout.addRow("透明度:", opacity_row)

        self._frameless_chk = QCheckBox("无边框模式")
        appear_layout.addRow("", self._frameless_chk)

        self._border_radius_spin = QSpinBox()
        self._border_radius_spin.setRange(0, 100)
        self._border_radius_spin.setSuffix(" px")
        self._border_radius_spin.setSpecialValueText("无圆角")
        appear_layout.addRow("窗口圆角:", self._border_radius_spin)

        self._bg_image_edit = QLineEdit()
        self._bg_image_edit.setPlaceholderText("背景图片路径（可选）")
        img_row = QHBoxLayout()
        img_row.setSpacing(6)
        img_row.addWidget(self._bg_image_edit)
        img_btn = QPushButton("…")
        img_btn.setObjectName("color_btn")
        img_btn.clicked.connect(self._pick_bg_image)
        img_row.addWidget(img_btn)
        appear_layout.addRow("背景图片:", img_row)

        scale_row = QHBoxLayout()
        scale_row.setSpacing(6)
        self._bg_scale_combo = QComboBox()
        self._bg_scale_combo.addItems(["crop（铺满裁剪）", "contain（完整显示）", "stretch（拉伸填充）"])
        scale_row.addWidget(self._bg_scale_combo)
        appear_layout.addRow("图片缩放:", scale_row)

        self._form.addRow(appear_group)

        layout_group = QGroupBox("关联布局")
        layout_lo = QFormLayout(layout_group)
        layout_lo.setSpacing(6)
        self._layout_combo = QComboBox()
        self._layout_combo.setMinimumWidth(220)
        layout_lo.addRow("布局:", self._layout_combo)
        self._form.addRow(layout_group)

        root.addWidget(form_widget)
        root.addStretch()

        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(14, 8, 14, 8)
        btn_row.addStretch()
        apply_btn = QPushButton("应用到窗口")
        apply_btn.clicked.connect(self._apply)
        btn_row.addWidget(apply_btn)
        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self._save)
        btn_row.addWidget(save_btn)
        root.addLayout(btn_row)

        statusbar = QWidget()
        statusbar.setAttribute(Qt.WA_StyledBackground, True)
        statusbar.setAutoFillBackground(False)
        statusbar.setObjectName("statusbar")
        statusbar.setFixedHeight(28)
        sb_layout = QHBoxLayout(statusbar)
        sb_layout.setContentsMargins(10, 0, 10, 0)
        self._status = QLabel("就绪")
        self._status.setObjectName("status_lbl")
        sb_layout.addWidget(self._status)
        root.addWidget(statusbar)

    # ── 数据 ────────────────────────────────────────────────────────

    def _refresh(self):
        self._windows = self._scan_windows()
        self._layouts = load_all_layouts()

        current = self._window_combo.currentData()
        self._window_combo.blockSignals(True)
        self._window_combo.clear()
        for key, cfg in self._windows.items():
            title = cfg.get("title", key)
            self._window_combo.addItem(f"{title}  [{key}]", key)
        if current and current in self._windows:
            idx = self._window_combo.findData(current)
            self._window_combo.setCurrentIndex(max(idx, 0))
        elif self._window_combo.count() > 0:
            self._window_combo.setCurrentIndex(0)
        self._window_combo.blockSignals(False)

        self._layout_combo.blockSignals(True)
        self._layout_combo.clear()
        self._layout_combo.addItem("（不改变）", "")
        for lname in sorted(self._layouts.keys()):
            self._layout_combo.addItem(lname, lname)
        self._layout_combo.blockSignals(False)

        if self._window_combo.count() > 0:
            self._on_window_selected(0)

    def _on_window_selected(self, _index):
        key = self._window_combo.currentData()
        if not key:
            return
        cfg = self._windows.get(key, {})
        self._title_edit.setText(cfg.get("title", ""))

        geo = cfg.get("geometry", {})
        self._x_spin.setValue(geo.get("x", 0))
        self._y_spin.setValue(geo.get("y", 0))
        self._w_spin.setValue(geo.get("width", 800))
        self._h_spin.setValue(geo.get("height", 600))

        self._opacity_spin.setValue(cfg.get("opacity", 1.0))
        self._frameless_chk.setChecked(cfg.get("frameless", False))

        self._border_radius_spin.setValue(cfg.get("border_radius", 0))

        bg_image = cfg.get("background_image", "")
        self._bg_image_edit.setText(bg_image or "")

        scale = cfg.get("background_image_scale", "crop")
        scale_map = {"crop": 0, "contain": 1, "stretch": 2}
        self._bg_scale_combo.setCurrentIndex(scale_map.get(scale, 0))

        layout_name = cfg.get("layout", "")
        idx = self._layout_combo.findData(layout_name)
        self._layout_combo.setCurrentIndex(idx if idx >= 0 else 0)

    def _pick_bg_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择背景图片", "",
            "图片文件 (*.png *.jpg *.jpeg *.bmp *.gif *.svg);;所有文件 (*)")
        if path:
            self._bg_image_edit.setText(path)

    # ── 操作 ────────────────────────────────────────────────────────

    def _save(self):
        key = self._window_combo.currentData()
        if not key:
            self._status.setText("未选择窗口")
            return

        bg_image = self._bg_image_edit.text().strip()
        scale_map = {0: "crop", 1: "contain", 2: "stretch"}
        bg_scale = scale_map.get(self._bg_scale_combo.currentIndex(), "crop")
        layout = self._layout_combo.currentData()

        update_window_config(
            key,
            title=self._title_edit.text().strip(),
            geometry={
                "x": self._x_spin.value(),
                "y": self._y_spin.value(),
                "width": self._w_spin.value(),
                "height": self._h_spin.value(),
            },
            opacity=self._opacity_spin.value(),
            frameless=self._frameless_chk.isChecked(),
            background_image=bg_image,
            background_image_scale=bg_scale,
            border_radius=self._border_radius_spin.value(),
            layout=layout,
        )
        self._windows = self._scan_windows()
        self._status.setText(f"已保存 [{key}]")

    def _apply(self):
        self._save()
        key = self._window_combo.currentData()
        win = self._get_target_window()
        if win is None:
            self._status.setText(f"未找到实时窗口 [{key}]，配置已保存")
            return

        cfg = self._windows.get(key, {})

        win.update_config(
            title=cfg.get("title", win.windowTitle()),
            opacity=cfg.get("opacity", 1.0),
            frameless=cfg.get("frameless", False),
            background_image=cfg.get("background_image"),
            background_image_scale=cfg.get("background_image_scale", "crop"),
            border_radius=cfg.get("border_radius", 0),
        )

        layout_name = cfg.get("layout")
        if layout_name:
            node = load_layout(layout_name)
            if node:
                apply_to_window(win, node)

        if not layout_name:
            win.apply_styles()

        win.show()
        self._status.setText(f"已应用 → [{key}]")

    @staticmethod
    def open_window(parent=None):
        from PyQt5.QtWidgets import QApplication
        for w in QApplication.topLevelWidgets():
            if isinstance(w, WindowStateController):
                w.show()
                w.raise_()
                w.activateWindow()
                w._refresh()
                return w
        ctrl = WindowStateController(parent)
        ctrl.show()
        return ctrl
