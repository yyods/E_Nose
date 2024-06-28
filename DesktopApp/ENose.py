#!/usr/bin/env python3

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from main_window import MainWindow

if __name__ == '__main__':
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app = QApplication(sys.argv)
    app.setApplicationName("Enose")
    app.setQuitOnLastWindowClosed(True)

    window = MainWindow()

    def handle_exit():
        window.close()

    app.aboutToQuit.connect(handle_exit)
    sys.exit(app.exec_())
