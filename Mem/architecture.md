# 工作架构

## 概述
基于 PyQt5 的配置驱动窗口管理系统。窗口样式由 `settings.json` 控制，内部控件布局由 `layout.json` 树结构描述，通过布局引擎动态构建。任何窗口通过 `layout` 字段自动渲染控件树。布局与窗口解耦，支持独立布局创建和页面切换。样式由 `styles.json` 四级级联（global→types→windows→widgets）控制，style_engine 生成组合 QSS 一次性应用。

## 依赖库

| 库 | 版本要求 | 功能 | 关键接口 |
|---|---|---|---|
| PyQt5 | >=5.15 | Qt GUI 框架，提供窗口/控件/布局/QSS | `QApplication`, `QMainWindow`, `QWidget` |

## 模块架构

见 [file-tree.md](file-tree.md)

## 各模块功能与接口

### 1. app/core/window_config.py — 窗口配置管理
- `load_config() -> dict` — 读取 settings.json
- `save_config(data)` — 写入 settings.json
- `get_window_config(key) -> dict` — 获取窗口配置段
- `update_window_config(key, **kwargs)` — 更新配置项（geometry/opacity/frameless/title/background_color/layout）

### 2. app/core/layout_loader.py — 布局加载
- `load_layout(name) -> dict` — 从 layout.json 按名称加载布局树节点
- `load_all_layouts() -> dict` — 加载全部布局
- `save_layout(name, node)` — 保存布局树节点到 layout.json

### 3. app/core/layout_engine.py — 布局引擎
**职责**: 将布局树节点递归转换为 PyQt5 widget 树

**注册的控件类型（20种）**: VBox, HBox, HSplitter, VSplitter, ToolBar, Action, Label, TreeView, Form, Button, ComboBox, TextEdit, LineEdit, CheckBox, SpinBox, DoubleSpinBox, TabWidget, GroupBox, Slider, ProgressBar

**接口**:
- `build(node) -> QWidget | None` — 递归创建单个节点对应的 widget，自动绑定事件
- `apply_to_window(window, node)` — 构建根 widget 并设为 window 的 centralWidget
- `BUILDERS: dict` — 类型→构建函数的注册表
- `WIDGET_TYPE_OPTIONS: list` — 所有可用控件类型名称（供 UI 下拉选择）
- `_node_id(node, path)` — 有名用名，无名用 `md5(path|type|label)` 生成 `wXXXXXXX` 稳定标识
- `_EventHandler(QObject)` — 事件过滤器，拦截 6 种事件（enter/leave/click/double_click/hover/drag）
- `_bind_events(widget, node)` — 读取 `node["events"]` 安装事件过滤器

**构造时**: `build()` 设置 `widget.setProperty("layout_type", type)` 供样式引擎识别

**扩展**: 向 BUILDERS 注册新 type 即可支持新控件类型

### 4. app/ui/config_window.py — 配置驱动窗口基类
- 构造时从 settings.json 加载窗口样式（geometry/opacity/frameless/bg/layout）
- 若配置含 `layout` 字段，自动调用布局引擎渲染控件树
- showEvent 恢复位置 + 重新应用自身 QSS（隔离父窗口样式污染）+ 应用样式引擎
- closeEvent 保存位置

### 5. app/ui/main_window.py — 主窗口类
- 继承 ConfigWindow("main")，注册 Ctrl+Shift+L → WidgetController / Ctrl+Shift+S → StyleController
- `open_sub_window(config_key, title)` — 打开/复用子窗口

### 6. app/core/window_factory.py — 窗口工厂
- `create_main_window(title)` — 创建主窗口
- `open_sub_window(parent, title)` — 创建子窗口

### 7. app/ui/widget_controller.py — 布局控制器（元工具）

**设计原则**: 手动构建 UI（VSCode Dark+ QSS），不依赖 layout.json 自渲染。它是编辑 layout.json 的工具，不是被编辑的对象。

**UI 骨架**: `VBox(margin=0) → #topbar → QSplitter(1px, 左: #panel_header+QTreeWidget / 右: #panel_header+属性+事件+保存) → #statusbar(26px)`

