"""
动作注册表 — 事件系统的可发现动作库。

每个 ActionDef 定义一个动作：名称、参数、代码模板。
UI 层根据注册表生成选择界面，用户填参数即可完成事件绑定。

扩展方式：
  1. 导入 ActionDef, ActionParam, register_action
  2. 定义 ActionDef 实例
  3. 调用 register_action(defn) 或 register_widget_actions(type, defns)
"""

_actions = {}                # id → ActionDef
_actions_by_category = {}    # category → [ActionDef]
_widget_actions = {}         # widget_type → [ActionDef]

# 事件类型映射：event_key → {widget_type → signal_name}
_SIGNAL_MAP = {
    "changed": {
        "ComboBox": "currentIndexChanged",
        "TextEdit": "textChanged",
        "LineEdit": "textChanged",
        "SpinBox": "valueChanged",
        "DoubleSpinBox": "valueChanged",
        "Slider": "valueChanged",
        "CheckBox": "toggled",
    },
    "clicked": {"Button": "clicked", "ToolButton": "clicked"},
    "toggled": {"Button": "toggled", "CheckBox": "toggled"},
    "return_pressed": {"LineEdit": "returnPressed"},
    "tab_changed": {"TabWidget": "currentChanged"},
    "item_activated": {"ComboBox": "activated"},
}

# 鼠标/事件过滤器事件（不需信号连接）
_MOUSE_EVENTS = {"enter", "leave", "click", "double_click", "hover", "drag", "right_click"}

# 所有可用的事件类型
ALL_EVENT_TYPES = sorted(_MOUSE_EVENTS | set(_SIGNAL_MAP.keys()))


def get_event_types_for_type(widget_type):
    """返回该控件类型可用的事件类型列表（鼠标事件 + 适用的信号事件）。"""
    result = list(_MOUSE_EVENTS)
    for evt_key, type_map in _SIGNAL_MAP.items():
        if widget_type in type_map:
            result.append(evt_key)
    return sorted(result)


def get_signal_for_event(widget_type, event_key):
    """返回 event_key 在该 widget_type 上对应的 Qt 信号名，无则返回 None。"""
    type_map = _SIGNAL_MAP.get(event_key, {})
    return type_map.get(widget_type)


def is_mouse_event(event_key):
    return event_key in _MOUSE_EVENTS


class ActionParam:
    def __init__(self, name, param_type, label, default="", options=None):
        self.name = name
        self.param_type = param_type
        self.label = label
        self.default = default
        self.options = options or []


class ActionDef:
    def __init__(self, action_id, name, description, category, params, code_template):
        self.id = action_id
        self.name = name
        self.description = description
        self.category = category
        self.params = params
        self.code_template = code_template


def register_action(defn):
    _actions[defn.id] = defn
    _actions_by_category.setdefault(defn.category, []).append(defn)


def register_widget_actions(widget_type, defns):
    existing = _widget_actions.setdefault(widget_type, [])
    for d in defns:
        register_action(d)
        existing.append(d)


def get_actions(category=None, widget_type=None):
    result = list(_actions.values())
    if category:
        result = [a for a in result if a.category == category]
    if widget_type:
        result = [a for a in result if a in _widget_actions.get(widget_type, [])]
    return result


def get_categories():
    return sorted(_actions_by_category.keys())


def get_widget_actions(widget_type):
    return _widget_actions.get(widget_type, [])


def generate_code(action_id, params_dict):
    """用参数填充模板，生成可执行的 Python 代码字符串。"""
    defn = _actions.get(action_id)
    if defn is None:
        return ""
    return defn.code_template.format(**params_dict)


