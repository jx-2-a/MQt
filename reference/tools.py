from PyQt5.QtWidgets import (
    QSplitter,QListWidget, QListWidgetItem,QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QScrollArea, QTextEdit, QFrame,QApplication
)
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QSize
import json
from json_manager import JsonManager
from datetime import datetime
config = JsonManager("_internal/jsons/setting.json")
import random
import string
import shutil
import os

class Tool:
    @staticmethod
    def to_bool(s):
        if s== "True"or s=="true":
            return True
        else:
            return False
    @staticmethod
    def add_image_button(parent_layout, icon_path, icon_size=(32, 32),callback=None
                         ):
        """动态创建一个带图标的按钮并添加到指定布局"""
        btn = QPushButton()
        btn.setIcon(QIcon(QPixmap(icon_path)))
        btn.setIconSize(QSize(*icon_size))
        btn.setFixedSize(QSize(icon_size[0], icon_size[1]))  # 给按钮外框一些边距
        # btn.setStyleSheet(f"""
        #         QPushButton {{
        #             background-color:rgba{b_color};
        #             color: rgba{f_color};
        #             border: {side}px ;
        #         }}
        #         QPushButton:hover {{
        #             background-color: rgba{in_bcolor};
        #             color: rgba{in_fcolor};
        #         }}
        #     """)
        if callback:
            btn.clicked.connect(callback)  # 可选的点击事件处理器
        parent_layout.addWidget(btn)
        return btn

    @staticmethod
    def add_text_button(parent_layout, text, callback=None, side=0, b_color=(0, 0, 0, 0),
                         f_color=(255, 255, 255, 255), in_bcolor=(255, 0, 0, 255),
                         in_fcolor=(255, 0, 0, 255)
                         ):
        """动态创建一个带图标的按钮并添加到指定布局"""
        btn = QPushButton(text)
        btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color:rgba{b_color};
                        color: rgba{f_color};
                        border: {side}px ;
                    }}
                    QPushButton:hover {{
                        background-color: rgba{in_bcolor};
                        color: rgba{in_fcolor};
                    }}
                """)

        if callback:
            btn.clicked.connect(callback)  # 可选的点击事件处理器
        parent_layout.addWidget(btn)
        return btn


    @staticmethod
    def get_nome_time(z = False):
        now = datetime.now()
        new_time_str = now.strftime("%Y-%m-%d %H:%M:%S")
        if z:
            return "当前时间："+new_time_str
        else:
            return new_time_str

    @staticmethod
    def get_nome_date(z=False):
        now = datetime.now()
        new_date_str = now.strftime("%Y-%m-%d")  # 只保留年月日
        if z:
            return "当前日期：" + new_date_str
        else:
            return new_date_str

    @staticmethod
    def generate_random_string(length=20):
        chars = string.ascii_letters + string.digits  # 包括大小写字母和数字
        return ''.join(random.choices(chars, k=length))
    @staticmethod
    def del_file(full_path):
        try:
            os.remove(full_path)
            print(f"已删除文件: {full_path}")
        except Exception as e:
            print(f"删除失败: {full_path}，错误: {e}")

    @staticmethod
    def del_in_path(folder_path):
        """
           删除指定文件夹下的所有内容（包括子文件夹和文件），但保留该文件夹本身。
           """
        if not os.path.exists(folder_path):
            print(f"路径不存在：{folder_path}")
            return

        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            try:
                if os.path.isfile(item_path) or os.path.islink(item_path):
                    os.remove(item_path)
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
            except Exception as e:
                print(f"无法删除：{item_path}，错误：{e}")
    @staticmethod
    def get_filename_with_extension(path: str) -> str:
        return os.path.basename(path)

    @staticmethod
    def get_font_weight(path):
        if config.get_set(path):
            return "bold"
        else:
            return "normal"

if __name__ == "__main__":
    a = Tool.generate_random_string(10)
    print(a)
