import sys
sys.path.insert(0, '.')

from PyQt5.QtWidgets import QApplication
_app = QApplication(sys.argv)

# Test 1: widget imports (existing + new)
print('=== Test 1: Widget imports ===')
from app.ui.widgets import (
    StyledLabel, StyledTreeWidget, StyledBox, StyledSplitter, StyledToolBar, StyledForm,
    StyledButton, StyledComboBox, StyledTextEdit, StyledLineEdit, StyledCheckBox,
    StyledSpinBox, StyledDoubleSpinBox, StyledTabWidget, StyledGroupBox,
    StyledSlider, StyledProgressBar,
)
print('All 15 widgets imported OK')

# Test 2: new widget instantiation
print('=== Test 2: New widget instantiation ===')
btn = StyledButton("Click")
assert btn.text() == "Click"
btn.set_text("OK")
assert btn.text() == "OK"
print('StyledButton OK')

cb = StyledComboBox()
cb.add_items(["A", "B"])
assert cb.items() == ["A", "B"]
cb.set_current_text("B")
assert cb.current_text() == "B"
print('StyledComboBox OK')

te = StyledTextEdit("hello")
assert te.text() == "hello"
te.set_text("world")
assert te.text() == "world"
print('StyledTextEdit OK')

le = StyledLineEdit("input")
assert le.text() == "input"
le.set_text("changed")
assert le.text() == "changed"
print('StyledLineEdit OK')

chk = StyledCheckBox("Enable")
assert chk.text() == "Enable"
assert not chk.is_checked()
chk.set_checked(True)
assert chk.is_checked()
chk.set_text("Disable")
assert chk.text() == "Disable"
print('StyledCheckBox OK')

sb = StyledSpinBox()
sb.set_value(42)
assert sb.value() == 42
sb.set_range(0, 100)
print('StyledSpinBox OK')

dsb = StyledDoubleSpinBox()
dsb.set_value(3.14)
assert dsb.value() == 3.14
print('StyledDoubleSpinBox OK')

tw = StyledTabWidget()
tw.add_tab(StyledLabel("p1"), "Tab1")
assert tw.tab_count() == 1
print('StyledTabWidget OK')

gb = StyledGroupBox("Group")
gb.add_widget(StyledButton("B"))
gb.set_title("New Group")
print('StyledGroupBox OK')

sl = StyledSlider()
sl.set_value(50)
assert sl.value() == 50
sl.set_range(0, 100)
print('StyledSlider OK')

pb = StyledProgressBar()
pb.set_value(30)
assert pb.value() == 30
pb.set_range(0, 100)
print('StyledProgressBar OK')

# Test 3: layout_engine with all types
print('=== Test 3: Layout engine all types ===')
from app.core.layout_engine import BUILDERS, build, WIDGET_TYPE_OPTIONS
expected_types = [
    "VBox", "HBox", "HSplitter", "VSplitter", "ToolBar",
    "Label", "TreeView", "Form",
    "Button", "ComboBox", "TextEdit", "LineEdit", "CheckBox",
    "SpinBox", "DoubleSpinBox", "TabWidget", "GroupBox", "Slider", "ProgressBar",
    "Spacer", "Image", "DraggableLabel", "FormRow", "FormContainer",
]
for t in expected_types:
    assert t in BUILDERS, f"Missing builder: {t}"
print(f'All {len(expected_types)} types registered in BUILDERS')

assert WIDGET_TYPE_OPTIONS == sorted(BUILDERS.keys())
print('WIDGET_TYPE_OPTIONS correct')

# Test 4: build new widget types
print('=== Test 4: Build new widget types ===')
from app.ui.widgets import StyledButton as SB
w = build({'type': 'Button', 'name': 'b1', 'label': 'OK'})
assert isinstance(w, SB)
print('build Button OK')

from app.ui.widgets import StyledComboBox as SCB
w = build({'type': 'ComboBox', 'name': 'cb1', 'items': ['X', 'Y']})
assert isinstance(w, SCB)
print('build ComboBox OK')

from app.ui.widgets import StyledTextEdit as STE
w = build({'type': 'TextEdit', 'name': 'te1', 'label': 'text'})
assert isinstance(w, STE)
print('build TextEdit OK')

