"""
资源管理器 — 统一资源路径解析 + 可选的机密文件加解密。

目录结构:
  app/assets/
  ├── images/        # 图片
  ├── fonts/         # 字体
  ├── data/          # 通用数据文件
  ├── secure/        # 加密存储 (.enc 文件)
  └── .key           # 加密密钥（git-ignored）

用法:
  from app.assets import resources

  # 公开资源
  path = resources.path("images/logo.png")
  data = resources.read("data/config.json")

  # 机密资源（自动解密 .enc 文件）
  data = resources.read_secure("api_key.txt")

  # 加密文件（开发时用）
  resources.encrypt_file("secret.png", "secure/secret.png.enc")
"""

import os
import hashlib
import secrets
import struct

_ASSETS_DIR = os.path.dirname(os.path.abspath(__file__))
_KEY_FILE = os.path.join(_ASSETS_DIR, ".key")
_KEY_LENGTH = 32
_NONCE_LENGTH = 16
_HMAC_LENGTH = 32


# ── 密钥管理 ────────────────────────────────────────────

def _derive_key(master_key: bytes, salt: bytes) -> bytes:
    """PBKDF2 派生 AES 级密钥（32 字节）。"""
    return hashlib.pbkdf2_hmac("sha256", master_key, salt, 100000, dklen=_KEY_LENGTH)


def _generate_key() -> bytes:
    """生成随机主密钥。"""
    return secrets.token_bytes(_KEY_LENGTH)


# ── XOR 流加密 ──────────────────────────────────────────

def _xor_encrypt(plaintext: bytes, key: bytes, nonce: bytes) -> bytes:
    """XOR 流加密：key_stream = SHA-256(key + nonce + counter)。"""
    result = bytearray(len(plaintext))
    block_size = 32  # SHA-256 output size
    for i in range(0, len(plaintext), block_size):
        counter = struct.pack(">I", i // block_size)
        keystream = hashlib.sha256(key + nonce + counter).digest()
        for j in range(min(block_size, len(plaintext) - i)):
            result[i + j] = plaintext[i + j] ^ keystream[j]
    return bytes(result)


def _encrypt(plaintext: bytes, master_key: bytes) -> bytes:
    """加密：nonce + hmac + ciphertext"""
    nonce = secrets.token_bytes(_NONCE_LENGTH)
    derived = _derive_key(master_key, nonce)
    enc_key = derived[:_KEY_LENGTH // 2]
    mac_key = derived[_KEY_LENGTH // 2:]
    ciphertext = _xor_encrypt(plaintext, enc_key, nonce)
    hmac = hashlib.sha256(mac_key + ciphertext).digest()
    return nonce + hmac + ciphertext


def _decrypt(payload: bytes, master_key: bytes) -> bytes:
    """解密：nonce + hmac + ciphertext → plaintext"""
    nonce = payload[:_NONCE_LENGTH]
    hmac_received = payload[_NONCE_LENGTH:_NONCE_LENGTH + _HMAC_LENGTH]
    ciphertext = payload[_NONCE_LENGTH + _HMAC_LENGTH:]
    derived = _derive_key(master_key, nonce)
    enc_key = derived[:_KEY_LENGTH // 2]
    mac_key = derived[_KEY_LENGTH // 2:]
    hmac_expected = hashlib.sha256(mac_key + ciphertext).digest()
    if not secrets.compare_digest(hmac_received, hmac_expected):
        raise ValueError("资源解密失败：HMAC 校验不通过，文件可能被篡改或密钥错误")
    return _xor_encrypt(ciphertext, enc_key, nonce)


# ── 资源管理器 ───────────────────────────────────────────

class ResourceManager:
    """统一资源访问：路径解析 + 可选加解密。"""

    def __init__(self):
        self._key = None
        self._key_loaded = False

    # ── 公开 API ─────────────────────────────────────────

    def path(self, relative_path: str) -> str:
        """解析资源绝对路径。
        relative_path 相对于 app/assets/，如 "images/logo.png"。
        """
        return os.path.join(_ASSETS_DIR, relative_path)

    def read(self, relative_path: str) -> bytes:
        """读取公开资源的二进制内容。"""
        full = self.path(relative_path)
        if not os.path.exists(full):
            raise FileNotFoundError(f"资源不存在: {relative_path}")
        with open(full, "rb") as f:
            return f.read()

    def read_text(self, relative_path: str, encoding="utf-8") -> str:
        """读取公开资源的文本内容。"""
        return self.read(relative_path).decode(encoding)

    def exists(self, relative_path: str) -> bool:
        """检查资源是否存在。"""
        return os.path.exists(self.path(relative_path))

    # ── 加密资源 ─────────────────────────────────────────

    def read_secure(self, relative_path: str) -> bytes:
        """读取加密资源（.enc 文件），自动解密。"""
        full = self.path(relative_path)
        if not os.path.exists(full):
            raise FileNotFoundError(f"加密资源不存在: {relative_path}")
        with open(full, "rb") as f:
            payload = f.read()
        return _decrypt(payload, self._load_key())

    def read_secure_text(self, relative_path: str, encoding="utf-8") -> str:
        """读取加密资源的文本内容。"""
        return self.read_secure(relative_path).decode(encoding)

    def encrypt_file(self, source_path: str, dest_relative: str):
        """加密文件并存入 secure/ 目录。
        source_path: 原始文件绝对路径
        dest_relative: 相对于 app/assets/ 的目标路径，如 "secure/api_key.txt.enc"
        """
        with open(source_path, "rb") as f:
            plaintext = f.read()
        payload = _encrypt(plaintext, self._load_key())
        dest_full = self.path(dest_relative)
        os.makedirs(os.path.dirname(dest_full), exist_ok=True)
        with open(dest_full, "wb") as f:
            f.write(payload)

    def has_key(self) -> bool:
        """检查密钥是否已配置。"""
        return os.path.exists(_KEY_FILE)

    def init_key(self):
        """生成新密钥文件（首次使用时调用）。"""
        if os.path.exists(_KEY_FILE):
            raise FileExistsError(f"密钥文件已存在: {_KEY_FILE}")
        key = _generate_key()
        with open(_KEY_FILE, "wb") as f:
            f.write(key)

    # ── 内部 ─────────────────────────────────────────────

    def _load_key(self) -> bytes:
        if self._key_loaded:
            return self._key
        if os.path.exists(_KEY_FILE):
            with open(_KEY_FILE, "rb") as f:
                self._key = f.read()
        else:
            raise FileNotFoundError(
                f"密钥文件不存在: {_KEY_FILE}\n"
                f"请先运行 resources.init_key() 生成密钥，"
                f"或在开发环境设置 RESOURCE_KEY 环境变量"
            )
        self._key_loaded = True
        return self._key


# 全局单例
resources = ResourceManager()
