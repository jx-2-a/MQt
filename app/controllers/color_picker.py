"""独立颜色选择器 — 暗色系，自包含样式，带 HSV 取色区和屏幕取色器。"""
from PyQt5.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QLineEdit, QSpinBox, QApplication,
)
from PyQt5.QtCore import Qt, QPoint, QTimer
from PyQt5.QtGui import (
    QColor, QPainter, QMouseEvent, QImage, QPixmap, QCursor,
    QPainterPath,
)

_SWATCH_SIZE = 20
_GAP = 3
_COLS = 18

# 紧凑模式
_C_SWATCH = 12
_C_GAP = 1

# 历史颜色（跨对话框共享）
_HISTORY = []
_MAX_HISTORY = 18

_PRESETS = [
    "#ff0000", "#ff4500", "#ff8c00", "#ffd700", "#ffff00", "#adff2f",
    "#00ff00", "#00ced1", "#00bfff", "#1e90ff", "#0000ff", "#8a2be2",
    "#9932cc", "#ff00ff", "#ff1493", "#dc143c", "#800080", "#c71585",
    "#ffffff", "#cccccc", "#999999", "#666666", "#333333", "#000000",
    "#f5f5dc", "#ffe4c4", "#ffebcd", "#fffacd", "#e6e6fa", "#d8bfd8",
    "#f0fff0", "#e0ffff", "#f0f8ff", "#fff0f5", "#fdf5e6", "#faebd7",
    "#faf0e6", "#fff5ee", "#f5fffa", "#ffefd5", "#ffdab9", "#ffdead",
    "#2f4f4f", "#556b2f", "#8b4513", "#a0522d", "#b8860b", "#bdb76b",
    "#6b8e23", "#4682b4", "#483d8b", "#4b0082", "#708090", "#778899",
]

COLOR_STYLE = """
QDialog {
    background-color: #1e1e1e;
    color: #cccccc;
}
QLabel {
    background-color: transparent;
    color: #aaaaaa;
    font-size: 14px;
    border: none;
}
QLabel#section_lbl {
    color: #8a8a8a;
    font-size: 12px;
    font-weight: bold;
}
QLineEdit {
    background-color: #3c3c3c;
    color: #cccccc;
    border: 1px solid #3c3c3c;
    padding: 5px 10px;
    font-size: 15px;
}
QLineEdit:focus {
    border-color: #007acc;
}
QSpinBox {
    background-color: #3c3c3c;
    color: #cccccc;
    border: 1px solid #3c3c3c;
    padding: 4px 8px;
    font-size: 14px;
    min-width: 72px;
}
QSpinBox:focus {
    border-color: #007acc;
}
QPushButton {
    background-color: #3c3c3c;
    color: #cccccc;
    border: 1px solid #3c3c3c;
    padding: 6px 20px;
    font-size: 15px;
}
QPushButton:hover {
    background-color: #4a4a4a;
    border-color: #555555;
}
QPushButton#ok_btn {
    background-color: #0e639c;
    color: #ffffff;
    border: 1px solid #0e639c;
}
QPushButton#ok_btn:hover {
    background-color: #1177bb;
}
QPushButton#dropper_btn {
    padding: 4px 12px;
    font-size: 16px;
}
"""