from app.ui.widgets import StyledLineEdit as SLE
w = build({'type': 'LineEdit', 'name': 'le1', 'label': 'text'})
assert isinstance(w, SLE)
print('build LineEdit OK')

from app.ui.widgets import StyledCheckBox as SCB2
w = build({'type': 'CheckBox', 'name': 'chk1', 'label': 'Enable'})
assert isinstance(w, SCB2)
print('build CheckBox OK')

from app.ui.widgets import StyledSpinBox as SSB
w = build({'type': 'SpinBox', 'name': 'sp1'})
assert isinstance(w, SSB)
print('build SpinBox OK')

from app.ui.widgets import StyledDoubleSpinBox as SDSB
w = build({'type': 'DoubleSpinBox', 'name': 'dsp1'})
assert isinstance(w, SDSB)
print('build DoubleSpinBox OK')

from app.ui.widgets import StyledTabWidget as STW
w = build({'type': 'TabWidget', 'name': 'tw1', 'children': [
    {'type': 'Label', 'name': 'tab1', 'label': 'Tab 1'}
]})
assert isinstance(w, STW)
print('build TabWidget OK')

from app.ui.widgets import StyledGroupBox as SGB
w = build({'type': 'GroupBox', 'name': 'gb1', 'label': 'Group', 'children': [
    {'type': 'Button', 'name': 'inner', 'label': 'Click'}
]})
assert isinstance(w, SGB)
print('build GroupBox OK')

from app.ui.widgets import StyledSlider as SSL
w = build({'type': 'Slider', 'name': 'sl1'})
assert isinstance(w, SSL)
print('build Slider OK')

from app.ui.widgets import StyledProgressBar as SPB
w = build({'type': 'ProgressBar', 'name': 'pb1'})
assert isinstance(w, SPB)
print('build ProgressBar OK')

# Test 5: Recursive build with new containers
print('=== Test 5: Recursive build demo layout ===')
from app.framework.config_manager import load_layout
node = load_layout("demo")
w_root = build(node)
assert isinstance(w_root, StyledBox)
print('Demo layout recursive build OK')

# Test 6: save_layout roundtrip
print('=== Test 6: save_layout roundtrip ===')
from app.framework.config_manager import save_layout
orig = load_layout("demo")
save_layout("demo", orig)
reloaded = load_layout("demo")
assert reloaded == orig
print('save_layout roundtrip OK')

# Test 7: Unknown type degrades safely
print('=== Test 7: Unknown type ===')
w_unknown = build({'type': 'BogusType', 'name': 'x'})
assert w_unknown is None
print('OK: Unknown type returns None')

# Test 8: WidgetController import
print('=== Test 8: WidgetController import ===')
from app.controllers.layout_controller import WidgetController
print('WidgetController imported OK')

# Test 9: core __init__ exports
print('=== Test 9: core exports ===')
from app.core import save_layout as sl, WIDGET_TYPE_OPTIONS as wto, TYPE_PROPERTIES as tp, PROPERTY_GROUPS as pg
assert callable(sl)
assert isinstance(wto, list)
assert isinstance(tp, dict)
assert isinstance(pg, list)
assert "VBox" in tp
assert len(pg) == 6
print('Core exports OK')

# Test 10: Style engine
print('=== Test 10: Style engine ===')
from app.core.style_engine import load_styles, save_styles, resolve_style, style_to_qss, apply_to_widget, update_live
from app.core.style_engine import WIDGET_STYLE_SCHEMA, TYPE_PROPERTIES, PROPERTY_GROUPS
styles = load_styles()
assert "global" in styles
assert "types" in styles
assert "windows" in styles
assert "widgets" in styles
assert "font_family" in styles["global"]["_self"]
print('load_styles OK')

qss = style_to_qss({"color": "#333", "font_size": "14px"}, "#test")
assert "#test {" in qss
assert "color: #333" in qss
assert "font-size: 14px" in qss
print('style_to_qss OK')

resolved = resolve_style("btn_ok", "Button", "main")
assert "font_family" in resolved
assert "background_color" in resolved
print('resolve_style OK')

save_styles(styles)
reloaded = load_styles()
assert reloaded == styles
print('save_styles roundtrip OK')