def try_parse_code(code):
    """尝试将代码反向匹配到已注册动作，匹配成功返回 (action_id, params_dict)，失败返回 None。"""
    import re
    for aid, defn in _actions.items():
        # 跳过纯占位模板（如 run_python 的 "{code}"），它们会匹配任何输入
        template = defn.code_template.strip()
        if template.count("{") == 1 and template.count("}") == 1:
            param_match = re.match(r"^\{(\w+)\}$", template)
            if param_match:
                continue
        # 将模板转为正则：{param} → (.+)
        escaped = re.escape(template)
        pattern = escaped.replace(r"\{", "{").replace(r"\}", "}")
        pattern = re.sub(r"\{(\w+)\}", r"(.+)", pattern)
        m = re.match("^" + pattern + "$", code)
        if m:
            values = list(m.groups())
            params = {}
            for i, p in enumerate(defn.params):
                if i < len(values):
                    params[p.name] = values[i]
            return aid, params
    return None


# ═══════════════════════════════════════════════════════════════
# 预注册动作
# ═══════════════════════════════════════════════════════════════

P = ActionParam

# ── 通用 ──
register_action(ActionDef(
    "print", "打印信息", "在控制台打印一条消息",
    "通用", [P("message", "string", "消息内容")],
    "print('{message}')",
))
register_action(ActionDef(
    "show_messagebox", "弹出消息框", "弹出一个信息提示框",
    "通用", [P("title", "string", "标题"), P("message", "string", "消息内容")],
    "widget.window()._show_message('{title}', '{message}')",
))
register_action(ActionDef(
    "run_python", "自定义代码", "直接执行一段 Python 代码（widget=触发源控件）",
    "通用", [P("code", "string", "Python 代码")],
    "{code}",
))

# ── 窗口 ──
for aid, aname, adesc, tmpl in [
    ("close_window", "关闭窗口", "关闭触发控件所在的窗口",
     "widget.window().close()"),
    ("toggle_fullscreen", "切换全屏", "切换窗口全屏状态",
     "w = widget.window(); w.showFullScreen() if not w.isFullScreen() else w.showNormal()"),
    ("minimize_window", "最小化窗口", "将窗口最小化到任务栏",
     "widget.window().showMinimized()"),
    ("maximize_window", "最大化/还原", "切换窗口最大化与正常状态",
     "w = widget.window(); w.showMaximized() if not w.isMaximized() else w.showNormal()"),
    ("toggle_always_on_top", "窗口置顶", "切换窗口始终在最上层显示",
     "w = widget.window(); f = w.windowFlags(); w.setWindowFlags(f ^ Qt.WindowStaysOnTopHint); w.show()"),
    ("drag_window", "移动窗口", "拖拽控件时移动窗口（需配合 drag 事件类型）",
     "# drag_move_window"),
]:
    register_action(ActionDef(aid, aname, adesc, "窗口", [], tmpl))

# ── 控件操作 ──
register_action(ActionDef(
    "toggle_visibility", "切换可见性", "切换目标控件的显示/隐藏状态",
    "控件操作", [P("target", "widget_ref", "目标控件")],
    "w=find_widget('{target}'); w.setVisible(not w.isVisible())",
))
register_action(ActionDef(
    "show_widget", "显示控件", "显示目标控件",
    "控件操作", [P("target", "widget_ref", "目标控件")],
    "find_widget('{target}').setVisible(True)",
))
register_action(ActionDef(
    "hide_widget", "隐藏控件", "隐藏目标控件",
    "控件操作", [P("target", "widget_ref", "目标控件")],
    "find_widget('{target}').setVisible(False)",
))
register_action(ActionDef(
    "set_enabled", "启用控件", "启用目标控件（可交互）",
    "控件操作", [P("target", "widget_ref", "目标控件")],
    "find_widget('{target}').setEnabled(True)",
))
register_action(ActionDef(
    "set_disabled", "禁用控件", "禁用目标控件（变灰不可交互）",
    "控件操作", [P("target", "widget_ref", "目标控件")],
    "find_widget('{target}').setEnabled(False)",
))
register_action(ActionDef(
    "set_text", "设置文本", "设置目标控件的显示文本",
    "控件操作", [P("target", "widget_ref", "目标控件"), P("text", "string", "文本内容")],
    "find_widget('{target}').set_text('{text}')",
))

