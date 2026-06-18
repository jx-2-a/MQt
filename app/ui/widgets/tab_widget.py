"""向后兼容代理 — 从 complex_widgets 导入。"""
from app.ui.complex_widgets.tab_widget import CachedTabWidget as StyledTabWidget
from app.ui.complex_widgets.tab_widget import CachedTabWidget

# 旧名别名
TabItem = None
TabBar = None
