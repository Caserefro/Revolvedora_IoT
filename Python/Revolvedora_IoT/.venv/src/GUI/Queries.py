import json
import multiprocessing
import sys
import time
import queue
import requests
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QLabel, QWidget

# Define operation codes
OP_SERVER_PING = 10
OP_DEVICE_SYNC = 11
OP_SENSOR_DATA = 12

OP_MOTOR_CONTROL = 14
OP_LEVEL_CONTROL = 15
OP_OPENING_PERCENTAGE_SETPOINT_CONTROL = 16

OP_SENSOR_RECORDS = 20

sensorList = [1, 2, 3, 4, 5, 6]
http_queue = queue.Queue()

def PostRequestOP_VARIABLE_SETPOINT_CONTROL(IP, Package):  # orders the thing to do some shit.
    print("Sending package:", Package)
    try:
        response = requests.post(
            f'http://{IP}/',
            data=json.dumps(Package),
            headers={'Content-Type': 'application/json'}
        )
        response.raise_for_status()  # Raise error if the request fails
        print("Response:", response.text)
        return response.text
    except requests.exceptions.RequestException as e:
        print("Error sending valve control request:", e)
        return None


def PostRequestOP_Sensor_Records(IP,
                                 SensorID):  # ID as in the DB. Returns the 100 most recent elements of that thingie.
    Package = {
        "Operation": OP_SENSOR_RECORDS,
        "SensorID": SensorID
    }
    print("Sending package:", Package)
    try:
        response = requests.post(
            f'http://{IP}/',
            data=json.dumps(Package),
            headers={'Content-Type': 'application/json'}
        )
        response.raise_for_status()  # Raise error if the request fails
        print("Response:", response.text)
        return response.text
    except requests.exceptions.RequestException as e:
        print("Error sending valve control request:", e)
        return None

#
# class HttpQueryWorker(QObject):
#     # Define a signal to update the GUI
#     task_processed = pyqtSignal(str)
#
#     def __init__(self, http_queue):
#         super().__init__()
#         self.http_queue = http_queue
#
#     def run(self):
#         while True:
#             if not self.http_queue.empty():
#                 PostRequest = self.http_queue.get_nowait()  # Non-blocking get
#                 print(f"Processing task: {PostRequest}")
#
#                 IP = PostRequest["IP"]
#                 SetPoint = PostRequest["SetPoint"]
#                 Operation = PostRequest["Operation"]
#                 ID = PostRequest["ID"]
#
#                 result = self.PostRequestOP_VARIABLE_SETPOINT_CONTROL(IP, SetPoint, Operation, ID)
#                 self.task_processed.emit(f"Processed: {result}")
#             else:
#                 print("Queue is empty. Waiting for tasks...")
#                 time.sleep(1)  # Avoid busy-waiting