class _ColorArea(QWidget):
    """SV 取色区 — 固定色相下的 Saturation × Value 平面，可点击/拖拽选色。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._hue = 0.0
        self._sat = 0.0
        self._val = 1.0
        self._sv_cache = None
        self._cache_hue = -1.0
        self.setFixedHeight(180)
        self.setMinimumWidth(120)
        self.setCursor(Qt.CrossCursor)
        self.setMouseTracking(True)

    def set_hsv(self, hue, sat, val):
        self._hue = hue
        self._sat = sat
        self._val = val
        self.update()

    def set_hue(self, hue):
        self._hue = hue
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        w, h = self.width(), self.height()

        if self._cache_hue != self._hue or self._sv_cache is None:
            self._sv_cache = self._make_sv_image(w, h)
            self._cache_hue = self._hue
        painter.drawImage(0, 0, self._sv_cache)

        cx = int(self._sat * (w - 1))
        cy = int((1.0 - self._val) * (h - 1))
        painter.setPen(QColor("#ffffff"))
        painter.drawEllipse(QPoint(cx, cy), 4, 4)
        painter.setPen(QColor("#000000"))
        painter.drawEllipse(QPoint(cx, cy), 5, 5)
        painter.end()

    def _make_sv_image(self, w, h):
        img = QImage(w, h, QImage.Format_ARGB32)
        for y in range(h):
            v = 1.0 - y / h
            for x in range(w):
                s = x / w
                img.setPixelColor(x, y, QColor.fromHsvF(self._hue, s, v))
        return img

    def _pos_to_sv(self, pos):
        s = max(0.0, min(1.0, pos.x() / max(self.width() - 1, 1)))
        v = 1.0 - max(0.0, min(1.0, pos.y() / max(self.height() - 1, 1)))
        return s, v

    def mousePressEvent(self, event: QMouseEvent):
        self._sat, self._val = self._pos_to_sv(event.pos())
        self.update()
        if self._on_change:
            self._on_change()

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() & Qt.LeftButton:
            self._sat, self._val = self._pos_to_sv(event.pos())
            self.update()
            if self._on_change:
                self._on_change()


class _HueBar(QWidget):
    """色相滑块 — 彩虹渐变条，可拖拽。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._hue = 0.0
        self._hue_cache = None
        self.setFixedHeight(18)
        self.setCursor(Qt.PointingHandCursor)

    def set_hue(self, h):
        self._hue = max(0.0, min(1.0, h))
        self.update()

    def hue(self):
        return self._hue

    def paintEvent(self, event):
        painter = QPainter(self)
        w, h = self.width(), self.height()
        if self._hue_cache is None or self._hue_cache.width() != w:
            self._hue_cache = self._make_hue_image(w)
        painter.drawImage(0, 1, self._hue_cache, 0, 0, w, h - 2)
        painter.setPen(QColor("#555555"))
        painter.drawRect(0, 0, w - 1, h - 1)
        hx = int(self._hue * (w - 1))
        painter.setPen(QColor("#cccccc"))
        painter.drawLine(hx, 0, hx, h - 1)
        painter.end()

    def _make_hue_image(self, w):
        img = QImage(w, 1, QImage.Format_ARGB32)
        for x in range(w):
            img.setPixelColor(x, 0, QColor.fromHsvF(x / w, 1.0, 1.0))
        return img

    def mousePressEvent(self, event: QMouseEvent):
        self._update_from_pos(event.pos())

    def mouseMoveEvent(self, event: QMouseEvent):
        self._update_from_pos(event.pos())

    def _update_from_pos(self, pos):
        self._hue = max(0.0, min(1.0, pos.x() / max(self.width() - 1, 1)))
        self.update()
        if self._on_change:
            self._on_change()


