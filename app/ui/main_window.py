from PyQt5.QtWidgets import QShortcut
from PyQt5.QtGui import QKeySequence
from app.ui.config_window import ConfigWindow
from app.ui.widget_controller import WidgetController
from app.ui.style_controller import StyleController


class MainWindow(ConfigWindow):
    def __init__(self, title="QS Controller"):
        super().__init__("main")
        self.setWindowTitle(title)
        self._widget_controller = None
        self._style_controller = None
        self._sub_windows = {}
        QShortcut(QKeySequence("Ctrl+Shift+L"), self, self._open_widget_controller)
        QShortcut(QKeySequence("Ctrl+Shift+S"), self, self._open_style_controller)

    def _open_widget_controller(self):
        if self._widget_controller is None:
            self._widget_controller = WidgetController(parent=self)
        self._widget_controller.show()
        self._widget_controller.raise_()
        self._widget_controller.activateWindow()

    def _open_style_controller(self):
        if self._style_controller is None:
            self._style_controller = StyleController(parent=self)
        self._style_controller.show()
        self._style_controller.raise_()
        self._style_controller.activateWindow()

    def open_sub_window(self, config_key="sub", title=None):
        if config_key in self._sub_windows:
            win = self._sub_windows[config_key]
            win.show()
            win.raise_()
            win.activateWindow()
            return win
        win = ConfigWindow(config_key, parent=self)
        if title:
            win.setWindowTitle(title)
        self._sub_windows[config_key] = win
        win.show()
        return win
