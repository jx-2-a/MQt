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
class LegendLine(QWidget):
    """单个图例项：一条彩色线 + 文本"""
    def __init__(self, color: QColor, text: str, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        self.text = text

        # 彩色线条
        self.color = color
        self.line_widget = QWidget()
        self.line_widget.setFixedHeight(2)
        self.line_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.line_widget.setMinimumWidth(30)
        self.line_widget.paintEvent = self.paint_line
        layout.addWidget(self.line_widget, 1)

        # 文本
        self.label = QLabel(text)
        layout.addWidget(self.label, 0)

    def paint_line(self, event):
        painter = QPainter(self.line_widget)
        pen = QPen(self.color, 2)
        painter.setPen(pen)
        painter.drawLine(0, event.rect().center().y(), event.rect().width(), event.rect().center().y())
class LegendWidget(QWidget):
    """图例容器"""
    def __init__(self, parent=None):
        super().__init__(parent)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 100, 10, 10)

        # 上部占位
        # main_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        # 标题
        title = QLabel("图例")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        main_layout.addWidget(title)

        # 图例项布局
        self.legend_layout = QVBoxLayout()
        self.legend_layout.setSpacing(8)
        main_layout.addLayout(self.legend_layout)

        # 下部占位
        # main_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        main_layout.addStretch(10)
    def add_legend_item(self, color: QColor, text: str):
        item = LegendLine(color, text)
        self.legend_layout.addWidget(item)
        return item

    def remove_legend_item(self, item: QWidget):
        """删除传入的 LegendLine item"""
        if item is not None:
            self.legend_layout.removeWidget(item)
            item.setParent(None)
            item.deleteLater()

    def clear_legend_items(self):
        """清空所有图例项"""
        while self.legend_layout.count():
            item = self.legend_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)
                widget.deleteLater()
class DynamicChartWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_date = content_data.get("chart_page_main")
        # ====== 主布局 ======
        main_layout = QHBoxLayout(self)

        # ====== 左边：图例区 ======
        self.legend = LegendWidget()
        main_layout.addWidget(self.legend,1)

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

        # ====== 右边：按钮区 ======
        button_layout = QVBoxLayout()
        button_layout.setContentsMargins(10,100,10,10)
        self.btn_main = QPushButton("选择主数据")
        self.btn_add = QPushButton("添加对比")
        self.btn_manage = QPushButton("管理对比")
        self.btn_replace = QPushButton("清除数据")

        button_layout.addWidget(self.btn_main)
        self.btn_main.clicked.connect(self.chuli_main)
        button_layout.addWidget(self.btn_add)
        self.btn_add.clicked.connect(self.chuli_add)

        button_layout.addWidget(self.btn_manage)
        self.btn_manage.clicked.connect(self.chuli_guanli)
        button_layout.addWidget(self.btn_replace)
        self.btn_replace.clicked.connect(self.chuli_clerr)
        button_layout.addStretch()
        main_layout.addLayout(button_layout, 1)

        # ====== 示例：画一条线 ======
        # self.add_curve("c1", "曲线1", [(0,0),(1,1),(2,4)], color="red")

    def on_hover(self, event):
        if event.inaxes != self.ax:
            return

        for curve_id, line in self.curves.items():
            cont, ind = line.contains(event)  # 检查是否命中点
            if cont:
                i = ind["ind"][0]  # 点的索引
                xdata, ydata = line.get_data()
                x_val, y_val = xdata[i], ydata[i]
                name = self.tuli[curve_id].text
                # 显示 tooltip
                QToolTip.showText(
                    self.mapToGlobal(self.canvas.pos()) + event.guiEvent.pos(),
                    f"{name}\n日期: {x_val}\n取值: {y_val}\nid:{curve_id}"
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

    def add_curve(self, curve_id, label, xy_data, color=None):
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
        jilu = self.legend.add_legend_item(QColor(color), label)
        self.tuli[curve_id] =jilu
        self.curves[curve_id] = line
        self.canvas.draw()

    def remove_curve(self, curve_id):
        """删除曲线"""
        if curve_id not in self.curves:
            return
        line = self.curves.pop(curve_id)
        self.used_colors.discard(line.get_color())  # 释放颜色
        line.remove()
        self.legend.remove_legend_item(self.tuli[curve_id])
        self.canvas.draw()
    def chuli_clerr(self):
        nedd_clear = self.fu_quxian
        nedd_clear.append("main_curve")
        for i in nedd_clear:
            self.remove_curve(i)
        self.fu_quxian = []
        self.ax.clear()  # 清空整个坐标轴
        self.curves.clear()
    def generate_plot_data(self,params,name=""):
        chuandi ={"客户":"customer_name","支付方式": "payment_method", "日期": "date",
                         "服务内容": "service", "备注": "note","收费":"fee","成本":"cost","利润":"profit"}
        label = params["mobiao"]
        params["mobiao"]=chuandi[label]
        analytics = BillingAnalytics("_internal/data/all.db")
        labels, series = analytics.aggregate(**params)
        full_data = self.fill_xy_data(labels, series)
        print("数据:", full_data)
        for n,i in enumerate(full_data):
            if label not in chuandi or i != chuandi[label]:
                label = i
            if n == 0 and name:
                self.add_curve(name, label, full_data[i])
            else:
                name = Tool.generate_random_string(10)
                self.fu_quxian.append(name)
                self.add_curve(name,label,full_data[i])

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
