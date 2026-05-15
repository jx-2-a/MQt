# QS Controller

基于 PyQt5 的配置驱动窗口管理系统。窗口样式由 `config/settings.json` 控制，控件布局由 `config/layout.json` 树结构描述，布局引擎动态渲染，任何窗口可通过 `layout` 字段自动构建控件树。关闭窗口时状态自动持久化。

## 安装依赖

```bash
pip install PyQt5
```

## 运行

```bash
cd RPControl
python main.py
```

## 项目结构

```
RPControl/
├── main.py                       # 程序入口
├── _test.py                      # 测试套件（18 项）
├── config/
│   ├── settings.json             # 窗口配置（样式、状态持久化、layout引用）
│   ├── layout.json               # 布局树配置（控件嵌套结构）
│   └── styles.json               # 四级级联样式配置（global/types/windows/widgets）
├── app/
│   ├── core/
│   │   ├── window_factory.py     # 窗口工厂
│   │   ├── window_config.py      # 配置读写管理
│   │   ├── layout_loader.py      # 布局文件加载
│   │   ├── layout_engine.py      # 布局渲染引擎（树→widget）
│   │   └── style_engine.py       # 样式引擎（四级级联→QSS）
│   └── ui/
│       ├── config_window.py      # 配置驱动窗口基类（自动应用layout+样式）
│       ├── main_window.py        # 主窗口类
│       ├── widget_controller.py  # 布局控制器（Ctrl+Shift+L 可视化编辑layout.json）
│       ├── style_controller.py   # 样式控制器（Ctrl+Shift+S 可视化编辑styles.json）
│       └── widgets/              # 独立控件库（15个控件，独立继承）
├── Mem/                          # 辅助记忆区（架构/计划/总结/文件树）
├── Ctrl/                         # 任务协调（request/follow/connect）
└── README.md
```

## 使用方法

### 窗口样式配置（settings.json）

```json
{
    "main": {
        "title": "窗口标题",
        "geometry": {"x": 200, "y": 150, "width": 800, "height": 600},
        "opacity": 1.0,
        "frameless": false,
        "background_color": null,
        "layout": null
    }
}
```

### 布局配置（layout.json）

定义窗口控件树结构，每个节点含 `type` / `name` / `label` / `children`。容器节点（VBox/HBox/Splitter）通过 children 包含子控件。叶子节点（Label/TreeView/Form/ToolBar/Action）无 children。

**已支持的控件类型（20种）**:
- 容器: VBox, HBox, HSplitter, VSplitter, TabWidget, GroupBox, ToolBar
- 展示: Label, TreeView, ProgressBar
- 输入: Button, ComboBox, TextEdit, LineEdit, CheckBox, SpinBox, DoubleSpinBox, Slider
- 其他: Form, Action

**配置中引用布局**: 在 settings.json 中设置 `"layout": "widget_controller"` 即可自动渲染。

### 代码中使用

```python
from app.core.window_factory import create_main_window

# 主窗口：自动读取 settings.json 的 "main" 段（含 layout 渲染）
main_win = create_main_window("标题")

# 任意窗口：通过 layout 字段自动渲染控件树
from app.ui.config_window import ConfigWindow
sub = ConfigWindow("widget_controller", parent=main_win)
sub.show()
```

### 布局控制器（Ctrl+Shift+L 打开）

暗色主题的布局编辑器，提供完整的 layout.json 可视化编辑功能：

**布局管理**
- 下拉选择任意已保存的布局进行编辑
- 新建独立布局（不关联窗口，可按需加载）
- 删除布局

**节点编辑**
- 树形视图展示布局节点（类型 | 名称 | 标签三列）
- 选中节点 → 右侧属性面板编辑：类型（20种可选）、名称、标签
- 选中容器节点 → 添加子节点（Label 默认）
- 选中节点 → 删除 / 上移 / 下移
- 所有修改自动持久化到 layout.json

**页面切换**
- 窗口下拉选择目标窗口
- 点击"应用到窗口"即时切换布局
- 同时更新 settings.json 的 layout 字段

### 样式控制器（Ctrl+Shift+S 打开）

暗色主题的样式编辑器，提供 styles.json 可视化编辑。遵循 **全局→类型→窗口→控件实例** 四级级联继承，下级属性覆盖上级。

**样式配置（styles.json）四级结构**:
```json
{
    "global": { "font_family": "Microsoft YaHei", "font_size": "14px", "color": "#333" },
    "types": { "Button": { "background_color": "#0078d4", "color": "#fff", "border_radius": "4px" } },
    "windows": { "main": { "background_color": "#f5f5f5" } },
    "widgets": { "btn_ok": { "background_color": "#28a745" } }
}
```
优先级: widgets[name] > windows[key] > types[type] > global。未设属性自动向上继承。

**界面功能**:
- 左侧四级层级树：全局样式 / 控件类型样式（20种）/ 窗口样式 / 控件实例样式
- 右侧属性编辑器：字体 / 颜色与背景（带拾色器）/ 边框 / 尺寸 / 间距 — 共 18 项 CSS 属性
- 实时预览：勾选后编辑即时应用到目标窗口
- 控件实例样式：输入 objectName 手动添加 / 右键删除

### 代码中使用独立布局

```python
from app.ui.widget_controller import WidgetController

# 加载任意布局到新窗口（独立布局，不依赖窗口配置）
win = WidgetController.apply_layout("demo")

# 切换已有窗口的页面
WidgetController.switch_page(main_window, "demo")
```
