import os
import json
import base64
import time
import hmac
import hashlib
from dataclasses import dataclass
from json_manager import JsonManager
try:
    from PyQt5.QtCore import pyqtSignal, Qt
    from PyQt5.QtWidgets import (
        QApplication, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QLineEdit, QPushButton
    )
    PYQT_VER = 5
except ImportError:
    from PyQt6.QtCore import pyqtSignal, Qt
    from PyQt6.QtWidgets import (
        QApplication, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QLineEdit, QPushButton
    )
    from PyQt6.QtCore import Qt as QtEnum
    Qt = QtEnum
    PYQT_VER = 6

DEFAULT_ITERATIONS = 200_000
DEFAULT_SALT_BYTES = 16
DEFAULT_KEY_BYTES = 32

# 固定密码文件路径，改为相对路径
FIXED_SECRET_PATH = os.path.join("_internal", "jsons", "denglu.json")

@dataclass
class StoredSecret:
    salt_b64: str
    hash_b64: str
    iterations: int
    created_at: float

    @staticmethod
    def from_dict(d: dict) -> "StoredSecret":
        return StoredSecret(
            salt_b64=d["salt"],
            hash_b64=d["hash"],
            iterations=int(d.get("iterations", DEFAULT_ITERATIONS)),
            created_at=float(d.get("created_at", 0.0)),
        )

    def to_dict(self) -> dict:
        return {
            "salt": self.salt_b64,
            "hash": self.hash_b64,
            "iterations": self.iterations,
            "created_at": self.created_at,
        }

class PasswordManager:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self._secret: StoredSecret | None = None
        self._load()

    def _load(self):
        if not os.path.exists(self.filepath):
            self._secret = None
            return
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._secret = StoredSecret.from_dict(data)
        except Exception:
            self._secret = None

    def _save(self):
        if self._secret is None:
            return
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(self._secret.to_dict(), f, ensure_ascii=False, indent=2)

    @staticmethod
    def _derive(password: str, salt: bytes, iterations: int) -> bytes:
        return hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            iterations,
            dklen=DEFAULT_KEY_BYTES,
        )

    def has_password(self) -> bool:
        return self._secret is not None

    def create_or_reset_password(self, password: str, iterations: int = DEFAULT_ITERATIONS):
        salt = os.urandom(DEFAULT_SALT_BYTES)
        key = self._derive(password, salt, iterations)
        self._secret = StoredSecret(
            salt_b64=base64.b64encode(salt).decode("ascii"),
            hash_b64=base64.b64encode(key).decode("ascii"),
            iterations=iterations,
            created_at=time.time(),
        )
        self._save()

    def verify(self, password: str) -> bool:
        if self._secret is None:
            return False
        salt = base64.b64decode(self._secret.salt_b64)
        expect = base64.b64decode(self._secret.hash_b64)
        got = self._derive(password, salt, self._secret.iterations)
        return hmac.compare_digest(expect, got)

