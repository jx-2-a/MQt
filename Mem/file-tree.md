# 项目文件树

```
RPControl/
├── main.py                              # 入口：创建 QApplication + 主窗口
├── _test.py                             # 测试套件（18 项，含样式/布局/引擎验证）
├── README.md                            # 项目说明（中文）
│
├── config/
│   ├── settings.json                    # 窗口配置（geometry/opacity/frameless/bg/layout）
│   ├── layout.json                      # 布局树（type/name/label/children/events）
│   └── styles.json                      # 四级级联样式（global/types/windows/widgets）
│
├── app/
│   ├── __init__.py                      # 空
│   │
│   ├── core/
│   │   ├── __init__.py                  # 统一导出：factory/config/loader/engine/style
│   │   ├── window_factory.py            # create_main_window() / open_sub_window()
│   │   ├── window_config.py             # load/save/get/update → settings.json
│   │   ├── layout_loader.py             # load_layout() / save_layout() / load_all_layouts()
│   │   ├── layout_engine.py             # build() 递归创建 widget 树 + 事件绑定
│   │   └── style_engine.py              # 级联解析 → QSS 生成 → 递归应用样式
│   │
│   └── ui/
│       ├── __init__.py                  # 导出 MainWindow / ConfigWindow / StyleController
│       ├── config_window.py             # 配置驱动窗口基类（自动 layout + 样式 + 状态持久化）
│       ├── main_window.py               # 主窗口：Ctrl+Shift+L/S 快捷键注册
│       ├── widget_controller.py         # 布局控制器 — 元工具：编辑 layout.json（暗色主题）
│       ├── style_controller.py          # 样式控制器 — 元工具：编辑 styles.json（暗色主题）
│       │
│       └── widgets/                     # 独立控件库（15 个，单文件单类）
│           ├── __init__.py              # 统一导出全部控件类
│           ├── container.py             # StyledBox(VBox/HBox) / StyledSplitter
│           ├── label.py                 # StyledLabel (QLabel)
│           ├── tree_view.py             # StyledTreeWidget (QTreeWidget)
│           ├── toolbar.py               # StyledToolBar (QToolBar)
│           ├── form.py                  # StyledForm (QFormLayout)
│           ├── button.py                # StyledButton (QPushButton)
│           ├── combo_box.py             # StyledComboBox (QComboBox)
│           ├── text_edit.py             # StyledTextEdit (QTextEdit)
│           ├── line_edit.py             # StyledLineEdit (QLineEdit)
│           ├── check_box.py             # StyledCheckBox (QCheckBox)
│           ├── spin_box.py              # StyledSpinBox / StyledDoubleSpinBox
│           ├── tab_widget.py            # StyledTabWidget (QTabWidget)
│           ├── group_box.py             # StyledGroupBox (QGroupBox)
│           ├── slider.py                # StyledSlider (QSlider)
│           └── progress_bar.py          # StyledProgressBar (QProgressBar)
│
├── Mem/                                 # 外部辅助记忆
│   ├── architecture.md                  # 模块架构 / 接口 / 数据流 / 配置格式
│   ├── plan.md                          # 工作计划 + 完成记录
│   ├── summary.md                       # 阶段总结
│   ├── file-tree.md                     # 项目文件树
│   └── widget-reference.md              # 控件参考手册（19种）
│
├── Ctrl/                                # 任务协调
│   ├── request.txt                      # 工作流程规则
│   ├── follow.text                      # 当前任务
│   └── connect.text                     # Agent 间通信
│
└── .vscode/
    └── launch.json                      # 调试配置（Python: main.py）
```
