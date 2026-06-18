"""
图标生成器 — QPainter 矢量绘制，输出透明 PNG 或 QPixmap。

用法:
  from app.assets.icon_generator import IconGenerator

  # 生成单个图标 pixmap
  pix = IconGenerator.pixmap("close", color="#cccccc", size=24)

  # 保存到文件
  path = IconGenerator.save("minimize", color="#ffffff")
  # → app/assets/images/icons/minimize_ffffff.png

  # 批量生成一套
  IconGenerator.generate_set(colors=["#cccccc", "#ffffff"], size=20)

支持的图标:
  minimize    — 水平线
  maximize    — 空心方框
  restore     — 重叠双框
  close       — ✕ 交叉线
  menu        — 三条横线
  arrow_left  — 左箭头
  arrow_right — 右箭头
  arrow_up    — 上箭头
  arrow_down  — 下箭头
  plus        — + 加号
  minus       — - 减号
  check       — ✓ 对勾
  search      — 放大镜
  settings    — 齿轮
  refresh     — 循环箭头
"""

import os
from PyQt5.QtGui import QPixmap, QPainter, QColor, QPen
from PyQt5.QtCore import Qt, QPointF, QRectF
from .resource_manager import resources


_ICONS_DIR = os.path.join(os.path.dirname(__file__), "images", "icons")


def _icon_dir():
    os.makedirs(_ICONS_DIR, exist_ok=True)
    return _ICONS_DIR


# ── 各图标绘制函数 ──────────────────────────────────────

def _draw_minimize(painter, cx, cy, s):
    y = int(cy + s * 0.3)
    painter.drawLine(int(cx - s), y, int(cx + s), y)

def _draw_maximize(painter, cx, cy, s):
    m = s * 0.7
    h = m * 2 / 1.6
    painter.drawRect(QRectF(cx - m, cy - h / 2, m * 2, h))

def _draw_restore(painter, cx, cy, s):
    m = s * 0.55
    h = m * 2 / 1.6
    off = s * 0.15
    painter.drawRect(QRectF(cx - m + off, cy - h / 2 - off, m * 2, h))
    painter.drawRect(QRectF(cx - m - off, cy - h / 2 + off, m * 2, h))

def _draw_close(painter, cx, cy, s):
    m = s * 0.7
    painter.drawLine(int(cx - m), int(cy - m), int(cx + m), int(cy + m))
    painter.drawLine(int(cx + m), int(cy - m), int(cx - m), int(cy + m))

def _draw_menu(painter, cx, cy, s):
    for i in (-1, 0, 1):
        y = int(cy + i * s * 0.5)
        painter.drawLine(int(cx - s), y, int(cx + s), y)

def _draw_arrow_left(painter, cx, cy, s):
    m = s * 0.7
    painter.drawLine(QPointF(cx + m, cy - m), QPointF(cx - m, cy))
    painter.drawLine(QPointF(cx - m, cy), QPointF(cx + m, cy + m))

def _draw_arrow_right(painter, cx, cy, s):
    m = s * 0.7
    painter.drawLine(QPointF(cx - m, cy - m), QPointF(cx + m, cy))
    painter.drawLine(QPointF(cx + m, cy), QPointF(cx - m, cy + m))

def _draw_arrow_up(painter, cx, cy, s):
    m = s * 0.7
    painter.drawLine(QPointF(cx - m, cy + m), QPointF(cx, cy - m))
    painter.drawLine(QPointF(cx, cy - m), QPointF(cx + m, cy + m))

def _draw_arrow_down(painter, cx, cy, s):
    m = s * 0.7
    painter.drawLine(QPointF(cx - m, cy - m), QPointF(cx, cy + m))
    painter.drawLine(QPointF(cx, cy + m), QPointF(cx + m, cy - m))

def _draw_plus(painter, cx, cy, s):
    painter.drawLine(int(cx - s), int(cy), int(cx + s), int(cy))
    painter.drawLine(int(cx), int(cy - s), int(cx), int(cy + s))

def _draw_minus(painter, cx, cy, s):
    painter.drawLine(int(cx - s), int(cy), int(cx + s), int(cy))