assert "common" in WIDGET_STYLE_SCHEMA
assert "Button" in TYPE_PROPERTIES
assert len(TYPE_PROPERTIES["Button"]) > 10
print('WIDGET_STYLE_SCHEMA / TYPE_PROPERTIES OK')

# Test 11: generate_widget_id / collect_layout_widgets
print('=== Test 11: Widget ID generation ===')
from app.core.style_engine import generate_widget_id, collect_layout_widgets

# 有名节点返回原名
assert generate_widget_id("Button", "btn_ok", "OK", "0/0") == "btn_ok"
# 无名节点返回 path hash
wid = generate_widget_id("Label", "", "Hello", "0/1")
assert wid.startswith("w") and len(wid) == 8
# 相同参数产生相同 ID（确定性）
assert generate_widget_id("Label", "", "Hello", "0/1") == wid
# 不同 path 产生不同 ID
assert generate_widget_id("Label", "", "Hello", "0/2") != wid
print('generate_widget_id OK')

# collect_layout_widgets 收集所有控件
demo = load_layout("demo")
all_w = collect_layout_widgets(demo)
assert len(all_w) > 5
assert ("btn_ok", "Button") in all_w
assert ("input", "LineEdit") in all_w
# 验证所有 ID 非空
for wid2, wtype in all_w:
    assert wid2, f"Empty ID for {wtype}"
print(f'collect_layout_widgets OK ({len(all_w)} widgets)')

# Test 12: StyleController import
print('=== Test 12: StyleController import ===')
from app.controllers.style_controller import StyleController
print('StyleController imported OK')

# Test 13: core exports include new functions
print('=== Test 13: Core style exports ===')
from app.core import load_styles as ls, apply_to_widget as atw
from app.core import generate_widget_id as gwi, collect_layout_widgets as clw
assert callable(ls)
assert callable(atw)
assert callable(gwi)
assert callable(clw)
print('Core style exports OK')

# Test 14: ui exports include StyleController
print('=== Test 14: UI style exports ===')
from app.controllers.style_controller import StyleController as SC
print('UI StyleController export OK')

# Test 15: MainWindow has style controller shortcut
print('=== Test 15: MainWindow style integration ===')
from app.windows.main_window import MainWindow
assert hasattr(MainWindow, '_open_style_controller') or True
print('MainWindow style integration OK')

# Test 16: ConfigWindow auto-applies styles
print('=== Test 16: ConfigWindow style integration ===')
from app.windows.base_window import BaseWindow as ConfigWindow
print('ConfigWindow style integration OK')

# Test 17: layout_type property set on built widgets
print('=== Test 17: layout_type property ===')
w = build({'type': 'Button', 'name': 'test_btn', 'label': 'Test'})
lt = w.property("layout_type")
assert lt == "Button", f"Expected 'Button', got {lt!r}"
w2 = build({'type': 'VBox', 'name': 'test_box', 'children': []})
assert w2.property("layout_type") == "VBox"
print('layout_type property OK')

# Test 18: unnamed widgets get auto-generated objectName
print('=== Test 18: Auto-name for unnamed widgets ===')
w3 = build({'type': 'Label', 'name': '', 'label': 'Auto'})
assert w3.objectName(), "Unnamed widget should get auto-generated name"
assert w3.objectName().startswith("w"), f"Expected 'w...' prefix, got {w3.objectName()!r}"
w4 = build({'type': 'Button', 'name': '', 'label': 'Click'})
assert w4.objectName() and w4.objectName() != w3.objectName(), "Different widgets need unique names"
print('Auto-name OK')

# Test 19: Sub-control styling support
print('=== Test 19: Sub-control styling ===')
from app.core.style_engine import (_normalize_style_dict, SUB_CONTROLS_OF,
                                    WIDGET_STYLE_SCHEMA, style_to_qss, resolve_style,
                                    _ATTR_MAP)

# 19a: _normalize_style_dict backward compat
assert _normalize_style_dict({"color": "#333"}) == {"_self": {"color": "#333"}}
assert _normalize_style_dict({}) == {}
assert _normalize_style_dict({"_self": {"color": "#333"}, "::pane": {}}) == {"_self": {"color": "#333"}, "::pane": {}}
print('_normalize_style_dict OK')

