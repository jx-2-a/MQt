import sqlite3
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class BillingAnalytics:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row

    def compute_date_range(self, kuadu: int, danwei: str, mouwei_n: str):
        """
        根据跨度、单位和末尾日期计算起止区间
        """
        kuadu = int(kuadu)
        end_date = datetime.strptime(mouwei_n, "%Y-%m-%d")
        if danwei == "日":
            start_date = end_date - timedelta(days=kuadu)
        elif danwei == "月":
            start_date = end_date - relativedelta(months=kuadu)
        elif danwei == "年":
            start_date = end_date - relativedelta(years=kuadu)
        else:
            raise ValueError(f"未知的单位: {danwei}")
        return start_date, end_date

    def split_by_chidu(self, start_date, end_date, chidu: str):
        """
        根据尺度拆分区间
        返回 [(x序号, start, end), ...]
        """
        result = []
        cur = start_date
        idx = 1
        while cur <= end_date:
            if chidu == "年":
                next_cur = (cur + relativedelta(years=1)).replace(month=1, day=1)
            elif chidu == "月":
                next_cur = (cur + relativedelta(months=1)).replace(day=1)
            elif chidu == "日":
                next_cur = cur + timedelta(days=1)
            else:
                raise ValueError(f"未知的尺度: {chidu}")

            result.append((idx, cur, min(next_cur, end_date)))
            idx += 1
            cur = next_cur
        return result

    def aggregate(self, kuadu, danwei, chidu, mouwei_n, mobiao, table="billings"):
        """
        主入口：返回 (labels, series_dict)
        - labels: x轴刻度（时间标签，而不是 1,2,3）
        - series_dict: {series_name: [(label, y), ...]}
        """
        start_date, end_date = self.compute_date_range(kuadu, danwei, mouwei_n)
        splits = self.split_by_chidu(start_date, end_date, chidu)

        cursor = self.conn.cursor()
        labels = []
        series_dict = {}

        for idx, seg_start, seg_end in splits:
            # 用真实标签而不是数字
            if chidu == "月":
                label = seg_start.strftime("%Y-%m")  # 例如 "2025-01"
            elif chidu == "日":
                label = seg_start.strftime("%Y-%m-%d")
            elif chidu == "年":
                label = seg_start.strftime("%Y")
            else:
                label = str(idx)  # 保底
            labels.append(label)

            # SQL 查询
            cursor.execute(f"""
                SELECT {mobiao} FROM {table}
                WHERE date >= ? AND date < ?
            """, (seg_start.strftime("%Y-%m-%d"), seg_end.strftime("%Y-%m-%d")))
            rows = cursor.fetchall()

            if not rows:
                # 没有数据时，强制写 0
                # series_dict.setdefault(mobiao, []).append((label, 0))
                continue

            # 判断字段是否是数字还是文本
            values = [r[mobiao] for r in rows if r[mobiao] is not None]

            if not values:
                series_dict.setdefault(mobiao, []).append((label, 0))
                continue

            if isinstance(values[0], (int, float)):
                y = sum(values)
                series_dict.setdefault(mobiao, []).append((label, y))
            else:
                # 文本：统计出现次数
                counter = {}
                for v in values:
                    counter[v] = counter.get(v, 0) + 1
                for k, v in counter.items():
                    series_dict.setdefault(k, []).append((label, v))

        return labels, series_dict

