import multiprocessing
import queue
import sys

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

ServerIP = ""


class Revolvedora_IoT_UI(QMainWindow, Ui_MainWindow):
    def __init__(self, ServerIP):
        super(Revolvedora_IoT_UI, self).__init__()
        self.setupUi(self)
        self.setupUiExtra(self)
        # Store instances for valves and tanks
        self.valve_controllers = {}  # To store ValveController instances
        self.tank_controllers = {}  # To store TankController instances
        self.server_ip = ServerIP
        self.devices_data = {}  # To store the retrieved data

        self.postNeeded = 0
        self.postIP = ""
        self.postSetPoint = ""
        self.postOperation = ""
        self.postID = ""
        self.SensorDataTicks = 0
        # Timer setup to call UpdateDevicesData every 5000 ms (5 seconds)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateDataPeriodically)  # Connect the timer to a method
        self.timer.start(500)  # Start the timer, update every 5000 ms
        self.timer2 = QTimer(self)
        self.timer2.timeout.connect(self.postDataPeriodically)  # Connect the timer to a method
        self.timer2.start(500)  # Start the timer, update every 5000 ms

    def setupUiExtra(self, MainWindow):
        self.close_window_button.clicked.connect(MainWindow.close)
        self.minimize_window_button.clicked.connect(MainWindow.showMinimized)
        self.restore_window_button.clicked.connect(self.toggle_maximize_restore)
        self.is_maximized = False

        self.open_close_side_bar_btn.clicked.connect(self.toggle_sidebar)

        self.Valve_1btn.clicked.connect(self.on_valve1_clicked)
        self.Valve_2btn.clicked.connect(self.on_valve2_clicked)
        self.Valve_3btn.clicked.connect(self.on_valve3_clicked)
        self.Tank_1btn.clicked.connect(self.on_tank1_clicked)
        self.Tank_2btn.clicked.connect(self.on_tank2_clicked)
        self.Tank_3btn.clicked.connect(self.on_tank3_clicked)
        self.Tank_4btn.clicked.connect(self.on_tank4_clicked)

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

    def postDataPeriodically(self):
        if self.postNeeded == 1:
            Package = {
                "Operation": postOperation,
                "SetPoint": postSetPoint,
                "ID": postID
            }
            PostRequestOP_VARIABLE_SETPOINT_CONTROL(self.server_ip,Package)
            self.postNeeded = 0

    def updateDataPeriodically(self):
        # Your list of sensor IDs (you should have a valid list)
        sensor_list = [1, 2, 3, 4, 5, 6, 7, 8]  # Replace with actual sensor IDs
        self.UpdateDevicesData(sensor_list)

    def UpdateDevicesData(self, sensor_list):
        """
        Updates local storage with data retrieved for each sensor in the list.
        Avoids adding duplicates and checks for changes in fields.
        """
        self.SensorDataTicks = self.SensorDataTicks + 1
        if self.SensorDataTicks == 9:
            self.SensorDataTicks = 0
            for sensor_id in sensor_list:
                print(f"Fetching data for SensorID: {sensor_id}")
                response = PostRequestOP_Sensor_Records(self.server_ip, sensor_id)
                try:
                    # Deserialize JSON response into a Python dictionary
                    data = json.loads(response)
                except json.JSONDecodeError:
                    print(f"Failed to decode JSON for SensorID {sensor_id}: {response}")
                    continue

                if data and "error" not in data:
                    self.devices_data[sensor_id] = data
                    print(f"Updated data for SensorID {sensor_id}: {data}")

                    # Extract details from the response
                    device_id = data["sensor_id"]
                    ip_address = data["ip_address"]
                    device_type = data["device_type"]
                    tag = data.get("tag", "N/A")
                    place = data["place"]
                    description = data["description"]
                    state = (
                        data["records"][0].get("flow_value", "N/A")
                        if device_type == "Flowmeter" else
                        data["records"][0].get("valve_value", "N/A")
                        if device_type == "Electromechanical Valve" else
                        data["records"][0].get("level_state", "N/A")
                        if device_type == "Liquid Level Meter" else
                        data["records"][0].get("motor_state", "N/A")
                        if device_type == "Mixer Motor" else "N/A"
                    ) if data["records"] else "No Data"

                    # Check if the device_id already exists in the table
                    row_position = None
                    for row in range(self.tableWidget.rowCount()):
                        existing_device_id = self.tableWidget.item(row,
                                                                   0).text()  # Assuming device_id is in the first column
                        if existing_device_id == str(device_id):
                            row_position = row
                            break

                    if row_position is None:
                        # Add a new row to the table if no duplicate was found
                        row_position = self.tableWidget.rowCount()
                        self.tableWidget.insertRow(row_position)

                    # Compare the existing row data with the new data and update if necessary
                    fields = [
                        (0, str(device_id)),  # device_id
                        (1, str(ip_address)),  # ip_address
                        (2, str(device_type)),  # device_type
                        (3, str(tag)),  # tag
                        (4, str(place)),  # place
                        (5, str(description)),  # description
                        (6, str(state)),  # state
                        (7, str(state))  # state (again for display purposes, or any other field)
                    ]

                    for column, new_value in fields:
                        current_item = self.tableWidget.item(row_position, column)
                        if current_item is None or current_item.text() != new_value:
                            # Update the table cell if there is a change in the value
                            self.tableWidget.setItem(row_position, column, QTableWidgetItem(new_value))

                    # Update UI components like labels based on device ID
                    if device_id == 1:
                        self.Valve_1L.setText(f"{str(state)}")
                    if device_id == 2:
                        self.Valve_1L.setText(f"{str(state)} / {self.Valve_1L.text()}")
                    if device_id == 3:
                        self.Valve_2L.setText(f"{str(state)}")
                    if device_id == 4:
                        self.Valve_2L.setText(f"{str(state)} / {self.Valve_2L.text()}")
                    if device_id == 5:
                        self.Valve_3L.setText(f"{str(state)}")
                    if device_id == 6:
                        self.Valve_3L.setText(f"{str(state)} / {self.Valve_3L.text()}")
                    if device_id == 7:
                        self.Tank_3L.setText(f"{str(state)}")
                    if device_id == 8:
                        self.Tank_3L.setText(f"{str(state)} / {self.Tank_3L.text()}")
                else:
                    print(f"Failed to update data for SensorID {sensor_id}")

