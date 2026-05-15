# 控件参考手册

共 19 种控件，分三类。

## 容器类（8种）— 可包含子控件

| 类型 | Qt 基类 | 说明 |
|---|---|---|
| **VBox** | QWidget | 垂直布局容器，子控件从上到下排列 |
| **HBox** | QWidget | 水平布局容器，子控件从左到右排列 |
| **HSplitter** | QSplitter | 水平分割器，子控件左右分布，可拖拽调整比例 |
| **VSplitter** | QSplitter | 垂直分割器，子控件上下分布，可拖拽调整比例 |
| **ToolBar** | QToolBar | 工具栏，子节点为 Action（只需设 label 作为按钮文字） |
| **TabWidget** | QTabWidget | 选项卡容器，每个子节点是一个标签页（label 为标签名） |
| **GroupBox** | QGroupBox | 分组框，带标题边框的容器（label 为标题） |
| **Form** | QFormLayout | 表单布局，子控件按"标签-输入框"两列排布 |

## 展示类（3种）— 只读显示

| 类型 | Qt 基类 | 说明 |
|---|---|---|
| **Label** | QLabel | 文本标签，显示一段文字 |
| **TreeView** | QTreeWidget | 树形列表视图，可展开/折叠层级数据 |
| **ProgressBar** | QProgressBar | 进度条，显示 0~100 的进度 |

## 输入类（8种）— 可交互

| 类型 | Qt 基类 | 说明 |
|---|---|---|
| **Button** | QPushButton | 按钮，显示文字，可绑定点击事件 |
| **ComboBox** | QComboBox | 下拉选择框，可从多个选项中选一个 |
| **TextEdit** | QTextEdit | 多行文本编辑器 |
| **LineEdit** | QLineEdit | 单行文本输入框 |
| **CheckBox** | QCheckBox | 复选框，勾选/取消 |
| **SpinBox** | QSpinBox | 整数微调器，上下箭头增减数值（0~9999） |
| **DoubleSpinBox** | QDoubleSpinBox | 浮点微调器，支持小数（0.00~9999.00） |
| **Slider** | QSlider | 滑块，拖动选择数值 |

## 节点配置格式

在 layout.json 中每个节点结构：

```json
{
    "type": "控件类型",
    "name": "唯一标识（可选，用于样式选择器 #name）",
    "label": "显示文字",
    "children": [],         // 仅容器类
    "events": {},           // 可选，事件绑定
    "items": ["选项A", "选项B"]  // ComboBox 专用
}
```

### 容器 vs 叶子
- **容器**（VBox/HBox/HSplitter/VSplitter/ToolBar/TabWidget/GroupBox/Form）：有 `children` 数组
- **叶子**（其余所有）：无 `children`，是控件树的终点
