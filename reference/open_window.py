from PyQt5.QtCore import Qt, QTimer, QObject, QEvent,QRectF
import sys
import json
import importlib
import ctypes
import pyautogui
from PyQt5.QtGui import QColor, QPainter, QIcon, QPainterPath, QRegion
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow,QVBoxLayout
QApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
from json_manager import JsonManager
import os
from tool_global_registry import register, registry,update_register
import traceback
from tool_resize_handle import ResizeHandle
from tool_mask import MaskWidget
from tool_config_style_binder import ConfigStyleBinder
from db_manager import DBManager
from page_main import Page_Main
db = DBManager("_internal/data/all.db")
register(db,"data_libary")

def excepthook(exc_type, exc_value, exc_tb):
    traceback.print_exception(exc_type, exc_value, exc_tb)
sys.excepthook = excepthook

#pyinstaller -F -w -i _internal/use_resource/photo/tubiao.ico open_window.py
#pyinstaller open_window.spec
class TransparentWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.init_config()
        self.radius = int(self.config.get_set("1_1_settings/04"))
        self.init_ui()

        STYLE ="""
                background-color: rgba{{1_2_settings/10:(0,0,0,255)}};
                """
        ConfigStyleBinder.bind("(Style)-main_background_color-(color)", self, STYLE)
        self.load_page("page_denglu")

        register([], name="child_window")
        register(self, name="main_window")


        # 创建右下角拖动控件
        self.resize_handle = ResizeHandle(self,name="主窗口", size=int(self.config.get_set("1_1_settings/08")))

        self.mask = MaskWidget(self)

    def init_config(self):
        self.config = JsonManager("_internal/jsons/setting.json")
        if self.config.get("new_in"):
            sw, sh = pyautogui.size()
            self.config.set("new_in", False)
            self.config.set_set("1_1_settings/02", int(sw*0.8))
            self.config.set_set("1_1_settings/03", int(sh*0.8))
        if self.config.get_set("1_1_settings/01"):
            w_h = self.config.get("more_w_h")
            self.WIDTH,self.HEIGHT = w_h[0],w_h[1]
        else:
            self.WIDTH = int(self.config.get_set("1_1_settings/02"))
            self.HEIGHT = int(self.config.get_set("1_1_settings/03"))

    def init_ui(self):
        def center():
            frame_geom = self.frameGeometry()
            screen = QApplication.primaryScreen()
            center_point = screen.availableGeometry().center()
            frame_geom.moveCenter(center_point)
            self.move(frame_geom.topLeft())
        self.setGeometry(0, 0, self.WIDTH, self.HEIGHT)
        self.setWindowTitle("记账簿")
        self.setWindowIcon(QIcon("_internal/use_resource/photo/tubiao.png"))
        center()

    def load_page(self, page_name):
        """动态导入页面，销毁旧页面，设置新页面为中心部件"""
        self.current_page = page_name

        # 获取模块名和类名
        module_name, obj_type = self.config.get("page_all_file")[page_name]

        # 动态导入模块
        module = importlib.import_module(page_name)
        page_class = getattr(module, module_name)

        # ---- 销毁旧页面 ----
        if self.centralWidget():
            old_widget = self.centralWidget()
            old_widget.setParent(None)  # 从界面移除
            old_widget.deleteLater()  # 延迟释放内存，防止立即崩溃

        # ---- 加载并设置新页面 ----
        self.main_content = page_class(self, self.set_page, self.WIDTH, self.HEIGHT)
        self.setCentralWidget(self.main_content)

    def set_page(self, data):
        """根据 data 设置页面状态：
        - 0: 加载页面
        """
        mode = data[0]
        if mode == "加载页面" and len(data) > 1:
            # 加载指定页面
            self.load_page(data[1])
        else:
            print(f"[Warning] 未知模式或参数不足: {data}")
        self.resize_handle.raise_()
        self.mask.raise_()

    def resizeEvent(self, event):
        """重新裁剪圆角"""
        path = QPainterPath()
        path.addRoundedRect(QRectF(0, 0, self.width(), self.height()), self.radius, self.radius)
        self.setMask(QRegion(path.toFillPolygon().toPolygon()))

class ClickFilter(QObject):
    """检测点击主窗口触发子窗口抖动"""

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            child_list = registry.get("child_window", [])
            if child_list:  # 判断非空
                child = child_list[-1]  # 取最后一个
            else:
                child = None  # 或者其他默认值
            if child and child.isVisible():
                # 如果点击在子窗口内部，则不抖动
                if child.geometry().contains(event.globalPos()):
                    return False  # 不处理，允许事件正常传递

                # 点击主窗口范围内，触发抖动
                if child.parent.geometry().contains(event.globalPos()):
                    child.shake_window()
        return False  # 不阻止事件传递


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = TransparentWindow()

    click_filter = ClickFilter()
    app.installEventFilter(click_filter)

    win.show()
    sys.exit(app.exec_())