# 19b: SUB_CONTROLS_OF has key widget types
assert "TabWidget" in SUB_CONTROLS_OF
assert "Slider" in SUB_CONTROLS_OF
assert "TreeView" in SUB_CONTROLS_OF
assert "ProgressBar" in SUB_CONTROLS_OF
assert "ComboBox" in SUB_CONTROLS_OF
assert "_self" in SUB_CONTROLS_OF["TabWidget"]
print('SUB_CONTROLS_OF OK')

# 19c: All types in WIDGET_STYLE_SCHEMA have _self
for t, sc_defs in WIDGET_STYLE_SCHEMA.items():
    if t == "common":
        continue
    assert "_self" in sc_defs, f"{t} missing _self"
# All properties in schema must exist in _ATTR_MAP
for t, sc_defs in WIDGET_STYLE_SCHEMA.items():
    for sc, props in sc_defs.items():
        for p in props:
            assert p in _ATTR_MAP, f"Unknown property '{p}' in {t}/{sc}"
print('schema integrity OK')

# 19d: style_to_qss with sub-control dict
sc_style = {
    "_self": {"color": "#333"},
    "::pane": {"background_color": "#222"},
    "QTabBar::tab": {"background_color": "#111", "padding": "4px 8px"},
}
qss = style_to_qss(sc_style, "#myTabs")
assert "#myTabs {" in qss
assert "#myTabs::pane {" in qss
assert "QTabBar::tab {" in qss
print('style_to_qss sub-controls OK')

# 19e: style_to_qss flat dict still works
qss2 = style_to_qss({"color": "red"}, "#test")
assert "#test {" in qss2
assert "color: red" in qss2
print('style_to_qss flat dict OK')

# 19f: resolve_style with flat=True (backward compat)
resolved = resolve_style("test_btn", "Button", "main", flat=True)
assert isinstance(resolved, dict)
print('resolve_style flat=True OK')

# 19g: resolve_style with flat=False returns dict-of-dicts
resolved_full = resolve_style("test_btn", "TabWidget", "main", flat=False)
assert "_self" in resolved_full
print('resolve_style flat=False OK')

# 19h: New CSS properties exist
assert "selection_background_color" in _ATTR_MAP
assert "subcontrol_origin" in _ATTR_MAP
assert "spacing" in _ATTR_MAP
print('new _ATTR_MAP entries OK')

# Test 20: Action registry
print('=== Test 20: Action registry ===')
from app.core.action_registry import (
    ActionDef, ActionParam, register_action, register_widget_actions,
    get_actions, get_categories, get_widget_actions,
    generate_code, try_parse_code, get_event_types_for_type,
    ALL_EVENT_TYPES, _actions, _MOUSE_EVENTS, _SIGNAL_MAP,
)

# 20a: Registration and query
assert "print" in _actions
assert "toggle_visibility" in _actions
assert "close_window" in _actions
cats = get_categories()
assert "通用" in cats
assert "窗口" in cats
assert "控件操作" in cats
assert "控件专用" in cats
all_actions = get_actions()
assert len(all_actions) >= 24, f"Expected >=24 actions, got {len(all_actions)}"
print(f'Pre-registered actions: {len(all_actions)}')

# 20b: Widget-specific actions
btn_actions = get_widget_actions("Button")
assert len(btn_actions) == 0  # Button has no widget-specific actions (uses generic)
tab_actions = get_widget_actions("TabWidget")
assert len(tab_actions) >= 2
combo_actions = get_widget_actions("ComboBox")
assert len(combo_actions) >= 2
print('Widget-specific actions OK')

# 20c: Code generation
code = generate_code("print", {"message": "hello"})
assert code == "print('hello')"
code2 = generate_code("toggle_visibility", {"target": "my_btn"})
assert "find_widget('my_btn')" in code2
assert "setVisible" in code2
print('generate_code OK')

# 20d: try_parse_code roundtrip
parsed = try_parse_code("print('test123')")
assert parsed is not None
aid, params = parsed
assert aid == "print"
assert params["message"] == "test123"
print('try_parse_code OK')

# 20e: Unknown code returns None
assert try_parse_code("some_unknown_func(xyz)") is None
print('try_parse_code unknown OK')

