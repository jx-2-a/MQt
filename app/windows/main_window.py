"""MainWindow — 应用主窗口。

继承 BaseWindow("main")，额外提供：
  - 三个控制器的快捷键注册
  - 子窗口创建与追踪管理
"""
from PyQt5.QtWidgets import QShortcut
from PyQt5.QtGui import QKeySequence

from app.windows.base_window import BaseWindow
from app.windows.sub_window import SubWindow


class MainWindow(BaseWindow):
    """应用主窗口。config_key 固定为 "main"。"""

    def __init__(self, title="QS Controller"):
        super().__init__("main")
        self.setWindowTitle(title)
        self._widget_controller = None
        self._style_controller = None
        self._window_state_controller = None
        self._icon_controller = None
        self._sub_windows: dict[str, SubWindow] = {}

        QShortcut(QKeySequence("Ctrl+Shift+L"), self, self._open_widget_controller)
        QShortcut(QKeySequence("Ctrl+Shift+S"), self, self._open_style_controller)
        QShortcut(QKeySequence("Ctrl+Shift+W"), self, self._open_window_state_controller)
        QShortcut(QKeySequence("Ctrl+Shift+I"), self, self._open_icon_controller)

    # ── 子窗口管理 ───────────────────────────────────────────

    def open_sub_window(self, config_key: str = "sub", title: str = None) -> SubWindow:
        """打开或激活一个子窗口（按 config_key 去重）。"""
        if config_key in self._sub_windows:
            win = self._sub_windows[config_key]
            if not win.isVisible():
                win.show()
            win.raise_()
            win.activateWindow()
            return win

        win = SubWindow(config_key, parent=self)
        if title:
            win.setWindowTitle(title)
        win.destroyed.connect(lambda: self._sub_windows.pop(config_key, None))
        self._sub_windows[config_key] = win
        win.show()
        return win

    def sub_window(self, config_key: str) -> SubWindow | None:
        """获取已打开的子窗口。"""
        return self._sub_windows.get(config_key)

    # ── 控制器 ───────────────────────────────────────────────

    def _open_widget_controller(self):
        from app.controllers.layout_controller import WidgetController
        if self._widget_controller is None:
            self._widget_controller = WidgetController(parent=self)
        self._widget_controller.show()
        self._widget_controller.raise_()
        self._widget_controller.activateWindow()

    def _open_style_controller(self):
        from app.controllers.style_controller import StyleController
        if self._style_controller is None:
            self._style_controller = StyleController(parent=self)
        self._style_controller.show()
        self._style_controller.raise_()
        self._style_controller.activateWindow()

    def _open_window_state_controller(self):
        from app.controllers.window_controller import WindowStateController
        if self._window_state_controller is None:
            self._window_state_controller = WindowStateController(parent=self)
        self._window_state_controller.show()
        self._window_state_controller.raise_()
        self._window_state_controller.activateWindow()

    def _open_icon_controller(self):
        from app.controllers.icon_controller import IconController
        if self._icon_controller is None:
            self._icon_controller = IconController(parent=self)
        self._icon_controller.show()
        self._icon_controller.raise_()
        self._icon_controller.activateWindow()
