import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QTextEdit, QComboBox, QFileDialog, QMessageBox
)
#pyinstaller -F -w -i _internal/use_resource/photo/tubiao.ico qs_contr.py
#pyinstaller open_window.spec
class SQLiteController(QWidget):
    def __init__(self):
        super().__init__()
        self.conn = None
        self.cursor = None
        self.current_table = None

        self.setWindowTitle("SQLite 控制器")
        self.resize(800, 600)

        layout = QVBoxLayout(self)

        # 文件选择
        file_layout = QHBoxLayout()
        self.file_edit = QLineEdit()
        btn_open = QPushButton("选择数据库文件")
        btn_open.clicked.connect(self.open_file)
        file_layout.addWidget(QLabel("数据库路径:"))
        file_layout.addWidget(self.file_edit)
        file_layout.addWidget(btn_open)
        layout.addLayout(file_layout)

        # 表选择
        table_layout = QHBoxLayout()
        self.table_combo = QComboBox()
        self.table_combo.currentTextChanged.connect(self.load_table_headers)
        btn_load_tables = QPushButton("加载表")
        btn_load_tables.clicked.connect(self.load_tables)
        table_layout.addWidget(QLabel("表名:"))
        table_layout.addWidget(self.table_combo)
        table_layout.addWidget(btn_load_tables)
        layout.addLayout(table_layout)

        # 表头选择
        header_layout = QHBoxLayout()
        self.header_combo = QComboBox()
        header_layout.addWidget(QLabel("表头:"))
        header_layout.addWidget(self.header_combo)
        layout.addLayout(header_layout)

        # 搜索框
        search_layout = QHBoxLayout()
        self.search_edit = QLineEdit()
        btn_search = QPushButton("查询")
        btn_search.clicked.connect(self.search_data)
        search_layout.addWidget(QLabel("搜索关键字:"))
        search_layout.addWidget(self.search_edit)
        search_layout.addWidget(btn_search)
        layout.addLayout(search_layout)

        # 文本展示
        self.text_area = QTextEdit()
        layout.addWidget(self.text_area)

        # 删除行
        delete_layout = QHBoxLayout()
        self.delete_edit = QLineEdit()
        btn_delete = QPushButton("按id删除行")
        btn_delete.clicked.connect(self.delete_row)
        delete_layout.addWidget(QLabel("输入 id:"))
        delete_layout.addWidget(self.delete_edit)
        delete_layout.addWidget(btn_delete)
        layout.addLayout(delete_layout)

    # 打开数据库文件
    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择数据库文件", "", "SQLite DB (*.db *.sqlite *.sqlite3);;All Files (*)")
        if path:
            self.file_edit.setText(path)
            self.conn = sqlite3.connect(path)
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()
            QMessageBox.information(self, "成功", f"已连接到数据库: {path}")

    # 加载表
    def load_tables(self):
        if not self.cursor:
            return
        self.table_combo.clear()
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [r[0] for r in self.cursor.fetchall()]
        self.table_combo.addItems(tables)

    # 加载表头
    def load_table_headers(self):
        if not self.cursor:
            return
        self.current_table = self.table_combo.currentText()
        if not self.current_table:
            return
        self.cursor.execute(f"PRAGMA table_info({self.current_table})")
        headers = [r[1] for r in self.cursor.fetchall()]
        self.header_combo.clear()
        self.header_combo.addItems(headers)

    # 查询
    def search_data(self):
        if not self.cursor or not self.current_table:
            return
        column = self.header_combo.currentText()
        keyword = self.search_edit.text()
        sql = f"SELECT * FROM {self.current_table} WHERE {column} LIKE ?"
        self.cursor.execute(sql, (f"%{keyword}%",))
        rows = self.cursor.fetchall()
        self.text_area.clear()
        for row in rows:
            self.text_area.append(str(dict(row)))
        if not rows:
            self.text_area.append("无匹配结果")

    # 删除
    def delete_row(self):
        if not self.cursor or not self.current_table:
            return
        row_id = self.delete_edit.text()
        if not row_id.isdigit():
            QMessageBox.warning(self, "错误", "id 必须是数字")
            return
        self.cursor.execute(f"DELETE FROM {self.current_table} WHERE id=?", (row_id,))
        self.conn.commit()
        QMessageBox.information(self, "成功", f"已删除 id={row_id} 的行")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = SQLiteController()
    w.show()
    sys.exit(app.exec_())
