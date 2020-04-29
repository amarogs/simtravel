from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import *
from src.app.main import SimtravelMainWindow

if __name__ == "__main__":
    # enable highdpi scaling
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)  
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

    # Create the application 
    app = QApplication([])
    QtGui.QApplication.setStyle(QtGui.QStyleFactory.create('Cleanlooks'))
    app.setApplicationName("SIMTRAVEL")
    main_window = SimtravelMainWindow()
    main_window.show()
    app.exec_()