from PyQt5.QtWidgets import QWidget, QLabel, QComboBox, QHBoxLayout, QSizePolicy
from PyQt5.QtGui import QFontMetrics
from PyQt5.QtCore import Qt
from item_select import LabeledComboBox


class EditableComboBox(LabeledComboBox):
    def __init__(self, text: str, items=None, parent=None):
        super().__init__(text, items, parent)
        self.combo.wheelEvent = lambda event: None  # 禁用滚轮切换
        self.combo.setEditable(True)  # 可编辑
        self._last_index = 0  # 记录最近选中的 index
        self._now_index = 0
        # 绑定信号：回车 / 编辑完成
        self.combo.currentIndexChanged.connect(self._on_index_changed)

        self.combo.lineEdit().returnPressed.connect(self._save_edit)

    def _on_index_changed(self, index: int):
        """保存用户切换的 index"""
        self._last_index = self._now_index
        self._now_index = index
    def _save_edit(self):
        """在编辑完成或回车时保存/删除"""
        idx = self._last_index
        text = self.combo.currentText().strip()
        if not text:
            self.combo.setCurrentIndex(self._now_index)
            return

        if text == "【删除】":
            self.combo.removeItem(self._last_index)
            self.combo.removeItem(self._now_index)
            self.combo.setCurrentIndex(0)
            self.update_min_width()
            return

        self.update_min_width()

    def set_current_text(self,text):
        self.combo.setCurrentText(text)
        # 查找文本在 ComboBox 中的索引
        idx = self.combo.findText(text)
        self._last_index  = idx
        self._now_index =idx

    def get_all_items(self):
        """获取所有选项"""
        return [self.combo.itemText(i) for i in range(self.combo.count())]

    def get_value(self):
        """获取当前选项"""
        return self.combo.currentText()


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication, QVBoxLayout, QWidget
    import sys

    app = QApplication(sys.argv)
    win = QWidget()
    layout = QVBoxLayout(win)

    box = EditableComboBox("水果：", ["苹果", "香蕉", "橙子"])
    layout.addWidget(box)

    win.show()
    sys.exit(app.exec_())
