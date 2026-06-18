# 复杂控件手册

复杂控件存放组合多个基础控件的复合型控件，分两类：

**`app/ui/complex_widgets/`** — 有模板系统的重型复合控件（DraggableLabel 等）
**`app/ui/widgets/form_row.py` + `form_container.py`** — 轻量 HV 布局容器

---

## FormRow

### 概述

水平行容器（对应 reference 中的 `RowWidget`）。控件从左到右排列，末尾自动弹簧。子控件插入时自动放到弹簧前面。

### 公开 API

| 方法 | 说明 |
|------|------|
| `add_widget(widget)` | 在弹簧前插入控件 |
| `add_stretch()` | 行尾追加弹簧 |
| `clear()` | 清空整行所有控件 |

### layout.json 用法

```json
{
    "type": "FormRow",
    "name": "row_1",
    "spacing": 40,
    "children": [
        {"type": "Label", "label": "名称:"},
        {"type": "LineEdit", "name": "name_input"}
    ]
}
```

---

## FormContainer

### 概述

垂直滚动表单容器（对应 reference 中的 `VerticalContainer`）。内嵌 QScrollArea，管理多行 FormRow，内容超出时自动显示滚动条。

### 公开 API

| 方法 | 说明 |
|------|------|
| `add_widget(widget, new_row=False)` | 添加到当前行（默认），new_row=True 则创建新行 |
| `add_row() -> FormRow` | 创建空行并返回 |
| `add_stretch()` | 末尾追加弹簧 |
| `clear()` | 清空所有行和控件 |

### layout.json 用法

```json
{
    "type": "FormContainer",
    "name": "settings_form",
    "row_spacing": 20,
    "margin": 10,
    "children": [
        {"type": "Label", "label": "设置项"},
        {"type": "LineEdit", "name": "setting_input"}
    ]
}
```

---

## DraggableLabel

### 概述

可拖拽的复合标签控件。继承 `CompositeWidget`，固定内部布局为 **图标 + 文本**。
三个功能维度可同时启用：图标、文本、按钮行为（点击信号），加上独立的拖拽开关。

### 槽位

| 槽位名 | 类型 | 选择器 | 说明 |
|--------|------|--------|------|
| `icon` | QLabel | `#icon` | 图标/图片显示区 |
| `text` | QLabel | `#text` | 文本显示区，自适应宽度 |

### 默认样式（Python 硬编码基线）

| 目标 | 属性 | 默认值 |
|------|------|--------|
| **控件自身** | background_color | `#2d2d30` |
| | border | `1px solid #3e3e42` |
| | border_radius | `6px` |
| | padding | `4px 8px` |
| | margin | `2px` |
| **图标 (#icon)** | background_color | `transparent` |
| | border_radius | `2px` |
| **文本 (#text)** | font_family | `Microsoft YaHei` |
| | font_size | `14px` |
| | color | `#cccccc` |
| | font_weight | `normal` |

### 模板完整结构

```python
template = {
    "icon": {
        "src": "icon.png",
        "width": 24,
        "height": 24,
        "visible": True,
        "style": {
            "background_color": "transparent",
            "border_radius": "4px",
        },
    },
    "text": {
        "content": "标签文字",
        "visible": True,
        "style": {
            "font_family": "Microsoft YaHei",
            "font_size": "14px",
            "color": "#ffffff",
            "font_weight": "bold",
        },
    },
    "button": {"enabled": True},
    "drag":   {"enabled": True},
    "style": {
        "background_color": "#3c3c3c",
        "border": "1px solid #555",
        "border_radius": "8px",
        "padding": "6px 12px",
    },
}
```

### 公开 API

| 方法 | 说明 |
|------|------|
| `set_template(template)` | 应用完整模板（与默认值深度合并） |
| `template() -> dict` | 返回当前模板深拷贝 |
| `update_template(partial)` | 合并更新部分项（粒度到 style 内单属性） |
| `set_text(text)` | 便捷设置文本 |
| `text() -> str` | 获取文本 |
| `set_icon(src, w, h)` | 便捷设置图标 |
| `set_button_enabled(bool)` | 启用/禁用按钮点击 |
| `is_button_enabled() -> bool` | 查询按钮状态 |
| `set_drag_enabled(bool)` | 启用/禁用拖拽 |
| `is_drag_enabled() -> bool` | 查询拖拽状态 |

### 信号

| 信号 | 触发条件 |
|------|---------|
| `clicked()` | `button.enabled=True` 时，鼠标在控件范围内释放触发 |

### layout.json 用法

```json
{
    "type": "VBox",
    "children": [{
        "type": "DraggableLabel",
        "name": "drag_title",
        "template": {
            "icon": {"src": "logo.png", "width": 24, "height": 24, "visible": true,
                     "style": {"border_radius": "4px"}},
            "text": {"content": "拖拽标题", "visible": true,
                     "style": {"color": "#fff", "font_size": "16px"}},
            "button": {"enabled": true},
            "drag": {"enabled": true},
            "style": {"background_color": "#333", "border_radius": "8px"}
        }
    }]
}
```

传统简写字段也兼容（自动合成模板）：
```json
{
    "type": "DraggableLabel",
    "name": "drag_1",
    "label": "拖我",
    "icon": "icon.png",
    "button_enabled": true,
    "drag_enabled": true
}
```

### 代码使用示例

```python
from app.ui.complex_widgets import DraggableLabel

# 三部分全开：图标 + 文本 + 按钮点击
lbl = DraggableLabel(template={
    "icon": {"src": "info.png", "width": 20, "height": 20, "visible": True},
    "text": {"content": "拖我移动", "visible": True,
             "style": {"color": "#ffffff", "font_weight": "bold"}},
    "button": {"enabled": True},
    "drag": {"enabled": True},
})
lbl.clicked.connect(lambda: print("clicked"))

# 运行时更新单属性（深度合并）
lbl.update_template({"text": {"style": {"color": "#ff6600"}}})
lbl.update_template({"style": {"border_radius": "12px"}})

# 查询当前完整状态
print(lbl.template())
```
