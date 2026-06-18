from PyQt5.QtCore import Qt, QSize,QEvent,QCoreApplication, QPoint, QThread, pyqtSignal

QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
from PyQt5.QtWidgets import (
    QStyledItemDelegate, QSplitter, QMenu, QAction, QSizePolicy, QListWidget, QStackedWidget, QListWidgetItem, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QScrollArea, QTextEdit, QFrame, QApplication
)
from PyQt5.QtGui import QPixmap, QIcon, QFontMetrics,QFont
import random
from tools import Tool
from json_manager import JsonManager
import importlib
from functools import partial
import ast
import sys
import os
from page_setting import SettingsWindow
from tool_global_registry import register, registry,add_register,update_register
import traceback
from tool_config_style_binder import ConfigStyleBinder

content_data = JsonManager("_internal/jsons/content_data.json")
def excepthook(exc_type, exc_value, exc_tb):
    traceback.print_exception(exc_type, exc_value, exc_tb)
sys.excepthook = excepthook

class Page_Main(QWidget):
    def __init__(self, parent, callback, width, height):
        super().__init__(parent)
        self.parent = parent  # 保存主窗口的引用
        self.config = JsonManager("_internal/jsons/setting.json")
        register(self, name="page_main")
        self.due_inf()
        self.set_background()
        self.judje_ooc_back()
        ConfigStyleBinder.bind_function("(Function)-change_background_photo-(path)",self.update_background,a=True)
        ConfigStyleBinder.bind_function("(Function)-open_background_photo-()", self.judje_ooc_back)
        self.width = width
        self.height = height

        self.anjian = ["店铺记账","游戏物品价格"]
        self.setStyleSheet(f"""
                background-color: transparent;
                border: 0 px;
                border-radius:0 px;

                font-family: '{self.config.get_set("1_2_1_1_settings/05")}', sans-serif;
                font-size: {self.config.get_set("1_2_1_1_settings/07")}px;
                font-weight: {self.config.get_set("1_2_1_1_settings/08")};
                color: rgba{self.config.get_set("1_2_1_1_settings/10")};

                padding:0 px;
        """)
        self.set_overall_layout()
        self.set_title_bar()
        self.set_main()
        self.little_max = False
        register(None, name="current_page_id")
    def judje_ooc_back(self):
        if self.config.get_set("1_2_settings/08"):
            self.photo_kai = True
            self.update_background(True)
        else:
            self.photo_kai = False
            if hasattr(self, "bg_label"):
                self.bg_label.clear()  # 清空文字和图片
    def set_background(self):
        # 设置背景 QLabel（仅初始化一次）
        self.bg_label = QLabel(self)
        self.bg_label.setScaledContents(True)  # 不推荐用于保持比例，真实缩放我们手动处理
        self.bg_label.lower()  # 保证在底层
    def update_background(self, a=False):
        """更新背景图尺寸和缩放显示，保证填满窗口并居中裁剪"""
        if self.photo_kai:
            if a:
                self.original_pixmap = QPixmap(self.config.get_set("1_2_settings/06"))
            cur_width = self.parent.width()
            cur_height = self.parent.height()
            # 设置背景控件大小
            self.bg_label.setGeometry(0, 0, cur_width, cur_height)
            if self.original_pixmap:
                # 按窗口大小缩放背景图，保持比例并填满
                scaled_pixmap = self.original_pixmap.scaled(
                    cur_width, cur_height,
                    Qt.KeepAspectRatioByExpanding,
                    Qt.SmoothTransformation
                )

                # 计算裁剪区域（保证居中）
                x = (scaled_pixmap.width() - cur_width) // 2
                y = (scaled_pixmap.height() - cur_height) // 2
                cropped_pixmap = scaled_pixmap.copy(x, y, cur_width, cur_height)

                # 设置背景图
                self.bg_label.setPixmap(cropped_pixmap)
    def due_inf(self):
        self.sty_mode = self.config.get_set("1_2_settings/02")
        if self.sty_mode == "亮主题":
            self.photo_path_root = "white_button"
        elif self.sty_mode == "暗主题":
            self.photo_path_root = "black_button"
        else:
            self.photo_path_root = "white_button"
    def load_page(self, page_id, **kwargs):
        """动态导入页面"""
        page_info =content_data.get(page_id)
        page_name, module_py, module_name,module_canshu = page_info[0], page_info[1], page_info[2],page_info[3]
        module = importlib.import_module(module_py)
        page_class = getattr(module, module_name)
        if module_canshu:
            kwargs.update(module_canshu)
        widget = page_class(**kwargs)
        return page_name, widget
    def set_overall_layout(self):
        """给Page_Main(QWidget)这个框架进行总布局"""
        self.overall_layout = QVBoxLayout(self)
        self.overall_layout.setContentsMargins(0, 0, 0, 0)
        self.overall_layout.setSpacing(0)
    def set_title_bar(self):
        """设置最上层标题栏"""
        def title_bar_parameter():
            """设置标题栏所用参数"""
            title_bar_widget_height = int(self.config.get_set("1_3_settings/02"))
            side = int(self.config.get_set("1_3_settings/03"))
            content_height = title_bar_widget_height - side * 2
            return title_bar_widget_height, side, content_height
        def toggle_maximize():
            if getattr(self, "_is_maximized", False):
                self.parent.setGeometry(self._normal_geometry)
                self._is_maximized = False
                self.max_butt.setIcon(QIcon(f"_internal/use_resource/{self.photo_path_root}/max.png"))
            else:
                self._normal_geometry = self.parent.geometry()
                desktop = QApplication.primaryScreen().availableGeometry()
                self.parent.setGeometry(desktop)
                self._is_maximized = True
                self.max_butt.setIcon(QIcon(f"_internal/use_resource/{self.photo_path_root}/down.png"))
            self.update_background()
        def set_style_for_buts(buts = {}):
            for i in buts:
                if i == "关闭":
                    buts[i].setStyleSheet(f"""
                                    QPushButton {{
                                        background-color:transparent;
                                        border-radius: {self.config.get_set("1_3_settings/07")} px; 
                                        border: 0 px ;
                                    }}
                                    QPushButton:hover {{
                                        background-color: rgba(201,79,79,255);
                                        border-radius: {self.config.get_set("1_3_settings/07")}px; 
                                    }}
                                """)
                else:
                    buts[i].setStyleSheet(f"""
                                    QPushButton {{
                                        background-color:transparent;
                                        border-radius: {self.config.get_set("1_3_settings/07")} px; 
                                        border: 0 px ;
                                    }}
                                    QPushButton:hover {{
                                        background-color: rgba{self.config.get_set("1_3_settings/08")};
                                        border-radius: {self.config.get_set("1_3_settings/07")}px; 
                                    }}
                                """)
        def set_style_for_text_b(tbuts={}):
            for i in tbuts:
                tbuts[i].setStyleSheet(f"""
                    QLabel {{
                        background: rgba{self.config.get_set("1_3_settings/11")};
                        border: 0px;
                        border-radius: {self.config.get_set("1_3_settings/12")}px;
                        padding: {self.config.get_set("1_3_settings/13")}px {self.config.get_set("1_3_settings/14")}px;
                        
                        font-family: '{self.config.get_set("1_3_settings/15")}', sans-serif;
                        font-size: {self.config.get_set("1_3_settings/16")}px;
                        font-weight: {Tool.get_font_weight("1_3_settings/17")};
                        color: rgba{self.config.get_set("1_3_settings/18")};  
                    }}
                    QLabel:hover {{
                            border-radius: {self.config.get_set("1_3_settings/12")}px;
                            background: rgba{self.config.get_set("1_3_settings/19")};
                    }}
                """)
        def call_back(folder_name):
            if folder_name == "关闭":
                QApplication.instance().quit()
            elif folder_name == "最大化":
                toggle_maximize()
            elif folder_name == "最小化":
                self.parent.showMinimized()
            elif folder_name == "设置":
                def open_settings():
                    add_register("child_window",SettingsWindow(self.parent,1400,800))
                open_settings()
        def edit_callback(item):
            l = content_data.get(f"big_title_content_{item}")
            t = content_data.get("big_title_content")
            self.update_title_and_file_list(t[int(item)],l)


        self._drag_active = False
        self._drag_start_pos = None

        title_bar_widget_height, side, content_height= title_bar_parameter()

        # 顶部状态栏容器
        self.title_bar_widget = QWidget()
        self.title_bar_widget.setFixedHeight(title_bar_widget_height)  # 设置标题栏高度
        STYLE = """
                        background-color: rgba{{1_3_settings/04:(20,20,20,100)}};
                        """
        ConfigStyleBinder.bind("(Style)-title_bar_widget-(color)", self.title_bar_widget, STYLE)

        # 添加横向布局
        title_bar = QHBoxLayout(self.title_bar_widget)
        title_bar.setSpacing(int(self.config.get_set("1_3_settings/05")))
        title_bar.setContentsMargins(side, side, side, side)


        # 左侧图标按钮
        icon_btn = QPushButton()
        icon_btn.setIcon(QIcon(f"_internal/use_resource/{self.photo_path_root}/tubiao.png"))
        icon_btn.setIconSize(QSize(content_height, content_height))
        icon_btn.setFixedSize(content_height, content_height)
        icon_btn.setStyleSheet("background: transparent; border: none;")  # 去掉背景和边框
        title_bar.addWidget(icon_btn)  # 向顶部添加ico

        # 标题栏文本按键部分
        title_button_r = QWidget()
        title_button_r.setStyleSheet(f"""
                            background-color: transparent;
                            border: 0px;
                            border-radius: 0 px;
                        """)
        title_button_r.setFixedHeight(content_height)  # 设置标题栏高度
        title_button_layout = QHBoxLayout(title_button_r)
        title_button_layout.setSpacing(0)
        title_button_layout.setContentsMargins(0, 0, 0, 0)
        tbuts = {}
        for shushu,i in enumerate(self.anjian):
            anjian = title_button(i,title_button_r)
            title_button_layout.addWidget(anjian)
            anjian.mousePressEvent = lambda e, b=shushu: edit_callback(b)
            tbuts[i] = anjian
        set_style_for_text_b(tbuts)
        ConfigStyleBinder.bind_function("(Function)-set_style_for_text_b-(color)", set_style_for_text_b, tbuts=tbuts)

        title_bar.addWidget(title_button_r)
        title_bar.addStretch()

        icon_paths = {
            "设置": f"_internal/use_resource/{self.photo_path_root}/setting.png",
            "最小化": f"_internal/use_resource/{self.photo_path_root}/min.png",
            "最大化": f"_internal/use_resource/{self.photo_path_root}/max.png",
            "关闭": f"_internal/use_resource/{self.photo_path_root}/close.png",
        }
        buts = {}
        for name, path in icon_paths.items():
            callback = partial(call_back, name)  # 给回调传 name，例如 “收件夹”
            if name == "最大化":
                but = self.max_butt = Tool.add_image_button(title_bar, icon_path=path,icon_size=(content_height, content_height), callback=callback)
            else:
                but = Tool.add_image_button(title_bar, icon_path=path, icon_size=(content_height, content_height),callback=callback)
            buts[name] = but
        set_style_for_buts(buts)
        ConfigStyleBinder.bind_function("(Function)-set_style_for_buts-(color)",set_style_for_buts,buts=buts)
        # 添加到总布局中
        self.overall_layout.addWidget(self.title_bar_widget)
    def set_main(self):
        """创建标题栏下主内容"""
        def set_main_mid():
            def style_title_label():
                self.title_label.setStyleSheet(f"""
                                            background-color: rgba(0,0,0,0);
                                            font-family: '{self.config.get_set("1_4_settings/06")}', sans-serif;
                                            font-size: {self.config.get_set("1_4_settings/07")}px;
                                            font-weight: {Tool.get_font_weight("1_4_settings/08")};                        /* 粗细：可选 normal、bold 或数字 */
                                            color: rgba{self.config.get_set("1_4_settings/09")};
                                            """)
            def left_title_label_buts(but=None):
                if but:
                    but.setStyleSheet(f"""
                                    QPushButton {{
                                        background-color:transparent;
                                        border-radius: {self.config.get_set("1_4_settings/11")} px; 
                                        border: 0 px ;
                                    }}
                                    QPushButton:hover {{
                                        background-color: rgba{self.config.get_set("1_4_settings/12")};
                                        border-radius: {self.config.get_set("1_4_settings/11")}px; 
                                    }}
                                """)
            def toggle_mid_panel():
                if self.mid_panel_visible:
                    self.mid_widget.hide()
                else:
                    self.mid_widget.show()
                self.mid_panel_visible = not self.mid_panel_visible
            def on_file_single_clicked(item):
                data = item.data(256)
                print("[单击] 文件路径:", data)
            def on_file_double_clicked(item):
                data = item.data(256)
                ids = data["ids"]
                title = data["name"]
                path = data["path"]
                chulinerong = data["chulinerong"]
                if path:
                    update_register("current_page_id", ids)
                    title, widget = self.load_page(path)
                    self.add_page(title, widget,chulinerong)

                print("[双击] 打开文件:", data)
            def call_back(folder_name):
                if folder_name == "最小化":
                    self.mid_widget.hide()
                    self.mid_panel_visible = False

            # 标志记录当前状态
            self.mid_panel_visible = False
            self.mid_widget = QWidget()
            self.mid_widget.setStyleSheet(f"""
                            background-color: transparent;
                            border: 0px;
                            border-radius: 0 px;
                        """)
            self.mid_widget.setMinimumWidth(int(self.config.get_set("1_4_settings/02")))
            self.mid_panel = QVBoxLayout(self.mid_widget)
            self.mid_panel.setContentsMargins(0, 0, 0, 0)
            self.mid_panel.setSpacing(0)

            # 小标题栏容器
            title_bar = QWidget()
            STYLE = """
                            background-color: rgba{{1_4_settings/13:transparent}};
                            border: 0px;
                            border-radius: 0 px;
                            """
            ConfigStyleBinder.bind("(Style)-left_title_bar-(color)", title_bar, STYLE)
            title_layout = QHBoxLayout(title_bar)
            title_bar_widget_height =int(self.config.get_set("1_4_settings/04"))
            title_bar.setFixedHeight(title_bar_widget_height)
            side1 = int(self.config.get_set("1_4_settings/10"))
            side2 = int(self.config.get_set("1_4_settings/05"))
            title_layout.setContentsMargins(side1, side2,side1, side2)

            # 标题文本
            self.title_label = QLabel()
            style_title_label()
            ConfigStyleBinder.bind_function("(Function)-style_title_label-(color)", style_title_label)
            title_layout.addWidget(self.title_label)
            title_layout.addStretch()
            icon_paths = {
                "最小化": f"_internal/use_resource/{self.photo_path_root}/min.png"
            }
            content_height = title_bar_widget_height - side2 * 2
            for name, path in icon_paths.items():
                callback = partial(call_back, name)  # 给回调传 name，例如 “收件夹”
                but = Tool.add_image_button(title_layout, icon_path=path, icon_size=(content_height, content_height),callback=callback)
            left_title_label_buts(but)
            ConfigStyleBinder.bind_function("(Function)-left_title_label_buts-(color)", left_title_label_buts, but=but)
            # 添加到 mid_panel 顶部
            self.mid_panel.addWidget(title_bar)

            self.file_paths = []
            # 文件列表控件
            self.file_list = QListWidget()
            self.file_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.file_list.setFocusPolicy(Qt.NoFocus)
            STYLE = """
                QListWidget {
                        background-color:  rgba{{1_4_settings/15:(0,0,0,0)}};
                        padding: 0px;
                        }
                QListWidget::item{
                        background-color: rgba{{1_4_settings/19:(10,10,10,110)}};
                        border-radius: {{1_4_settings/23:8}}px;
                        padding: {{1_4_settings/16:10}}px {{1_4_settings/17:10}}px;
                    }
                QListWidget::item:hover {
                        background-color: rgba{{1_4_settings/20:(20,20,20,110)}};
                    }
                QListWidget::item:focus {
                        outline: none;
                    }
                QListWidget::item:selected {
                        background-color: rgba{{1_4_settings/21:(30,30,30,110)}};
                        border-radius: {{1_4_settings/23:8}}px;
                    }
                /* 滚动条整体 */
                QScrollBar:vertical {
                    width: {{1_4_settings/34:12}}px;                        /* 滚动条宽度 */
                    background: transparent;           /* 背景透明 */
                    margin: 0px 0px 0px 0px;           /* 上下左右间距 */
                    border-radius: {{1_4_settings/37:12}}px;
                    }
                
                /* 滑块 */
                QScrollBar::handle:vertical {
                    background: rgba{{1_4_settings/35:(150,150,150,120)}}; /* 滑块颜色 */
                    border-radius: {{1_4_settings/37:12}}px;
                    min-height: 0px;                  /* 最小高度 */
                    }
                QScrollBar::handle:vertical:hover {
                    background: rgba{{1_4_settings/36:(180,180,180,180)}}; /* 悬停颜色 */
                    }
                /* 上下按钮 (去掉) */
                QScrollBar::sub-line:vertical,
                QScrollBar::add-line:vertical {
                    height: 0px;
                    subcontrol-origin: margin;
                    }
                /* 滑块之外的区域 (去掉) */
                QScrollBar::add-page:vertical,
                QScrollBar::sub-page:vertical {
                    background: none;
                    }
                 """
            ConfigStyleBinder.bind("(Style)-file_list-(color)", self.file_list, STYLE)
            self.file_list.setSpacing(int(self.config.get_set("1_4_settings/22")))
            self.file_list.itemDoubleClicked.connect(on_file_double_clicked)
            self.mid_panel.addWidget(self.file_list)
            self.mid_widget.hide()
        def set_main_right():
            def set_little_title():
                self.tab_widgets = []
                self.little_titles_tab = []
                height = int(self.config.get_set("1_5_settings/03"))
                self.little_title_widget = QWidget()
                self.little_title_widget.setStyleSheet(f"""
                                            background-color: transparent;
                                            border: 0px;
                                            border-radius: 0 px;
                                            padding: 0px;
                                        """)
                self.little_title_widget.setFixedHeight(height)  # 设置标题栏高度
                # 添加横向布局
                title_bar = QHBoxLayout(self.little_title_widget)
                title_bar.setContentsMargins(0, 0, 0, 0)
                title_bar.setSpacing(0)
                # --- 标签区域（可滚动） ---
                self.scroll_area = QScrollArea()
                STYLE ="""/* 横向滚动条 */
                    QScrollBar:horizontal {
                        height:{{1_5_settings/06:6}}px;
                        background: transparent;           /* 背景透明 */
                        margin: 0px 0px 0px 0px;           /* 上下左右间距 */
                        border-radius: {{1_5_settings/07:3}}px;
                    }
                    QScrollBar::handle:horizontal {
                        background: rgba{{1_5_settings/08:(159, 150, 150, 120)}};
                        border-radius: {{1_5_settings/07:3}}px;
                        min-width: 0px;
                    }
                    QScrollBar::handle:horizontal:hover {
                        background: rgba{{1_5_settings/09:(180,180,180,180)}};
                    }
                    QScrollBar::sub-line:horizontal,
                    QScrollBar::add-line:horizontal {
                        width: 0px;
                    }
                    QScrollBar::add-page:horizontal,
                    QScrollBar::sub-page:horizontal {
                        background: none;
                    }
                    """
                ConfigStyleBinder.bind("(Style)-little_title_widget_scroll_area-(color)", self.scroll_area, STYLE)
                self.scroll_area.setFixedHeight(height)
                self.scroll_area.setWidgetResizable(True)
                self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
                self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

                self.tab_container = QWidget()
                self.tab_layout = QHBoxLayout(self.tab_container)

                STYLE = """
                            background-color: rgba{{1_5_settings/02:transparent}};
                            border: 0px;
                            border-radius: 0 px;
                            padding: 0px;
                            """
                ConfigStyleBinder.bind("(Style)-tab_container-(color)", self.tab_container, STYLE)
                side1 = int(self.config.get_set("1_5_settings/04"))
                side2 = int(self.config.get_set("1_5_settings/05"))
                self.tab_layout.setContentsMargins(side1, side2, side1, side2)
                self.tab_layout.setSpacing(0)
                self.scroll_area.setWidget(self.tab_container)
                title_bar.addWidget(self.scroll_area)

                self.right_panel.addWidget(self.little_title_widget)
            def set_little_main():
                self.current_page = None
                self.little_main_widget = QStackedWidget()
                self.little_main_widget.setStyleSheet(f"""
                            background-color: transparent;
                            border: 0px;
                            border-radius: 0 px;
                """)
                self.little_main_widget.setMinimumWidth(self.width // 5)

                self.right_panel.addWidget(self.little_main_widget)

            self.right_widget = QWidget()
            self.right_widget.setStyleSheet(f"""
                            background-color: transparent;
                            border: 0px;
                            border-radius: 0 px;
                        """)
            self.right_panel = QVBoxLayout(self.right_widget)
            self.right_panel.setContentsMargins(0, 0, 0, 0)
            self.right_panel.setSpacing(0)

            set_little_title()
            set_little_main()

        # 这里采用布局嵌套布局
        self.content_layout = QHBoxLayout()

        set_main_mid()
        set_main_right()

        self.tab_layout.addStretch()

        # 创建画布大小修改条
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self.mid_widget)
        splitter.addWidget(self.right_widget)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 5)
        splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: rgba(255, 255, 255, 0);
                width: 0px;  /* 这里调节分割条宽度 */
                margin-left: 0px;
                margin-right: 0px;
            }
        """)
        self.content_layout.addWidget(splitter)
        self.overall_layout.addLayout(self.content_layout)

    def shuxin_FileListItem(self, new_title: str, new_files: dict,lists=[]):
        for i in lists:
            i.FileListItem_title_label()
        self.update_title_and_file_list(new_title,new_files)
    def update_title_and_file_list(self, new_title: str, new_files: dict):

        """外部调用：更新标题栏和文件列表"""
        if not self.mid_panel_visible:
            self.mid_widget.show()
            self.mid_panel_visible = not self.mid_panel_visible
        self.little_ji = new_title
        self.title_label.setText(new_title)
        # 清空原有文件列表
        self.file_list.clear()
        lists = []
        if new_files:
            self.file_paths = new_files.copy()
            for ids, info_list in self.file_paths.items():
                if len(info_list) != 4:
                    continue  # 或 raise 错误

                name, path, chulinerong, summary = info_list
                item = QListWidgetItem()

                self.file_list.addItem(item)
                widget = FileListItem(name, summary, self.config, code=ids)  # 传入 [标题, 时间, 摘要]
                self.file_list.setItemWidget(item, widget)
                item.setSizeHint(widget.sizeHint())  # 设置 item 推荐大小
                item.setData(Qt.UserRole, {"ids":ids,"path": path, "name": name,"chulinerong":chulinerong})
                lists.append(widget)
        ConfigStyleBinder.bind_function("(Function)-shuxin_FileListItem-(color)", self.shuxin_FileListItem, new_title=new_title, new_files=new_files, lists=lists)

    def add_page(self, title, widget,chulinerong):
        def set_right_title_button(tbuts={}):
            for i in tbuts:
                tbuts[i].setStyleSheet(f"""
                    QLabel {{
                        background: rgba{self.config.get_set("1_5_settings/20")};
                        border: 0px;
                        border-radius: {self.config.get_set("1_5_settings/12")}px;
                        padding: {self.config.get_set("1_5_settings/13")}px {self.config.get_set("1_5_settings/14")}px;

                        font-family: '{self.config.get_set("1_5_settings/15")}', sans-serif;
                        font-size: {self.config.get_set("1_5_settings/16")}px;
                        font-weight: {Tool.get_font_weight("1_5_settings/17")};
                        color: rgba{self.config.get_set("1_5_settings/18")};  
                    }}
                    QLabel:hover {{
                            border-radius: {self.config.get_set("1_5_settings/12")}px;
                            background: rgba{self.config.get_set("1_5_settings/19")};
                    }}
                """)
        def set_current_page(widget):
            self.little_main_widget.setCurrentWidget(widget)
        def close_page(widget):
            if widget:
                self.little_main_widget.removeWidget(widget)
                widget.deleteLater()
        def clear_tabs():
            # 遍历保存的 tab
            for tab in self.little_titles_tab:
                self.tab_layout.removeWidget(tab)  # 从布局里移除
                tab.deleteLater()
            # 清空列表
            self.little_titles_tab.clear()
        def tab_callback(item):
            t = item.text
            if t == "退出":
                self.current_page.save_all()
                clear_tabs()
                close_page(self.current_page)
                self.current_page =None
            elif t == "收起卡片":
                if title == "每日记账":
                    newtext = self.current_page.card_state()
                    item.update_text(newtext)
                print(title,t)

        if self.current_page != widget:
            last_widget = self.current_page
            self.current_page = widget
            close_page(last_widget)
            clear_tabs()
            self.little_main_widget.addWidget(widget)
            tbuts = {}
            for i,item in enumerate(chulinerong):
                tab = title_button(item,self.tab_container)
                tab.mousePressEvent = lambda e, b=tab: tab_callback(b)
                self.tab_layout.insertWidget(i, tab)
                self.little_titles_tab.append(tab)
                tbuts[i] = tab
            set_right_title_button(tbuts)
            ConfigStyleBinder.bind_function("(Function)-set_right_title_button-(color)", set_right_title_button, tbuts=tbuts)
            set_current_page(widget)
        else:
            widget.deleteLater()
    def mousePressEvent(self, event):
        def _in_titlebar(pos):
            # 判断是否在你自己定义的标题栏区域，比如前 40 像素
            return pos.y() <= self.height // 20

        if event.button() == Qt.LeftButton and _in_titlebar(event.pos()):
            self._drag_active = True
            # 注意用 globalPos() 减去主窗口的位置
            self._drag_start_pos = event.globalPos() - self.parent.frameGeometry().topLeft()
    def mouseMoveEvent(self, event):
        if self._drag_active:
            self.parent.move(event.globalPos() - self._drag_start_pos)
    def mouseReleaseEvent(self, event):
        self._drag_active = False


class TabButton(QWidget):
    def __init__(self, title, on_switch, on_close, config):
        super().__init__()
        self.config = config
        layout = QHBoxLayout(self)
        layout.setContentsMargins(int(self.config.get_set("1_2_1_5_settings/14")),
                                  int(self.config.get_set("1_2_1_5_settings/15")),
                                  int(self.config.get_set("1_2_1_5_settings/16")),
                                  int(self.config.get_set("1_2_1_5_settings/17")))
        layout.setSpacing(int(self.config.get_set("1_2_1_5_settings/18")))
        self.setStyleSheet(f"""
                        font-family: '{self.config.get_set("1_2_1_5_settings/06.2")}', sans-serif; /* 字体 */
                        font-size: {self.config.get_set("1_2_1_5_settings/06.4")}px;
                        font-weight: {self.config.get_set("1_2_1_5_settings/06.3")};
                    """)

        self.label_btn = QPushButton(title)
        self.label_btn.clicked.connect(on_switch)

        self.close_btn = QPushButton("×")
        # self.close_btn.setFixedWidth(12)
        self.close_btn.clicked.connect(on_close)

        layout.addWidget(self.label_btn)
        layout.addWidget(self.close_btn)

    def set_active(self, active: bool):
        if active:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: rgba{self.config.get_set("1_2_1_5_settings/23")};
                    color: rgba{self.config.get_set("1_2_1_5_settings/24")};
                    border-radius: {self.config.get_set("1_2_1_5_settings/25")}px;
                    padding: {self.config.get_set("1_2_1_5_settings/26")};
                }}
                QPushButton:hover {{
                    background-color: rgba{self.config.get_set("1_2_1_5_settings/27")};
                    color:rgba{self.config.get_set("1_2_1_5_settings/28")};
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: rgba{self.config.get_set("1_2_1_5_settings/30")};
                    color: rgba{self.config.get_set("1_2_1_5_settings/31")};
                    border-radius: {self.config.get_set("1_2_1_5_settings/32")}px;
                    padding: {self.config.get_set("1_2_1_5_settings/33")};
                }}
                QPushButton:hover {{
                    background-color: rgba{self.config.get_set("1_2_1_5_settings/34")};
                    color:rgba{self.config.get_set("1_2_1_5_settings/35")};
                }}
            """)
