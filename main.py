import sys
from PyQt5.QtWidgets import QApplication
from app.core.window_factory import create_main_window


def main():
    app = QApplication(sys.argv)
    window = create_main_window()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
