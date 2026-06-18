"""BaseWindow — 配置驱动窗口基类。

职责:
  - 从 settings.json 读取窗口配置（geometry/opacity/frameless/title/layout/background）
  - 调用 layout_engine 渲染控件树
  - 调用 style_engine 应用控件 QSS
  - 管理窗口背景层（QLabel 方案，保持 rgba 半透明合成）
  - showEvent 恢复位置 / closeEvent 持久化 geometry

不做:
  - config 的持久化写入 — 由 WindowStateController 负责
"""
import os

from PyQt5.QtWidgets import QMainWindow, QLabel, QMessageBox
from PyQt5.QtGui import QPixmap, QPainter, QBitmap, QPainterPath
from PyQt5.QtCore import Qt, QRectF

from app.framework.config_manager import get_window_config, update_window_config, load_layout
from app.core.layout_engine import apply_to_window
from app.core.style_engine import apply_to_widget

_STYLES_DIR = os.path.join(os.path.dirname(__file__), "..", "config")


class BaseWindow(QMainWindow):
    """配置驱动的窗口基类。

    config_key: settings.json 中的键，如 "main"、"sub"
    """

    BG_OBJ_NAME = "__bg_layer__"

    def __init__(self, config_key: str, parent=None):
        super().__init__(parent)
        self._config_key = config_key
        self._bg_image = None
        self._bg_scale = "crop"
        self._border_radius = 0
        self._img_cache = None

        self.setAttribute(Qt.WA_StyledBackground, False)
        self.setAutoFillBackground(False)

        cfg = get_window_config(config_key)
        self._apply_window_props(cfg)

        layout_name = cfg.get("layout")
        if layout_name:
            node = load_layout(layout_name)
            if node:
                apply_to_window(self, node)
        else:
            apply_to_widget(self, config_key)
            self._ensure_background_layer()

    # ── 公开 API ─────────────────────────────────────────────

    @property
    def config_key(self) -> str:
        return self._config_key

    def apply_layout(self, name: str):
        """运行时切换布局。apply_to_window 内部已处理 QSS 重载 + 背景重建。"""
        node = load_layout(name)
        if node is None:
            raise ValueError(f"布局 '{name}' 不存在")
        apply_to_window(self, node)

    def _show_message(self, title: str, message: str):
        """弹出消息框（供事件系统 action 模板调用）。"""
        QMessageBox.information(self, title, message)

    def apply_styles(self):
        """重新应用样式（QSS + 背景层）。"""
        apply_to_widget(self, self._config_key)
        self._ensure_background_layer()

    def ensure_background(self):
        """强制刷新背景层（布局切换后 centralWidget 被替换时调用）。"""
        self._ensure_background_layer()

    def update_config(self, **kwargs):
        """运行时更新窗口属性并立即生效。

        接受: title, geometry(dict), opacity, frameless,
              background_image, background_image_scale, border_radius, layout
        """
        if "title" in kwargs:
            self.setWindowTitle(kwargs["title"])
        if "opacity" in kwargs:
            self.setWindowOpacity(kwargs["opacity"])
        if "frameless" in kwargs:
            flags = self.windowFlags()
            if kwargs["frameless"]:
                flags |= Qt.FramelessWindowHint
            else:
                flags &= ~Qt.FramelessWindowHint
            self.setWindowFlags(flags)
        if "geometry" in kwargs:
            geo = kwargs["geometry"]
            self.resize(geo.get("width", 800), geo.get("height", 600))
            if "x" in geo and "y" in geo:
                self.move(geo["x"], geo["y"])
        if "background_image" in kwargs:
            self._bg_image = kwargs["background_image"]
            self._img_cache = None
        if "background_image_scale" in kwargs:
            self._bg_scale = kwargs["background_image_scale"]
        if "border_radius" in kwargs:
            self._border_radius = int(kwargs["border_radius"])
        if any(k in kwargs for k in ("background_image", "background_image_scale", "border_radius")):
            self._ensure_background_layer()
        if "layout" in kwargs:
            self.apply_layout(kwargs["layout"])

    # ── 内部方法 ─────────────────────────────────────────────

    def _apply_window_props(self, cfg: dict):
        """从配置字典设置窗口基础属性。"""
        self.setWindowTitle(cfg.get("title", "Window"))
        if cfg.get("frameless", False):
            self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowOpacity(cfg.get("opacity", 1.0))
        geo = cfg.get("geometry", {})
        self.resize(geo.get("width", 800), geo.get("height", 600))

        self._bg_image = cfg.get("background_image")
        self._bg_scale = cfg.get("background_image_scale", "crop")
        self._border_radius = cfg.get("border_radius", 0)

    # ── 背景层管理 ───────────────────────────────────────────

    def _ensure_background_layer(self):
        """维护 QLabel 背景层（仅用于图片叠加），保持在最底层。

        bg_label 始终全透明——窗口背景色由 root 节点的 paintEvent 负责，
        这里只叠加背景图片（如果配置了的话）。
        """
        cw = self.centralWidget()
        if cw is None:
            return

        bg_image = self._bg_image
        bg_scale = self._bg_scale or "crop"

        bg_label = cw.findChild(QLabel, self.BG_OBJ_NAME)

        # 不需要背景层时移除
        if not bg_image and self._border_radius <= 0:
            if bg_label is not None:
                bg_label.deleteLater()
            if hasattr(cw, '_bg_hook_installed'):
                del cw._bg_hook_installed
            return

        if bg_label is None:
            bg_label = QLabel(cw)
            bg_label.setObjectName(self.BG_OBJ_NAME)
            bg_label.setAttribute(Qt.WA_TransparentForMouseEvents, True)
            bg_label.show()

        self._apply_bg_pixmap(bg_label, bg_image, bg_scale)

        if not hasattr(cw, '_bg_hook_installed'):
            cw._bg_hook_installed = True
            self._install_cw_resize_hook(cw)

        self._apply_window_mask()

    def _apply_bg_pixmap(self, bg_label, bg_image, bg_scale):
        """生成 pixmap 并应用到 bg_label，geometry 跟随 centralWidget。"""
        cw = self.centralWidget()
        if cw is None:
            return
        w = max(cw.width(), 1)
        h = max(cw.height(), 1)
        bg_label.setGeometry(0, 0, w, h)
        bg_label.setPixmap(self._make_bg_pixmap(bg_image, w, h, bg_scale or "crop"))
        bg_label.lower()

    def _install_cw_resize_hook(self, cw):
        """在 centralWidget 上安装 resizeEvent 钩子，跟随 Qt 异步布局更新背景。"""
        original_resize = cw.resizeEvent

        def hooked_resize(event):
            original_resize(event)
            lbl = cw.findChild(QLabel, self.BG_OBJ_NAME)
            if lbl:
                self._apply_bg_pixmap(lbl, self._bg_image, self._bg_scale)
            self._apply_window_mask()

        cw.resizeEvent = hooked_resize

    def _apply_window_mask(self):
        """应用窗口圆角遮罩。"""
        if self._border_radius > 0:
            r = self._border_radius
            bitmap = QBitmap(self.size())
            bitmap.fill(Qt.color0)
            painter = QPainter(bitmap)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setBrush(Qt.color1)
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(self.rect(), r, r)
            painter.end()
            self.setMask(bitmap)
        else:
            self.setMask(QBitmap())

    def _make_bg_pixmap(self, bg_image, w, h, scale="crop"):
        """生成全透明底板 + 背景图片的 QPixmap。

        scale 模式:
          - "crop": 等比缩放铺满，居中裁剪（CSS cover）
          - "contain": 等比缩放完整显示，居中放置
          - "stretch": 拉伸填充，忽略宽高比

        底板全透明——窗口背景色由 root 节点 paintEvent 负责，
        bg_label 只叠加图片，多余区域保持透明以露出 root 背景色。
        """
        bg_pix = QPixmap(w, h)
        bg_pix.fill(Qt.transparent)

        if self._border_radius > 0 and not bg_image:
            return bg_pix

        img_pix = None
        if bg_image:
            path = bg_image.replace("\\", "/")
            if not os.path.exists(path):
                path = os.path.join(_STYLES_DIR, bg_image)
            if os.path.exists(path):
                if self._img_cache and self._img_cache[0] == path:
                    img_pix = self._img_cache[1]
                else:
                    img_pix = QPixmap(path)
                    if not img_pix.isNull():
                        self._img_cache = (path, img_pix)

        radius = self._border_radius

        if img_pix and not img_pix.isNull():
            painter = QPainter(bg_pix)
            painter.setRenderHint(QPainter.Antialiasing)
            if radius > 0:
                path = QPainterPath()
                path.addRoundedRect(QRectF(0, 0, w, h), radius, radius)
                painter.setClipPath(path)

            if scale == "stretch":
                scaled = img_pix.scaled(w, h, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
                painter.drawPixmap(0, 0, scaled)
            elif scale == "contain":
                scaled = img_pix.scaled(w, h, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                x = (w - scaled.width()) // 2
                y = (h - scaled.height()) // 2
                painter.drawPixmap(x, y, scaled)
            else:  # crop
                expanded = img_pix.scaled(w, h, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
                x = (expanded.width() - w) // 2
                y = (expanded.height() - h) // 2
                cropped = expanded.copy(x, y, w, h)
                painter.drawPixmap(0, 0, cropped)
            painter.end()

        return bg_pix

    # ── Qt 事件 ──────────────────────────────────────────────

    def showEvent(self, event):
        """恢复上次位置 + 重新应用 QSS + 刷新背景 + 窗口圆角遮罩。"""
        cfg = get_window_config(self._config_key)
        geo = cfg.get("geometry", {})
        if geo and "x" in geo and "y" in geo:
            self.move(geo["x"], geo["y"])
        apply_to_widget(self, self._config_key)
        self._ensure_background_layer()
        self._apply_window_mask()
        super().showEvent(event)

    def closeEvent(self, event):
        """持久化当前 geometry 到 settings.json。"""
        g = {"x": self.x(), "y": self.y(),
             "width": self.width(), "height": self.height()}
        update_window_config(self._config_key, geometry=g)
        super().closeEvent(event)

    def resizeEvent(self, event):
        """窗口大小变化时更新背景层和圆角遮罩。"""
        super().resizeEvent(event)
        self._update_background_pixmap()
        self._apply_window_mask()

    def _update_background_pixmap(self):
        """resizeEvent 触发：更新背景层尺寸。"""
        cw = self.centralWidget()
        if cw is None:
            return
        lbl = cw.findChild(QLabel, self.BG_OBJ_NAME)
        if lbl is None:
            return
        self._apply_bg_pixmap(lbl, self._bg_image, self._bg_scale)
