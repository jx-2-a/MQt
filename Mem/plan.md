# 工作计划

## 下一阶段：引擎迁移 / 控件层整理 / 全局注册表

根据 follow.text 要求（参考 reference 进行项目重构）：
1. ✅ 第一步（阶段二十）：窗口与窗口设置
2. ✅ 第二步（阶段二十一）：迁移控制器到 app/controllers/（本次完成）
3. 第三步：迁移引擎 app/core/ → app/engine/
4. 第四步：整理控件层 app/ui/widgets/ → app/widgets/
5. 第五步：创建 framework/registry.py
6. 第六步：README.md 编写

---

## 完成记录（合并）

- ✅ 阶段一（任务 1-6）：基础窗口系统 — MainWindow / window_factory / main.py
- ✅ 阶段二（任务 7-13）：配置驱动窗口样式 — settings.json / ConfigWindow / 状态持久化
- ✅ 阶段三（任务 14-21）：背景色 + 控件控制器 + layout.json 树结构
- ✅ 阶段四（任务 22-28）：布局渲染引擎 — layout_engine / layout_loader / build() 递归
- ✅ 阶段五（任务 29-34）：丰富控件库 — 10 个新控件 / BUILDERS 20 种类型 / WidgetController 重构
- ✅ 阶段六（任务 35-40）：WidgetController 完全重写 — 暗色主题 / 节点增删 / 独立布局 / 页面切换 + bug 修复
- ✅ 阶段七（任务 41-43）：控件交互事件绑定 — EventHandler / 6 种事件 / WidgetController 事件编辑 UI
- ✅ 阶段八（任务 44-48）：样式控制器 — StyleController / style_engine / styles.json 四级级联
- ✅ 阶段八补充（任务 49-53）：样式修复 — 组合 QSS / WIDGET_STYLE_SCHEMA / 动态属性面板 / 布局控件实例树
- ✅ 阶段九（任务 54-59）：样式系统修复 — 移除类型门控 / StyleController 重构 / 无名控件 hash ID / 实时预览修复
- ✅ 阶段十（任务 60-62）：控制器面板布局统一 — topbar/splitter/statusbar 骨架 / VSCode Dark+ QSS
- ✅ 阶段十补充（任务 63-66）：showEvent 隔离父窗口样式污染 / 移除实时预览 / 保存按钮移至底部
- ✅ 阶段十一（任务 67-69）：Parent 解耦 — StyleController / WidgetController 改用 topLevelWidgets()
- ✅ 阶段十二（本次）：结构整理 — file-tree.md / Mem 压缩 / README 更新 / 测试全通过
- ✅ 阶段十三（任务A+B 2026-06-01）：窗口背景渲染修复 — config_window.py 移除死代码 / layout_engine 递归透明属性 / style_engine QLabel 背景层方案（参考 New_HB） / styles.json 中间容器透明化
- ✅ 阶段十四（2026-06-01）：背景图片缩放裁剪 — StyledImage crop 模式居中裁剪 / _make_bg_pixmap 三模式（crop/contain/stretch）+ QPainter 合成 / background_image_scale 配置项贯通 settings→window_config→style_engine
- ✅ 阶段十五（2026-06-01）：修复 HBox/VBox 实色背景失效 — layout_engine 移除无条件 WA_TranslucentBackground / style_engine 新增 _apply_transparency_hints 按解析结果精准设置透明穿透（仅 transparent/none/rgba）
- ✅ 阶段十六（2026-06-01）：Splitter 分隔缝样式 — HSplitter/VSplitter 的 ::handle schema 扩展 border/border_radius/margin / styles.json 默认 3px 暗色分隔条
- ✅ 阶段十七（2026-06-01）：复合控件基类 — CompositeWidget（固定布局+命名槽位）/ StyledTabWidget 继承 CompositeWidget（tab_bar + content）/ TabItem 复合标签（icon + label + actions）/ __init__.py 导出更新

---

## 完成记录（合并）

