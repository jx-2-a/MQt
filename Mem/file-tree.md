# 项目文件树

```
RPControl/
├── main.py                              # 入口：创建 QApplication + 主窗口
├── _test.py                             # 测试套件（23 项，含样式/布局/引擎/事件验证）
├── README.md                            # 项目说明（中文）
│
├── app/
│   ├── __init__.py                      # 包入口
│   │
│   ├── config/                          # 配置文件（3 个 JSON）
│   │   ├── settings.json                # 窗口配置（geometry/opacity/frameless/bg/layout）
│   │   ├── layout.json                  # 布局树（type/name/label/children/events）
│   │   └── styles.json                  # 四级级联样式（global/types/windows/widgets）
│   │
│   ├── assets/                          # 资源库（图片/字体/数据/加密存储）
│   │   ├── __init__.py                  # 导出 resources, ResourceManager
│   │   ├── resource_manager.py          # ResourceManager 单例 + PBKDF2/XOR/HMAC 加解密
│   │   ├── .key                         # 加密密钥（git-ignored）
│   │   ├── images/                      # 公开图片资源
│   │   ├── fonts/                       # 字体文件
│   │   ├── data/                        # 通用数据文件
│   │   └── secure/                      # 加密存储（.enc 文件，git-ignored）
│   │
│   ├── framework/                       # 框架层
│   │   └── config_manager.py            # 统一配置入口（合并 window_config + layout_loader）
│   │
│   ├── core/                            # 核心引擎
│   │   ├── __init__.py                  # 统一导出
│   │   ├── action_registry.py           # 动作注册表（30 种预注册动作 + 模板系统）
│   │   ├── window_factory.py            # create_main_window() / open_sub_window()
│   │   ├── window_config.py             # load/save/get/update → settings.json
│   │   ├── layout_loader.py             # load_layout() / save_layout() / load_all_layouts()
│   │   ├── layout_engine.py             # build() 递归创建 widget 树 + 事件绑定（24 种 BUILDERS）
│   │   └── style_engine.py              # 级联解析 → QSS 生成 → apply_to_widget 递归应用
│   │
│   ├── engine/                          # 引擎扩展（预留）
│   │
│   ├── controllers/                     # 控制器（元工具窗口）
│   │   ├── __init__.py                  # 导出所有控制器
│   │   ├── layout_controller.py         # 布局编辑器 — 编辑 layout.json（暗色主题）
│   │   ├── style_controller.py          # 样式编辑器 — 编辑 styles.json（暗色主题）
│   │   ├── window_controller.py         # 窗口状态控制器 — geometry 持久化
│   │   ├── event_editor.py              # 事件编辑器 — action_registry 驱动的可视化事件绑定
│   │   └── color_picker.py              # 颜色选择器
│   │
│   ├── windows/                         # 窗口类
│   │   └── base_window.py               # BaseWindow — 配置驱动窗口基类（背景层/圆角/QSS）
│   │
│   └── ui/                              # UI 层
│       ├── __init__.py                  # 向后兼容代理 + 懒加载
│       │
│       ├── widgets/                     # 基础控件库（20 个文件）
│       │   ├── __init__.py              # 统一导出全部控件类
│       │   ├── composite.py             # CompositeWidget 复合控件基类（命名槽位系统）
│       │   ├── container.py             # StyledBox(VBox/HBox) / StyledSplitter(HSplitter/VSplitter)
│       │   ├── label.py                 # StyledLabel (QLabel)
│       │   ├── image.py                 # StyledImage (QLabel 图片，crop/contain/stretch)
│       │   ├── tree_view.py             # StyledTreeWidget (QTreeWidget)
│       │   ├── toolbar.py               # StyledToolBar (QToolBar)
│       │   ├── form.py                  # StyledForm (QFormLayout)
│       │   ├── button.py                # StyledButton (QPushButton)
│       │   ├── combo_box.py             # StyledComboBox (QComboBox)
│       │   ├── text_edit.py             # StyledTextEdit (QTextEdit)
│       │   ├── line_edit.py             # StyledLineEdit (QLineEdit)
│       │   ├── check_box.py             # StyledCheckBox (QCheckBox)
│       │   ├── spin_box.py              # StyledSpinBox / StyledDoubleSpinBox
│       │   ├── tab_widget.py            # StyledTabWidget + TabItem (CompositeWidget 子类)
│       │   ├── group_box.py             # StyledGroupBox (QGroupBox)
│       │   ├── slider.py                # StyledSlider (QSlider)
│       │   ├── progress_bar.py          # StyledProgressBar (QProgressBar)
│       │   ├── spacer.py                # StyledSpacer (QWidget 占位弹簧)
│       │   ├── form_row.py              # FormRow — 水平行容器（H 布局 + 自动弹簧）
│       │   └── form_container.py        # FormContainer — 垂直滚动容器（QScrollArea + 行管理）
│       │
│       └── complex_widgets/             # 复杂控件库
│           ├── __init__.py              # 导出 DraggableLabel
│           └── draggable_label.py       # DraggableLabel 可拖拽复合标签（图标/文本/按钮模式）
│
├── reference/                           # 参考代码（DSSP 原项目）
│   └── ...                              # 50+ 个参考文件（item_*/page_*/tool_* 等）
│
├── Mem/                                 # 外部辅助记忆
│   ├── architecture.md                  # 模块架构 / 接口 / 数据流 / 配置格式
│   ├── plan.md                          # 工作计划 + 完成记录
│   ├── summary.md                       # 阶段总结
│   ├── file-tree.md                     # 项目文件树（本文件）
│   ├── widget-reference.md              # 控件参考手册（24 种）
│   ├── complex-widgets.md               # 复杂控件手册
│   └── action-registry.md               # 动作注册表手册
│
├── Ctrl/                                # 任务协调
│   ├── request.txt                      # 工作流程规则
│   ├── follow.text                      # 当前任务
│   └── connect.text                     # Agent 间通信
│
└── .vscode/
    └── launch.json                      # 调试配置（Python: main.py）
```