class FileListItem(QWidget):
    def __init__(self, title, summary, config, code=None):
        super().__init__()
        self.config = config
        self.code = code
        self.setStyleSheet(f"""background-color: rgba{self.config.get_set("1_2_1_4_settings/47")};""")

        # 垂直布局
        layout = QVBoxLayout(self)
        layout.setSpacing(int(self.config.get_set("1_2_1_4_settings/42")))
        side = int(self.config.get_set("1_2_1_4_settings/43"))
        layout.setContentsMargins(side, side, side, side)

        self.title_label = QLabel(title)
        layout.addWidget(self.title_label)
        # 摘要
        self.summary_label = ElidedLabel(summary)
        self.summary_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        layout.addWidget(self.summary_label)
        self.FileListItem_title_label()

    def FileListItem_title_label(self):
        self.title_label.setStyleSheet(f"""
                                font-family: '{self.config.get_set("1_4_settings/25")}', sans-serif; /* 字体 */
                                font-size: {self.config.get_set("1_4_settings/26")}px;
                                font-weight: {Tool.get_font_weight("1_4_settings/27")};                        /* 粗细：可选 normal、bold 或数字 */
                                color: rgba{self.config.get_set("1_4_settings/28")};
                                line-height: {float(self.config.get_set("1_4_settings/26"))*2}px;   /* 行高 */
                                """)
        self.summary_label.setStyleSheet(f"""
                                font-family: '{self.config.get_set("1_4_settings/29")}', sans-serif; /* 字体 */
                                font-size: {self.config.get_set("1_4_settings/30")}px;
                                font-weight: {Tool.get_font_weight("1_4_settings/31")};                        /* 粗细：可选 normal、bold 或数字 */
                                color: rgba{self.config.get_set("1_4_settings/32")};
                                """)

class ElidedLabel(QLabel):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self._full_text = text
        self.setWordWrap(False)

    def setText(self, text):
        self._full_text = text
        self.updateElidedText()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.updateElidedText()

    def updateElidedText(self):
        if not self._full_text:
            super().setText("")
            return

        metrics = QFontMetrics(self.font())
        elided = metrics.elidedText(self._full_text, Qt.ElideRight, self.width())
        super().setText(elided)
        # self.setToolTip(self._full_text)
class title_button(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.text = text
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        # 🔑 设置文本水平、垂直居中
        self.setAlignment(Qt.AlignCenter)

    def update_text(self, new_text: str):
        """修改当前的文本"""
        self.setText(new_text)