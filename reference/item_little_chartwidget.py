import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QCheckBox, QLabel, QListWidget, QSizePolicy, QSpacerItem, QToolTip
)
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from tool_global_registry import register, registry,update_register,add_register
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from page_select_MainDataSelector import MainDataSelector
from json_manager import JsonManager
from page_tip import tipWindow
from tool_get_data_witn_point import BillingAnalytics
from tools import Tool
from page_chuli_list import chuli_listtWindow
import random
content_data = JsonManager("_internal/jsons/content_data.json")

# ✅ 设置中文字体和负号显示
plt.rcParams['font.sans-serif'] = ['SimHei']   # 支持中文（黑体）
plt.rcParams['axes.unicode_minus'] = False     # 正确显示负号

class littleChartWidget(QWidget):
    def __init__(self, parent=None,id=""):
        super().__init__(parent)
        self.id = id
        self.main_date = content_data.get("chart_page_main")
        # ====== 主布局 ======
        main_layout = QHBoxLayout(self)
        # ====== 中间：matplotlib 图表 ======
        self.figure = Figure(figsize=(5, 4))
        self.canvas = FigureCanvas(self.figure)
        self.figure.patch.set_facecolor("lightgray")  # 整个 figure 背景
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_xlabel("日期")
        self.ax.set_ylabel("取值")
        self.curves = {}  # 保存曲线对象，key=id
        self.tuli = {}
        self.fu_quxian = []
        self.used_colors = set()  # 已用颜色
        # 绑定鼠标移动事件
        self.canvas.mpl_connect("motion_notify_event", self.on_hover)
        main_layout.addWidget(self.canvas, 8)

        self.generate_plot_data()


    def on_hover(self, event):
        if event.inaxes != self.ax:
            return

        for curve_id, line in self.curves.items():
            cont, ind = line.contains(event)  # 检查是否命中点
            if cont:
                i = ind["ind"][0]  # 点的索引
                xdata, ydata = line.get_data()
                x_val, y_val = xdata[i], ydata[i]
                # 显示 tooltip
                QToolTip.showText(
                    self.mapToGlobal(self.canvas.pos()) + event.guiEvent.pos(),
                    f"日期: {x_val}\n取值: {y_val}\nid:{curve_id}"
                )
                return

        # 鼠标不在任何点上时，隐藏 tooltip
        QToolTip.hideText()
    def chuli_guanli(self):
        def callback(data):
            for i in ins:
                if i not in data:
                    self.remove_curve(self.fu_quxian[duizhao[i]])


        ins = []
        duizhao = {}
        for n,i in enumerate(self.fu_quxian):
            name = self.tuli[i].text
            re = f"{i}/{name}"
            duizhao[re] = n
            ins.append(re)
        tip = add_register("child_window", chuli_listtWindow(parent=registry["main_window"]
                                                            , title=f"管理辅助数据", callback=callback, content=ins))
        tip.exec_()
    def chuli_main(self):
        def callback(text):
            self.main_date = text
            self.generate_plot_data(text,name="main_curve")
        if "main_curve" in self.curves:
            self.tip_tip("主曲线已存在，请清除数据后，再尝试！")
        else:
            tip = add_register("child_window", MainDataSelector(parent=registry["main_window"]
                                                             , title=f"主数据选择", callback=callback,name="chart_page_main"))
            tip.exec_()
    def chuli_add(self):
        def callback(text):
            self.add_date = text
            self.generate_plot_data(text)
        tip = add_register("child_window", MainDataSelector(parent=registry["main_window"]
                                                         , title=f"辅数据选择", callback=callback,name="chart_page_add",add= [True,self.main_date]))
        tip.exec_()
    def _get_random_color(self):
        """生成随机颜色，确保不重复"""
        while True:
            color = "#{:06x}".format(random.randint(0, 0xFFFFFF))
            if color not in self.used_colors:
                self.used_colors.add(color)
                return color

    def add_curve(self, curve_id, xy_data, color=None):
        """
        添加曲线
        支持两种输入：
        1. xy_data = [(x1, y1), (x2, y2), ...]
        2. xy_data = {"x": [...], "y": [...]} 或 {"profit": [(1, v1), (2, v2), ...]}
        """
        if curve_id in self.curves:
            self.remove_curve(curve_id)

        if color is None:
            color = self._get_random_color()

        x, y = [], []
        # 🔹情况1: 直接是 (x,y) 对列表
        if isinstance(xy_data, list):
            x, y = zip(*xy_data) if xy_data else ([], [])

        # 🔹情况2: dict 包含 "x" 和 "y"
        elif isinstance(xy_data, dict) and "x" in xy_data and "y" in xy_data:
            x, y = xy_data["x"], xy_data["y"]

        # 🔹情况3: dict 只有一个 key，值是 (x,y) 列表
        elif isinstance(xy_data, dict) and len(xy_data) == 1:
            data_list = list(xy_data.values())[0]
            x, y = zip(*data_list) if data_list else ([], [])


        line, = self.ax.plot(x, y, color=color, marker="o")
        self.curves[curve_id] = line
        self.canvas.draw()

    def remove_curve(self, curve_id):
        """删除曲线"""
        if curve_id not in self.curves:
            return
        line = self.curves.pop(curve_id)
        self.used_colors.discard(line.get_color())  # 释放颜色
        line.remove()
        self.canvas.draw()
    def chuli_clerr(self):
        nedd_clear = self.fu_quxian
        nedd_clear.append("main_curve")
        for i in nedd_clear:
            self.remove_curve(i)
        self.fu_quxian = []
        self.ax.clear()  # 清空整个坐标轴
        self.curves.clear()
    def generate_plot_data(self,name="main_line"):
        full_data = registry["data_libary"].get_shopper_prices_by_date(self.id)
        print("数据:", full_data)
        self.add_curve(name, full_data)

    def fill_xy_data(self,x_axis, series_dict):
        """
        补全 series_dict 中每条曲线的数据，让每个 x 轴都有值，没有的填 0
        - x_axis: ['2024-09', '2024-10', ...]  # 完整的 X 轴
        - series_dict: {'profit': [('2025-05', 17310.0), ('2025-06', 19275.0), ...]}

        返回新的 series_dict，保证每条曲线的 x 都等于 x_axis
        """
        filled_series = {}
        for key, xy_list in series_dict.items():
            # 先把已有数据转换成字典便于查找
            xy_map = dict(xy_list)
            # 补全
            new_xy_list = [(x, xy_map.get(x, 0)) for x in x_axis]
            filled_series[key] = new_xy_list
        return filled_series
    def tip_tip(self,text):
        tip = add_register("child_window",tipWindow(registry["main_window"],text))
        tip.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = DynamicChartWidget()
    w.resize(900, 600)
    w.show()
    sys.exit(app.exec_())
