"""SubWindow — 子窗口。

继承 BaseWindow，使用独立 config_key。
由 MainWindow.open_sub_window() 创建和追踪。
"""
from app.windows.base_window import BaseWindow


class SubWindow(BaseWindow):
    """子窗口。与 BaseWindow 行为一致，仅身份不同。"""

    def __init__(self, config_key: str, parent=None):
        super().__init__(config_key, parent=parent)