class PasswordWidget(QWidget):
    login_successful = pyqtSignal(str)
    login_failed = pyqtSignal()
    password_set = pyqtSignal(str)

    def __init__(self, parent, callback, width, height):
        super().__init__(parent)
        self.config = JsonManager("_internal/jsons/setting.json")
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
        self.secret_path = FIXED_SECRET_PATH
        self.manager = PasswordManager(self.secret_path)
        self.callback = callback
        self._build_ui()
        self._refresh_mode()

    def _build_ui(self):
        self.setWindowTitle("登录密码")
        root = QVBoxLayout(self)

        pwd_row = QHBoxLayout()
        self.input = QLineEdit()
        self.input.setPlaceholderText("请输入密码…")
        self.input.setEchoMode(QLineEdit.Password)
        self.toggle_btn = QPushButton("显示")
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.toggled.connect(self._toggle_echo)
        pwd_row.addWidget(QLabel("密码："))
        pwd_row.addWidget(self.input, 1)
        pwd_row.addWidget(self.toggle_btn)
        root.addLayout(pwd_row)

        self.confirm_container = QWidget()
        confirm_row = QHBoxLayout(self.confirm_container)
        self.confirm = QLineEdit()
        self.confirm.setPlaceholderText("再次输入密码…")
        self.confirm.setEchoMode(QLineEdit.Password)
        confirm_row.addWidget(QLabel("确认："))
        confirm_row.addWidget(self.confirm, 1)
        root.addWidget(self.confirm_container)

        btn_row = QHBoxLayout()
        self.action_btn = QPushButton()
        self.action_btn.clicked.connect(self._on_action)
        self.change_btn = QPushButton("取消")
        self.change_btn.clicked.connect(self._on_change_password)
        btn_row.addWidget(self.action_btn)
        btn_row.addWidget(self.change_btn)
        root.addLayout(btn_row)

        self.status = QLabel()
        root.addWidget(self.status)

        self.input.returnPressed.connect(self._on_action)
        self.confirm.returnPressed.connect(self._on_action)

        self.setLayout(root)

    def _toggle_echo(self, checked: bool):
        mode = QLineEdit.Normal if checked else QLineEdit.Password
        self.input.setEchoMode(mode)
        if self.confirm.isVisible():
            self.confirm.setEchoMode(mode)
        self.toggle_btn.setText("隐藏" if checked else "显示")

    def _refresh_mode(self):
        has_pwd = self.manager.has_password()
        if not has_pwd:
            self._error("密码文件不存在，无法登录。")
            return None
        self.confirm_container.setVisible(not has_pwd)
        # self.change_btn.setVisible(has_pwd)
        self.action_btn.setText("登录" if has_pwd else "设置密码并登录")
        self.status.setText("已设置密码，输入后点击登录。" if has_pwd else "首次使用：请设置一个新密码。")
        self.input.clear()
        self.confirm.clear()

    def _on_action(self):
        if not self.manager.has_password():
            p1 = self.input.text()
            p2 = self.confirm.text()
            if len(p1) < 6:
                self._error("密码长度至少 6 位。")
                return
            if p1 != p2:
                self._error("两次输入不一致。")
                return
            self.manager.create_or_reset_password(p1)
            self._ok("密码已设置并保存。")
            self.password_set.emit(self.secret_path)
            self.login_successful.emit(self.secret_path)
            self._refresh_mode()
        else:
            p = self.input.text()
            if self.manager.verify(p):
                self._ok("登录成功。")
                self.login_successful.emit(self.secret_path)
                self.callback(["加载页面","page_main"])
            else:
                self._error("密码错误。")
                self.login_failed.emit()

    def _on_change_password(self):
        QApplication.instance().quit()
        # if not self.manager.has_password():
        #     return
        # old = self.input.text()
        # if not self.manager.verify(old):
        #     self._error("原密码不正确。先在上方输入原密码。")
        #     return
        # new1, ok1 = self._prompt_text("输入新密码：")
        # if not ok1 or not new1:
        #     return
        # if len(new1) < 6:
        #     self._error("密码长度至少 6 位。")
        #     return
        # new2, ok2 = self._prompt_text("再次输入新密码：")
        # if not ok2 or new1 != new2:
        #     self._error("两次输入不一致。")
        #     return
        # self.manager.create_or_reset_password(new1)
        # self._ok("密码已修改。")
        # self.password_set.emit(self.secret_path)
        # self._refresh_mode()

    def _ok(self, msg: str):
        self.status.setStyleSheet("color: green;")
        self.status.setText(msg)


    def _error(self, msg: str):
        self.status.setStyleSheet("color: red;")
        self.status.setText(msg)

    def _prompt_text(self, title: str) -> tuple[str, bool]:
        dlg = QWidget()
        dlg.setWindowTitle(title)
        lay = QVBoxLayout(dlg)
        edit = QLineEdit()
        edit.setEchoMode(QLineEdit.Password)
        btns = QHBoxLayout()
        okb = QPushButton("确定")
        cb = QPushButton("取消")
        btns.addWidget(okb)
        btns.addWidget(cb)
        lay.addWidget(QLabel(title))
        lay.addWidget(edit)
        lay.addLayout(btns)
        ret = {"ok": False, "text": ""}

        def on_ok():
            ret["ok"] = True
            ret["text"] = edit.text()
            dlg.close()

        def on_cancel():
            ret["ok"] = False
            dlg.close()

        okb.clicked.connect(on_ok)
        cb.clicked.connect(on_cancel)
        edit.returnPressed.connect(on_ok)
        dlg.setWindowModality(Qt.ApplicationModal)
        dlg.resize(360, 120)
        dlg.show()
        app = QApplication.instance()
        while dlg.isVisible():
            app.processEvents()
        return ret["text"], ret["ok"]

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    w = PasswordWidget()
    w.resize(520, 180)
    w.show()
    sys.exit(app.exec())
