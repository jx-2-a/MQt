from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QApplication
)
import re
from PyQt5.QtCore import Qt
from item_card import SummaryCard,CardContainer
from item_excel import TableWidget
import sys
from json_manager import JsonManager
import traceback
from tool_config_style_binder import ConfigStyleBinder
from page_edit import EditTextWindow
from page_select_kehu import UserSearchWindow
from page_select_shangpin import spSearchWindow
from page_heards_set import heards_Window
from page_card_set import cards_Window
from tool_global_registry import register, registry,update_register,add_register
from tools import Tool
from page_edit_select import EditTextWindow_add
from tool_formula_calculator import FormulaCalculator
config = JsonManager("_internal/jsons/setting.json")
content_data = JsonManager("_internal/jsons/content_data.json")

def excepthook(exc_type, exc_value, exc_tb):
    traceback.print_exception(exc_type, exc_value, exc_tb)
sys.excepthook = excepthook

class MyTableWidget(TableWidget):
    def __init__(self, headers,parent=None, allow_add_row=True):
        self.need_bang_col = []
        self.todate = []
        self.kehu = {}
        self.last_gaoliang = None
        super().__init__(headers,parent,allow_add_row)
        if registry["current_page_id"] == "5IbCZ8Z5ZN":
            self.get_today()
        elif registry["current_page_id"] == "25wLSppHzL":
            self.get_baoxiujil()
        elif registry["current_page_id"] == "9eDvzcwp2o":
            self.get_shangpinjil()
        elif registry["current_page_id"] == "o9GjUsU6V3":
            self.get_daoju()

        self.headers = headers
        self.headers_settings = {}
        self.names = {}
        self.need_jsiuan = {}
        self.need_lianjie = {}
        self.lianjie_data = {}
        self.load_heards()
    def get_baoxiujil(self):
        def get_inform(today):
            self.todate = registry["data_libary"].get_day_warranty_card(self.nome_date)
            for i, u in enumerate(self.todate):
                row_values = [
                    str(i + 1),
                    str(u.get("date", "")),
                    str(u.get("customer_name", "")),
                    str(u.get("product", "")),
                    str(u.get("product_id", "")),
                    str(u.get("start", "")),
                    str(u.get("long", "")),
                    str(u.get("end", "")),
                    str(u.get("state", "")),
                    str(u.get("note", ""))
                ]
                self.on_add_new_row(row_values)

        self.heards_duizhao = ["", "date", "customer_name", "product", "product_id",
                               "start", "long", "end", "state","note"]
        self.spath = "baoxiujil"
        self.nome_date = Tool.get_nome_date()
        self.on_add_new_row(self.headers)
        get_inform(self.nome_date)
    def get_daoju(self):
        def get_inform(today):
            self.todate = registry["data_libary"].get_day_daojus(self.nome_date)
            for i, u in enumerate(self.todate):
                row_values = [
                    str(i + 1),
                    str(u.get("date", "")),
                    str(u.get("shopper_name", "")),
                    str(u.get("shopper_jia_name", "")),
                    str(u.get("fenlei", "")),
                    str(u.get("jiage", "")),
                    str(u.get("laiyuan", "")),
                    str(u.get("how_use", "")),
                    str(u.get("note", ""))
                ]
                self.on_add_new_row(row_values)

        self.heards_duizhao = ["", "date", "shopper_name", "shopper_jia_name", "fenlei",
                               "jiage", "laiyuan","how_use", "note"]
        self.spath = "daoju"
        self.nome_date = Tool.get_nome_date()
        self.on_add_new_row(self.headers)
        get_inform(self.nome_date)
    def get_shangpinjil(self):
        def get_inform(today):
            self.todate = registry["data_libary"].get_day_shoppingss(self.nome_date)
            for i, u in enumerate(self.todate):
                row_values = [
                    str(i + 1),
                    str(u.get("date", " ")),
                    str(u.get("shopper_name", " ")),
                    str(u.get("xinghao", " ")),
                    str(u.get("shopper_jia_name", " ")),
                    str(u.get("fenlei", " ")),
                    str(u.get("jiage", " ")),
                    str(u.get("laiyuan", " ")),
                    str(u.get("note", " "))
                ]
                self.on_add_new_row(row_values)

        self.heards_duizhao = ["", "date", "shopper_name","xinghao","shopper_jia_name", "fenlei",
                               "jiage", "laiyuan","note"]
        self.spath = "shoppings"
        self.nome_date = Tool.get_nome_date()
        self.on_add_new_row(self.headers)
        get_inform(self.nome_date)
    def bangding_(self,col,cards):
        for row in self.rows:
            row.cells[col].textChanged.connect(cards.jisuan)
    def bangding_dan(self,item,i):
        for shuzu in self.need_bang_col:
            if i == shuzu[0]:
                item.textChanged.connect(shuzu[1].jisuan)
                shuzu[1].jisuan("",i)
    def get_today(self):
        def get_inform(today):
            self.todate = registry["data_libary"].get_day_billings(self.nome_date)
            for i,u in enumerate(self.todate):
                row_values = [
                    str(i + 1),
                    str(u.get("date", "")),
                    str(u.get("customer_name", "")),
                    str(u.get("service", "")),
                    str(u.get("fee", "")),
                    str(u.get("cost", "")),
                    str(u.get("profit", "")),
                    str(u.get("payment_method", "")),
                    str(u.get("note", ""))
                ]
                self.on_add_new_row(row_values)
        self.heards_duizhao = ["","date","customer_name","service","fee",
                               "cost","profit","payment_method","note",]
        self.spath = "today_datd"
        self.nome_date = Tool.get_nome_date()
        self.on_add_new_row(self.headers)
        get_inform(self.nome_date)
    def save_today_data(self):
        registry["data_libary"].save_day_billings(self.todate)

    def get_row_text(self,row):
        """获取单行的文本,更新记录中此行内容"""
        results = []
        for i,item in enumerate(row.cells):
            result = item.text()
            results.append(item.text())
            self.bangding_dan(item,i)

            if self.heards_duizhao[i]:
                self.todate[row.now_rows-1][self.heards_duizhao[i]] = result

        print(row.jilu_id, "行id")
        if self.spath == "today_datd":
            self.todate[row.now_rows - 1]["customer_id"] = row.jilu_id["customer_id"]
        elif self.spath == "baoxiujil":
            self.todate[row.now_rows - 1]["customer_id"] = row.jilu_id["customer_id"]
        elif self.spath == "shoppings":
            self.todate[row.now_rows - 1]["shopper_id"] = row.jilu_id["shopper_id"]
        elif self.spath == "daoju":
            self.todate[row.now_rows - 1]["shopper_id"] = row.jilu_id["shopper_id"]

    def save_all(self):
        if self.spath == "today_datd":
            self.save_today_data()
        elif self.spath == "baoxiujil":
            registry["data_libary"].save_day_warranty_card(self.todate)
        elif self.spath == "shoppings":
            registry["data_libary"].save_day_shoppingss(self.todate)
        elif self.spath == "daoju":
            registry["data_libary"].save_day_daojus(self.todate)

    def add_to_jilu(self):
        """
        向值记录数组中添加空占位数据
        """
        if self.spath == "today_datd":
            self.todate.append({
                "id": " ",
                "customer_id": " ",
                "customer_name": " ",
                "date": " ",
                "service": " ",
                "fee": " ",
                "cost": " ",
                "profit": " ",
                "payment_method": " ",
                "note": " "
            })
        elif self.spath == "baoxiujil":
            self.todate.append({
                "id": " ",
                "customer_id":" ",
                "customer_name": " ",
                "date": " ",
                "product": " ",
                "product_id": " ",
                "start": " ",
                "long": " ",
                "end":" ",
                "state": " ",
                "note": " "
            })
        elif self.spath == "shoppings":
            self.todate.append({
                "id": " ",
                "shopper_id": " ",
                "shopper_name": " ",
                "xinghao":" ",
                "date": " ",
                "shopper_jia_name":" ",
                "fenlei": " ",
                "jiage": " ",
                "laiyuan": " ",
                "note": " "
            })
        elif self.spath == "daoju":
            self.todate.append({
                "id": " ",
                "shopper_id": " ",
                "shopper_name": " ",
                "date": " ",
                "shopper_jia_name":" ",
                "fenlei": " ",
                "jiage": " ",
                "laiyuan": " ",
                "how_use":" ",
                "note": " "
            })

    def load_heards(self):
        self.config = content_data
        for id in self.headers:
            path = registry["current_page_id"] + "_heards" + id
            had = self.config.deep_check(path)
            if had:
                self.headers_settings[id] = self.config.get(path)
            else:
                self.headers_settings[id] = self.config.get("moren_heards")
        self.goujianjisuanshi()
    def goujianjisuanshi(self):
        get_jisuanshi = False
        get_lianjie = False
        name = None
        for i ,item in enumerate(self.headers_settings):
            for n,tset in enumerate(self.headers_settings[item]):
                sett = self.headers_settings[item][tset]
                if sett["label"] == "名称:":
                    name = sett["default"]
                    if not name:
                        name = f"第{i}列"
                    self.names[name] = i
                elif sett["label"] == "内容来源:" and sett["default"] == "自动计算":
                    get_jisuanshi = True
                elif sett["label"] == "内容来源:" and sett["default"] == "数据关联":
                    get_lianjie = True
                elif sett["label"] == "若计算，则计算公式:" and get_jisuanshi:
                    self.need_jsiuan[name] = sett["default"]
                    get_jisuanshi = False
                elif sett["label"] == "若关联，则关联地址:" and get_lianjie:
                    self.need_lianjie[name] = sett["default"]
                    get_lianjie = False

    def get_cell(self,row, col):
        hang = self.rows[row-1]
        item = hang.cells[col]
        result = item.text()
        if result and result!=" ":
            return result
        else:
            return "0"
    def set_cell(self,row, col,text):
        hang = self.rows[row-1]
        item = hang.cells[col]
        item.setText(text)
        self.adjust_min_width(item, text, col)
        self.get_row_text(hang)
        self.check_jisuan(row, col)
    def calc_formula(self, row, jisuanshi,jisuan = True):
        if jisuan :
            Calculator = FormulaCalculator(parent=self)
            result = Calculator.calc_formula(row, jisuanshi)
        else:
            vars_in_formula = re.findall(r"\[(.*?)\]", jisuanshi)
            for i,var in enumerate(vars_in_formula):
                if i ==0:
                    pass
                else:
                    print(self.lianjie_data,"pppp")
                    if var  in self.lianjie_data:
                        result = self.lianjie_data[var]
                    else:
                        result = ""

        # 找出所有形如 [xxx] 的变量
        # vars_in_formula = re.findall(r"\[(.*?)\]", jisuanshi)
        #
        # # 替换变量
        # expr = jisuanshi
        # for var in vars_in_formula:
        #     if var not in self.names:
        #         raise ValueError(f"变量 {var} 未在 self.names 中定义")
        #     col = self.names[var]  # 获取列号
        #     val = self.get_cell(row, col)  # 假设你有这个函数来取表格数据
        #     expr = expr.replace(f"[{var}]", str(val))
        # print(expr)
        #
        # # ^ 替换成 **，符合 Python 语法
        # expr = expr.replace("^", "**")
        #
        # # 安全计算
        # try:
        #     result = eval(expr, {"__builtins__": None}, {})
        # except Exception as e:
        #     raise ValueError(f"公式计算出错: {e}")
        return result
    def zhuanhua_jisuan(self,row,key):
        jisuanshi = self.need_jsiuan[key]
        result = self.calc_formula(row, jisuanshi)
        col = self.names[key]
        self.set_cell(row,col,str(result))
    def zhuanhua_lianjie(self,row,key):
        jisuanshi = self.need_lianjie[key]
        print(jisuanshi)
        result = self.calc_formula(row, jisuanshi,False)
        col = self.names[key]
        self.set_cell(row,col,str(result))
    def get_col_data(self,col):
        data = []
        for row in self.rows:
            data.append(row.cells[col].text())
        return data
    def check_jisuan(self,row,col):
        changed_k = None
        for k, v in self.names.items():
            if v == col:
                changed_k = k
                break
        for k2,v2 in self.need_jsiuan.items():
            if changed_k in v2:
                self.zhuanhua_jisuan(row,k2)
        for k3,v3 in self.need_lianjie.items():
            if changed_k in v3:
                self.zhuanhua_lianjie(row,k3)

    def bind_funcation(self,row,i):
        for n, cell in enumerate(row.cells):
            cell.mousePressEvent = lambda e,b=cell, r=i,c=n: self.on_row_clicked(b,r,c)
            cell.mouseDoubleClickEvent = lambda e,b=cell, r=i,c=n: self.on_row_double_clicked(b,r,c)
    def on_row_clicked(self,button,row,col):
        if row>1:
            if self.last_gaoliang is not None:
                self.rows[self.last_gaoliang].set_highlight(False)
                self.last_gaoliang = row-1
                self.rows[row-1].set_highlight()
            else:
                self.last_gaoliang = row - 1
                self.rows[row-1].set_highlight()
    def on_row_double_clicked(self,button,row,col):
        print("双击",row,col)
        def get_laiyaun(col):
            data = self.headers_settings[self.headers[col]]
            for i in data:
                if data[i]["label"] == "内容来源:":
                    return data[i]["default"]

        def callback_edit(text,is_shuzhu = False,all_data={}):
            print("按键内容更该",text)
            self.lianjie_data = all_data
            if not is_shuzhu:
                if text:
                    button.setText(text)
                    self.adjust_min_width(button, text, col)
                    self.check_jisuan(row,col)
                    self.get_row_text(self.rows[row-1])
            else:
                if text:
                    button.setText(text[0])
                    self.adjust_min_width(button, text[0], col)
                    self.check_jisuan(row,col)
                    self.rows[row - 1].jilu_id[text[2]] = text[1]
                    self.get_row_text(self.rows[row-1])



        type_ = get_laiyaun(col)
        if row > 1:
            if type_ == "文本编辑":
                tip = add_register("child_window", EditTextWindow(parent=registry["main_window"]
                                                                  , title=f"编辑-第{row}行-{self.headers[col]}项", callback=callback_edit, content=button.text()))
                tip.exec_()
            elif type_ == "日期选择":
                tip = add_register("child_window", EditTextWindow(parent=registry["main_window"]
                                                                  , title=f"编辑-第{row}行-{self.headers[col]}项", callback=callback_edit, content=Tool.get_nome_time()))
                tip.exec_()
            elif type_ == "客户选择":
                tip = add_register("child_window", UserSearchWindow(parent=registry["main_window"]
                                                                    , title=f"选则-第{row}行-{self.headers[col]}项", callback=callback_edit, content=button.text()))
                tip.exec_()
            elif type_ == "选择编辑":
                tip = add_register("child_window", EditTextWindow_add(parent=registry["main_window"]
                                                                    , title=f"编辑-第{row}行-{self.headers[col]}项", callback=callback_edit, content=button.text(),duixiang =registry["current_page_id"]+self.headers[col]+"selects"))
                tip.exec_()
            elif type_ == "服务选择":
                tip = add_register("child_window", spSearchWindow(parent=registry["main_window"]
                                                                    , title=f"编辑-第{row}行-{self.headers[col]}项", callback=callback_edit, content=button.text()))
                tip.exec_()
            else:
                tip = add_register("child_window", EditTextWindow(parent=registry["main_window"]
                                                                  , title=f"编辑-第{row}行-{self.headers[col]}项", callback=callback_edit, content=button.text()))
                tip.exec_()
        else:
            tip = add_register("child_window", heards_Window(parent=registry["main_window"]
                                                              , title=f"控制表头-{self.headers[col]}项", callback=callback_edit, content=button.text()))
            tip.exec_()
