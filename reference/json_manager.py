import json
import atexit
import os

class JsonManager:
    _instances = {}  # 每个路径一个实例

    def __new__(cls, path="data.json", default_data=None):
        abs_path = os.path.abspath(path)
        if abs_path not in cls._instances:
            instance = super().__new__(cls)
            instance._initialized = False
            cls._instances[abs_path] = instance
        return cls._instances[abs_path]

    def __init__(self, path="data.json", default_data=None):
        if self._initialized:
            return
        self.path = os.path.abspath(path)
        self.default_data = default_data or {}
        self.data = {}

        self._load()
        atexit.register(self._save)
        self._initialized = True

    def _load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
            except json.JSONDecodeError:
                print(f"[JsonManager] 文件格式错误：{self.path}，将使用默认数据。")
                self.data = self.default_data.copy()
        else:
            print(f"[JsonManager] 文件不存在，创建默认数据：{self.path}")
            self.data = self.default_data.copy()

    def _save(self):
        try:
            with open(self.path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=4, ensure_ascii=False)
                print(f"[JsonManager] 自动保存：{self.path}")
        except Exception as e:
            print(f"[JsonManager] 保存失败：{e}")

    def get(self, key, default=None):
        return self.data.get(key, default)
    def get_set(self,path):
        keys = path.split("/")
        if len(keys) == 2:
            top_key, sub_key = keys
            if self.check(top_key):
                old_value = self.get(top_key)
                if sub_key in old_value:
                    return old_value[sub_key]["default"]
                else:
                    print(path)
                    print("没有找到枝干")
                    return None
            else:
                print("没有找到主干")
                return None
        else:
            print(f"{path}--路径格式错误")
            return None
    def get_opt(self,path):
        keys = path.split("/")
        if len(keys) == 2:
            top_key, sub_key = keys
            if self.check(top_key):
                old_value = self.get(top_key)
                if sub_key in old_value:
                    return old_value[sub_key]["options"]
                else:
                    print(path)
                    print("没有找到枝干")
                    return None
            else:
                print("没有找到主干")
                return None
        else:
            print("路径格式错误")
            return None
    def set_set(self,path,new_value):
        keys = path.split("/")
        if len(keys) == 2:
            top_key, sub_key = keys
            if self.check(top_key):
                old_value = self.get(top_key)
                if sub_key in old_value:
                    old_value[sub_key]["default"] = new_value
                    self.set(top_key, old_value)
    def set_dic(self,path,new_value):
        keys = path.split("/")
        if len(keys) == 2:
            top_key, sub_key = keys
            if self.check(top_key):
                old_value = self.get(top_key)
                old_value[sub_key] = new_value
                self.set(top_key, old_value)
    def del_dic(self,path):
        keys = path.split("/")
        if len(keys) == 2:
            top_key, sub_key = keys
            if self.check(top_key):
                old_value = self.get(top_key)
                del old_value[sub_key]
                self.set(top_key, old_value)
    def get_dic(self,path):
        keys = path.split("/")
        if len(keys) == 2:
            top_key, sub_key = keys
            if self.check(top_key):
                old_value = self.get(top_key)
                if sub_key in old_value:
                    return old_value[sub_key]
                else:
                    print("没有找到枝干")
                    return None
            else:
                print("没有找到主干")
                return None
        else:
            print("路径格式错误")
            return None

    def check(self,key):
        if key in self.data:
            return True
        else:
            return False
    def deep_check(self,key):
        if self.check(key):
            if self.data[key]:
                return True
            else:
                return False
        else:
            return False

    def set(self, key, value):
        self.data[key] = value

    def delete(self, key):
        if key in self.data:
            del self.data[key]

    def update_set(self, changes: dict):
        for key, value in changes.items():
            self.set_set(key, value)
