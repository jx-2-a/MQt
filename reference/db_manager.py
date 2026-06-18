# db_manager.py
import sqlite3
from typing import Any, List, Dict, Tuple
import random
from datetime import datetime, timedelta
def rows_to_dicts(rows):
    return [dict(r) for r in rows]
class DBManager:
    def __init__(self, db_path: str = "data.db"):
        """初始化数据库管理器"""
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # 返回 dict 风格结果
        self.cursor = self.conn.cursor()

    def execute(self, query: str, params: Tuple = ()) -> None:
        """执行增删改语句"""
        self.cursor.execute(query, params)
        self.conn.commit()

    def fetch_one(self, query: str, params: Tuple = ()) -> Dict[str, Any]:
        """查询单条记录"""
        self.cursor.execute(query, params)
        row = self.cursor.fetchone()
        return dict(row) if row else None

    def fetch_all(self, query: str, params: Tuple = ()) -> List[Dict[str, Any]]:
        """查询多条记录"""
        self.cursor.execute(query, params)
        rows = self.cursor.fetchall()
        return [dict(r) for r in rows]

    def create_table(self, table_name: str, columns: Dict[str, str]) -> None:
        """
        创建表
        columns 示例:
        {
            "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
            "name": "TEXT NOT NULL",
            "phone": "TEXT",
            "customer_id": "INTEGER",
            "FOREIGN KEY(customer_id)": "REFERENCES customer(id)"
        }
        """
        col_defs = []
        for col, ctype in columns.items():
            if col.upper().startswith("FOREIGN KEY"):
                # 外键约束，拼接成 "FOREIGN KEY(customer_id) REFERENCES customer(id)"
                col_defs.append(f"{col} {ctype}")
            else:
                # 普通字段
                col_defs.append(f"{col} {ctype}")
        col_str = ", ".join(col_defs)
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({col_str});"
        self.execute(query)

    def insert(self, table: str, data: Dict[str, Any]) -> None:
        """插入记录"""
        keys = ", ".join(data.keys())
        placeholders = ", ".join(["?"] * len(data))
        values = tuple(data.values())
        query = f"INSERT INTO {table} ({keys}) VALUES ({placeholders})"
        self.execute(query, values)

    def update(self, table: str, data: Dict[str, Any], where: str, params: Tuple) -> None:
        """更新记录"""
        set_clause = ", ".join([f"{k} = ?" for k in data.keys()])
        values = tuple(data.values()) + params
        query = f"UPDATE {table} SET {set_clause} WHERE {where}"
        self.execute(query, values)

    def delete(self, table: str, where: str, params: Tuple) -> None:
        """删除记录"""
        query = f"DELETE FROM {table} WHERE {where}"
        self.execute(query, params)

    def close(self):
        """关闭数据库"""
        self.conn.close()
    """创建，修改账单表单"""
    def creat_billing_table(self):
        """创建账单记录表"""
        # 账单表
        self.create_table("billings", {
            "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
            "customer_id": "INTEGER NOT NULL",
            "customer_name": "TEXT NOT NULL",
            "date": "TEXT NOT NULL",  # 存储日期时间，ISO 格式字符串
            "service": "TEXT",  # 服务内容
            "fee": "REAL",  # 收费
            "cost": "REAL",  # 成本
            "profit": "REAL",  # 利润
            "payment_method": "TEXT",  # 支付方式
            "note": "TEXT",  # 备注
            "FOREIGN KEY(customer_id)": "REFERENCES customers(id)"
        })

        # 创建常用索引，加快查询
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_billings_customer_id ON billings(customer_id);")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_billings_date ON billings(date);")

        self.conn.commit()
    def save_day_billings(self, billings):
            """
            保存账单记录，支持新增和修改
            billings: 列表，每个元素是 dict，格式：
            {
                "id": 1,  # 修改时提供
                "customer_id": 12,
                "customer_name": "张三",
                "service": "洗车",
                "fee": 50.0,
                "cost": 30.0,
                "profit": 20.0,
                "payment_method": "现金",
                "note": "快速洗",
                "date": "2025-09-01 12:00:00"  # 可选
            }
            """

            def safe_int(value, default=None):
                """
                把值安全转换为整数，如果不能转换返回默认值
                """
                try:
                    return int(str(value).strip())
                except (ValueError, TypeError):
                    return default
            def to_number(value, default=0, num_type=float):
                try:
                    v = str(value).strip()
                    if v == "":
                        return default
                    return num_type(v)
                except (ValueError, TypeError):
                    return default

            for b in billings:
                # 数值字段安全转换
                customer_id = to_number(b.get("customer_id", 0), default=0, num_type=int)
                customer_name = str(b.get("customer_name", ""))
                service = str(b.get("service", ""))
                fee = to_number(b.get("fee", 0))
                cost = to_number(b.get("cost", 0))
                profit = to_number(b.get("profit", 0))
                payment_method = str(b.get("payment_method", ""))
                note = str(b.get("note", ""))

                # 日期字段统一格式，没提供就用当前时间
                d_t = b.get("date")
                if not d_t:
                    d_t = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                b["date"] = d_t  # 更新原对象，方便后续修改

                record_id = safe_int(b.get("id"))
                if record_id is not None:
                    self.cursor.execute("""
                        UPDATE billings
                        SET customer_id=?, customer_name=?, date=?, service=?, fee=?, cost=?, profit=?, payment_method=?, note=?
                        WHERE id=?
                    """, (
                        customer_id, customer_name, d_t, service, fee, cost, profit, payment_method, note,
                        b["id"]
                    ))
                else:  # 新增
                    self.cursor.execute("""
                        INSERT INTO billings (customer_id, customer_name, date, service, fee, cost, profit, payment_method, note)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        customer_id, customer_name, d_t, service, fee, cost, profit, payment_method, note
                    ))

            self.conn.commit()
            print("保存成功！")
    # 读取某天账单
    def get_day_billings(self, date_str):
        """
        获取指定日期的所有账单
        date_str: 'YYYY-MM-DD' 格式
        """
        like_pattern = f"{date_str}%"  # 匹配当天所有时间
        self.cursor.execute("""
               SELECT * FROM billings
               WHERE date LIKE ?
               ORDER BY id
           """, (like_pattern,))
        rows = self.cursor.fetchall()
        return [dict(r) for r in rows]
    def search_billings_by_customer_field(self, customer_id: int, field_key: str, text: str) -> list[dict]:
        """
        根据客户ID，在指定字段中搜索包含 text 的账单记录
        参数:
            customer_id: 客户ID
            field_key: 要搜索的字段名，例如 "service"、"note" 等
            text: 搜索的内容（模糊匹配）
        返回:
            list[dict] - 匹配的账单记录列表
        """
        # 安全检查字段名，防止 SQL 注入
        allowed_fields = {"service", "note", "payment_method","date"}
        if field_key not in allowed_fields:
            raise ValueError(f"不允许搜索字段: {field_key}")

        query = f"""
            SELECT *
            FROM billings
            WHERE customer_id = ? AND {field_key} LIKE ?
            ORDER BY date, id
        """
        self.cursor.execute(query, (customer_id, f"%{text}%"))
        rows = self.cursor.fetchall()

        # 转成字典列表
        result = []
        for r in rows:
            result.append({
                "id": r["id"],
                "customer_id": r["customer_id"],
                "customer_name": r["customer_name"],
                "date": r["date"],
                "service": r["service"],
                "fee": r["fee"],
                "cost": r["cost"],
                "profit": r["profit"],
                "payment_method": r["payment_method"],
                "note": r["note"]
            })
        return result
    def get_billings_by_customer_id(self, customer_id: int) -> list[dict]:
        """
        根据客户 ID 查询该客户所有账单记录
        返回列表，每条记录是 dict，包括完整日期时间
        """
        self.cursor.execute("""
            SELECT *
            FROM billings
            WHERE customer_id = ?
            ORDER BY date, id
        """, (customer_id,))

        rows = self.cursor.fetchall()

        # 转成字典列表
        result = []
        for r in rows:
            result.append({
                "id": r["id"],
                "customer_id": r["customer_id"],
                "customer_name": r["customer_name"],
                "date": r["date"],  # 完整时间字符串
                "service": r["service"],
                "fee": r["fee"],
                "cost": r["cost"],
                "profit": r["profit"],
                "payment_method": r["payment_method"],
                "note": r["note"]
            })
        return result

    def get_billings(self,
                     date_str: str = None,
                     filter_mode: bool = True,
                     order_by: str = "date",
                     desc: bool = True,
                     limit: int = 100,
                     field_key: str = None,
                     text: str = None):
        """
        获取账单，可以指定日期、搜索条件、排序、数量
        :param date_str: 日期字符串 'YYYY-MM-DD'，None 表示查询全部
        :param filter_mode: 是否开启筛选（排序、数量限制）
        :param order_by: 排序字段（默认 id）
        :param desc: 是否倒序
        :param limit: 限制返回数量，None 表示全部
        :param field_key: 搜索字段，例如 'customer'、'remark'
        :param text: 搜索关键字
        """
        valid_fields = {"service", "note", "payment_method",
                        "date","fee","cost","profit","customer_name"}
        if order_by not in valid_fields:
            order_by = "date"
        if field_key and field_key not in valid_fields:
            field_key = None
        # 构建 WHERE 条件
        where_clauses = []
        params = []

        if date_str:
            where_clauses.append("date LIKE ?")
            params.append(f"{date_str}%")

        if field_key and text:
            print(field_key)
            where_clauses.append(f"{field_key} LIKE ?")
            params.append(f"%{text}%")

        where_clause = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

        if filter_mode:
            # 筛选模式
            order_clause = f"ORDER BY {order_by} {'DESC' if desc else 'ASC'}"
            limit_clause = f"LIMIT {limit}" if limit else ""
            query = f"""
                SELECT * FROM billings
                {where_clause}
                {order_clause}
                {limit_clause}
            """
        else:
            # 默认行为
            query = f"""
                SELECT * FROM billings
                {where_clause}
                ORDER BY id
            """

        self.cursor.execute(query, params)
        rows = self.cursor.fetchall()
        return [dict(r) for r in rows]

    """创建，修改保修卡表单"""

    def creat_warranty_card_table(self):
        """创建账单记录表"""
        # 账单表
        self.create_table("warranty_card", {
            "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
            "customer_id": "INTEGER NOT NULL",
            "customer_name": "TEXT NOT NULL",
            "date": "TEXT NOT NULL",  # 存储日期时间，ISO 格式字符串
            "product": "TEXT",  # 服务内容
            "product_id": "TEXT",  # 收费
            "start": "TEXT",  # 成本
            "long": "TEXT",  # 利润
            "end": "TEXT",  # 支付方式
            "state": "TEXT",
            "note": "TEXT",  # 备注
            "FOREIGN KEY(customer_id)": "REFERENCES customers(id)"
        })

        # 创建常用索引，加快查询
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_warranty_card_customer_id ON warranty_card(customer_id);")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_warranty_card_date ON billings(date);")

        self.conn.commit()

    def save_day_warranty_card(self, billings):
        """
        保存账单记录，支持新增和修改
        "warranty_card", {
            "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
            "customer_id": "INTEGER NOT NULL",
            "customer_name": "TEXT NOT NULL",
            "date": "TEXT NOT NULL",  # 存储日期时间，ISO 格式字符串
            "product": "TEXT",  # 服务内容
            "product_id": "TEXT",  # 收费
            "start": "REAL",  # 成本
            "long": "REAL",  # 利润
            "end": "TEXT",  # 支付方式
            "state": "TEXT",
            "note": "TEXT",  # 备注
            "FOREIGN KEY(customer_id)": "REFERENCES customers(id)"
        }
        """
        def safe_int(value, default=None):
            """
            把值安全转换为整数，如果不能转换返回默认值
            """
            try:
                return int(str(value).strip())
            except (ValueError, TypeError):
                return default
        def to_number(value, default=0, num_type=float):
            try:
                v = str(value).strip()
                if v == "":
                    return default
                return num_type(v)
            except (ValueError, TypeError):
                return default

        for b in billings:
            # 数值字段安全转换
            customer_id = to_number(b.get("customer_id", 0), default=0, num_type=int)
            customer_name = str(b.get("customer_name", ""))
            product = str(b.get("product", ""))
            product_id = str(b.get("product_id", ""))
            start = str(b.get("start", ""))
            long = str(b.get("long", ""))
            end = str(b.get("end", ""))
            state = str(b.get("state", ""))
            note = str(b.get("note", ""))

            # 日期字段统一格式，没提供就用当前时间
            d_t = b.get("date")
            if not d_t:
                d_t = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            b["date"] = d_t  # 更新原对象，方便后续修改

            record_id = safe_int(b.get("id"))
            if record_id is not None:
                self.cursor.execute("""
                            UPDATE warranty_card
                            SET customer_id=?, customer_name=?, date=?, product=?, product_id=?, start=?, long=?, end=?, state=?, note=?
                            WHERE id=?
                        """, (
                    customer_id, customer_name, d_t, product, product_id, start, long, end, state,note,
                    b["id"]
                ))
            else:  # 新增
                self.cursor.execute("""
                            INSERT INTO warranty_card (customer_id, customer_name, date, product, product_id, start, long, end, state, note)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                    customer_id, customer_name, d_t, product, product_id, start, long, end, state,note
                ))

        self.conn.commit()
        print("保存成功！")

    # 读取某天账单
    def get_day_warranty_card(self, date_str):
        """
        获取指定日期的所有账单
        date_str: 'YYYY-MM-DD' 格式
        """
        like_pattern = f"{date_str}%"  # 匹配当天所有时间
        self.cursor.execute("""
                   SELECT * FROM warranty_card
                   WHERE date LIKE ?
                   ORDER BY id
               """, (like_pattern,))
        rows = self.cursor.fetchall()
        return [dict(r) for r in rows]

    def search_warranty_card_by_customer_field(self, customer_id: int, field_key: str, text: str) -> list[dict]:
        # 安全检查字段名，防止 SQL 注入
        allowed_fields = {"product", "product_id", "long", "date"}
        if field_key not in allowed_fields:
            raise ValueError(f"不允许搜索字段: {field_key}")

        query = f"""
                SELECT *
                FROM warranty_card
                WHERE customer_id = ? AND {field_key} LIKE ?
                ORDER BY date, id
            """
        self.cursor.execute(query, (customer_id, f"%{text}%"))
        rows = self.cursor.fetchall()
        # 转成字典列表
        result = []
        for r in rows:
            result.append({
                "id": r["id"],
                "customer_id": r["customer_id"],
                "customer_name": r["customer_name"],
                "date": r["date"],
                "product": r["product"],
                "product_id": r["product_id"],
                "start": r["start"],
                "long": r["long"],
                "end": r["end"],
                "state": r["state"],
                "note": r["note"]
            })
        return result

    def get_warranty_card_by_customer_id(self, customer_id: int) -> list[dict]:
        """
        根据客户 ID 查询该客户所有账单记录
        返回列表，每条记录是 dict，包括完整日期时间
        """
        self.cursor.execute("""
                SELECT *
                FROM warranty_card
                WHERE customer_id = ?
                ORDER BY date, id
            """, (customer_id,))

        rows = self.cursor.fetchall()

        # 转成字典列表
        result = []
        for r in rows:
            result.append({
                "id": r["id"],
                "customer_id": r["customer_id"],
                "customer_name": r["customer_name"],
                "date": r["date"],
                "product": r["product"],
                "product_id": r["product_id"],
                "start": r["start"],
                "long": r["long"],
                "end": r["end"],
                "state": r["state"],
                "note": r["note"]
            })
        return result
    def get_warranty_card(self,
                     date_str: str = None,
                     filter_mode: bool = True,
                     order_by: str = "date",
                     desc: bool = True,
                     limit: int = 100,
                     field_key: str = None,
                     text: str = None):
        """
        获取账单，可以指定日期、搜索条件、排序、数量
        :param date_str: 日期字符串 'YYYY-MM-DD'，None 表示查询全部
        :param filter_mode: 是否开启筛选（排序、数量限制）
        :param order_by: 排序字段（默认 id）
        :param desc: 是否倒序
        :param limit: 限制返回数量，None 表示全部
        :param field_key: 搜索字段，例如 'customer'、'remark'
        :param text: 搜索关键字
        """
        # ✅ 允许的字段白名单，防止拼接注入
        valid_fields = {"product", "product_id", "long", "date","customer_name","state","start","end"}
        if order_by not in valid_fields:
            order_by = "date"
        if field_key and field_key not in valid_fields:
            field_key = None

        # 构建 WHERE 条件
        where_clauses = []
        params = []

        if date_str:
            where_clauses.append("date LIKE ?")
            params.append(f"{date_str}%")

        if field_key and text:
            where_clauses.append(f"{field_key} LIKE ?")
            params.append(f"%{text}%")

        where_clause = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

        if filter_mode:
            # 筛选模式
            order_clause = f"ORDER BY {order_by} {'DESC' if desc else 'ASC'}"
            limit_clause = f"LIMIT {limit}" if limit else ""
            query = f"""
                SELECT * FROM warranty_card
                {where_clause}
                {order_clause}
                {limit_clause}
            """
        else:
            # 默认行为
            query = f"""
                SELECT * FROM warranty_card
                {where_clause}
                ORDER BY id
            """

        self.cursor.execute(query, params)
        rows = self.cursor.fetchall()
        return [dict(r) for r in rows]

    """创建，修改客户表单"""
    def creat_kehu_table(self):
        """创建客户记录表"""
        def create_indexes_for_kehu():
            """创建常用索引，加快查询速度"""
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_customers_name ON customers(name);")
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_phone_customer_id ON phone(customer_id);")
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_plate_customer_id ON plate(customer_id);")
            self.conn.commit()
        # 客户表
        self.create_table("customers", {
            "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
            "name": "TEXT NOT NULL",
            "title": "TEXT",
            "wechat": "TEXT",
            "note": "TEXT"
        })

        # 电话表
        self.create_table("phone", {
            "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
            "customer_id": "INTEGER",
            "phone": "TEXT",
            "FOREIGN KEY(customer_id)": "REFERENCES customers(id)"
        })

        # 车牌表
        self.create_table("plate", {
            "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
            "customer_id": "INTEGER",
            "plate": "TEXT",
            "FOREIGN KEY(customer_id)": "REFERENCES customers(id)"
        })
        create_indexes_for_kehu()
    def insert_customer(self, customer: Dict[str, Any]) -> int:
        """插入客户及其电话、车牌信息，返回customer_id"""

        # 把列表取第一个元素（如果有），否则为空字符串
        def first_or_empty(value):
            if isinstance(value, list):
                return str(value[0]) if value else ""
            return str(value or "")

        base_data = {
            "name": first_or_empty(customer.get("name")),
            "title": first_or_empty(customer.get("title")),
            "wechat": first_or_empty(customer.get("wechat")),
            "note": first_or_empty(customer.get("note"))
        }
        self.insert("customers", base_data)

        customer_id = self.cursor.lastrowid  # 获取自增ID

        # 电话：可能是多个，直接循环
        for phone in customer.get("phones", []):
            self.insert("phone", {
                "customer_id": customer_id,
                "phone": str(phone)
            })

        # 车牌：可能是多个，直接循环
        for plate in customer.get("plates", []):
            self.insert("plate", {
                "customer_id": customer_id,
                "plate": str(plate)
            })

        return customer_id
    def update_customer(self, customer: Dict[str, Any], customer_id: int) -> None:
        """根据 customer_id 更新客户及其电话、车牌信息"""

        # 把列表取第一个元素（如果有），否则为空字符串
        def first_or_empty(value):
            if isinstance(value, list):
                return str(value[0]) if value else ""
            return str(value or "")

        base_data = {
            "name": first_or_empty(customer.get("name")),
            "title": first_or_empty(customer.get("title")),
            "wechat": first_or_empty(customer.get("wechat")),
            "note": first_or_empty(customer.get("note"))
        }
        self.update("customers", base_data, "id = ?", (customer_id,))

        # 1. 删除旧电话
        self.execute("DELETE FROM phone WHERE customer_id = ?", (customer_id,))
        # 2. 插入新电话
        for phone in customer.get("phones", []):
            self.insert("phone", {
                "customer_id": customer_id,
                "phone": str(phone)
            })

        # 1. 删除旧车牌
        self.execute("DELETE FROM plate WHERE customer_id = ?", (customer_id,))
        # 2. 插入新车牌
        for plate in customer.get("plates", []):
            self.insert("plate", {
                "customer_id": customer_id,
                "plate": str(plate)
            })
    def get_customer_by_id(self, customer_id: int) -> dict | None:
        """根据客户ID返回完整信息，包含电话和车牌"""
        # 1. 查询主表
        self.cursor.execute("SELECT * FROM customers WHERE id = ?", (customer_id,))
        customer = self.cursor.fetchone()
        if not customer:
            return None

        # 2. 查询电话表
        self.cursor.execute("SELECT phone FROM phone WHERE customer_id = ?", (customer_id,))
        phones = [row["phone"] for row in self.cursor.fetchall()]

        # 3. 查询车牌表
        self.cursor.execute("SELECT plate FROM plate WHERE customer_id = ?", (customer_id,))
        plates = [row["plate"] for row in self.cursor.fetchall()]

        # 4. 返回完整 dict
        return {
            "id": customer_id,
            "name": customer["name"],
            "title": customer["title"],
            "wechat": customer["wechat"],
            "note": customer["note"],
            "phones": phones,
            "plates": plates
        }
    def get_customers_random(self, limit=10) -> list[dict]:
        """随机获取若干客户"""
        self.cursor.execute("SELECT * FROM customers")
        rows = self.cursor.fetchall()
        rows = random.sample(rows, min(len(rows), limit))
        result = []
        for c in rows:
            customer_id = c["id"]
            self.cursor.execute("SELECT phone FROM phone WHERE customer_id=?", (customer_id,))
            phones = [r["phone"] for r in self.cursor.fetchall()]
            self.cursor.execute("SELECT plate FROM plate WHERE customer_id=?", (customer_id,))
            plates = [r["plate"] for r in self.cursor.fetchall()]
            result.append({
                "id":customer_id,
                "name": c["name"],
                "title": c["title"],
                "wechat": c["wechat"],
                "note": c["note"],
                "phones": phones,
                "plates": plates
            })
        return result
    def search_customers_by_field(self, field: str, value: str):
        """
        按指定字段模糊搜索客户
        field: 'name' | 'phone' | 'plate'
        value: 当前输入文本
        返回 list[dict]
        """
        if not value:
            return []  # 空输入不返回

        value = f"%{value}%"

        if field == "name":
            query = "SELECT * FROM customers WHERE name LIKE ?"
            params = (value,)
        elif field == "phone":
            query = """
            SELECT DISTINCT c.*
            FROM customers c
            JOIN phone p ON p.customer_id = c.id
            WHERE p.phone LIKE ?
            """
            params = (value,)
        elif field == "plate":
            query = """
            SELECT DISTINCT c.*
            FROM customers c
            JOIN plate pl ON pl.customer_id = c.id
            WHERE pl.plate LIKE ?
            """
            params = (value,)
        else:
            query = f"SELECT * FROM customers WHERE {field} LIKE ?"
            params = (value,)

        self.cursor.execute(query, params)
        rows = self.cursor.fetchall()
        result = []

        for c in rows:
            customer_id = c["id"]

            self.cursor.execute("SELECT phone FROM phone WHERE customer_id=?", (customer_id,))
            phones = [r["phone"] for r in self.cursor.fetchall()]

            self.cursor.execute("SELECT plate FROM plate WHERE customer_id=?", (customer_id,))
            plates = [r["plate"] for r in self.cursor.fetchall()]

            result.append({
                "id":customer_id,
                "name": c["name"],
                "title": c["title"],
                "wechat": c["wechat"],
                "note": c["note"],
                "phones": phones,
                "plates": plates
            })

        return result
    """创建，修改商品表单"""
    def creat_shoppings_table(self):
        self.create_table("shoppingss", {
            "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
            "shopper_id": "TEXT NOT NULL",
            "shopper_name": "TEXT NOT NULL",
            "xinghao": "TEXT",
            "date": "TEXT NOT NULL",
            "shopper_jia_name": "TEXT",
            "fenlei": "TEXT",
            "jiage": "REAL",
            "laiyuan": "TEXT",
            "note": "TEXT",
            "FOREIGN KEY(shopper_id)": "REFERENCES shoppers(id)"
        })

        # 创建常用索引，加快查询
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_shoppingss_shopper_id ON shoppingss(shopper_id);")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_shoppingss_date ON shoppingss(date);")

        self.conn.commit()
    def save_day_shoppingss(self, shoppingss):
            def safe_int(value, default=None):
                """
                把值安全转换为整数，如果不能转换返回默认值
                """
                try:
                    return int(str(value).strip())
                except (ValueError, TypeError):
                    return default
            def to_number(value, default=0, num_type=float):
                try:
                    v = str(value).strip()
                    if v == "":
                        return default
                    return num_type(v)
                except (ValueError, TypeError):
                    return default

            for b in shoppingss:
                # 数值字段安全转换
                shopper_id = str(b.get("shopper_id", ""))
                shopper_name = str(b.get("shopper_name", ""))
                xinghao = str(b.get("xinghao", ""))
                shopper_jia_name = str(b.get("shopper_jia_name", ""))
                fenlei = str(b.get("fenlei", ""))
                jiage = to_number(b.get("jiage", 0))
                laiyuan = str(b.get("laiyuan", ""))
                note = str(b.get("note", ""))

                # 日期字段统一格式，没提供就用当前时间
                d_t = b.get("date")
                if not d_t:
                    d_t = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                b["date"] = d_t  # 更新原对象，方便后续修改

                record_id = safe_int(b.get("id"))
                if record_id is not None:
                    self.cursor.execute("""
                        UPDATE shoppingss
                        SET shopper_id=?, shopper_name=?, date=?, shopper_jia_name=?,xinghao=?, fenlei=?,jiage=?, laiyuan=?, note=?
                        WHERE id=?
                    """, (
                        shopper_id, shopper_name, d_t, shopper_jia_name,xinghao, fenlei,jiage, laiyuan, note,
                        b["id"]
                    ))
                else:  # 新增
                    self.cursor.execute("""
                        INSERT INTO shoppingss (shopper_id, shopper_name, date, shopper_jia_name,xinghao, fenlei,jiage, laiyuan, note)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        shopper_id, shopper_name, d_t, shopper_jia_name,xinghao, fenlei,jiage, laiyuan, note
                    ))

            self.conn.commit()
            print("保存成功！")
    # 读取某天账单
    def get_day_shoppingss(self, date_str):
        """
        获取指定日期的所有账单
        date_str: 'YYYY-MM-DD' 格式
        """
        like_pattern = f"{date_str}%"  # 匹配当天所有时间
        self.cursor.execute("""
               SELECT * FROM shoppingss
               WHERE date LIKE ?
               ORDER BY id
           """, (like_pattern,))
        rows = self.cursor.fetchall()
        return [dict(r) for r in rows]
    def search_shoppingss_by_shopper_field(self, shopper_id: int, field_key: str, text: str) -> list[dict]:
        """
        根据客户ID，在指定字段中搜索包含 text 的账单记录
        参数:
            shopper_id: 客户ID
            field_key: 要搜索的字段名，例如 "service"、"note" 等
            text: 搜索的内容（模糊匹配）
        返回:
            list[dict] - 匹配的账单记录列表
        """
        # 安全检查字段名，防止 SQL 注入
        allowed_fields = {"shopper_name": "TEXT NOT NULL",
            "xinghao": "TEXT",
            "date": "TEXT NOT NULL",
            "shopper_jia_name": "TEXT",
            "fenlei": "TEXT",
            "jiage": "REAL",
            "laiyuan": "TEXT",
            "note": "TEXT",  }
        if field_key not in allowed_fields:
            raise ValueError(f"不允许搜索字段: {field_key}")

        query = f"""
            SELECT *
            FROM shoppingss
            WHERE shopper_id = ? AND {field_key} LIKE ?
            ORDER BY date, id
        """
        self.cursor.execute(query, (shopper_id, f"%{text}%"))
        rows = self.cursor.fetchall()
        # 转成字典列表
        result = []
        for r in rows:
            result.append({
                "id": r["id"],
                "shopper_id": r["shopper_id"],
                "shopper_name": r["shopper_name"],
                "xinghao":r["xinghao"],
                "date": r["date"],
                "shopper_jia_name": r["shopper_jia_name"],
                "fenlei": r["fenlei"],
                "jiage": r["jiage"],
                "laiyuan": r["laiyuan"],
                "note": r["note"]
            })
        return result
    def get_shoppingss_by_shopper_id(self, shopper_id: int) -> list[dict]:
        """
        根据客户 ID 查询该客户所有账单记录
        返回列表，每条记录是 dict，包括完整日期时间
        """
        self.cursor.execute("""
            SELECT *
            FROM shoppingss
            WHERE shopper_id = ?
            ORDER BY date, id
        """, (shopper_id,))

        rows = self.cursor.fetchall()

        # 转成字典列表
        result = []
        for r in rows:
            result.append({
                "id": r["id"],
                "shopper_id": r["shopper_id"],
                "shopper_name": r["shopper_name"],
                "xinghao": r["xinghao"],
                "date": r["date"],
                "shopper_jia_name": r["shopper_jia_name"],
                "fenlei": r["fenlei"],
                "jiage": r["jiage"],
                "laiyuan": r["laiyuan"],
                "note": r["note"]
            })
        return result
    def get_shopper_random(self, limit=10) -> list[dict]:
        """随机获取若干客户"""
        self.cursor.execute("SELECT * FROM shoppingss")
        rows = self.cursor.fetchall()
        rows = random.sample(rows, min(len(rows), limit))
        result = []
        for c in rows:
            result.append({
                "id":c["id"],
                "shopper_id": c["shopper_id"],
                "shopper_name": c["shopper_name"],
                "xinghao": r["xinghao"],
                "date": c["date"],
                "shopper_jia_name": c["shopper_jia_name"],
                "fenlei": c["fenlei"],
                "jiage": c["jiage"],
                "laiyuan": c["laiyuan"],
                "note": c["note"]
            })
        return result
    def get_shoppingss(self,
                     date_str: str = None,
                     filter_mode: bool = True,
                     order_by: str = "date",
                     desc: bool = True,
                     limit: int = 100,
                     field_key: str = None,
                     text: str = None):
        """
        获取账单，可以指定日期、搜索条件、排序、数量
        :param date_str: 日期字符串 'YYYY-MM-DD'，None 表示查询全部
        :param filter_mode: 是否开启筛选（排序、数量限制）
        :param order_by: 排序字段（默认 id）
        :param desc: 是否倒序
        :param limit: 限制返回数量，None 表示全部
        :param field_key: 搜索字段，例如 'shopper'、'remark'
        :param text: 搜索关键字
        """
        valid_fields = {"service", "note", "payment_method",
                        "date","fee","cost","profit","shopper_name"}
        if order_by not in valid_fields:
            order_by = "date"
        if field_key and field_key not in valid_fields:
            field_key = None
        # 构建 WHERE 条件
        where_clauses = []
        params = []

        if date_str:
            where_clauses.append("date LIKE ?")
            params.append(f"{date_str}%")

        if field_key and text:
            print(field_key)
            where_clauses.append(f"{field_key} LIKE ?")
            params.append(f"%{text}%")

        where_clause = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

        if filter_mode:
            # 筛选模式
            order_clause = f"ORDER BY {order_by} {'DESC' if desc else 'ASC'}"
            limit_clause = f"LIMIT {limit}" if limit else ""
            query = f"""
                SELECT * FROM shoppingss
                {where_clause}
                {order_clause}
                {limit_clause}
            """
        else:
            # 默认行为
            query = f"""
                SELECT * FROM shoppingss
                {where_clause}
                ORDER BY id
            """

        self.cursor.execute(query, params)
        rows = self.cursor.fetchall()
        return [dict(r) for r in rows]

    def get_latest_per_shopper_shoppingss(self, field_key=None, text=None):
        valid_fields = {
            "shopper_name", "xinghao", "date",
            "shopper_jia_name", "fenlei", "jiage",
            "laiyuan", "note"
        }

        where_clause = ""
        params = []

        if field_key and field_key in valid_fields and text:
            where_clause = f"WHERE s.{field_key} LIKE ?"
            params.append(f"%{text}%")

        query = f"""
            SELECT s.*
            FROM shoppingss s
            JOIN (
                SELECT shopper_id, MAX(date) AS max_date
                FROM shoppingss
                GROUP BY shopper_id
            ) t
            ON s.shopper_id = t.shopper_id AND s.date = t.max_date
            {where_clause}
        """
        self.cursor.execute(query, params)
        rows = self.cursor.fetchall()
        return [dict(r) for r in rows]

    def get_shopper_prices_by_date(self, shopper_id: str):
        query = """
            SELECT date, jiage
            FROM shoppingss
            WHERE shopper_id = ?
            ORDER BY date ASC
        """
        self.cursor.execute(query, (shopper_id,))
        rows = self.cursor.fetchall()
        return [(row["date"], row["jiage"]) for row in rows]

    """创建，修改道具表单"""

    def creat_daojus_table(self):
        """创建账单记录表"""
        # 账单表
        self.create_table("daojus", {
            "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
            "shopper_id": "TEXT NOT NULL",
            "shopper_name": "TEXT NOT NULL",
            "date": "TEXT NOT NULL",
            "shopper_jia_name": "TEXT",
            "fenlei": "TEXT",
            "jiage": "REAL",
            "laiyuan": "TEXT",
            "how_use": "TEXT",
            "note": "TEXT",
            "FOREIGN KEY(shopper_id)": "REFERENCES shoppers(id)"
        })

        # 创建常用索引，加快查询
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_daojus_shopper_id ON daojus(shopper_id);")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_daojus_date ON daojus(date);")

        self.conn.commit()

    def save_day_daojus(self, daojus):
        def safe_int(value, default=None):
            """
            把值安全转换为整数，如果不能转换返回默认值
            """
            try:
                return int(str(value).strip())
            except (ValueError, TypeError):
                return default

        def to_number(value, default=0, num_type=float):
            try:
                v = str(value).strip()
                if v == "":
                    return default
                return num_type(v)
            except (ValueError, TypeError):
                return default

        for b in daojus:
            # 数值字段安全转换
            shopper_id = str(b.get("shopper_id", ""))
            shopper_name = str(b.get("shopper_name", ""))
            how_use = str(b.get("how_use", ""))
            shopper_jia_name = str(b.get("shopper_jia_name", ""))
            fenlei = str(b.get("fenlei", ""))
            jiage = to_number(b.get("jiage", 0))
            laiyuan = str(b.get("laiyuan", ""))
            note = str(b.get("note", ""))

            # 日期字段统一格式，没提供就用当前时间
            d_t = b.get("date")
            if not d_t:
                d_t = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            b["date"] = d_t  # 更新原对象，方便后续修改

            record_id = safe_int(b.get("id"))
            if record_id is not None:
                self.cursor.execute("""
                            UPDATE daojus
                            SET shopper_id=?, shopper_name=?, date=?, shopper_jia_name=?, fenlei=?,jiage=?, laiyuan=?,how_use=?, note=?
                            WHERE id=?
                        """, (
                    shopper_id, shopper_name, d_t, shopper_jia_name, fenlei, jiage, laiyuan, how_use, note,
                    b["id"]
                ))
            else:  # 新增
                self.cursor.execute("""
                            INSERT INTO daojus (shopper_id, shopper_name, date, shopper_jia_name, fenlei,jiage, laiyuan,how_use, note)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                    shopper_id, shopper_name, d_t, shopper_jia_name, fenlei, jiage, laiyuan, how_use, note
                ))

        self.conn.commit()
        print("保存成功！")

    # 读取某天账单
    def get_day_daojus(self, date_str):
        """
        获取指定日期的所有账单
        date_str: 'YYYY-MM-DD' 格式
        """
        like_pattern = f"{date_str}%"  # 匹配当天所有时间
        self.cursor.execute("""
                   SELECT * FROM daojus
                   WHERE date LIKE ?
                   ORDER BY id
               """, (like_pattern,))
        rows = self.cursor.fetchall()
        return [dict(r) for r in rows]

    def search_daojus_by_shopper_field(self, shopper_id: int, field_key: str, text: str) -> list[dict]:
        """
        根据客户ID，在指定字段中搜索包含 text 的账单记录
        参数:
            shopper_id: 客户ID
            field_key: 要搜索的字段名，例如 "service"、"note" 等
            text: 搜索的内容（模糊匹配）
        返回:
            list[dict] - 匹配的账单记录列表
        """
        # 安全检查字段名，防止 SQL 注入
        allowed_fields = {"shopper_name": "TEXT NOT NULL",
            "date": "TEXT NOT NULL",
            "shopper_jia_name": "TEXT",
            "fenlei": "TEXT",
            "jiage": "REAL",
            "laiyuan": "TEXT",
            "how_use": "TEXT",
            "note": "TEXT"}
        if field_key not in allowed_fields:
            raise ValueError(f"不允许搜索字段: {field_key}")

        query = f"""
                SELECT *
                FROM daojus
                WHERE shopper_id = ? AND {field_key} LIKE ?
                ORDER BY date, id
            """
        self.cursor.execute(query, (shopper_id, f"%{text}%"))
        rows = self.cursor.fetchall()
        # 转成字典列表
        result = []
        for r in rows:
            result.append({
                "id": r["id"],
                "shopper_id": r["shopper_id"],
                "shopper_name": r["shopper_name"],
                "date": r["date"],
                "shopper_jia_name": r["shopper_jia_name"],
                "fenlei": r["fenlei"],
                "jiage": r["jiage"],
                "laiyuan": r["laiyuan"],
                "how_use": r["how_use"],
                "note": r["note"]
            })
        return result

    def get_daojus_by_shopper_id(self, shopper_id: int) -> list[dict]:
        """
        根据客户 ID 查询该客户所有账单记录
        返回列表，每条记录是 dict，包括完整日期时间
        """
        self.cursor.execute("""
                SELECT *
                FROM daojus
                WHERE shopper_id = ?
                ORDER BY date, id
            """, (shopper_id,))

        rows = self.cursor.fetchall()

        # 转成字典列表
        result = []
        for r in rows:
            result.append({
                "id": r["id"],
                "shopper_id": r["shopper_id"],
                "shopper_name": r["shopper_name"],
                "date": r["date"],
                "shopper_jia_name": r["shopper_jia_name"],
                "fenlei": r["fenlei"],
                "jiage": r["jiage"],
                "laiyuan": r["laiyuan"],
                "how_use": r["how_use"],
                "note": r["note"]
            })
        return result

    def get_shopper_random(self, limit=10) -> list[dict]:
        """随机获取若干客户"""
        self.cursor.execute("SELECT * FROM daojus")
        rows = self.cursor.fetchall()
        rows = random.sample(rows, min(len(rows), limit))
        result = []
        for c in rows:
            result.append({
                "id": c["id"],
                "shopper_id": c["shopper_id"],
                "shopper_name": c["shopper_name"],
                "date": c["date"],
                "shopper_jia_name": c["shopper_jia_name"],
                "fenlei": c["fenlei"],
                "jiage": c["jiage"],
                "laiyuan": c["laiyuan"],
                "how_use": r["how_use"],
                "note": c["note"]
            })
        return result

    def get_daojus(self,
                       date_str: str = None,
                       filter_mode: bool = True,
                       order_by: str = "date",
                       desc: bool = True,
                       limit: int = 100,
                       field_key: str = None,
                       text: str = None):
        """
        获取账单，可以指定日期、搜索条件、排序、数量
        :param date_str: 日期字符串 'YYYY-MM-DD'，None 表示查询全部
        :param filter_mode: 是否开启筛选（排序、数量限制）
        :param order_by: 排序字段（默认 id）
        :param desc: 是否倒序
        :param limit: 限制返回数量，None 表示全部
        :param field_key: 搜索字段，例如 'shopper'、'remark'
        :param text: 搜索关键字
        """
        valid_fields = {"service", "note", "payment_method",
                        "date", "fee", "cost", "profit", "shopper_name"}
        if order_by not in valid_fields:
            order_by = "date"
        if field_key and field_key not in valid_fields:
            field_key = None
        # 构建 WHERE 条件
        where_clauses = []
        params = []

        if date_str:
            where_clauses.append("date LIKE ?")
            params.append(f"{date_str}%")

        if field_key and text:
            print(field_key)
            where_clauses.append(f"{field_key} LIKE ?")
            params.append(f"%{text}%")

        where_clause = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

        if filter_mode:
            # 筛选模式
            order_clause = f"ORDER BY {order_by} {'DESC' if desc else 'ASC'}"
            limit_clause = f"LIMIT {limit}" if limit else ""
            query = f"""
                    SELECT * FROM daojus
                    {where_clause}
                    {order_clause}
                    {limit_clause}
                """
        else:
            # 默认行为
            query = f"""
                    SELECT * FROM daojus
                    {where_clause}
                    ORDER BY id
                """

        self.cursor.execute(query, params)
        rows = self.cursor.fetchall()
        return [dict(r) for r in rows]

    def get_latest_per_daoju_shoppingss(self, field_key=None, text=None):
        valid_fields = {
            "shopper_name", "xinghao", "date",
            "shopper_jia_name", "fenlei", "jiage",
            "laiyuan", "note"
        }

        where_clause = ""
        params = []

        if field_key and field_key in valid_fields and text:
            where_clause = f"WHERE s.{field_key} LIKE ?"
            params.append(f"%{text}%")

        query = f"""
            SELECT d.*
            FROM daojus d
            JOIN (
                SELECT shopper_id, MAX(date) AS max_date
                FROM daojus
                GROUP BY shopper_id
            ) t
            ON d.shopper_id = t.shopper_id AND d.date = t.max_date
            {where_clause}
        """
        self.cursor.execute(query, params)
        rows = self.cursor.fetchall()
        return [dict(r) for r in rows]
    def get_shopper_prices_by_date(self, shopper_id: str):
        query = """
            SELECT date, jiage
            FROM daojus
            WHERE shopper_id = ?
            ORDER BY date ASC
        """
        self.cursor.execute(query, (shopper_id,))
        rows = self.cursor.fetchall()
        return [(row["date"], row["jiage"]) for row in rows]

    """模拟生成"""

    def generate_fake_data(self, num_customers=10, start_date="2025-01-01", end_date="2025-01-10", max_billings_per_day=5):
        """
        随机生成客户和账单数据
        :param num_customers: 生成客户数量
        :param start_date: 开始日期（YYYY-MM-DD）
        :param end_date: 结束日期（YYYY-MM-DD）
        :param max_billings_per_day: 每天最大账单条数
        """

        # 一些随机候选
        names = ["张三", "李四", "王五", "赵六", "孙七", "周八", "吴九", "郑十"]
        titles = ["先生", "女士", "老板", "经理", "客户"]
        services = ["洗车", "打蜡", "保养", "美容", "维修", "贴膜", "轮胎更换"]
        payments = ["现金", "微信", "支付宝", "银行卡"]

        # 1. 生成客户
        customer_ids = []
        for _ in range(num_customers):
            name = random.choice(names) + random.choice("ABCDEFG")
            title = random.choice(titles)
            wechat = f"wx_{random.randint(10000, 99999)}"
            note = "测试客户"

            customer_id = self.insert_customer({
                "name": name,
                "title": title,
                "wechat": wechat,
                "note": note,
                "phones": [f"138{random.randint(10000000, 99999999)}"],
                "plates": [f"粤A{random.randint(10000, 99999)}"]
            })
            customer_ids.append((customer_id, name))

        print(f"生成客户 {len(customer_ids)} 个")

        # 2. 生成账单
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        delta = (end_dt - start_dt).days + 1

        for i in range(delta):
            current_date = start_dt + timedelta(days=i)
            billings = []
            num_bills = random.randint(1, max_billings_per_day)
            for _ in range(num_bills):
                customer_id, customer_name = random.choice(customer_ids)
                service = random.choice(services)
                fee = random.randint(50, 500)  # 收费
                cost = random.randint(20, fee)  # 成本不超过收费
                profit = fee - cost
                payment_method = random.choice(payments)
                note = "自动生成"

                billings.append({
                    "customer_id": customer_id,
                    "customer_name": customer_name,
                    "service": service,
                    "fee": fee,
                    "cost": cost,
                    "profit": profit,
                    "payment_method": payment_method,
                    "note": note,
                    "date": current_date.strftime("%Y-%m-%d %H:%M:%S")
                })

            self.save_day_billings(billings)

        print(f"生成账单 {delta} 天，已保存！")
    def creat_all(self):
        self.creat_kehu_table()
        self.creat_billing_table()
        self.creat_warranty_card_table()
        self.creat_daojus_table()
        self.creat_shoppings_table()