class new_SummaryCard(SummaryCard):
    def __init__(self,parent=None, title="", value="0", min_width=300):
        self.parent = parent
        self.title = title
        self.get_setting()
        super().__init__(title,value,min_width)

    def get_setting(self):
        self.path = registry["current_page_id"] + "_cards" + self.title
        self.had = content_data.deep_check(self.path)
        if self.had:
            self.settings = content_data.get(self.path)
        else:
            self.settings = content_data.get("moren_cards")
        self.get_way_duix()
    def get_way_duix(self):
        self.duix = None
        self.way = None
        self.mubiao = None
        for i, item in enumerate(self.settings):
            sett = self.settings[item]
            if sett["label"] == "关联列:":
                self.duix = sett["default"]
            elif sett["label"] == "取值方式:":
                self.way = sett["default"]
            elif sett["label"] == "计数目标:":
                self.mubiao = sett["default"]

    def jisuan(self, text, col):
        result = 0
        data = self.parent.table.get_col_data(col)
        if self.way =="计数":
            for i in data:
                if i ==self.mubiao:
                    result +=1
        else:
            nums = []
            for x in data:
                x = str(x).strip()  # 去掉前后空格
                if not x:  # 如果是空字符串，跳过
                    continue
                try:
                    nums.append(float(x))  # 转换成数字
                except ValueError:
                    continue  # 如果不是数字，直接忽略

            if not nums:  # 如果没有有效数字
                result = ""
            elif self.way == "求和":
                result = sum(nums)
            elif self.way == "最大值":
                result = max(nums)
            elif self.way == "最小值":
                result = min(nums)
            else:
                raise ValueError(f"未知计算方式: {self.way}")

            # ✅ 直接更新控件，不 return
        self.setValue(str(result))

    def callback(self):
        print("p")
    def mouseDoubleClickEvent(self, event):
        # 这里写你的逻辑
        tip = add_register("child_window", cards_Window(parent=registry["main_window"]
                                                         , title=f"控制卡片-{self.title}项", callback=self.callback,content=self.title))
        tip.exec_()
        # super().mouseDoubleClickEvent(event)

