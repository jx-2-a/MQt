from PyQt5.QtWidgets import (
    QDialog,QWidget, QTreeWidget, QTreeWidgetItem, QStackedWidget, QVBoxLayout,
    QLabel, QLineEdit, QCheckBox, QComboBox, QHBoxLayout, QApplication,
    QSpacerItem, QSizePolicy,QInputDialog,QTextEdit, QPushButton,QScrollArea
)
import sys
from json_manager import JsonManager
from PyQt5.QtCore import Qt
from tools import Tool
import traceback
def excepthook(exc_type, exc_value, exc_tb):
    traceback.print_exception(exc_type, exc_value, exc_tb)
sys.excepthook = excepthook
class SettingsPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("设置面板")
        self.resize(1000, 900)
        # 设置为最上层窗口
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)#setting
        self.settings_data = JsonManager("_internal/jsons/content_data.json")#content_data
        self.widgets_map = {}   # 存储控件映射：键为 主类/子类/名称
        self.page_map = {}      # 存储 QStackedWidget 中的页面引用
        self.setup_ui()

    def setup_ui(self):
        main_layout = QHBoxLayout(self)

        # 左侧树分类导航
        self.category_tree = QTreeWidget()
        self.category_tree.setHeaderHidden(True)
        self.category_tree.itemClicked.connect(self.on_tree_item_clicked)
        self.category_tree.itemDoubleClicked.connect(self.on_item_double_clicked)
        main_layout.addWidget(self.category_tree, 1)

        # 右侧页面堆叠
        self.stacked_pages = QStackedWidget()
        main_layout.addWidget(self.stacked_pages, 3)

        self.create_pages()

    def on_item_double_clicked(self, item, column):
        try:
            if not item or not item.text(0):
                return
            options = ["编辑内容","添加子级"]
            # ✅ 使用 None 避免父窗口问题
            op, ok = QInputDialog.getItem(self, "选择操作",
                                          f"你想对 [{item.text(0)}] 做什么？",
                                          options, editable=False)
            if ok:
                if op == "添加子级":
                    self.add_child(item)
                elif op == "编辑内容":
                    self.add_setting_item(item)
        except Exception as e:
            print("捕获异常：", e)

    def add_child(self, item):

        # 获取当前项的唯一标识 key（假设你之前设置过 setData）
        key = item.data(0, Qt.UserRole)
        u_key = "set_"+key
        if not key:
            return

        # 弹出输入框让用户输入子项名称
        new_name, ok = QInputDialog.getText(self, "添加子项", "请输入子项名称：")
        if not ok or not new_name.strip():
            return  # 用户取消或未输入

        # 检查并获取原来的设置数据
        if self.settings_data.check(u_key):
            new = self.settings_data.get(u_key)
        else:
            new = []
        new.append(new_name)
        # 添加到树
        new_item = QTreeWidgetItem([new_name])
        new_item.setData(0, Qt.UserRole, key +"_"+str(len(new)+1))  # 设置新 key，保持路径一致
        item.addChild(new_item)
        item.setExpanded(True)

        # 添加到 settings_data 中

        self.settings_data.set(u_key, new)

    def add_setting_item(self, item):
        key = item.data(0, Qt.UserRole)
        if not key:
            return

        full = key + "_settings"
        settings = self.settings_data.get(full, {})
        count = str(len(settings)+1) if len(str(len(settings)+1))>1 else "0"+str(len(settings)+1)
        dialog = AddSettingDialog(self,count=count)

        if dialog.exec_() == QDialog.Accepted:
            setting,key2 = dialog.get_data()
            print(setting,key2)
            if setting["type"] == "check":
                if setting["default"] == "True" or "true":
                    setting["default"] = True
                else:
                    setting["default"] = False
            # 添加到数据
            settings = self.settings_data.get(full, {})
            settings[key2] = setting
            self.settings_data.set(full, settings)

            # 动态添加到界面
            if full in self.page_map:
                scroll_area = self.page_map[full]
                container = scroll_area.widget()
                layout = container.layout()
                # 插入在 spacer 之前
                layout.insertLayout(layout.count() - 1, self.create_setting_item(full+ "/" + key2, setting))

                # 切换显示此页
                self.stacked_pages.setCurrentWidget(self.page_map[full])
            else:
                page = QWidget()
                layout = QVBoxLayout(page)
                layout.addLayout(self.create_setting_item(full+ "/" + key2, setting))
                layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
                # ✅ 包一层 QScrollArea
                scroll = QScrollArea()
                scroll.setWidgetResizable(True)
                scroll.setWidget(page)

                # ✅ 加入到堆叠容器中
                self.page_map[full] = scroll
                self.stacked_pages.addWidget(scroll)
                self.stacked_pages.setCurrentWidget(self.page_map[full])

    def create_pages(self,parent=None,new_i = "1"):
        if self.settings_data.check(f"set_{new_i}"):
            for i,cat in enumerate(self.settings_data.get(f"set_{new_i}")):
                item = QTreeWidgetItem([cat])
                next_i = new_i +"_"+str(i+1)
                item.setData(0, Qt.UserRole, next_i)
                is_par = self.create_pages(item,next_i)
                # if not is_par:
                #     key = next_i+"_settings"
                #     page = QWidget()
                #     layout = QVBoxLayout(page)
                #     if self.settings_data.check(key):
                #         for sid, setting in self.settings_data.get(key).items():
                #             layout.addLayout(self.create_setting_item(key + "/" + sid, setting))
                #         layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
                #         # ✅ 包一层 QScrollArea
                #         scroll = QScrollArea()
                #         scroll.setWidgetResizable(True)
                #         scroll.setWidget(page)
                #
                #         # ✅ 加入到堆叠容器中
                #         self.page_map[key] = scroll
                #         self.stacked_pages.addWidget(scroll)
                if parent:
                    parent.addChild(item)
                else:
                    self.category_tree.addTopLevelItem(item)
            return True
        else:
            return False

    def create_setting_item(self, prefix, setting):
        layout = QVBoxLayout()
        stype = setting.get("type")
        label = QLabel(setting["label"]+stype)
        layout.addWidget(label)


        widget = None
        key = prefix  # ✅ 你只要保证 prefix 是唯一的就行

        if stype == "select":
            widget = QComboBox()
            options = setting.get("options", [])
            widget.addItems(options)
            default = setting.get("default")
            if default in options:
                widget.setCurrentText(default)

        elif stype == "text":
            widget = QLineEdit()
            widget.setText(str(setting.get("default", "")))
        elif stype == "text_b":
            widget = QLineEdit()
            widget.setText(str(setting.get("default", "")))
        elif stype == "zhushi":
            label = QLabel(setting.get("default", ""))
            font = label.font()
            font.setPointSize(font.pointSize() + 2)  # ⬅️ 字体大一点
            font.setBold(True)
            label.setFont(font)
            label.setStyleSheet("color: gray;")  # 可选：提示风格
            layout.addWidget(label)
        elif stype == "fenge":
            label = QLabel(setting.get("default", "")+"-分割线-")
            font = label.font()
            font.setPointSize(font.pointSize() + 2)  # ⬅️ 字体大一点
            font.setBold(True)
            label.setFont(font)
            label.setStyleSheet("color: gray;")  # 可选：提示风格
            layout.addWidget(label)
        elif stype == "check":
            widget = QCheckBox(setting["label"])
            widget.setStyleSheet("""
                                QCheckBox {
                                    font-size: 24px;
                                }
                                QCheckBox::indicator {
                                    width: 24px;
                                    height: 24px;
                                }
                            """)
            default = setting.get("default")
            if isinstance(default, str):
                default = Tool.to_bool(default)
            widget.setChecked(default)  # 默认勾选

        if widget:
            layout.addWidget(widget)
            self.widgets_map[key] = (stype, widget)

        layout.setSpacing(4)
        return layout

    def creat_page(self,key):
        page = QWidget()
        layout = QVBoxLayout(page)
        if self.settings_data.check(key):
            for sid, setting in self.settings_data.get(key).items():
                layout.addLayout(self.create_setting_item(key + "/" + sid, setting))
            layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

            # ✅ 包一层 QScrollArea
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setWidget(page)

            # ✅ 加入到堆叠容器中
            self.page_map[key] = scroll
            self.stacked_pages.addWidget(scroll)
            return True
        else:
            return False
    def on_tree_item_clicked(self, item, column):
        if item.childCount() == 0:
            key = item.data(0, Qt.UserRole)
            full_key = key + "_settings"
            # 保存并销毁旧页面
            if hasattr(self, "current_key") and self.current_key in self.page_map:
                old_widget = self.page_map.pop(self.current_key)

                # 👉 保存当前页面状态
                self.get_values()

                # 👉 移除并销毁旧控件
                self.stacked_pages.removeWidget(old_widget)
                old_widget.deleteLater()
                self.widgets_map={}
            # 创建新页面并添加
            a = self.creat_page(full_key)
            if a:
                self.stacked_pages.setCurrentWidget(self.page_map[full_key])
                self.current_key = full_key



    def get_values(self):
        result = {}
        for key, (stype, widget) in self.widgets_map.items():
            if stype == "check":
                value = widget.isChecked()
            elif stype == "select":
                value = widget.currentText()
            elif stype == "text":
                value = widget.text()
            elif stype == "text_b":
                value = widget.text()
            else:
                value = None
            result[key] = value
        self.save_value(self.settings_data,result)
        # print(result)
        return result
    def save_value(self,settings_data,flat_setting):
        for path, new_value in flat_setting.items():
            keys = path.split("/")
            if len(keys) == 2:
                top_key, sub_key = keys
                if settings_data.check(top_key):
                    old_value = settings_data.get(top_key)
                    if sub_key in old_value:
                        old_value[sub_key]["default"] = new_value
                        settings_data.set(top_key,old_value)
        # settings_data._save()

