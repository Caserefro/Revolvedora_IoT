import json
import multiprocessing
import queue
import sys
import sys
import threading

import matplotlib
import requests
from ContinousMode import *
from Diagrams import Diagrams_rc
from Icons import Icons_rc
from MixtureMode import *
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal, QTimer, Qt, QRect
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QLineEdit, QTableWidgetItem, QTextEdit
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QMdiSubWindow
from Queries import *
from Revolvedora_IoT import *
from tank import *
from valve import *

# from Qdialogs import *

matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.ticker as ticker
import queue
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5 import uic
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtMultimedia import QAudioDeviceInfo, QAudio, QCameraInfo

SetPointValve1 = 0
SetPointValve2 = 0
SetPointValve3 = 0
SetPointTank3 = 0
ServerIP = "127.0.0.1:5000"
sensor_list = [1, 2, 3, 4, 5, 6]  # Replace with actual sensor IDs
task_queue = queue.Queue()


class Revolvedora_IoT_UI(QMainWindow, Ui_MainWindow):
    def __init__(self, serverIP):
        super(Revolvedora_IoT_UI, self).__init__()
        self.setupUi(self)
        self.setupUiExtra(self)
        # Store instances for valves and tanks
        self.valve_controllers = {}  # To store ValveController instances
        self.tank_controllers = {}  # To store TankController instances
        self.server_ip = serverIP
        self.devices_data = {}  # To store the retrieved data
        # Available Modes: Mixing, Continous.
        self.SelectedMode = "M"
        self.CurrentMode = "M"  # will change to this once a controlSchema is mandated.
        # Timer setup to call UpdateDevicesData every 5000 ms (5 seconds)
        self.subwindow_manager = []

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateDataPeriodically)  # Connect the timer to a method
        self.timer.start(5000)  # Start the timer, update every 5000 ms

    def setupUiExtra(self, MainWindow):
        self.close_window_button.clicked.connect(MainWindow.close)
        self.minimize_window_button.clicked.connect(MainWindow.showMinimized)
        self.restore_window_button.clicked.connect(self.toggle_maximize_restore)
        self.is_maximized = False
        self.setFixedSize(1570, 900)

        self.open_close_side_bar_btn.clicked.connect(self.toggle_sidebar)
        self.MixingModeRbtn.toggled.connect(self.handle_MixingModeCbtn_state)
        self.ContinousModeRbtn.toggled.connect(self.handle_ContinousModebtn_state)
        self.QuickConfigbtn.clicked.connect(self.onQuickSetupClicked)

        self.Valve_1btn.clicked.connect(self.on_valve1_clicked)
        self.Valve_2btn.clicked.connect(self.on_valve2_clicked)
        self.Valve_3btn.clicked.connect(self.on_valve3_clicked)
        self.Tank_1btn.clicked.connect(self.on_tank1_clicked)
        self.Tank_2btn.clicked.connect(self.on_tank2_clicked)
        self.Tank_3btn.clicked.connect(self.on_tank3_clicked)
        self.Tank_4btn.clicked.connect(self.on_tank4_clicked)

        self.DashboardAddbtn.clicked.connect(self.AddWindow)  # here goes the function that adds tabs to the mdi Area.

        self.Valve_1btn.setStyleSheet("QPushButton { background-color: transparent; border: none; }")
        self.Valve_2btn.setStyleSheet("QPushButton { background-color: transparent; border: none; }")
        self.Valve_3btn.setStyleSheet("QPushButton { background-color: transparent; border: none; }")
        self.Tank_1btn.setStyleSheet("QPushButton { background-color: transparent; border: none; }")
        self.Tank_2btn.setStyleSheet("QPushButton { background-color: transparent; border: none; }")
        self.Tank_3btn.setStyleSheet("QPushButton { background-color: transparent; border: none; }")
        self.Tank_4btn.setStyleSheet("QPushButton { background-color: transparent; border: none; }")
        self.Valve_1btn.setCursor(QtCore.Qt.PointingHandCursor)
        self.Valve_2btn.setCursor(QtCore.Qt.PointingHandCursor)
        self.Valve_3btn.setCursor(QtCore.Qt.PointingHandCursor)
        self.Tank_1btn.setCursor(QtCore.Qt.PointingHandCursor)
        self.Tank_2btn.setCursor(QtCore.Qt.PointingHandCursor)
        self.Tank_3btn.setCursor(QtCore.Qt.PointingHandCursor)
        self.Tank_4btn.setCursor(QtCore.Qt.PointingHandCursor)
        self.DevicetableWidget.setColumnWidth(1, 150)  # Column 2 width: 200 pixels
        self.DevicetableWidget.setColumnWidth(2, 200)  # Column 2 width: 200 pixels
        self.DevicetableWidget.setColumnWidth(5, 250)  # Column 2 width: 200 pixels
        self.ActiveDevicesTable.setColumnWidth(0, 80)  # Column 2 width: 200 pixels
        self.ActiveDevicesTable.setColumnWidth(1, 100)  # Column 2 width: 200 pixels

        # self.mdiAreaDashboard = QtWidgets.QMdiArea(self.frame_2)
        # self.gridLayout.addWidget(self.mdiAreaDashboard, 0, 0, 1, 1)

    def toggle_sidebar(self):
        current_width = self.left_frame.width()
        new_width = 0 if current_width > 0 else 200  # or whatever width you want when expanded
        self.left_frame.setFixedWidth(new_width)

    def toggle_maximize_restore(self):
        """Toggles between maximized and normal state."""
        window = QtWidgets.QApplication.activeWindow()
        if self.is_maximized:
            window.showNormal()
            self.is_maximized = False
            # Update the button icon to "maximize"

        else:
            window.showMaximized()
            self.is_maximized = True
            # Update the button icon to "restore"
        # Define functions for button clicks

    def on_valve1_clicked(self):
        print("Valve 1 clicked")
        if 1 not in self.valve_controllers:  # Create if not already created
            self.valve_controllers[1] = ValveController("FT-103", 1, "FC-102", 2)
        self.valve_controllers[1].show()

    def on_valve2_clicked(self):
        print("Valve 2 clicked")
        if 2 not in self.valve_controllers:
            self.valve_controllers[2] = ValveController("FT-203", 3, "FC-202", 4)
        self.valve_controllers[2].show()

    def on_valve3_clicked(self):
        print("Valve 3 clicked")
        if 3 not in self.valve_controllers:
            self.valve_controllers[3] = ValveController("FT-304", 5, "FC-303", 6)
        self.valve_controllers[3].show()

    def on_tank1_clicked(self):
        print("Tank 1 clicked")
        if 1 not in self.tank_controllers:
            self.tank_controllers[1] = TankController("Not Asssigned", 0, "Not Assigned", 0)
        self.tank_controllers[1].show()

    def on_tank2_clicked(self):
        print("Tank 2 clicked")
        if 2 not in self.tank_controllers:
            self.tank_controllers[2] = TankController("Not Asssigned", 0, "Not Assigned", 0)
        self.tank_controllers[2].show()

    def on_tank3_clicked(self):
        print("Tank 3 clicked")
        if 3 not in self.tank_controllers:
            self.tank_controllers[3] = TankController("LT-302", 7, "SC301", 8)
        self.tank_controllers[3].show()

    def on_tank4_clicked(self):
        print("Tank 4 clicked")
        if 4 not in self.tank_controllers:
            self.tank_controllers[4] = TankController("Not Asssigned", 0, "Not Assigned", 0)
        self.tank_controllers[4].show()

    def updateDataPeriodically(self):
        sensor_list = [1, 2, 3, 4, 5, 6, 7, 8]  # Replace with actual sensor IDs
        self.UpdateDevicesData(sensor_list)

    def UpdateDevicesData(self, sensor_list):
        for sensor_id in sensor_list:
            # Fetch data for the sensor
            response = PostRequestOP_Sensor_Records(self.server_ip, sensor_id)
            try:
                data = json.loads(response)  # Deserialize JSON response
            except json.JSONDecodeError:
                continue  # Skip if response is not valid JSON

            if data and "error" not in data:
                self.devices_data[sensor_id] = data

                # Extract details
                device_id = data["sensor_id"]
                ip_address = data["ip_address"]
                device_type = data["device_type"]
                tag = data.get("tag", "N/A")
                place = data["place"]
                description = data["description"]
                state = (
                    data["records"][0].get("flow_value", "N/A")
                    if device_type == "Flowmeter" else
                    data["records"][0].get("valve_angle", "N/A")
                    if device_type == "Electromechanical Valve" else
                    data["records"][0].get("level_state", "N/A")
                    if device_type == "Liquid Level Meter" else
                    data["records"][0].get("motor_state", "N/A")
                    if device_type == "Mixer Motor" else "N/A"
                ) if data["records"] else "No Data"

                # Update or add data in DevicetableWidget
                row_position = None
                for row in range(self.DevicetableWidget.rowCount()):
                    existing_device_id = self.DevicetableWidget.item(row, 0).text()
                    if existing_device_id == str(device_id):
                        row_position = row
                        break

                if row_position is None:
                    row_position = self.DevicetableWidget.rowCount()
                    self.DevicetableWidget.insertRow(row_position)

                fields = [
                    (0, str(device_id)),
                    (1, str(ip_address)),
                    (2, str(device_type)),
                    (3, str(tag)),
                    (4, str(place)),
                    (5, str(description)),
                    (6, str(state)),
                    (7, str(state))
                ]

                for column, new_value in fields:
                    current_item = self.DevicetableWidget.item(row_position, column)
                    if current_item is None or current_item.text() != new_value:
                        self.DevicetableWidget.setItem(row_position, column, QTableWidgetItem(new_value))

                # Update or add data in ActiveDevicesTable
                active_row_position = None
                for row in range(self.ActiveDevicesTable.rowCount()):
                    existing_tag = self.ActiveDevicesTable.item(row, 1).text().strip()
                    if existing_tag.lower() == str(tag).strip().lower():
                        active_row_position = row
                        break

                if active_row_position is None:
                    active_row_position = self.ActiveDevicesTable.rowCount()
                    self.ActiveDevicesTable.insertRow(active_row_position)

                active_fields = [
                    (0, str(device_id)),  # D_ID
                    (1, str(tag).strip()),  # TAG
                    (2, str(state))  # STATE
                ]

                for column, new_value in active_fields:
                    current_item = self.ActiveDevicesTable.item(active_row_position, column)
                    if current_item is None or current_item.text() != new_value:
                        self.ActiveDevicesTable.setItem(active_row_position, column, QTableWidgetItem(new_value))

                # Update PID-specific UI elements
                if device_id == 1:
                    buffer = str(state)
                if device_id == 2:
                    valve_text = (
                        f"Valve 1:\nSP: {str(SetPointValve1)} L\nCV: {buffer} L/min/ {str(state)}º"
                        if self.CurrentMode == "M" else
                        f"Valve 1:\nSP: {str(SetPointValve1)} L/min\nCV: {buffer} L/min/ {str(state)}º"
                    )
                    self.Valve_1L.setText(valve_text)
                if device_id == 3:
                    buffer = str(state)
                if device_id == 4:
                    valve_text = (
                        f"Valve 2:\nSP: {str(SetPointValve2)} L\nCV: {buffer} L/min/ {str(state)}º"
                        if self.CurrentMode == "M" else
                        f"Valve 2:\nSP: {str(SetPointValve2)} L/min\nCV: {buffer} L/min/ {str(state)}º"
                    )
                    self.Valve_2L.setText(valve_text)
                if device_id == 5:
                    buffer = str(state)
                if device_id == 6:
                    valve_text = (
                        f"Valve 3:\nSP: {str(SetPointValve3)} L\nCV: {buffer} L/min/ {str(state)}º"
                        if self.CurrentMode == "M" else
                        f"Valve 3:\nSP: {str(SetPointValve3)} L/min\nCV: {buffer} L/min/ {str(state)}º"
                    )
                    self.Valve_3L.setText(valve_text)
                if device_id == 7:
                    self.Tank_3L.setText(f"Nivel tanque 3:\n{str(state)}")
                if device_id == 8:
                    self.Tank_3ML.setText("Motor: ON" if state == 1 else "Motor: OFF")
            else:
                print(f"Failed to update data for SensorID {sensor_id}")
        self.UpdateAllGraphs()
        # Function activated by the button

    def onQuickSetupClicked(self):
        try:
            if self.SelectedMode == "M":
                # Attempt to close the ContinuousMode dialog if it exists
                self.ContinousModeDialog.dialog.close()
            elif self.SelectedMode == "C":
                # Attempt to close the MixtureMode dialog if it exists
                self.MixtureModeDialog.dialog.close()
        except AttributeError:
            # Ignore if the dialog doesn't exist or is already closed
            pass

        # Open the appropriate dialog
        if self.SelectedMode == "M":
            self.MixtureModeDialog = MixtureMode()
            self.MixtureModeDialog.show()
        elif self.SelectedMode == "C":
            self.ContinousModeDialog = ContinousMode()
            self.ContinousModeDialog.show()

    def handle_MixingModeCbtn_state(self, checked):
        if checked:
            self.SelectedMode = "M"
            print(f"Mode change: {self.SelectedMode}")

    def handle_ContinousModebtn_state(self, checked):
        if checked:
            self.SelectedMode = "C"
            print(f"Mode change: {self.SelectedMode}")

    def AddWindow(self):
        selected_row = self.ActiveDevicesTable.currentRow()
        if selected_row == -1:
            print("No row selected.")
            return

        # Get the tag (device_ID) from the selected row in the table
        device_ID = int(self.ActiveDevicesTable.item(selected_row, 0).text().strip())

        # Check if a subwindow for this device_ID already exists
        for sub_window, canvas, existing_id in self.subwindow_manager:
            if existing_id == device_ID:
                print(f"Subwindow for Device ID {device_ID} already exists.")
                return

        # Call Recover_recordsLocal and store the returned flow_values and times
        flow_values, times = self.Recover_recordsLocal(device_ID)

        # Check if any records were found
        if not flow_values or not times:
            print(f"No data found for Device ID: {device_ID}")
            return

        # Create a new QMdiSubWindow
        sub_window = QtWidgets.QMdiSubWindow()
        sub_window.setWindowTitle(f"Graph for Device ID: {device_ID}")

        # Create a canvas for the plot
        canvas = MplCanvas(self, width=5, height=4, dpi=100)

        times.reverse()
        flow_values.reverse()
        # Plot the data on the canvas
        canvas.axes.plot(times, flow_values, marker='o', linestyle='-', color='b')
        canvas.axes.set_title(f"Flow Data for Device ID: {device_ID}")
        canvas.axes.set_xlabel("Time")
        canvas.axes.set_ylabel("Flow Value")
        canvas.axes.set_xticklabels([])
        canvas.axes.tick_params(axis='x', which='both', bottom=False, top=False)

        # Set the canvas as the widget for the subwindow
        sub_window.setWidget(canvas)

        # Add the subwindow to the MDI area and display it
        self.mdiAreaDashboard.addSubWindow(sub_window)
        sub_window.show()

        # Add the subwindow and its associated device_ID to the subwindow_manager
        self.subwindow_manager.append((sub_window, canvas, device_ID))

        # Connect the subwindow's destruction event to the cleanup function
        sub_window.destroyed.connect(lambda: self.cleanUpSubwindow(sub_window))

        # Optional: Arrange windows neatly
        self.mdiAreaDashboard.tileSubWindows()

    def cleanUpSubwindow(self, sub_window):
        # Find the index of the subwindow in the manager
        for index, (window, _, device_ID) in enumerate(self.subwindow_manager):
            if window == sub_window:
                # Remove the closed subwindow from the manager
                del self.subwindow_manager[index]
                print(f"Subwindow for Device ID {device_ID} has been removed.")
                break

    def UpdateAllGraphs(self):
        for sub_window, canvas, device_ID in self.subwindow_manager:
            flow_values, times = self.Recover_recordsLocal(device_ID)
            if flow_values and times:
                canvas.axes.clear()
                times.reverse()
                flow_values.reverse()
                canvas.axes.plot(times, flow_values, marker='o', linestyle='-', color='g')
                canvas.axes.set_title(f"Updated Flow Data for Device ID: {device_ID}")
                canvas.axes.set_xlabel("Time")
                canvas.axes.set_ylabel("Flow Value")
                canvas.axes.set_xticklabels([])
                canvas.draw()

    def Recover_recordsLocal(self, device_ID):
        # Check if device_ID exists and has 'records'
        if device_ID in self.devices_data and 'records' in self.devices_data[device_ID]:
            records = self.devices_data[device_ID]['records']
            device_type = self.devices_data[device_ID].get('device_type', '')

            # Determine which value to extract based on the device type
            if device_type == 'Flowmeter':
                values = [record.get('flow_value', 0) for record in records]
            elif device_type == 'Electromechanical Valve':
                values = [record.get('valve_angle', 0) for record in records]
            else:
                print(f"Unsupported device type '{device_type}' for Device ID: {device_ID}")
                return [], []

            # Extract timestamps
            times = [record.get('time', '') for record in records]
            return values, times
        else:
            print(f"No records found for Device ID: '{device_ID}'")
            return [], []