class ea(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.card_show = True

        STYLE = """
            background-color: rgba{{1_6_1_settings/02:(20,20,20,100)}};
            border: 0px;
            border-radius: 0px;
                                """
        ConfigStyleBinder.bind("(Style)-ea_style-(color)", self, STYLE)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        headers = content_data.get(registry["current_page_id"] + "_heards",[])
        self.table = MyTableWidget(headers,allow_add_row=True)


        self.container = CardContainer()
        neirong = content_data.get(registry["current_page_id"] + "_cards")
        cads = []
        if neirong:
            for i in neirong:
                card = new_SummaryCard(self, i, "")
                cads.append(card)
                self.container.addCard(card)
        ConfigStyleBinder.bind_function("(Function)-reflash_cads-(color)", self.reflash_cads, cads=cads)
        self.check_need_connect()
        self.shauxin_cards()
        layout.addWidget(self.container)
        layout.addWidget(self.table)
    def check_need_connect(self):
        for i in self.container.cards:
            if i.duix:
                bangding_col = self.table.names[i.duix]
                self.table.need_bang_col.append((bangding_col,i))
                self.table.bangding_(bangding_col,i)
    def shauxin_cards(self):
        for i in self.container.cards:
            if i.duix:
                bangding_col = self.table.names[i.duix]
                print(bangding_col)
                i.jisuan("",bangding_col)


    def bind_funcation(self):
        # 绑定行点击事件（可选）
        for i, row in enumerate(self.table.rows):
            for n, cell in enumerate(row.cells):
                cell.mousePressEvent = lambda e,b=cell, r=i,c=n: self.on_row_clicked(b,r,c)
                cell.mouseDoubleClickEvent = lambda e,b=cell, r=i,c=n: self.on_row_double_clicked(b,r,c)

    def reflash_cads(self,cads=[]):
        for i in cads:
            i.set_SummaryCard_style()
    def clear(self):
        """清空所有内容"""
        while self.v_layout.count():
            item = self.v_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    def card_state(self):
        if self.card_show:
            self.container.hide()
            but = "展开"
        else:
            self.container.show()
            but = "收起"
        self.card_show = not self.card_show
        return f"{but}卡片"
    def save_all(self):
        self.table.save_all()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = ea()
    w.setWindowTitle("商铺记账表格 Demo")
    w.show()
    sys.exit(app.exec_())