# ── 控件专用 ──
register_widget_actions("TabWidget", [
    ActionDef("tabwidget_set_index", "切换标签页", "切换到指定索引的标签页",
              "控件专用", [P("target", "widget_ref", "目标TabWidget"), P("index", "number", "标签索引", "0")],
              "find_widget('{target}').setCurrentIndex({index})"),
    ActionDef("tabwidget_next", "下一个标签", "切换到下一个标签页",
              "控件专用", [P("target", "widget_ref", "目标TabWidget")],
              "w=find_widget('{target}'); w.setCurrentIndex((w.currentIndex()+1)%w.count())"),
])

register_widget_actions("ComboBox", [
    ActionDef("combobox_set_index", "设置选中项", "设置下拉框当前选中项的索引",
              "控件专用", [P("target", "widget_ref", "目标ComboBox"), P("index", "number", "索引", "0")],
              "find_widget('{target}').setCurrentIndex({index})"),
    ActionDef("combobox_set_text", "设置选中文本", "设置下拉框当前选中项的文本",
              "控件专用", [P("target", "widget_ref", "目标ComboBox"), P("text", "string", "文本")],
              "find_widget('{target}').setCurrentText('{text}')"),
])

register_widget_actions("Slider", [
    ActionDef("slider_set_value", "设置滑块值", "设置滑块的当前值",
              "控件专用", [P("target", "widget_ref", "目标Slider"), P("value", "number", "值", "50")],
              "find_widget('{target}').setValue({value})"),
])

register_widget_actions("ProgressBar", [
    ActionDef("progressbar_set_value", "设置进度值", "设置进度条的当前值",
              "控件专用", [P("target", "widget_ref", "目标ProgressBar"), P("value", "number", "值", "50")],
              "find_widget('{target}').setValue({value})"),
])

register_widget_actions("CheckBox", [
    ActionDef("checkbox_toggle", "切换复选框", "切换复选框的选中状态",
              "控件专用", [P("target", "widget_ref", "目标CheckBox")],
              "w=find_widget('{target}'); w.setChecked(not w.isChecked())"),
    ActionDef("checkbox_set_checked", "设置选中", "设置复选框的选中状态",
              "控件专用", [P("target", "widget_ref", "目标CheckBox"), P("checked", "bool", "选中")],
              "find_widget('{target}').setChecked({checked})"),
])

register_widget_actions("TextEdit", [
    ActionDef("textedit_append", "追加文本", "在文本编辑器末尾追加文本",
              "控件专用", [P("target", "widget_ref", "目标TextEdit"), P("text", "string", "追加文本")],
              "find_widget('{target}').append('{text}')"),
    ActionDef("textedit_clear", "清空文本", "清空文本编辑器内容",
              "控件专用", [P("target", "widget_ref", "目标TextEdit")],
              "find_widget('{target}').clear()"),
])

register_widget_actions("LineEdit", [
    ActionDef("lineedit_clear", "清空输入框", "清空输入框内容",
              "控件专用", [P("target", "widget_ref", "目标LineEdit")],
              "find_widget('{target}').clear()"),
    ActionDef("lineedit_select_all", "全选文本", "选中输入框中所有文本",
              "控件专用", [P("target", "widget_ref", "目标LineEdit")],
              "find_widget('{target}').selectAll()"),
])

register_widget_actions("SpinBox", [
    ActionDef("spinbox_set_value", "设置数值", "设置数字选择框的值",
              "控件专用", [P("target", "widget_ref", "目标SpinBox"), P("value", "number", "值", "0")],
              "find_widget('{target}').setValue({value})"),
])

register_widget_actions("DoubleSpinBox", [
    ActionDef("doublespinbox_set_value", "设置数值", "设置浮点数字选择框的值",
              "控件专用", [P("target", "widget_ref", "目标DoubleSpinBox"), P("value", "number", "值", "0.0")],
              "find_widget('{target}').setValue({value})"),
])

register_widget_actions("Image", [
    ActionDef("image_set_src", "切换图片", "切换图片控件的图片源",
              "控件专用", [P("target", "widget_ref", "目标Image"), P("src", "string", "图片路径")],
              "find_widget('{target}').set_src('{src}')"),
])
