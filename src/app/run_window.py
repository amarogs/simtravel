# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\run_window.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from src.simulator.simulation import Simulation
from PyQt5 import QtCore, QtGui, QtWidgets
from src.app.animationOGL import AnimationWidget
from src.models.cities import SquareCity

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 800)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        # Create the OpenGL animation.



        # Create the simulation
        simulation = Simulation(0.1, 0.1, "central")

        simulation.set_simulation_units(speed=10, cell_length=5, simulation_speed=1, battery=0.1, cs_power=7)
        simulation.set_battery_distribution(lower=0.2, std=0.25)
        simulation.set_idle_distribution(upper=10, lower=1, std=0.25)
        simulation.create_city(SquareCity, scale=3, block_scale=2)
        simulation.stations_placement(min_plugs_per_station=2, min_num_stations=10)
        simulation.create_simulator()


        self.animation = AnimationWidget(simulation.SIZE, 800, 800, 10,simulation.city_matrix)
        self.animation.add_vehicles(simulation.vehicles)

        self.animation.setGeometry(QtCore.QRect(70, 80, 671, 471))
        self.animation.setObjectName("animation")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(10, 30, 231, 16))
        self.label.setObjectName("label")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 25))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label.setText(_translate("MainWindow", "Simulated time: "))