class AddSettingDialog(QDialog):
    def __init__(self, parent=None,count=""):
        super().__init__(parent)
        self.setWindowTitle("添加设置项")

        layout = QVBoxLayout(self)

        # ✅ key 唯一标识符
        self.key_edit = QLineEdit()
        layout.addLayout(self._line("键名 (key)：", self.key_edit))
        self.key_edit.setText(count)

        # label
        self.label_edit = QLineEdit()
        layout.addLayout(self._line("显示名称 (label)：", self.label_edit))
        self.label_edit.setText("")

        # type
        self.type_combo = QComboBox()
        self.type_combo.addItems(["text", "select", "zhushi","check","fenge","text_b"])
        layout.addLayout(self._line("类型 (type)：", self.type_combo))

        # default
        self.default_edit = QLineEdit()
        layout.addLayout(self._line("默认值 (default)：", self.default_edit))

        # state
        self.state_check = QCheckBox("换行")
        self.state_check.setChecked(True)  # 默认 True
        layout.addLayout(self._line("状态 (state)：", self.state_check))

        # relect
        self.relect = QLineEdit()
        layout.addLayout(self._line("对象 (relect)：", self.relect))

        # options (for select)
        self.options_edit = QTextEdit()
        layout.addLayout(self._line("选项列表（仅限 select，用逗号分隔）：", self.options_edit))

        # 确定/取消按钮
        btn_layout = QHBoxLayout()
        self.ok_btn = QPushButton("确定")
        self.cancel_btn = QPushButton("取消")
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

    def _line(self, text, widget):
        layout = QHBoxLayout()
        layout.addWidget(QLabel(text))
        layout.addWidget(widget)
        return layout

    def get_data(self):
        key = self.key_edit.text().strip()
        label = self.label_edit.text().strip()
        setting_type = self.type_combo.currentText()
        default = self.default_edit.text().strip()
        relect = self.relect.text().strip()
        state = self.state_check.isChecked()  # 新增：获取状态

        if not key or not label:
            return None  # 你可以加 QMessageBox 提示空值

        setting = {
            "label": label,
            "type": setting_type,
            "default": default,
            "state": state,  # 新增字段
            "relect": relect
        }

        if setting_type == "select":
            raw = self.options_edit.toPlainText().strip()
            options = [x.strip() for x in raw.split(",") if x.strip()]
            setting["options"] = options

        return setting, key


# ✅ 示例调用
if __name__ == "__main__":
    app = QApplication(sys.argv)
    panel = SettingsPanel()
    panel.show()

    def on_close():
        values = panel.get_values()
        print("设置值：")
        for k, v in values.items():
            print(f"{k}: {v}")

    app.aboutToQuit.connect(on_close)
    sys.exit(app.exec_())