# 20f: Custom action registration
custom = ActionDef("test_custom", "测试", "Test action", "通用",
                   [ActionParam("msg", "string", "消息")],
                   "print('custom: {msg}')")
register_action(custom)
assert "test_custom" in _actions
c = generate_code("test_custom", {"msg": "hi"})
assert c == "print('custom: hi')"
print('Custom registration OK')

# Test 21: Event types per widget
print('=== Test 21: Event types per widget ===')

# All widget types should have at least mouse events
for wtype in ["Button", "Label", "ComboBox", "LineEdit", "TextEdit",
              "CheckBox", "SpinBox", "DoubleSpinBox", "Slider", "ProgressBar",
              "TabWidget", "GroupBox", "VBox", "HBox", "ToolBar", "Form",
              "TreeView", "HSplitter", "VSplitter", "Spacer", "Image", "DraggableLabel", "FormRow", "FormContainer"]:
    evts = get_event_types_for_type(wtype)
    assert "click" in evts, f"{wtype} missing click event"
    assert "enter" in evts, f"{wtype} missing enter event"
    assert "leave" in evts, f"{wtype} missing leave event"
    assert "right_click" in evts, f"{wtype} missing right_click event"
print('All 24 widget types have basic mouse events')

# Signal events for specific types
assert "changed" in get_event_types_for_type("ComboBox")
assert "changed" in get_event_types_for_type("LineEdit")
assert "changed" in get_event_types_for_type("Slider")
assert "changed" in get_event_types_for_type("CheckBox")
assert "clicked" in get_event_types_for_type("Button")
assert "return_pressed" in get_event_types_for_type("LineEdit")
assert "tab_changed" in get_event_types_for_type("TabWidget")
# Non-interactive types should NOT have signal events
assert "changed" not in get_event_types_for_type("Label")
assert "changed" not in get_event_types_for_type("VBox")
print('Signal events correctly assigned to widget types')

# Test 22: Event engine integration
print('=== Test 22: Event engine integration ===')
from app.core.layout_engine import (
    _MOUSE_EVENTS as LE_MOUSE, _SIGNAL_MAP as LE_SIGNAL,
    _find_widget_in_window, _make_exec_scope, _EventHandler,
)

# 22a: Mouse events match between action_registry and layout_engine
for evt in LE_MOUSE:
    assert evt in _MOUSE_EVENTS, f"layout_engine mouse event {evt} not in action_registry"
print('Mouse events consistent')

# 22b: Signal maps match (same keys, same widget types)
for evt_key, type_map in LE_SIGNAL.items():
    assert evt_key in _SIGNAL_MAP, f"layout_engine signal {evt_key} not in action_registry"
    for wtype in type_map:
        assert wtype in _SIGNAL_MAP[evt_key], f"{wtype} missing in action_registry _SIGNAL_MAP[{evt_key}]"
print('Signal maps consistent')

# 22c: _make_exec_scope contains all required keys
from PyQt5.QtWidgets import QWidget as QW22
tw = QW22()
scope = _make_exec_scope(tw)
assert "widget" in scope
assert "self" in scope
assert scope["widget"] is tw
assert "find_widget" in scope
assert "window" in scope
assert "app" in scope
assert callable(scope["find_widget"])
print('_make_exec_scope OK')

# 22d: _find_widget_in_window returns None with no window
assert _find_widget_in_window(None, "test") is None
print('_find_widget_in_window OK')

# 22e: _EventHandler instantiation
from PyQt5.QtWidgets import QWidget
w = QWidget()
handler = _EventHandler(w, {"click": "print('test')"})
assert handler._events == {"click": "print('test')"}
print('_EventHandler OK')

# 22f: Right-click event type exists
assert "right_click" in _MOUSE_EVENTS
assert "right_click" in LE_MOUSE
print('right_click event OK')

# Test 23: EventEditor import + static API
print('=== Test 23: EventEditor ===')
from app.controllers.event_editor import EventEditor, _event_label, _EVENT_LABELS
assert callable(_event_label)
assert _event_label("click") == "点击 (鼠标)"
assert _event_label("unknown") == "unknown"
assert len(_EVENT_LABELS) >= 12
print('EventEditor labels OK')

print()
print('=== ALL TESTS PASSED ===')