**功能**:
- **布局管理**: ComboBox 切换/新建/删除 layout.json 中的布局
- **树形编辑**: 三列树视图（类型 | 名称 | 标签），展开/折叠节点
- **属性面板**: 类型下拉 + 名称输入 + 标签输入 → 保存
- **事件编辑**: 6 个 QLineEdit 对应 6 种交互事件（enter/leave/click/double_click/hover/drag）
- **节点操作**: +子节点 / −删除 / ↑上移 / ↓下移（工具栏按钮）
- **页面切换**: 窗口选择器 + "应用到窗口"按钮 → 即时切换布局
- **独立布局**: 创建不关联窗口的布局，通过静态方法按需加载
- **自动持久化**: 所有操作即时写入 layout.json

**双索引节点映射**:
- `_node_items: dict[id(node) → QTreeWidgetItem]` — 从数据找树项
- `_item_nodes: dict[id(item) → node]` — 从树项找数据（用 id() 因为 QTreeWidgetItem 不可哈希）

**公开 API**:
- `WidgetController.apply_layout(name, window=None)` — 加载布局到窗口（无窗口则自动创建）
- `WidgetController.switch_page(window, layout_name)` — 即时切换窗口页面，持久化到 settings.json

**已知约束**:
- 类型在容器↔叶子间切换时需重建树项（children 字段增删），其他情况原地更新
- 保存属性前检查旧类型，仅当容器/叶子身份变化时才触发 `_persist_and_reload`

**窗口发现**: 通过 `QApplication.topLevelWidgets()` 扫描（按 `_config_key` 匹配），不依赖 parent

### 8. app/ui/style_controller.py — 样式控制器（元工具）

**设计原则**: 与 WidgetController 同级，手动构建 UI（VSCode Dark+ QSS）。它是编辑 `config/styles.json` 的元工具。通过 `QApplication.topLevelWidgets()` 扫描目标窗口，不依赖 parent。

**UI 骨架**: 同 WidgetController — `VBox(margin=0) → #topbar → QSplitter → #statusbar`

**功能**:
- **布局选择**: 顶部栏 ComboBox 选择布局 → 树中展示该布局完整控件树
- **层级浏览**: 左面板树形展示 布局控件实例 → 全局样式 → 控件类型样式 → 窗口样式
- **属性编辑**: 选中节点后在右侧面板编辑其样式属性，动态按类型加载属性组
- **保存/应用**: `_commit_fields()` 公共入口（读表单→写内存→持久化），保存时自动应用
- **showEvent**: 每次显示时重新应用自身 QSS，隔离父窗口样式污染

**公开 API**:
- `StyleController.apply_styles(window_key)` — 对指定窗口应用其样式
- `StyleController.update_window(window)` — 运行时热更新窗口样式

### 9. app/ui/widgets/ — 独立控件库
每个控件独立文件、独立继承 Qt 基类，便于后续单独设置样式或功能扩展。

**容器类**: VBox/HBox(StyledBox), HSplitter/VSplitter(StyledSplitter), TabWidget(StyledTabWidget), GroupBox(StyledGroupBox), ToolBar(StyledToolBar)
**展示类**: Label(StyledLabel), TreeView(StyledTreeWidget), ProgressBar(StyledProgressBar)
**输入类**: Button(StyledButton), ComboBox(StyledComboBox), TextEdit(StyledTextEdit), LineEdit(StyledLineEdit), CheckBox(StyledCheckBox), SpinBox(StyledSpinBox), DoubleSpinBox(StyledDoubleSpinBox), Slider(StyledSlider), Form(StyledForm)

## 样式系统架构

### config/styles.json — 样式配置存储

四级级联结构:
```json
{
    "global": { "font_family": "Microsoft YaHei", "font_size": "14px", "color": "#333333", "background_color": "#ffffff" },
    "types": { "Button": { "background_color": "#0078d4", "color": "#ffffff", "border_radius": "4px" } },
    "windows": { "main": { "background_color": "#f5f5f5" } },
    "widgets": { "btn_ok": { "background_color": "#28a745" } }
}
```

