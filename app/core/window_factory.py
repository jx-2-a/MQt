from app.ui.main_window import MainWindow


def create_main_window(title="QS Controller"):
    return MainWindow(title)


def open_sub_window(parent, title="Sub Window", config_key="sub"):
    if isinstance(parent, MainWindow):
        return parent.open_sub_window(config_key, title)
    from app.ui.config_window import ConfigWindow
    sub = ConfigWindow(config_key, parent)
    sub.setWindowTitle(title)
    sub.show()
    return sub
