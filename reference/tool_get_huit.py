from datetime import datetime, timedelta
import pandas as pd

class PlotParamBuilder:
    def __init__(self, params: dict):
        """
        params: {
            'kuadu': '3',        # 跨度长度（数字）
            'danwei': '月',      # 跨度单位（日/周/月/年）
            'chidu': '月',       # 横坐标刻度（日/周/月）
            'mouwei_n': '2025-08-25',  # 末尾时间点
            'mobiao': '成本'     # 纵坐标目标（字段名）
        }
        """
        self.params = params
        self.end_date = datetime.strptime(params['mouwei_n'], "%Y-%m-%d")
        self.kuadu = int(params['kuadu'])
        self.danwei = params['danwei']
        self.chidu = params['chidu']
        self.mobiao = params['mobiao']

    def get_date_range(self):
        """生成时间序列"""
        if self.danwei == '日':
            start = self.end_date - timedelta(days=self.kuadu-1)
            freq = 'D'
        elif self.danwei == '周':
            start = self.end_date - timedelta(weeks=self.kuadu-1)
            freq = 'W'
        elif self.danwei == '月':
            start = self.end_date - pd.DateOffset(months=self.kuadu-1)
            freq = 'M'
        elif self.danwei == '年':
            start = self.end_date - pd.DateOffset(years=self.kuadu-1)
            freq = 'Y'
        else:
            raise ValueError("不支持的跨度单位")

        dates = pd.date_range(start=start, end=self.end_date, freq=freq)
        return dates

    def build(self):
        """返回绘图所需参数"""
        dates = self.get_date_range()
        return {
            "x": dates.strftime("%Y-%m-%d").tolist(),  # 横坐标
            "xlabel": self.chidu,
            "ylabel": self.mobiao,
            "title": f"{self.end_date.strftime('%Y-%m-%d')}前{self.kuadu}{self.danwei}{self.mobiao}变化"
        }
if __name__ == "__main__":
    a = PlotParamBuilder({'kuadu': '3', 'danwei': '月', 'chidu': '月', 'mouwei_n': '2025-08-25', 'mobiao': '成本'})
    re = a.build()
    print(re)