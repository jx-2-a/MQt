# 动作注册表 — Agent 扩展指南

## 概述

动作注册表 (`app/core/action_registry.py`) 是事件系统的核心。每个"动作"是一个可复用的 Python 代码模板，用户通过事件编辑器对话框选择动作 + 填写参数，系统自动生成代码并绑定到控件事件上。

## 核心概念

- **ActionDef**：动作定义，包含 id、名称、描述、分类、参数列表、代码模板
- **ActionParam**：参数定义，包含名称、类型（string/widget_ref/choice/number/bool）、标签、默认值
- **事件类型**：分为鼠标事件（enter/leave/click/right_click 等）和信号事件（changed/clicked/toggled 等）

## 预注册动作分类

| 分类 | 说明 | 适用范围 |
|---|---|---|
| `通用` | 打印、弹窗、自定义代码 | 所有控件 |
| `窗口` | 关闭/最小化/最大化/全屏 | 所有控件 |
| `控件操作` | 切换可见性、启用/禁用、设置文本 | 所有控件，需 widget_ref 参数 |
| `控件专用` | 各控件类型的特有操作 | 仅对特定控件类型可见 |

## 如何为新控件注册专属动作

### 1. 导入 API

```python
from app.core.action_registry import ActionDef, ActionParam, register_widget_actions
```

### 2. 定义动作

每个动作需要一个唯一的 `action_id`、中文名称、描述、参数和代码模板。

```python
P = ActionParam  # 快捷方式

actions = [
    ActionDef(
        "mywidget_do_something",           # 唯一 ID
        "执行某操作",                       # 中文名称（在动作列表中显示）
        "对目标控件执行某操作的详细说明",     # 描述（hover 提示）
        "控件专用",                          # 分类
        [                                   # 参数列表
            P("target", "widget_ref", "目标控件"),
            P("value", "number", "数值", "0"),
            P("text", "string", "文本", ""),
        ],
        "find_widget('{target}').do_something({value}, '{text}')",  # 代码模板
    ),
]
```

### 3. 参数类型说明

| param_type | UI 控件 | 占位替换 |
|---|---|---|
| `string` | QLineEdit | `'{param}'` 带引号 |
| `widget_ref` | QComboBox（列出布局中所有具名控件） | `'{param}'` 不带引号 |
| `choice` | QComboBox（固定选项） | `'{param}'` |
| `number` | QSpinBox | `{param}` 不带引号 |
| `bool` | QCheckBox | `{param}` True/False |

### 4. 代码模板规则

模板使用 Python `str.format()` 填充：
- `{target}` → 用户选择的控件名（widget_ref 类型）
- `{value}` → 用户输入的数值
- `{text}` → 用户输入的文本（已做单引号转义）
- `{source}` → 特殊值，代表"触发源控件自身"

可用辅助函数：
- `find_widget(name)` — 按 objectName 查找窗口中的任意控件
- `widget` / `self` — 触发事件的控件本身
- `window` — 所在窗口对象

### 5. 注册

```python
register_widget_actions("MyWidgetType", actions)
```

注意：`widget_type` 必须与 `layout_engine.py` 中 `BUILDERS` 字典的 key 一致。

## 如何添加新的事件类型

### 鼠标/通用事件

在 `app/core/layout_engine.py` 的 `_MOUSE_EVENTS` 集合中添加新的 key，然后在 `_EventHandler.eventFilter()` 中添加对应的 Qt 事件映射。

```python
_MOUSE_EVENTS = {"enter", "leave", "click", "double_click", "hover", "drag", "right_click", "my_new_event"}
```

### 信号级事件

在 `app/core/layout_engine.py` 的 `_SIGNAL_MAP` 中添加映射：

```python
_SIGNAL_MAP = {
    # ...
    "my_new_event": {
        "Button": "customSignal",
        "ComboBox": "customSignal",
    },
}
```

同时在 `app/core/action_registry.py` 的 `_SIGNAL_MAP` 中添加相同映射（两个文件各自维护一份，layout_engine 不导入 action_registry 以保证无循环依赖）。

## 事件执行流程

```
用户交互 → Qt 事件/信号
         → eventFilter / signal handler
         → exec(code, scope)
         → scope = {widget, self, find_widget, window, app}
         → 代码执行（可访问 find_widget 跨控件操作）
```

## 文件清单

| 文件 | 职责 |
|---|---|
| `app/core/action_registry.py` | 动作定义 + 注册 API + 代码生成 |
| `app/core/layout_engine.py` | 事件绑定 + exec 执行（独立维护 SIGNAL_MAP） |
| `app/ui/event_editor.py` | 事件编辑器对话框 UI |
| `app/ui/widget_controller.py` | 布局控制器（事件列表 + 编辑入口） |
