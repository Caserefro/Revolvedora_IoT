import sqlite3
import json
from flask import Flask, render_template, request, redirect, session
import time
from sqlalchemy import *
from sqlalchemy import Column, Integer, Float, String, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from Classes import *

OP_SERVER_PING = 10
OP_DEVICE_SYNC = 11
OP_SENSOR_DATA = 12
OP_VALVE_SETPOINT_CONTROL = 13  # used in devices
OP_MOTOR_CONTROL = 14  # used in devices

# Database setup
Base = declarative_base()
engine = create_engine('sqlite:///test.db')  # Use an in-memory SQLite database for testing
Session = sessionmaker(bind=engine)


def Response(operation_code, JsonDataReceived):
    if operation_code == OP_SERVER_PING:
        return handle_SERVER_PING()
    elif operation_code == OP_DEVICE_SYNC:
        return handle_DEVICE_SYNC(JsonDataReceived)
    elif operation_code == OP_SENSOR_DATA:
        return handle_SENSOR_DATA(JsonDataReceived)


def handle_SERVER_PING():
    return "PING"

def handle_DEVICE_SYNC(JsonDataReceived):
    session = Session()

    # Check if the device with the given ID already exists
    existing_device = session.query(Device).filter_by(device_id=JsonDataReceived["ID"]).first()

    if existing_device:
        # Track if any field has been modified
        is_updated = False

        # Update only the changed fields
        if existing_device.ip_address != JsonDataReceived["IP"]:
            existing_device.ip_address = JsonDataReceived["IP"]
            is_updated = True
        if existing_device.place != JsonDataReceived["Place"]:
            existing_device.place = JsonDataReceived["Place"]
            is_updated = True
        if existing_device.tag != JsonDataReceived.get("Tag", existing_device.tag):
            existing_device.tag = JsonDataReceived["Tag"]
            is_updated = True
        if existing_device.description != JsonDataReceived.get("Description", existing_device.description):
            existing_device.description = JsonDataReceived["Description"]
            is_updated = True

        if is_updated:
            print(f"Updated existing device: {existing_device}")
        else:
            print("No changes detected for the existing device.")

    else:
        # Device does not exist, create a new one
        new_device = Device(
            device_id=JsonDataReceived["ID"],
            ip_address=JsonDataReceived["IP"],
            device_type=JsonDataReceived["Type"],
            tag=JsonDataReceived.get("Tag", ""),
            place=JsonDataReceived["Place"],
            description=JsonDataReceived.get("Description", "")
        )
        session.add(new_device)
        print(f"Added new device: {new_device}")

    # Commit the transaction only if changes were made
    session.commit()
    session.close()

    return "DEVICE_SYNC"


def handle_SENSOR_DATA(JsonDataReceived):
    session = Session()
    try:
        # Check if the device exists
        existing_device = session.query(Device).filter_by(device_id=JsonDataReceived["ID"]).first()

        if existing_device:
            device_type = existing_device.device_type

            # Create a record based on the device type
            if device_type == "Flowmeter":
                new_record = FlowRecords(
                    sensor_id=existing_device.device_id,
                    flow_value=JsonDataReceived["Flow"],
                    tag =existing_device.tag
                )
                session.add(new_record)

            elif device_type == "Electromechanical Valve":
                new_record = ValveRecords(
                    sensor_id=existing_device.device_id,
                    valve_value=JsonDataReceived["valve_value"],
                    time=JsonDataReceived["time"],
                    location=JsonDataReceived["location"]
                )
                session.add(new_record)

            elif device_type == "Liquid Level Meter":
                new_record = LevelRecords(
                    sensor_id=existing_device.device_id,
                    level_state=JsonDataReceived["level_state"],
                    time=JsonDataReceived["time"],
                    location=JsonDataReceived["location"]
                )
                session.add(new_record)

            elif device_type == "Mixer Motor":
                new_record = MotorRecords(
                    sensor_id=existing_device.device_id,
                    motor_state=JsonDataReceived["motor_state"],
                    time=JsonDataReceived["time"],
                    location=JsonDataReceived["location"]
                )
                session.add(new_record)

            else:
                print("Unknown device type.")
                return

            print(f"Record created for {device_type} with ID {existing_device.device_id}")

        else:
            print("Device not found.")

        session.commit()

    except Exception as e:
        session.rollback()
        print(f"An error occurred: {e}")
        return "Failure"

    finally:
        session.close()
        return "DEVICE_SYNC"
