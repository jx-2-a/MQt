import re
from PyQt5.QtWidgets import QWidget
from json_manager import JsonManager

# 全局配置对象
config = JsonManager("_internal/jsons/setting.json")


class ConfigStyleBinder:
    """
    全局共享样式绑定器
    占位符语法：
        {{配置路径[:默认值]}}
    单位直接写在模板外面
    """
    PLACEHOLDER_PATTERN = re.compile(r"\{\{([^}:]+)(:([^}]+))?\}\}")

    _bindings = {}       # {name: {"widget": widget, "template": template}}
    _func_bindings = {} # 通用函数绑定

    # ----------------- 样式表绑定 -----------------
    @classmethod
    def bind(cls, name: str, widget: QWidget, template: str):
        """
        绑定控件和样式模板
        :param name: 人为编号/名称
        :param widget: 控件对象
        :param template: 样式模板字符串
        """
        cls._bindings[name] = {"widget": widget, "template": template}
        cls.apply(name)

    @classmethod
    def apply(cls, name: str):
        """应用样式到指定控件"""
        binding = cls._bindings.get(name)
        if not binding:
            return
        widget = binding["widget"]
        template = binding["template"]

        def replace(match):
            path = match.group(1).strip()
            default = match.group(3)
            val = config.get_set(path)
            result = str(val) if val is not None else (default or "")
            # print(f"[DEBUG] 替换占位符: {path} -> {result!r}")
            return result

        qss = cls.PLACEHOLDER_PATTERN.sub(replace, template)
        widget.setStyleSheet(qss)

    # ----------------- 刷新统一接口 -----------------
    @classmethod
    def refresh(cls, name: str = None):
        """
        刷新控件样式和函数
        :param name: 指定名称刷新，如果为 None 则刷新所有绑定控件
        """
        if name:
            cls.apply(name)
        else:
            for n in cls._bindings:
                cls.apply(n)
    # ----------------- 完全通用函数绑定 -----------------
    @classmethod
    def bind_function(cls, name: str, func, **param_values):
        """
        注册任意函数
        :param name: 唯一名称
        :param func: 可调用对象
        :param param_values: 函数的形参及对应值
        """
        cls._func_bindings[name] = {"func": func, "params": param_values}

    @classmethod
    def call_function(cls, name: str, override_params: dict = None):
        """
        调用注册函数
        :param name: 函数名称
        :param override_params: 可覆盖的参数字典
        """
        binding = cls._func_bindings.get(name)
        if not binding:
            print(f"[WARN] 函数 {name} 未注册")
            return
        func = binding["func"]
        params = dict(binding["params"])
        if override_params:
            params.update(override_params)
        try:
            func(**params)
        except Exception as e:
            print(f"[ERROR] 调用函数 {name} 出错: {e}")