from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QMainWindow
from src.app.run_window import Ui_MainWindow
import sys

QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)  # enable highdpi scaling

app = QApplication(sys.argv)
MainWindow = QMainWindow()
ui = Ui_MainWindow()
ui.setupUi(MainWindow)
MainWindow.show()
sys.exit(app.exec_())
# http: // trevorius.com/scrapbook/uncategorized/part-1-drawing-with-pyopengl-using-moden-opengl-buffers/