class _AlphaBar(QWidget):
    """Alpha 滑块 — 棋盘格底色 + alpha 渐变条。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._color = QColor("#ffffff")
        self._alpha = 1.0
        self.setFixedHeight(18)
        self.setCursor(Qt.PointingHandCursor)

    def set_color_and_alpha(self, color, alpha):
        self._color = QColor(color)
        self._alpha = max(0.0, min(1.0, alpha))
        self.update()

    def set_alpha(self, a):
        self._alpha = max(0.0, min(1.0, a))
        self.update()

    def alpha(self):
        return self._alpha

    def paintEvent(self, event):
        painter = QPainter(self)
        w, h = self.width(), self.height()
        cell = 5
        for row in range(0, h, cell):
            for col in range(0, w, cell):
                c = QColor("#ffffff") if ((row // cell) + (col // cell)) % 2 == 0 else QColor("#cccccc")
                painter.fillRect(col, row, min(cell, w - col), min(cell, h - row), c)
        r, g, b = self._color.red(), self._color.green(), self._color.blue()
        for x in range(w):
            t = x / max(w - 1, 1)
            painter.fillRect(x, 1, 1, h - 2, QColor(r, g, b, int(t * 255)))
        painter.setPen(QColor("#555555"))
        painter.drawRect(0, 0, w - 1, h - 1)
        hx = int(self._alpha * (w - 1))
        painter.setPen(QColor("#cccccc"))
        painter.drawLine(hx, 0, hx, h - 1)
        painter.end()

    def mousePressEvent(self, event: QMouseEvent):
        self._update_from_pos(event.pos())

    def mouseMoveEvent(self, event: QMouseEvent):
        self._update_from_pos(event.pos())

    def _update_from_pos(self, pos):
        self._alpha = max(0.0, min(1.0, pos.x() / max(self.width() - 1, 1)))
        self.update()
        if self._on_change:
            self._on_change()


class _SwatchGrid(QWidget):
    """预设色块网格 — paintEvent 直绘。

    compact=True 使用 12×12 色块 + 1px 间距。
    """

    def __init__(self, colors, parent=None, compact=False):
        super().__init__(parent)
        self._colors = colors
        self._hovered = -1
        self._compact = compact
        size = _C_SWATCH if compact else _SWATCH_SIZE
        gap = _C_GAP if compact else _GAP
        rows = (len(colors) + _COLS - 1) // _COLS
        self.setFixedSize(_COLS * (size + gap) + gap,
                          rows * (size + gap) + gap)
        self.setMouseTracking(True)
        self.setCursor(Qt.PointingHandCursor)

    def paintEvent(self, event):
        painter = QPainter(self)
        size = _C_SWATCH if self._compact else _SWATCH_SIZE
        gap = _C_GAP if self._compact else _GAP
        for i, hex_color in enumerate(self._colors):
            row, col = divmod(i, _COLS)
            x = gap + col * (size + gap)
            y = gap + row * (size + gap)
            painter.fillRect(x, y, size, size, QColor(hex_color))
            if i == self._hovered:
                painter.setPen(QColor("#007acc"))
                painter.drawRect(x - 1, y - 1, size + 1, size + 1)
        painter.end()

    def mouseMoveEvent(self, event):
        size = _C_SWATCH if self._compact else _SWATCH_SIZE
        gap = _C_GAP if self._compact else _GAP
        col = event.pos().x() // (size + gap)
        row = event.pos().y() // (size + gap)
        idx = row * _COLS + col
        self._hovered = idx if 0 <= idx < len(self._colors) else -1
        self.update()

    def leaveEvent(self, event):
        self._hovered = -1
        self.update()

    def mousePressEvent(self, event):
        size = _C_SWATCH if self._compact else _SWATCH_SIZE
        gap = _C_GAP if self._compact else _GAP
        col = event.pos().x() // (size + gap)
        row = event.pos().y() // (size + gap)
        idx = row * _COLS + col
        if 0 <= idx < len(self._colors) and self._on_select:
            self._on_select(self._colors[idx])


class _ScreenPicker(QWidget):
    """屏幕取色器 — 全屏遮罩，点击提取屏幕像素颜色。"""

    def __init__(self):
        super().__init__(None)
        self._color = None
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        self.setCursor(Qt.CrossCursor)
        self.setMouseTracking(True)

    def pick(self):
        """进入取色模式，返回 QColor 或 None。"""
        self._color = None
        for screen in QApplication.screens():
            geo = screen.geometry()
            if geo.contains(QCursor.pos()):
                self._screenshot = screen.grabWindow(0)
                break
        else:
            screen = QApplication.primaryScreen()
            self._screenshot = screen.grabWindow(0)
        self.setGeometry(QApplication.primaryScreen().geometry())
        self.show()
        self.grabMouse()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self._screenshot)
        c = QColor(0, 0, 0, 80)
        painter.fillRect(self.rect(), c)

        pos = self.mapFromGlobal(QCursor.pos())
        r = 40
        src_x = int(pos.x() * self._screenshot.width() / self.width())
        src_y = int(pos.y() * self._screenshot.height() / self.height())
        zoom = self._screenshot.copy(
            max(0, src_x - 11), max(0, src_y - 11), 22, 22).scaled(
            r * 2, r * 2, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        painter.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        path.addEllipse(QPoint(pos.x(), pos.y() - int(r * 1.2)), r, r)
        painter.setClipPath(path)
        painter.drawPixmap(pos.x() - r, pos.y() - int(r * 1.2) - r, zoom)
        painter.setClipping(False)

        painter.setPen(QColor("#ffffff"))
        painter.drawEllipse(QPoint(pos.x(), pos.y() - int(r * 1.2)), r, r)
        painter.drawEllipse(QPoint(pos.x(), pos.y() - int(r * 1.2)), r + 1, r + 1)

        cross = 6
        cx, cy = pos.x(), pos.y() - int(r * 1.2)
        painter.drawLine(cx - cross, cy, cx + cross, cy)
        painter.drawLine(cx, cy - cross, cx, cy + cross)
        painter.end()

    def mouseMoveEvent(self, event):
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            pos = self.mapFromGlobal(QCursor.pos())
            px = int(pos.x() * self._screenshot.width() / self.width())
            py = int(pos.y() * self._screenshot.height() / self.height())
            self._color = QColor(self._screenshot.toImage().pixel(px, py))
            self.releaseMouse()
            self.hide()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.releaseMouse()
            self.hide()


class _ColorPreview(QWidget):
    """颜色预览块 — 棋盘格背景 + 颜色叠加。"""

    def __init__(self, color, parent=None):
        super().__init__(parent)
        self._color = color
        self.setFixedHeight(80)
        self.setMinimumWidth(48)

    def set_color(self, color):
        self._color = color
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        w, h = self.width(), self.height()
        cell = 8
        for row in range(0, h, cell):
            for col in range(0, w, cell):
                c = QColor("#ffffff") if ((row // cell) + (col // cell)) % 2 == 0 else QColor("#cccccc")
                painter.fillRect(col, row, min(cell, w - col), min(cell, h - row), c)
        if self._color:
            painter.fillRect(0, 0, w, h, self._color)
        painter.setPen(QColor("#555555"))
        painter.drawRect(0, 0, w - 1, h - 1)
        painter.end()


class ColorPickerWidget(QWidget):
    """可嵌入的颜色选择控件 — SV 取色区 + 色相/Alpha 条 + Hex + 预览 + 预设色块。

    用法:
        w = ColorPickerWidget(parent)
        w.on_change = lambda c: print(c.name())
        w.set_color(some_qcolor)
    """

    _busy = False

    def __init__(self, parent=None, compact_presets=True):
        super().__init__(parent)
        self._color = QColor("#ffffffff")
        self._compact_presets = compact_presets
        self.on_change = None
        self._build_ui()
        self._sync_all_from_color()

    def set_color(self, color):
        if isinstance(color, str):
            from app.core.style_engine import parse_color
            color = parse_color(color) or QColor("#ffffffff")
        self._color = QColor(color)
        self._sync_all_from_color()

    def color(self):
        return QColor(self._color)

    # ── UI ────────────────────────────────────────────────────

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(6)

        # 预览(1) + SV取色区(3)，同高
        top_row = QHBoxLayout()
        top_row.setSpacing(8)

        self._preview = _ColorPreview(self._color, self)
        self._preview.setFixedHeight(130)
        top_row.addWidget(self._preview, 1)

        self._sv_area = _ColorArea(self)
        self._sv_area._on_change = self._on_sv_changed
        self._sv_area.setFixedHeight(130)
        top_row.addWidget(self._sv_area, 3)
        root.addLayout(top_row)

        # 色相条
        hue_row = QHBoxLayout()
        hue_row.setSpacing(8)
        hue_label = QLabel("色相")
        hue_label.setFixedWidth(28)
        hue_row.addWidget(hue_label)
        self._hue_bar = _HueBar(self)
        self._hue_bar._on_change = self._on_hue_changed
        hue_row.addWidget(self._hue_bar, 1)
        root.addLayout(hue_row)

        # Alpha 条
        alpha_row = QHBoxLayout()
        alpha_row.setSpacing(8)
        alpha_label = QLabel("透明")
        alpha_label.setFixedWidth(28)
        alpha_row.addWidget(alpha_label)
        self._alpha_bar = _AlphaBar(self)
        self._alpha_bar._on_change = self._on_alpha_bar_changed
        alpha_row.addWidget(self._alpha_bar, 1)
        root.addLayout(alpha_row)

        # Hex + dropper
        hex_row = QHBoxLayout()
        hex_row.setSpacing(6)
        hex_label = QLabel("Hex")
        hex_label.setFixedWidth(28)
        hex_row.addWidget(hex_label)
        self._hex_edit = QLineEdit()
        self._hex_edit.setPlaceholderText("#AARRGGBB")
        self._hex_edit.editingFinished.connect(self._on_hex_changed)
        hex_row.addWidget(self._hex_edit, 1)
        dropper_btn = QPushButton("\U0001F4A7")
        dropper_btn.setObjectName("dropper_btn")
        dropper_btn.setToolTip("从屏幕取色")
        dropper_btn.clicked.connect(self._on_pick_screen)
        hex_row.addWidget(dropper_btn)
        root.addLayout(hex_row)

        # 预设
        preset_label = QLabel("预设")
        preset_label.setFixedWidth(28)
        root.addWidget(preset_label)

        self._swatch_grid = _SwatchGrid(_PRESETS, self, compact=self._compact_presets)
        self._swatch_grid._on_select = self._on_swatch_selected
        root.addWidget(self._swatch_grid, alignment=Qt.AlignCenter)

        # 历史（始终显示，为空时占位）
        hist_label = QLabel("历史")
        hist_label.setFixedWidth(28)
        root.addWidget(hist_label)

        hist_colors = [c.name(QColor.HexArgb) for c in _HISTORY] if _HISTORY else []
        self._hist_grid = _SwatchGrid(hist_colors, self, compact=self._compact_presets)
        self._hist_grid._on_select = self._on_history_selected
        root.addWidget(self._hist_grid, alignment=Qt.AlignCenter)

    # ── 信号处理 ──────────────────────────────────────────────

    def _emit(self):
        self._add_history(self._color)
        if self.on_change:
            self.on_change(self._color)

    def _add_history(self, color):
        hex_str = color.name(QColor.HexArgb)
        for i, c in enumerate(_HISTORY):
            if c.name(QColor.HexArgb) == hex_str:
                _HISTORY.pop(i)
                break
        _HISTORY.insert(0, QColor(color))
        if len(_HISTORY) > _MAX_HISTORY:
            _HISTORY[:] = _HISTORY[:_MAX_HISTORY]

    def _on_sv_changed(self):
        self._color = QColor.fromHsvF(
            self._hue_bar.hue(), self._sv_area._sat, self._sv_area._val,
            self._alpha_bar.alpha())
        self._sync_except_sv_hue()
        self._emit()

    def _on_hue_changed(self):
        self._sv_area.set_hue(self._hue_bar.hue())
        self._color = QColor.fromHsvF(
            self._hue_bar.hue(), self._sv_area._sat, self._sv_area._val,
            self._alpha_bar.alpha())
        self._sync_except_sv_hue()
        self._emit()

    def _on_alpha_bar_changed(self):
        self._color.setAlpha(int(self._alpha_bar.alpha() * 255))
        self._sync_except_sv_hue()
        self._emit()

    def _on_hex_changed(self):
        from app.core.style_engine import parse_color
        c = parse_color(self._hex_edit.text().strip())
        if c:
            self._color = c
            self._sync_all_from_color()
            self._emit()

    def _on_swatch_selected(self, hex_color):
        from app.core.style_engine import parse_color
        c = parse_color(hex_color)
        if c:
            self._color = c
            self._sync_all_from_color()
            self._emit()

    def _on_history_selected(self, hex_color):
        self._on_swatch_selected(hex_color)

    def _on_pick_screen(self):
        w = self.window()
        if w:
            w.hide()
        QTimer.singleShot(200, self._do_pick)

    def _do_pick(self):
        picker = _ScreenPicker()
        picker.pick()
        while picker.isVisible():
            QApplication.processEvents()
        if picker._color and picker._color.isValid():
            self._color = picker._color
            self._sync_all_from_color()
            self._emit()
        picker.deleteLater()
        w = self.window()
        if w:
            w.show()

    # ── 同步 ──────────────────────────────────────────────────

    def _sync_all_from_color(self):
        self._busy = True
        c = self._color
        self._preview.set_color(c)
        self._hex_edit.setText(c.name(QColor.HexArgb))
        h = c.hueF() if c.hue() >= 0 else 0.0
        self._hue_bar.set_hue(h)
        self._sv_area.set_hsv(h, c.saturationF(), c.valueF())
        self._alpha_bar.set_color_and_alpha(c, c.alphaF())
        self._busy = False

    def _sync_except_sv_hue(self):
        self._busy = True
        c = self._color
        self._preview.set_color(c)
        self._hex_edit.setText(c.name(QColor.HexArgb))
        self._alpha_bar.set_color_and_alpha(c, c.alphaF())
        self._busy = False


class ColorPicker(QDialog):
    """独立颜色选择对话框 — 暗色系，包装 ColorPickerWidget + OK/Cancel。

    用法:
        dlg = ColorPicker(initial_color, parent)
        if dlg.exec_() == QDialog.Accepted:
            color = dlg.selected_color()  # QColor
    """

    def __init__(self, initial_color=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("颜色选择器")
        self.setFixedSize(470, 530)
        self.setStyleSheet(COLOR_STYLE)

        self._result = None

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(8)

        self._picker = ColorPickerWidget(self, compact_presets=False)
        self._picker._sv_area.setFixedHeight(200)
        self._picker._preview.setFixedHeight(200)
        root.addWidget(self._picker)

        # OK/Cancel
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        btn_row.addStretch()
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)
        ok_btn = QPushButton("确定")
        ok_btn.setObjectName("ok_btn")
        ok_btn.clicked.connect(self._on_ok)
        btn_row.addWidget(ok_btn)
        root.addLayout(btn_row)

        if initial_color is None:
            initial_color = QColor("#ffffffff")
        if isinstance(initial_color, str):
            from app.core.style_engine import parse_color
            initial_color = parse_color(initial_color) or QColor("#ffffffff")
        self._picker.set_color(initial_color)
        self._picker._add_history(QColor(initial_color))

    def selected_color(self):
        return QColor(self._result) if self._result else self._picker.color()

    def _on_ok(self):
        self._result = self._picker.color()
        self.accept()
