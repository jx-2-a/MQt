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

## 阶段十三（窗口背景渲染修复，任务A+B）— 2026-06-01

**问题根因：** QMainWindow CSS 背景被子控件树完全覆盖，Qt5 QSS 不支持跨 widget 边界的 alpha 混合。

**修复方案（参考 New_HB 项目的 QLabel 背景层方案）：**

1. **config_window.py** — 移除 `setStyleSheet(f"QMainWindow {{ background-color: {bg}; }}")`，它被随后的 `apply_to_widget()` 覆盖，从未生效
2. **layout_engine.py build()** — 新增 `widget.setAutoFillBackground(False)` 防止 palette 填充不透明底色；新增 `_propagate_translucent()` 递归为所有后代（含 Qt 内部子控件）设置 `WA_TranslucentBackground` + `setAutoFillBackground(False)`
3. **style_engine.py apply_to_widget()** — 核心改动：不再通过 QSS 为 QMainWindow 设背景色，而是在 centralWidget 内放置 QLabel 作为背景层（`setGeometry(0,0,w,h)` + `lower()` + resize 钩子），子控件的 rgba 半透明背景自然与 QLabel 背景混合
4. **window_state_controller.py _apply()** — 移除冗余的 `setStyleSheet` 调用（同样被 `apply_to_widget()` 覆盖）
5. **styles.json** — `ide_root` / `work_hsplit` 等中间容器改为 `transparent`，只让叶子内容控件保留 rgba 半透明背景
6. **settings.json** — 移除测试用的 `rgba(0,255,127,0)` 透明色，让 styles.json 紫色 `#3a1f6e` 生效

## 阶段十四（背景图片缩放裁剪）— 2026-06-01
StyledImage crop 模式居中裁剪 / `_make_bg_pixmap` 三模式（crop/contain/stretch）+ QPainter 合成 / `background_image_scale` 配置项贯通 settings→window_config→style_engine。

## 阶段十五（HBox/VBox 实色背景修复）— 2026-06-01
layout_engine 移除无条件 `WA_TranslucentBackground`，style_engine 新增 `_apply_transparency_hints` 按解析结果精准设置透明穿透（仅 transparent/none/rgba）。

## 阶段十六（Splitter 分隔缝样式）— 2026-06-01
HSplitter/VSplitter `::handle` schema 扩展 border/border_radius/margin，styles.json 默认 3px 暗色分隔条。

## 阶段十七（复合控件基类）— 2026-06-01
CompositeWidget（固定布局+命名槽位）/ StyledTabWidget 继承 CompositeWidget（tab_bar + content）/ TabItem 复合标签（icon + label + actions）。

## 阶段十八（复杂控件库）— 2026-06-02
新建 `app/ui/complex_widgets/` 目录 / DraggableLabel 可拖拽复合标签（图标+文本双槽位，三种模式：image/text/button）。

## 阶段十九（样式架构大改）— 2026-06-03
控件自治 `apply_style()` 递归系统 / `cascade_apply_styles` 统一入口 / `props_to_qss` 公共工具 / window 级样式隔离 / 所有 17 种控件全部支持 `apply_style`。

## 阶段二十～二十一（项目结构重构）— 2026-06-04～05
新目录结构：app/windows/, app/framework/, app/controllers/, app/engine/ / windows 迁移 / config_manager 合并 window_config + layout_loader / widget_controller→layout_controller, window_state_controller→window_controller / style_controller + event_editor 迁入 controllers / 配置文件迁入 app/config/ / 向后兼容代理 / 23 项测试全部通过。

## 阶段二十二（StyledButton QSS 修复）— 2026-06-06
Qt 5 QSS 不支持 #AARRGGBB 格式 / `_sanitize_value` 新增 hex8→rgba() 转换 / styles.json 历史数据批量转换。

## 阶段二十三（_show_message + 图片切换）— 2026-06-07
BaseWindow 添加 `_show_message()` 调用 QMessageBox.information / action_registry 新增 image_set_src 动作 / 修复 drag+click 共存时模态对话框吃掉 MouseButtonRelease 导致窗口持续跟随的 bug。

## 阶段二十四（FormRow / FormContainer）— 2026-06-07
新增 HV 布局控件：FormRow 水平行容器（add_widget 自动在 stretch 前插入）/ FormContainer 垂直滚动表单容器（QScrollArea + 行管理）/ 注册到 BUILDERS（24 种类型）。

## 阶段二十六～二十八（IconController + ColorPicker + Splitter 修复）— 2026-06-08

参考 plan.md 阶段二十六～二十八记录。

## 阶段二十九（QTreeWidget 表头+边框全面修复）— 2026-06-16

### 表头内置背景去除
**问题**: QHeaderView 有三层默认白色叠加在半透明 QSS 之下——控件调色板、viewport 层、原生 Windows 样式取色。
**修复** ([tree_view.py](app/ui/widgets/tree_view.py)):
- `_strip_header_bg()` 三重清理：`setAutoFillBackground(False)` + viewport `WA_TranslucentBackground` + 调色板 Base/Window/Button 置零
- `_propagate_styled_bg` 同步处理 QHeaderView viewport

### 表头显隐控制
- `tree_view.py`: 新增 `set_header_visible(bool)` 方法
- `layout_engine.py`: `_build_treeview` 读取 `header_hidden` 属性
- `layout_controller.py`: 属性面板新增「隐藏表头」复选框（仅 TreeView 节点可见）

### QHeaderView::section 边框不生效
**根因**: `_normalize_style_dict` 不识别含 `::` 但不以 `::` 开头的 key（如 `QHeaderView::section`），导致样式被错误包装到 `_self`。
**修复**:
- `_normalize_style_dict`: 检测 `"::" in k` 替代 `k.startswith("::")`
- `style_to_qss`: 新增 `"::" in sub_key` 分支处理已含类名的子控件选择器
- `_apply_header_section_styles`: 将 section QSS 直接应用到 QHeaderView 控件自身（绕过根级联）

### ::item 不同状态边框
- TreeView schema 扩展：`::item` 新增 `border_radius`；`::item:selected` / `::item:hover` 新增 `border`、`border_radius`、`color`

### RuntimeError 修复
- `_apply_splitter_handle_styles` 中 `QTimer.singleShot(0, _defer)` 在 splitter 销毁后触发，`_defer` 包裹 try/except RuntimeError

## 阶段二十五（资源库 app/assets/ + 加密）— 2026-06-07
创建 images/fonts/data/secure/ 目录结构 / ResourceManager 单例统一资源访问（path/read/read_secure） / PBKDF2 + XOR 流加密 + HMAC-256 完整性校验（纯 Python 无外部依赖） / image.py 改用 resources.path() 解析路径 / .gitignore 保护 .key 和 secure/ 目录。
