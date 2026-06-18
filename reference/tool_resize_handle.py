# resize_handle.py
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor
from json_manager import JsonManager
from tool_global_registry import registry
config = JsonManager("_internal/jsons/setting.json")
class ResizeHandle(QWidget):
    """
    右下角透明控件，用于给父窗口添加可拖动调整大小的功能。

    使用方法：
        handle = ResizeHandle(parent_window, size=10)
    """

    def __init__(self,parent,name="", size=10):
        super().__init__(parent)
        self.name = name
        self.parent_window = parent
        self.handle_size = size
        self.setFixedSize(size, size)
        self.setCursor(Qt.SizeFDiagCursor)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self._resizing = False
        self._drag_pos = None
        self._start_size = None
        self.new_width = None
        self.new_height = None

        # 初始位置：父窗口右下角
        self.move(self.parent_window.width() - self.handle_size,
                  self.parent_window.height() - self.handle_size)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._resizing = True
            self._drag_pos = event.globalPos()
            self._start_size = self.parent_window.size()

    def mouseMoveEvent(self, event):
        if self._resizing and event.buttons() & Qt.LeftButton:
            delta = event.globalPos() - self._drag_pos
            self.new_width = max(100, self._start_size.width() + delta.x())
            self.new_height = max(100, self._start_size.height() + delta.y())
            self.parent_window.resize(self.new_width, self.new_height)
            # 保证 handle 永远在右下角
            self.move(self.parent_window.width() - self.handle_size,
                      self.parent_window.height() - self.handle_size)
            if self.name == "主窗口":
                registry["page_main"].update_background()
    def mouseReleaseEvent(self, event):
        self._resizing = False
        if self.name == "主窗口":
            config.set("more_w_h",(self.new_width,self.new_height))
            config.set_set("1_1_settings/05", f"当前为({self.new_width}, {self.new_height})，不勾选此项，将使用下方自定义大小",)


    def update_position(self):
        """可在父窗口 resizeEvent 中调用，保证 handle 位置正确"""
        self.move(self.parent_window.width() - self.handle_size,
                  self.parent_window.height() - self.handle_size)