def _draw_check(painter, cx, cy, s):
    m = s * 0.7
    painter.drawLine(int(cx - m), int(cy), int(cx - m * 0.2), int(cy + m))
    painter.drawLine(int(cx - m * 0.2), int(cy + m), int(cx + m), int(cy - m))

def _draw_search(painter, cx, cy, s):
    r = s * 0.55
    painter.drawEllipse(QPointF(cx, cy), r, r)
    d = r * 0.7
    painter.drawLine(int(cx + d), int(cy + d), int(cx + s), int(cy + s))

def _draw_settings(painter, cx, cy, s):
    r = s * 0.35  # 内圆
    or_ = s * 0.7  # 外齿
    painter.drawEllipse(QPointF(cx, cy), r, r)
    for a in range(0, 360, 60):
        import math
        rad = math.radians(a)
        x1 = cx + r * math.cos(rad)
        y1 = cy - r * math.sin(rad)
        x2 = cx + or_ * math.cos(rad)
        y2 = cy - or_ * math.sin(rad)
        painter.drawLine(int(x1), int(y1), int(x2), int(y2))

def _draw_refresh(painter, cx, cy, s):
    import math
    r = s * 0.6
    arc_rect = QRectF(cx - r, cy - r, r * 2, r * 2)
    painter.drawArc(arc_rect, 45 * 16, 270 * 16)
    # 箭头
    end_angle = math.radians(45 + 270)
    ex = cx + r * math.cos(end_angle)
    ey = cy - r * math.sin(end_angle)
    painter.drawLine(int(ex), int(ey), int(ex + 5), int(ey))
    painter.drawLine(int(ex), int(ey), int(ex), int(ey + 5))


_DRAWERS = {
    "minimize": _draw_minimize, "maximize": _draw_maximize, "restore": _draw_restore,
    "close": _draw_close, "menu": _draw_menu,
    "arrow_left": _draw_arrow_left, "arrow_right": _draw_arrow_right,
    "arrow_up": _draw_arrow_up, "arrow_down": _draw_arrow_down,
    "plus": _draw_plus, "minus": _draw_minus, "check": _draw_check,
    "search": _draw_search, "settings": _draw_settings, "refresh": _draw_refresh,
}

AVAILABLE_ICONS = sorted(_DRAWERS.keys())


# ── 图标生成器 ──────────────────────────────────────────

class IconGenerator:
    """静态方法集：QPainter 矢量图标 → QPixmap / PNG 文件。"""

    @staticmethod
    def pixmap(name: str, color: str = "#cccccc", size: int = 24) -> QPixmap:
        """生成单个 QPixmap 图标。透明背景，仅含前景图形。"""
        draw_fn = _DRAWERS.get(name)
        if draw_fn is None:
            raise ValueError(f"未知图标: {name}，可用: {AVAILABLE_ICONS}")

        pm = QPixmap(size, size)
        pm.fill(Qt.transparent)

        painter = QPainter(pm)
        painter.setRenderHint(QPainter.Antialiasing)
        pen = QPen(QColor(color), max(1.0, size / 18))
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)

        margin = size * 0.15
        draw_fn(painter, size / 2, size / 2, size / 2 - margin)
        painter.end()
        return pm

    @staticmethod
    def save(name: str, color: str = "#cccccc", size: int = 24,
             dest: str = "", filename: str = "") -> str:
        """生成图标并保存为透明 PNG 文件。

        默认路径: app/assets/images/icons/{name}_{color}.png
        """
        pm = IconGenerator.pixmap(name, color, size)
        if dest:
            path = dest
        elif filename:
            path = os.path.join(_icon_dir(), filename)
        else:
            color_hex = color.lstrip("#")
            path = os.path.join(_icon_dir(), f"{name}_{color_hex}.png")
        pm.save(path, "PNG")
        return path

    @staticmethod
    def generate_set(colors: list = None, size: int = 24,
                     names: list = None):
        """批量生成一套图标。

        colors: 颜色列表，如 ["#cccccc", "#ffffff"]
        names: 图标名列表，默认全部
        """
        if colors is None:
            colors = ["#cccccc"]
        if names is None:
            names = AVAILABLE_ICONS
        generated = []
        for name in names:
            for color in colors:
                path = IconGenerator.save(name, color, size)
                generated.append(path)
        return generated
