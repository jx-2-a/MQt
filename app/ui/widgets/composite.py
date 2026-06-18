from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt
from app.core.style_engine import props_to_qss


class CompositeWidget(QWidget):
    """复合控件基类 — 内部布局固定，通过命名槽位添加内容。

    子类覆盖 _build_layout() 定义固定的内部结构，
    通过 _register_slot(name, widget) 注册命名槽位。
    外部代码通过 slot(name) 获取槽位向其添加子控件，
    不得直接修改内部布局。

    槽位内的 widget 自动获得 objectName=name，样式引擎可
    通过 #name 选择器精确控制子区域样式。
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._slots = {}
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setAutoFillBackground(False)
        self._build_layout()

    def _build_layout(self):
        raise NotImplementedError("子类必须实现 _build_layout()")

    def _register_slot(self, name, widget):
        """注册命名槽位。widget 自动获得 objectName 供样式定位。"""
        widget.setObjectName(name)
        widget.setAttribute(Qt.WA_StyledBackground, True)
        widget.setAutoFillBackground(False)
        self._slots[name] = widget

    def slot(self, name):
        """获取命名槽位，可向其中添加子控件或设置样式。"""
        return self._slots.get(name)

    def slot_names(self):
        """返回所有已注册的槽位名称。"""
        return list(self._slots.keys())

    def apply_style(self, style_props=None):
        """应用样式到自身，并递归到所有命名槽位。"""
        self.setStyleSheet(props_to_qss(style_props) if style_props else "")
        # 递归槽位
        for slot_widget in self._slots.values():
            if hasattr(slot_widget, "apply_style"):
                from app.core.style_engine import resolve_style
                name = slot_widget.objectName()
                lt = slot_widget.property("layout_type") or type(slot_widget).__name__
                merged = resolve_style(name, lt, None, flat=True)
                slot_widget.apply_style(merged if merged else None)
