# 阶段总结

## 阶段一～四（基础框架）— 2026-05-13
搭建 PyQt5 配置驱动窗口系统：
- `main.py` → `window_factory.create_main_window()` → `MainWindow(ConfigWindow)`
- `settings.json` 控制 geometry/opacity/frameless/background_color，showEvent 恢复、closeEvent 保存
- `layout.json` 树结构描述控件嵌套，`layout_engine.build(node)` 递归创建 widget 树
- `Ctrl+Shift+L` 打开 WidgetController 子窗口

## 阶段五（丰富控件库）— 2026-05-13
新增 10 个控件：Button / ComboBox / TextEdit / LineEdit / CheckBox / SpinBox+DoubleSpinBox / TabWidget / GroupBox / Slider / ProgressBar。BUILDERS 注册 20 种类型。WidgetController 重构为纯布局控件。

## 阶段六（WidgetController 重写）— 2026-05-13
完全重写为元工具：手动 UI（暗色 QSS），树形编辑（类型/名称/标签），节点增删移动，独立布局创建，页面切换。公开 API: `apply_layout()` / `switch_page()`。

## 阶段七（事件绑定）— 2026-05-13
`layout_engine` 新增 `_EventHandler(QObject)` 事件过滤器，拦截 6 种事件（enter/leave/click/double_click/hover/drag）。WidgetController 属性面板新增事件编辑区。布局节点支持 `events` 字段。

## 阶段八（样式控制器）— 2026-05-14
实现 `style_engine.py`：四级级联解析（global→types→windows→widgets）→ QSS 生成 → 递归应用。`style_controller.py`：暗色主题 UI，树形层级编辑，属性面板（18 项 CSS 属性含拾色器），实时预览。`styles.json` 存储四级样式。

## 阶段八补充（样式修复）— 2026-05-14
修复 setStyleSheet 分散应用冲突 → 组合 QSS 一次性 `window.setStyleSheet()`。新增 `WIDGET_STYLE_SCHEMA` + `TYPE_PROPERTIES`，动态属性面板按控件类型加载。树结构重排为：布局控件实例 → 全局 → 类型 → 窗口。控件设置 `layout_type` 属性供样式引擎识别。

## 阶段九（样式系统修复 + 重构）— 2026-05-15
- 修复 `apply_to_widget` 类型门控跳过未定义类型 → 遍历 findChildren 为所有命名控件生成 `#name` 选择器
- StyleController 重构：控件实例下拉改为布局选择器，树中展示布局完整控件树，选择布局自动应用到窗口
- 无名控件自动 hash ID：`_node_id()` 基于 path md5 生成 `wXXXXXXX`
- 实时预览修复：`apply_to_widget` / `update_live` 接受 `_styles` 可选参数
- 保存/应用按钮修复：抽取 `_commit_fields()` 公共入口

## 阶段十（面板 UI 统一）— 2026-05-15
两个控制器统一为 VSCode Dark+ 风格骨架：`VBox(margin=0) → #topbar → QSplitter(1px) → #statusbar(26px)`。统一配色（#1e1e1e/#252526/#007acc）。

## 阶段十补充（体验修复）— 2026-05-15
- showEvent 重新应用自身 QSS 隔离父窗口样式污染
- 移除 StyleController 实时预览 checkbox、emoji 前缀
- WidgetController 保存按钮移至底部

## 阶段十一（Parent 解耦）— 2026-05-16
两个控制器移除 `self.parent()` 依赖，改用 `QApplication.topLevelWidgets()` 扫描窗口（按 `_config_key` 匹配）。全部 18 项测试通过。

## 阶段十二（结构整理）— 2026-05-31
创建 `Mem/file-tree.md` 完整项目文件树。压缩 Mem 文件去重。更新 README。
