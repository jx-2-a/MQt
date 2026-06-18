import re
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta  # 需要安装 pip install python-dateutil

class FormulaCalculator:
    def __init__(self,parent):
        self.parent = parent


    def parse_value(self, val):
        """解析值，如果是日期字符串则转 datetime"""
        if isinstance(val, datetime):
            return val
        if isinstance(val, str):
            # 先尝试时间格式
            for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d"]:
                try:
                    return datetime.strptime(val.strip(), fmt)
                except ValueError:
                    pass
            # 普通字符串直接返回
            return val
        return val

    def apply_date_op(self, base, num, unit):
        """处理日期 + N(单位)"""
        if not isinstance(base, datetime):
            raise ValueError(f"不能对非日期值 {base} 做日期运算")

        if unit in ("天", "日", None):  # 默认天
            return base + timedelta(days=num)
        elif unit == "月":
            return base + relativedelta(months=num)
        elif unit == "年":
            return base + relativedelta(years=num)
        else:
            raise ValueError(f"不支持的时间单位: {unit}")

    def calc_formula(self, row, jisuanshi):
        # 替换变量
        expr = jisuanshi

        # 处理特殊变量 [*now*]
        expr = expr.replace("[*now*]", f'"{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}"')

        vars_in_formula = re.findall(r"\[(.*?)\]", expr)
        for var in vars_in_formula:
            if var not in self.parent.names:
                raise ValueError(f"变量 {var} 未在 self.names 中定义")
            col = self.parent.names[var]
            val = self.parent.get_cell(row, col)
            val = self.parse_value(val)
            if isinstance(val, datetime):
                expr = expr.replace(f"[{var}]", f'"{val.strftime("%Y-%m-%d %H:%M:%S")}"')
            else:
                expr = expr.replace(f"[{var}]", str(val))

        print("替换后表达式:", expr)

        # ^ 替换成 **
        expr = expr.replace("^", "**")

        # 处理 if(条件, 真值, 假值)
        def if_func(cond, a, b):
            return a if cond else b

        # 处理日期加减匹配： "日期字符串 + N（单位）"
        date_pattern = r'"([\d\- :]+)"\s*([+-])\s*(\d+)(?:（(.+?)）)?'

        def repl_date(m):
            date_str, sign, num, unit = m.groups()
            base = datetime.strptime(date_str.strip(), "%Y-%m-%d %H:%M:%S")
            num = int(num)
            if sign == "-":
                num = -num
            result = self.apply_date_op(base, num, unit)
            # 返回 datetime(...) 对象的构造字符串，而不是直接字符串
            return f"datetime.strptime('{result.strftime('%Y-%m-%d %H:%M:%S')}', '%Y-%m-%d %H:%M:%S')"

        expr = re.sub(date_pattern, repl_date, expr)

        # 安全 eval
        try:
            result = eval(expr, {"__builtins__": None, "if_func": if_func, "datetime": datetime})
        except Exception as e:
            raise ValueError(f"公式计算出错: {e}")

        # 如果结果是字符串形式的日期，转回 datetime
        if isinstance(result, str):
            try:
                return datetime.strptime(result, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                return result
        return result