- ✅ 阶段一（任务 1-6）：基础窗口系统 — MainWindow / window_factory / main.py
- ✅ 阶段二（任务 7-13）：配置驱动窗口样式 — settings.json / ConfigWindow / 状态持久化
- ✅ 阶段三（任务 14-21）：背景色 + 控件控制器 + layout.json 树结构
- ✅ 阶段四（任务 22-28）：布局渲染引擎 — layout_engine / layout_loader / build() 递归
- ✅ 阶段五（任务 29-34）：丰富控件库 — 10 个新控件 / BUILDERS 20 种类型 / WidgetController 重构
- ✅ 阶段六（任务 35-40）：WidgetController 完全重写 — 暗色主题 / 节点增删 / 独立布局 / 页面切换 + bug 修复
- ✅ 阶段七（任务 41-43）：控件交互事件绑定 — EventHandler / 6 种事件 / WidgetController 事件编辑 UI
- ✅ 阶段八（任务 44-48）：样式控制器 — StyleController / style_engine / styles.json 四级级联
- ✅ 阶段八补充（任务 49-53）：样式修复 — 组合 QSS / WIDGET_STYLE_SCHEMA / 动态属性面板 / 布局控件实例树
- ✅ 阶段九（任务 54-59）：样式系统修复 — 移除类型门控 / StyleController 重构 / 无名控件 hash ID / 实时预览修复
- ✅ 阶段十（任务 60-62）：控制器面板布局统一 — topbar/splitter/statusbar 骨架 / VSCode Dark+ QSS
- ✅ 阶段十补充（任务 63-66）：showEvent 隔离父窗口样式污染 / 移除实时预览 / 保存按钮移至底部
- ✅ 阶段十一（任务 67-69）：Parent 解耦 — StyleController / WidgetController 改用 topLevelWidgets()
- ✅ 阶段十二（本次）：结构整理 — file-tree.md / Mem 压缩 / README 更新 / 测试全通过
- ✅ 阶段十三（任务A+B 2026-06-01）：窗口背景渲染修复 — config_window.py 移除死代码 / layout_engine 递归透明属性 / style_engine QLabel 背景层方案（参考 New_HB） / styles.json 中间容器透明化
- ✅ 阶段十四（2026-06-01）：背景图片缩放裁剪 — StyledImage crop 模式居中裁剪 / _make_bg_pixmap 三模式（crop/contain/stretch）+ QPainter 合成 / background_image_scale 配置项贯通 settings→window_config→style_engine
- ✅ 阶段十五（2026-06-01）：修复 HBox/VBox 实色背景失效 — layout_engine 移除无条件 WA_TranslucentBackground / style_engine 新增 _apply_transparency_hints 按解析结果精准设置透明穿透（仅 transparent/none/rgba）
- ✅ 阶段十六（2026-06-01）：Splitter 分隔缝样式 — HSplitter/VSplitter 的 ::handle schema 扩展 border/border_radius/margin / styles.json 默认 3px 暗色分隔条
- ✅ 阶段十七（2026-06-01）：CompositeWidget 复合控件基类 — 固定内部布局 + 命名槽位系统 / StyledTabWidget 重构继承 CompositeWidget（槽位: tab_bar, content）/ TabItem 可组合标签头（槽位: icon, label, actions）/ CompositeWidget._register_slot() 自动设置 WA_StyledBackground + objectName 供样式引擎定位
- ✅ 阶段十八（2026-06-02）：复杂控件库 — 新建 app/ui/complex_widgets/ 目录 / DraggableLabel 可拖拽复合标签（图标+文本双槽位，三种模式：image/text/button）/ 按钮模式支持 clicked 信号 / 拖拽边界限制在父容器内 / Mem/complex-widgets.md 文档
- ✅ 阶段十九（2026-06-03）：样式架构大改 — 控件自治 apply_style() 递归系统 / cascade_apply_styles 统一入口 / props_to_qss 公共工具 / window 级样式隔离 / 所有 17 种控件全部支持 apply_style
- ✅ 阶段二十（2026-06-04）：项目结构重构第一步：窗口与窗口设置 — 新目录结构 app/windows/, app/framework/, app/controllers/, app/engine/ / windows 从 app/ui/windows/ 迁移到 app/windows/ / 创建 app/framework/config_manager.py 合并 window_config + layout_loader / 删除 shim 文件 config_window.py, main_window.py / 解决循环引用（app/ui/__init__.py 使用 __getattr__ 懒加载）/ 23 项测试全部通过
- ✅ 阶段二十一（2026-06-05）：项目结构重构第二步：迁移控制器到 app/controllers/ — widget_controller → layout_controller / window_state_controller → window_controller / style_controller + event_editor 迁入 / app/ui/__init__.py 向后兼容代理 / 11 处导入路径更新 / 23 项测试全部通过
- ✅ 阶段二十一补充（2026-06-05）：配置文件移入 app/config/ — config/ 从项目根迁入 app/config/ / 6 个文件路径引用更新（config_manager / style_engine / layout_loader / window_config / base_window / widget_controller）
- ✅ 阶段二十二（2026-06-06）：修复 StyledButton QSS 解析错误 — Qt 5 QSS 不支持 #AARRGGBB 格式 / _sanitize_value 新增 hex8→rgba() 转换（颜色属性） / style_to_qss 也调用 _sanitize_value（修复遗漏） / style_controller 颜色选取改用 color_to_qss() / styles.json 历史数据批量转换为 rgba() / 23 项测试全部通过
- ✅ 阶段二十三（2026-06-07）：修复 _show_message 报错 + 新增图片切换动作 — BaseWindow 添加 _show_message() 调用 QMessageBox.information / action_registry 新增 image_set_src 动作（切换图片源）/ 修复 drag+click 共存时模态对话框吃掉 MouseButtonRelease 导致窗口持续跟随的 bug / 23 项测试全部通过
- ✅ 阶段二十四（2026-06-07）：新增 hv/spilte 控件 — FormRow 水平行容器（FormRow.add_widget 自动在 stretch 前插入）/ FormContainer 垂直滚动表单容器（管理多行 FormRow，超出自动滚动）/ 注册到 BUILDERS（24 种类型）/ 23 项测试全部通过
- ✅ 阶段二十五（2026-06-07）：资源库 app/assets/ + 加密保护 — 创建 images/fonts/data/secure/ 目录结构 / ResourceManager 单例统一资源访问 / PBKDF2 + XOR 流加密 + HMAC 完整性校验（纯 Python 无依赖）/ image.py 改用 resources.path() 解析路径 / .gitignore 保护 .key 和 secure/ 目录 / 23 项测试全部通过
- ✅ 阶段二十六（2026-06-08）：原生图片支持控制器 — IconGenerator QPainter 矢量图标→透明 PNG（16 种图标，任意颜色/尺寸）/ Ctrl+Shift+I 打开 IconController 可视化界面（图库点选+颜色+尺寸+保存）/ 预生成 minimize/maximize/close 三色图标 / 移除 QPainter 手绘 WindowControls 方案 / 23 项测试全部通过
- ✅ 阶段二十七（2026-06-08）：IconController 颜色选择升级 — 替换 QColorDialog 为项目自带 ColorPicker（支持 Alpha 透明通道）/ 颜色值输出 HexArgb 格式支持透明度 / 23 项测试全部通过
- ✅ 阶段二十八（2026-06-08）：修复 HSplitter/VSplitter 把手宽高不生效 — 步骤1: 移除 val > 0 门控让 0px 生效 / 步骤2: width/height=0 时强制透明背景+无边框+保留 4px 抓取区域，实现视觉隐藏但可拖拽 / 23 项测试全部通过
- ✅ 阶段二十九（2026-06-16）：QTreeWidget 表头+边框全面修复 — 表头三重透明清理（控件→viewport→调色板）/ header_hidden 显隐控制 + 布局编辑器 UI / _normalize_style_dict 识别含 :: 的 key / _apply_header_section_styles 直设 section QSS / ::item 各状态 border 属性扩展 / RuntimeError try/except 修复

- ✅ 阶段三十（2026-06-17）：TabWidget 样式支持补全 — CachedTabWidget 新增 apply_style() 方法参与级联系统 / WIDGET_STYLE_SCHEMA 扩展：#header_row 新增 height/min_height/max_height/border_radius/border_top/left/right/margin，#content 新增 height/min_height/max_height/border/border_radius/border 四边/padding/margin / 23 项测试全部通过

---
## 下一阶段：TabWidget 改进
