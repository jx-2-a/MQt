from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import Qt
from app.core.window_config import get_window_config, update_window_config
from app.core.layout_loader import load_layout
from app.core.layout_engine import apply_to_window
from app.core.style_engine import apply_to_widget


class ConfigWindow(QMainWindow):
    def __init__(self, config_key, parent=None):
        super().__init__(parent)
        cfg = get_window_config(config_key)
        self._config_key = config_key
        self.setWindowTitle(cfg.get("title", "Window"))
        if cfg.get("frameless", False):
            self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowOpacity(cfg.get("opacity", 1.0))
        bg = cfg.get("background_color")
        if bg:
            self.setStyleSheet(f"QMainWindow {{ background-color: {bg}; }}")
        geo = cfg.get("geometry", {})
        self.resize(geo.get("width", 800), geo.get("height", 600))
        layout_name = cfg.get("layout")
        if layout_name:
            node = load_layout(layout_name)
            if node:
                apply_to_window(self, node)
        apply_to_widget(self, config_key)

    def showEvent(self, event):
        cfg = get_window_config(self._config_key)
        geo = cfg.get("geometry", {})
        if geo and "x" in geo and "y" in geo:
            self.move(geo["x"], geo["y"])
        apply_to_widget(self, self._config_key)
        super().showEvent(event)

    def closeEvent(self, event):
        g = {"x": self.x(), "y": self.y(), "width": self.width(), "height": self.height()}
        update_window_config(self._config_key, geometry=g)
        super().closeEvent(event)
