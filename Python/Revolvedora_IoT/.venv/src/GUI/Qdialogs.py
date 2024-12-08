from Diagrams import Diagrams_rc
from Icons import Icons_rc
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QLineEdit
from PyQt5.QtWidgets import QTableWidgetItem
from Queries import *
from Revolvedora_IoT import *
from tank import *
from valve import *
from Qdialogs import *
import multiprocessing
import queue
import sys


class TankController(Ui_tank):
    def __init__(self, levelName, level_ID, motorName, motorID):
        super().__init__()
        self.dialog = QtWidgets.QDialog()  # Create the QDialog instance
        self.dialog.setWindowModality(QtCore.Qt.NonModal)  # Make the dialog non-modal
        self.dialog.setWindowFlags(QtCore.Qt.Window)  # Ensure it behaves as a regular window
        self.setupUi(self.dialog)  # Set up the UI components

        # Connect UI signals to methods
        self.minimize_window_button.clicked.connect(self.minimize_window)
        self.close_window_button.clicked.connect(self.close_window)
        self.applyChangesLevelbtn.clicked.connect(self.update_level_setpoint)
        self.applyChangesMixerbtn.clicked.connect(self.update_mixer_setpoint)

        self.__levelName = levelName
        self.__level_ID = level_ID
        self.__motorName = motorName
        self.__motorID = motorID
        self.DeviceName.setText(f"{levelName} and {motorName}")
        self.initialize_data()

    def show(self):
        """Show the dialog."""
        self.dialog.show()  # Use `show()` instead of `exec_()` for non-modal behavior

    def minimize_window(self):
        self.dialog.showMinimized()

    def close_window(self):
        self.dialog.close()

    def update_level_setpoint(self):
        value = self.eTextLevelSetpoint.toPlainText()
        try:
            value = float(value)
            if 0 <= value <= 30:
                print(f"Level setpoint updated to: {value}")
                Package = {
                    "Operation": OP_LEVEL_CONTROL,
                    "SetPoint": value,
                    "ID": self.__level_ID
                }
                print(PostRequestOP_VARIABLE_SETPOINT_CONTROL(ServerIP, Package))
                self.dialog.close()
            else:
                print("Error: The level must be between 0 and 30.")
        except ValueError:
            print("Error: The input must be a number.")

    def update_mixer_setpoint(self):
        value = self.eTextMixerSetpoint.toPlainText()
        try:
            value = float(value)
            if value == 0 or value == 1:
                print(f"Mixer setpoint updated to: {value}")
                Package = {
                    "Operation": OP_MOTOR_CONTROL,
                    "SetPoint": value,
                    "ID": self.__motorID
                }
                print(PostRequestOP_VARIABLE_SETPOINT_CONTROL(ServerIP, Package))
                self.dialog.close()
            else:
                print("Error: The mixer setpoint must be either 0 or 1.")
        except ValueError:
            print("Error: The input must be 0 or 1.")

    def initialize_data(self):
        """Set default values for Valve properties."""
        self.actualStateLLevel.setText("0.00")
        self.actualStateLMixer.setText("0%")


class ValveController(Ui_Valve):
    def __init__(self, flowmeterName, flowmeterID, valveName, valveID):
        super().__init__()
        self.dialog = QtWidgets.QDialog()  # Create the QDialog instance
        self.dialog.setWindowModality(QtCore.Qt.NonModal)  # Make the dialog non-modal
        self.dialog.setWindowFlags(QtCore.Qt.Window)  # Ensure it behaves as a regular window
        self.setupUi(self.dialog)  # Set up the UI components

        # Connect buttons to actions
        self.minimize_window_button_2.clicked.connect(self.minimize_window)
        self.close_window_button_2.clicked.connect(self.close_window)
        self.applyChangesOPbtn.clicked.connect(self.update_OpeningPercentage)

        self.__flowmeterName = flowmeterName
        self.__flowmeterID = flowmeterID
        self.__valveName = valveName
        self.__valveID = valveID
        self.DeviceName.setText(f"{flowmeterName} and {valveName}")
        self.initialize_data()

    def show(self):
        """Show the dialog."""
        self.dialog.show()  # Use `show()` instead of `exec_()` for non-modal behavior

    def minimize_window(self):
        self.dialog.showMinimized()

    def close_window(self):
        self.dialog.close()

    def update_OpeningPercentage(self):
        """Handle level setpoint changes."""
        value = self.eTextOpeningPercentageSetpoint.toPlainText()
        try:
            value = float(value)
            if 0 <= value <= 90:
                print(f"Opening Percentage setpoint updated to: {value}")
                Package = {
                    "Operation": OP_OPENING_PERCENTAGE_SETPOINT_CONTROL,
                    "SetPoint": value,
                    "ID": self.__valveID
                }
                print(PostRequestOP_VARIABLE_SETPOINT_CONTROL(ServerIP, Package))
                self.dialog.close()
            else:
                print("Error: The value must be between 0 and 90.")
        except ValueError:
            print("Error: The input must be a number.")

    def initialize_data(self):
        """Set default values for Valve properties."""
        self.actualStateLFlow.setText("0.00")
        self.actualStateLOpeningPercentage.setText("0%")