if __name__ == "__main__":
    db = DBManager("_internal/data/all.db")
    db.creat_all()
    ##清除表
    # db.cursor.execute("DROP TABLE IF EXISTS shoppingss")
    # # 创建
    # db.creat_shoppings_table()
    #随机生成数据
    # db.generate_fake_data(
    #     num_customers=20,  # 生成 20 个客户
    #     start_date="2025-05-01",  # 数据起始日期
    #     end_date="2025-08-31",  # 数据结束日期
    #     max_billings_per_day=8  # 每天最多 8 条账单
    # )

    # 查看表内内容
    # db.cursor.execute("SELECT id, shopper_name,shopper_id FROM shoppingss")
    # for r in db.cursor.fetchall():
    #     print(dict(r))
    # db.cursor.execute("SELECT id,customer_id,customer_name  FROM billings")
    # for r in db.cursor.fetchall():
    #     print(dict(r))



    # 读取今天的账单
    # 假设用户修改/新增后，得到新的账单列表
    # new_records = [
    #     {"customer_id": 1, "service": "hhh", "fee": 100, "cost": 70, "profit": 30, "payment_method": "现金", "note": "改价"},
    #     {"customer_id": 2, "service": "打蜡", "fee": 200, "cost": 150, "profit": 50, "payment_method": "微信", "note": "新增一条"}
    # ]
    # #
    # # 保存当天账单（覆盖旧的）
    # db.save_day_billings(new_records)
    # records = db.get_day_billings("2025-09-01")
    # print(records)