class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)
        fig.tight_layout()


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

    # def update_level_setpoint(self):
    #     value = self.eTextLevelSetpoint.toPlainText()
    #     try:
    #         value = float(value)
    #         if 0 <= value <= 30:
    #             print(f"Level setpoint updated to: {value}")
    #             Package = {
    #                 "Operation": OP_LEVEL_CONTROL,
    #                 "SetPoint": value,
    #                 "ID": self.__level_ID
    #             }
    #             print(PostRequestOP_VARIABLE_SETPOINT_CONTROL(ServerIP, Package))
    #             self.dialog.close()
    #         else:
    #             print("Error: The level must be between 0 and 30.")
    #     except ValueError:
    #         print("Error: The input must be a number.")

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
                    "Operation": OP_OPENING_ANGLE_SETPOINT_CONTROL,
                    "SetPoint": value,
                    "SensorID": self.__valveID
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


class GraphWidget(QWidget):
    def __init__(self, parent=None):
        super(GraphWidget, self).__init__(parent)
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def plot_data(self, x, y):
        """Plots data on the graph."""
        ax = self.figure.add_subplot(111)
        ax.clear()
        ax.plot(x, y)
        ax.set_title("Sample Graph")
        ax.set_xlabel("X-axis")
        ax.set_ylabel("Y-axis")
        self.canvas.draw()