class TankController(Ui_tank):
    def __init__(self, levelName, level_ID, motorName, motorID):
        super().__init__()
        self.dialog = QtWidgets.QDialog()  # Create the QDialog instance
        self.setupUi(self.dialog)  # Set up the UI components
        """Connect UI signals to methods."""
        self.minimize_window_button.clicked.connect(self.minimize_window)
        self.close_window_button.clicked.connect(self.close_window)
        # self.eTextLevelSetpoint.textChanged.connect(self.update_level_setpoint)
        # self.eTextMixerSetpoint.textChanged.connect(self.update_mixer_setpoint)
        self.applyChangesLevelbtn.clicked.connect(self.update_level_setpoint)
        self.applyChangesMixerbtn.clicked.connect(self.update_mixer_setpoint)
        self.DeviceName.setText(f"{levelName} and {motorName}")
        self.initialize_data()

    def show(self):
        """Show the dialog."""
        self.dialog.exec_()

    def minimize_window(self):
        """Minimize the dialog."""
        self.dialog.showMinimized()

    def close_window(self):
        """Close the dialog."""
        self.dialog.close()

    def update_level_setpoint(self, ID, OP_LEVEL_CONTROL):
        """Handle level setpoint changes."""
        value = self.eTextLevelSetpoint.toPlainText()
        try:
            # Convert value to float
            value = float(value)

            # Validate range
            if 0 <= value <= 30:
                print(f"Level setpoint updated to: {value}")
                self.postNeeded = 1
                self.postSetPoint = value,
                self.postOperation = OP_LEVEL_CONTROL,  # Replace with actual operation
                self.postID = ID  # Replace with actual ID

                self.dialog.close()  # Close the dialog after starting the request
            else:
                print("Error: The level must be between 0 and 30.")
                self.dialog.close()  # Close the dialog
        except ValueError:
            print("Error: The input must be a number.")
            self.dialog.close()  # Close the dialog

    def update_mixer_setpoint(self):
        """Handle mixer setpoint changes."""
        value = self.eTextMixerSetpoint.toPlainText()
        try:
            # Try to convert the value to a float and check if it's either 0 or 1
            value = float(value)

            if value == 0 or value == 1:
                print(f"Mixer setpoint updated to: {value}")
                print(PostRequestOP_VARIABLE_SETPOINT_CONTROL(ServerIP, value, OP_MOTOR_CONTROL, motorID))
                self.dialog.close()  # Close the dialog after valid update
            else:
                print("Error: The mixer setpoint must be either 0 or 1.")
                self.dialog.close()  # Close the dialog after valid update
        except ValueError:
            # Handle the case where the value is not a valid float
            print("Error: The input must be 0 or 1.")
            self.dialog.close()  # Close the dialog after valid update

    def initialize_data(self):
        """Set default values for Valve properties."""
        self.actualStateLLevel.setText("0.00")
        self.actualStateLMixer.setText("0%")


class ValveController(Ui_Valve):
    def __init__(self, flowmeterName, flowmeterID, valveName, valveID):
        super().__init__()
        self.dialog = QtWidgets.QDialog()  # Create the QDialog instance
        self.setupUi(self.dialog)  # Set up the UI components

        # Connect buttons to actions
        self.minimize_window_button_2.clicked.connect(self.minimize_window)
        self.close_window_button_2.clicked.connect(self.close_window)
        self.DeviceName.setText(f"{flowmeterName} and {valveName}")
        self.applyChangesOPbtn.clicked.connect(self.update_OpeningPercentage)

        self.initialize_data()

    def show(self):
        """Show the dialog."""
        self.dialog.exec_()

    def minimize_window(self):
        self.dialog.showMinimized()

    def close_window(self):
        self.dialog.close()

    def update_OpeningPercentage(self):
        """Handle level setpoint changes."""
        value = self.eTextOpeningPercentageSetpoint.toPlainText()
        try:
            # Try to convert the value to a float
            value = float(value)

            # Check if the value is within the valid boundary (0-90)
            if 0 <= value <= 90:
                print(f"Opening Percentage setpoint updated to: {value}")
                self.dialog.close()  # Close the dialog after valid update
            else:
                print("Error: The value must be between 0 and 90.")

                self.dialog.close()  # Close the dialog after valid update
        except ValueError:
            # Handle the case where the value is not a valid float
            print("Error: The input must be a number.")
            self.dialog.close()  # Close the dialog after valid update

    def initialize_data(self):
        """Set default values for Valve properties."""
        self.actualStateLFlow.setText("0.00")
        self.actualStateLOpeningPercentage.setText("0%")


if __name__ == "__main__":
    # ServerIP = input("IP of server: ")
    ServerIP = "127.0.0.1:5000"
    sensor_list = [1, 2, 3, 4, 5, 6, 7, 8]  # Replace with actual sensor IDs

    task_queue = queue.Queue()

    app = QApplication(sys.argv)
    window = Revolvedora_IoT_UI(ServerIP)
    window.UpdateDevicesData(sensor_list)
    window.show()
    app.exec_()
