# 全局注册表
registry = {}

def register(obj, name=None):
    """
    注册对象到全局 registry
    obj: 要注册的对象（变量、函数、类实例等）
    name: 注册名，默认使用对象的 __name__ 或自定义
    """
    key = name or getattr(obj, "__name__", None)
    if key is None:
        raise ValueError("必须提供 name 参数或者对象有 __name__ 属性")
    registry[key] = obj
    return obj  # 支持装饰器链式调用

def update_register(name, obj):
    """更新已注册对象"""
    if name not in registry:
        raise KeyError(f"{name} 未注册，无法更新")
    registry[name] = obj

def add_register(name, obj):
    """更新已注册对象"""
    if name not in registry:
        raise KeyError(f"{name} 未注册，无法更新")
    registry[name].append(obj)
    return obj
def remove_register(name, obj):
    """删除已注册对象"""
    if name not in registry:
        raise KeyError(f"{name} 未注册，无法删除")

    try:
        registry[name].remove(obj)  # 从列表中移除第一个匹配的 obj
        # 如果列表空了，可以选择是否自动删除该 key
        # if not registry[name]:
        #     del registry[name]
    except ValueError:
        raise ValueError(f"{obj} 不在 {name} 的注册列表中")