**级联优先级（低→高）**: global → types[type] → windows[key] → widgets[name]

### app/core/style_engine.py — 样式引擎

**职责**: 加载 styles.json，按级联规则解析任一控件的最终样式，生成组合 QSS 字符串，一次性应用到窗口。

**接口**:
- `load_styles() -> dict` / `save_styles(data)` — 读写 styles.json
- `resolve_style(name, type, window_key) -> dict` — 四级级联合并
- `style_to_qss(style_dict, selector) -> str` — 属性 dict → QSS 规则
- `apply_to_widget(widget, window_key, _styles=None)` — 遍历 findChildren，收集所有规则拼接为组合 QSS，`window.setStyleSheet(combined)` 一次性应用
- `update_live(window, window_key, _styles=None)` — 运行时热更新（接受可选 _styles 参数避免读磁盘）
- `generate_widget_id(name, type, path)` — 为无名控件生成 `wXXXXXXX` hash ID
- `collect_layout_widgets(layout_node, path_prefix)` — 递归收集布局中所有控件的 ID 信息
- `WIDGET_STYLE_SCHEMA: dict` — 各控件类型支持的样式属性
- `TYPE_PROPERTIES: dict` — 自动计算的类型完整属性列表
- `PROPERTY_GROUPS: dict` — 属性分组（字体/颜色背景/边框/尺寸/间距）

**支持 18 项样式属性**: font_family, font_size, font_weight, font_style, color, background_color, border, border_radius, border_top/right/bottom/left, padding, margin, width, height, min/max_width, min/max_height

## 数据流

```
settings.json ──→ window_config ──→ ConfigWindow (geometry/opacity/bg/...)
     │                                    │
     │ layout: "main"                     │ load_layout("main")
     └────────────────────────────────────┤
                                          ↓
layout.json ──→ layout_loader ──→ layout_engine.build(node) ──→ widget 树 ──→ centralWidget
                                          │
                                          │ setProperty("layout_type", type)
                                          ↓
styles.json ──→ style_engine.apply_to_widget(window, key)
                  ├── 遍历 findChildren
                  ├── resolve_style(name, type, key) → 四级合并
                  ├── style_to_qss(flat, selector) → QSS 规则
                  └── window.setStyleSheet(combined) 一次性应用

运行时编辑流:
widget_controller ──→ 修改 self._all_layouts ──→ _save_all_layouts() ──→ layout.json
                   ──→ apply_to_window() ──→ 目标窗口即时刷新
                   ──→ save_config() ──→ settings.json (更新 layout 字段)

style_controller ──→ _commit_fields() ──→ save_styles() ──→ styles.json
                   ──→ apply_to_widget(_styles=...) ──→ 目标窗口即时刷新
```

## 配置格式

### config/settings.json
```json
{
    "<key>": {
        "title": "窗口标题",
        "geometry": {"x": 200, "y": 150, "width": 800, "height": 600},
        "opacity": 1.0,
        "frameless": false,
        "background_color": null,
        "layout": "<layout_name>"
    }
}
```

### config/layout.json
树节点结构: `{ "type": "TypeName", "name": "id", "label": "显示文本", "children": [...], "events": {...} }`
- 容器节点（VBox/HBox/HSplitter/VSplitter/TabWidget/GroupBox/ToolBar/Form）含 `children` 数组
- 叶子节点不含 `children`
- 可选 `events` 字段绑定交互事件
- 顺序由 children 数组顺序决定

### config/styles.json
四级级联: `global` → `types` → `windows` → `widgets`，下级覆盖上级同名属性。空值不保存。

## 窗口发现

两个控制器通过 `QApplication.topLevelWidgets()` 扫描窗口（按 `_config_key` 属性匹配），不依赖 parent 链：
```
StyleController ──→ QApplication.topLevelWidgets() ──→ 找目标窗口
WidgetController ──→ QApplication.topLevelWidgets() ──→ 找目标窗口
                  ──→ styles.json / layout.json / settings.json (直接读写)
```