class MixtureMode(Ui_MixtureMode):
    def __init__(self):
        super().__init__()
        self.dialog = QtWidgets.QDialog()  # Create the QDialog instance
        self.dialog.setWindowModality(QtCore.Qt.NonModal)  # Make the dialog non-modal
        self.dialog.setWindowFlags(QtCore.Qt.Window)  # Ensure it behaves as a regular window
        self.setupUi(self.dialog)  # Set up the UI components

        # Connect UI signals to methods
        self.minimize_window_button.clicked.connect(self.minimize_window)
        self.close_window_button.clicked.connect(self.close_window)
        self.applyChangesbtn.clicked.connect(self.UpdateControlSchema)
        self.tankSelectorCBox.addItem("Tanque #3")

        # this is rigged to work only with tank 3. ideally, here a query would be made for all the online tanks.
        self.__tagValve1 = "FC-102"
        self.__Valve1_ID = 2
        self.__tagValve2 = "FC-202"
        self.__Valve2_ID = 4

        self.tagValve1L.setText(f"Input Valve:\n{self.__tagValve1}")
        self.tagValve2L.setText(f"Input Valve:\n{self.__tagValve2}")

    # self.initialize_data()

    def show(self):
        self.dialog.show()  # Use `show()` instead of `exec_()` for non-modal behavior

    def minimize_window(self):
        self.dialog.showMinimized()

    def close_window(self):
        self.dialog.close()

    def UpdateControlSchema(self):
        pass


