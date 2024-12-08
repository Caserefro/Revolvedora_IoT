import json
import sqlite3

import requests
from Classes import *
from sqlalchemy import *
from sqlalchemy import Column, Integer, Float, String, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import requests
import threading
import json
# Define operation codes
OP_SERVER_PING = 10
OP_DEVICE_SYNC = 11
OP_SENSOR_DATA = 12
OP_VALVE_SETPOINT_CONTROL = 13
OP_MOTOR_CONTROL = 14
OP_LEVEL_CONTROL = 15
OP_OPENING_PERCENTAGE_SETPOINT_CONTROL = 16
OP_SENSOR_RECORDS = 20

# Set up database engine and session
engine = create_engine('sqlite:///test.db')  # SQLite database
Session = sessionmaker(bind=engine)


# Define POST requests
def PostRequestOP_VALVE_SETPOINT_CONTROL(IP, Operation, SetPoint):
    Package = {
        "Operation": Operation,
        "SetPoint": SetPoint
    }
    print("Sending package:", Package)
    try:
        response = requests.post(
            f'http://{IP}/',
            data=json.dumps(Package),
            headers={'Content-Type': 'application/json'},
            timeout=.1  # Very short timeout
        )
        response.raise_for_status()  # Raise error if the request fails
        print("Response:", response.text)
        return response.text
    except requests.exceptions.RequestException as e:
        print("Error sending valve control request:", e)
        return None


def PostRequestOP_MOTOR_CONTROL(IP, State):
    Package = {
        "Operation": OP_MOTOR_CONTROL,
        "State": State
    }
    print("Sending package:", Package)
    try:
        response = requests.post(
            f'http://{IP}/',
            data=json.dumps(Package),
            headers={'Content-Type': 'application/json'}
        )
        response.raise_for_status()
        print("Response:", response.text)
        return response.text
    except requests.exceptions.RequestException as e:
        print("Error sending motor control request:", e)
        return None


# Set up session and retrieve a device of type "Valve"
session = Session()
testsubject = session.query(Device).filter_by(device_type="Valve").first()
session.close()

if testsubject:
    print(PostRequestOP_VALVE_SETPOINT_CONTROL(testsubject.ip_address, 0))
else:
    print("No device of type 'Valve' found in the database.")

# Send a GET request to retrieve data
# response = requests.get('http://192.168.223.73:5000/Time')
#
# # Check the response status code
# if response.status_code == 200:
#     # Parse the JSON data from the response
#     data = response.json()
#     print(data)
# else:
#     print(f"Error: {response.status_code}")
