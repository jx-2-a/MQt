"""窗口工厂函数。"""
from app.windows.main_window import MainWindow
from app.windows.sub_window import SubWindow


def create_main_window(title: str = "QS Controller") -> MainWindow:
    """创建应用主窗口。"""
    return MainWindow(title)


def open_sub_window(parent, title: str = "Sub Window", config_key: str = "sub") -> SubWindow:
    """打开或创建一个子窗口。如果 parent 是 MainWindow，走其内部追踪。"""
    if isinstance(parent, MainWindow):
        return parent.open_sub_window(config_key, title)
    # 非 MainWindow parent：直接创建独立子窗口
    sub = SubWindow(config_key, parent=parent)
    sub.setWindowTitle(title)
    sub.show()
    return sub