class ContinousMode(Ui_ContinousMode):
    def __init__(self):
        super().__init__()
        self.dialog = QtWidgets.QDialog()  # Create the QDialog instance
        self.dialog.setWindowModality(QtCore.Qt.NonModal)  # Make the dialog non-modal
        self.dialog.setWindowFlags(QtCore.Qt.Window)  # Ensure it behaves as a regular window
        self.setupUi(self.dialog)  # Set up the UI components
        # Connect UI signals to methods
        self.minimize_window_button.clicked.connect(self.minimize_window)
        self.close_window_button.clicked.connect(self.close_window)
        self.applyChangesbtn.clicked.connect(self.UpdateControlSchema)
        self.tankSelectorCBox.addItem("Tanque #3")
        # this is rigged to work only with tank 3. ideally, here a query would be made for all the online tanks, and also their control lines would be described aswell.
        self.__tagValve1 = "FC-102"
        self.__Valve1_ID = 2
        self.__tagValve2 = "FC-202"
        self.__Valve2_ID = 4
        self.__tagValveOutputL = "FC-304"
        self.__ValveOutputL_ID = 6
        self.tagValve1L.setText(f"Input Valve:\n{self.__tagValve1}")
        self.tagValve2L.setText(f"Input Valve:\n{self.__tagValve2}")
        self.tagValveOutputL.setText(f"Output Valve:\n{self.__tagValveOutputL}")

    # self.initialize_data()

    def show(self):
        self.dialog.show()  # Use `show()` instead of `exec_()` for non-modal behavior

    def minimize_window(self):
        self.dialog.showMinimized()

    def close_window(self):
        self.dialog.close()

    def UpdateControlSchema(self):
        try:
            # Retrieve and convert setpoints to floats
            DFlowValve1 = float(self.eTextDesiredFlowValve1.toPlainText())
            DFlowValve2 = float(self.eTextDesiredFlowValve2.toPlainText())
            DFlowoutputValve = float(self.eTextDesiredFlowValveOutput.toPlainText())
        except ValueError:
            print("Error: All input values must be valid numbers.")
            return

        # Check if input valves are at least 10% less than output valve
        if not (DFlowValve1 + DFlowValve2 < DFlowoutputValve * 0.9):
            print("Error: The sum of input valves must be at least 10% less than the output valve.")
            return

        def send_setpoint(operation, setpoint, device_id):
            Package = {
                "Operation": operation,
                "SetPoint": setpoint,
                "SensorID": device_id
            }
            response = PostRequestOP_VARIABLE_SETPOINT_CONTROL(ServerIP, Package)
            print(f"Setpoint sent for device {device_id}: {setpoint}, Response: {response}")

        # Send the POST requests sequentially (praying the server is fast enough)
        send_setpoint(OP_CONTINOUSMODE_SETPOINT, DFlowValve1, 2)
        send_setpoint(OP_CONTINOUSMODE_SETPOINT, DFlowValve2, 4)
        send_setpoint(OP_CONTINOUSMODE_SETPOINT, DFlowoutputValve, 6)

        print("Control schema update completed.")
        self.dialog.close()


if __name__ == "__main__":
    # ServerIP = input("IP of server: ")
    app = QApplication(sys.argv)
    window = Revolvedora_IoT_UI(ServerIP)
    window.UpdateDevicesData(sensor_list)
    window.show()
    app.exec_()
