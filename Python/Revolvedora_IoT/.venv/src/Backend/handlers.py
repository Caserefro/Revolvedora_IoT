import json
import sqlite3
import time

from Classes import *
from flask import Flask, render_template, request, redirect, session, jsonify
from sqlalchemy import *
from sqlalchemy import Column, Integer, Float, String, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from Query import *

# Define operation codes
OP_SERVER_PING = 10
OP_DEVICE_SYNC = 11
OP_SENSOR_DATA = 12

OP_MOTOR_CONTROL = 14
OP_OPENING_ANGLE_SETPOINT_CONTROL = 16
OP_MIXTUREMODE_SETPOINT = 17
OP_CONTINOUSMODE_SETPOINT = 18

OP_SENSOR_RECORDS = 20
OP_MIXTUREMODE_DONE = 21


OnlineDevices = {}
OnlineDevicesData = {}
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

    elif operation_code == OP_MOTOR_CONTROL:
        return handle_MOTOR_CONTROL(JsonDataReceived)

    elif operation_code == OP_OPENING_ANGLE_SETPOINT_CONTROL:
        return handle_OPENING_ANGLE_SETPOINT_CONTROL(JsonDataReceived)
    elif operation_code == OP_SENSOR_RECORDS:
        return handle_SENSOR_RECORDS(JsonDataReceived)

    elif operation_code == OP_MIXTUREMODE_SETPOINT:
        return handle_OP_MIXTUREMODE_SETPOINT(JsonDataReceived)
    elif operation_code == OP_CONTINOUSMODE_SETPOINT:
        return handle_OP_CONTINOUSMODE_SETPOINT(JsonDataReceived)
    elif operation_code == OP_MIXTUREMODE_DONE:
        return handle_OP_MIXTUREMODE_DONE(JsonDataReceived)

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
        print(f"{existing_device}")
        if existing_device:
            device_type = existing_device.device_type

            # # Check if the device is marked online in the dictionary and update if necessary
            # if OnlineDevices.get(existing_device.device_id) != True:
            #     OnlineDevices[existing_device.device_id] = True
            #     print(f"Device {existing_device.device_id} is now online.")

            # Create a record based on the device type
            if device_type == "Flowmeter":
                new_record = FlowRecords(
                    sensor_id=existing_device.device_id,
                    flow_value=JsonDataReceived["Flow"],
                    tag=existing_device.tag
                )
                session.add(new_record)

            elif device_type == "Electromechanical Valve":
                new_record = ValveRecords(
                    sensor_id=existing_device.device_id,
                    valve_angle=JsonDataReceived["ValveAngle"],
                    tag=existing_device.tag
                )
                session.add(new_record)

            elif device_type == "Liquid Level Meter":
                new_record = LevelRecords(
                    sensor_id=existing_device.device_id,
                    level_state=JsonDataReceived["level_state"],
                    tag=existing_device.tag
                )
                session.add(new_record)

            elif device_type == "Mixer Motor":
                new_record = MotorRecords(
                    sensor_id=existing_device.device_id,
                    motor_state=JsonDataReceived["motor_state"],
                    tag=existing_device.tag
                )
                session.add(new_record)

            else:
                print("Unknown device type.")
                return "Failure"

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
        return "SENSOR_DATA"


def handle_MOTOR_CONTROL(JsonDataReceived):
    print(JsonDataReceived)
    sensor_id = JsonDataReceived.get("SensorID")
    state = JsonDataReceived.get("State")  # State indicates ON/OFF or specific control for the motor

    # Step 1: Validate inputs
    if not sensor_id:
        return jsonify({"error": "SensorID is required"}), 400
    if state is None:
        return jsonify({"error": "State is required"}), 400

    session = Session()
    try:
        # Step 2: Get the device from the database
        device = session.query(Device).filter(Device.device_id == sensor_id).first()

        if not device:
            return jsonify({"error": "Device not found"}), 404

        # Step 3: Verify that the device type is a Mixer Motor
        if device.device_type != "Mixer Motor":
            return jsonify({"error": "Device is not a Mixer Motor"}), 400

        # Step 4: Send the motor control command to the device
        response = PostRequestOP_MOTOR_CONTROL(device.ip_address, state)

        if response:
            # Assume the response is a success message
            print(f"Motor control response: {response}")
            return jsonify({"message": "Motor control command sent successfully"}), 200
        else:
            return jsonify({"error": "Failed to send motor control command"}), 500

    except Exception as e:
        print(f"Error in handle_MOTOR_CONTROL: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

    finally:
        session.close()
    return "handle_MOTOR_CONTROL"


def handle_OPENING_ANGLE_SETPOINT_CONTROL(JsonDataReceived):
    print(JsonDataReceived)

    # Extract required data
    sensor_id = JsonDataReceived.get("SensorID")
    setpoint = JsonDataReceived.get("SetPoint")
    print(sensor_id)
    # Step 1: Validate inputs
    if not sensor_id:
        return jsonify({"error": "SensorID is required"}), 400
    if setpoint is None:
        return jsonify({"error": "SetPoint is required"}), 400

    session = Session()
    try:
        # Step 2: Get the device from the database
        device = session.query(Device).filter(Device.device_id == sensor_id).first()

        if not device:
            return jsonify({"error": "Device not found"}), 404

        # Step 3: Verify that the device type is an Electromechanical Valve
        if device.device_type != "Electromechanical Valve":
            return jsonify({"error": "Device is not an Electromechanical Valve"}), 400

        # Step 4: Send the valve opening angle setpoint command
        print(device.ip_address)
        print(OP_OPENING_ANGLE_SETPOINT_CONTROL)
        print(setpoint)
        response = PostRequestOP_VALVE_SETPOINT_CONTROL(device.ip_address, OP_OPENING_ANGLE_SETPOINT_CONTROL, setpoint)

        if response:
            print(f"Valve opening angle control response: {response}")
            return jsonify({"message": "Valve opening angle setpoint command sent successfully"}), 200
        else:
            return jsonify({"error": "Failed to send valve opening angle setpoint command"}), 500

    except Exception as e:
        print(f"Error in handle_OPENING_ANGLE_SETPOINT_CONTROL: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

    finally:
        session.close()
    return "handle_OPENING_ANGLE_SETPOINT_CONTROL"

def handle_OP_MIXTUREMODE_SETPOINT(JsonDataReceived):
    print(JsonDataReceived)

    # Extract required data
    sensor_id = JsonDataReceived.get("SensorID")
    setpoint = JsonDataReceived.get("SetPoint")
    operation = "SET_MIXTURE_MODE"

    # Step 1: Validate inputs
    if not sensor_id:
        return jsonify({"error": "SensorID is required"}), 400
    if setpoint is None:
        return jsonify({"error": "SetPoint is required"}), 400

    session = Session()
    try:
        # Step 2: Get the device from the database
        device = session.query(Device).filter(Device.device_id == sensor_id).first()

        if not device:
            return jsonify({"error": "Device not found"}), 404

        # Step 3: Send the mixture mode setpoint command
        response = PostRequestOP_VALVE_SETPOINT_CONTROL(device.ip_address, operation, setpoint)

        if response:
            print(f"Mixture mode setpoint control response: {response}")
            return jsonify({"message": "Mixture mode setpoint command sent successfully"}), 200
        else:
            return jsonify({"error": "Failed to send mixture mode setpoint command"}), 500

    except Exception as e:
        print(f"Error in handle_OP_MIXTUREMODE_SETPOINT: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

    finally:
        session.close()
    return "handle_OP_MIXTUREMODE_SETPOINT"

def handle_OP_CONTINOUSMODE_SETPOINT(JsonDataReceived):

    # Extract required data
    sensor_id = JsonDataReceived.get("SensorID")
    setpoint = JsonDataReceived.get("SetPoint")
    operation = OP_CONTINOUSMODE_SETPOINT

    # Step 1: Validate inputs
    if not sensor_id:
        return jsonify({"error": "SensorID is required"}), 400
    if setpoint is None:
        return jsonify({"error": "SetPoint is required"}), 400

    session = Session()
    try:
        # Step 2: Get the device from the database
        device = session.query(Device).filter(Device.device_id == sensor_id).first()

        if not device:
            return jsonify({"error": "Device not found"}), 404

        # Step 3: Send the continuous mode setpoint command
        response = PostRequestOP_VALVE_SETPOINT_CONTROL(device.ip_address, operation, setpoint)

        if response:
            print(f"Continuous mode setpoint control response: {response}")
            return jsonify({"message": "Continuous mode setpoint command sent successfully"}), 200
        else:
            return jsonify({"error": "Failed to send continuous mode setpoint command"}), 500

    except Exception as e:
        print(f"Error in handle_OP_CONTINOUSMODE_SETPOINT: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

    finally:
        session.close()
    return "handle_OP_CONTINOUSMODE_SETPOINT"

def handle_OP_MIXTUREMODE_DONE(JsonDataReceived):
    print(JsonDataReceived)
   # identify whos who, then give call to output valve to open 100%.

    return "handle_OP_MIXTUREMODE_DONE"

def handle_SENSOR_RECORDS(JsonDataReceived):
    session = Session()
    sensor_id = JsonDataReceived.get("SensorID")
    if not sensor_id:
        return jsonify({"error": "SensorID is required"}), 400

    # Step 1: Get the device type and additional device details
    device = session.query(Device).filter(Device.device_id == sensor_id).first()

    if not device:
        return {"error": "Device not found"}

    if device.device_type == "Flowmeter":
        records = (
            session.query(FlowRecords, Device)
            .join(Device, FlowRecords.sensor_id == Device.device_id)
            .filter(FlowRecords.sensor_id == sensor_id)
            .order_by(FlowRecords.time.desc())
            .limit(100)
            .all()
        )
        records_data = [{"time": record.FlowRecords.time, "flow_value": record.FlowRecords.flow_value} for record in
                        records]
    elif device.device_type == "Electromechanical Valve":
        records = (
            session.query(ValveRecords, Device)
            .join(Device, ValveRecords.sensor_id == Device.device_id)
            .filter(ValveRecords.sensor_id == sensor_id)
            .order_by(ValveRecords.time.desc())
            .limit(100)
            .all()
        )
        records_data = [{"time": record.ValveRecords.time, "valve_angle": record.ValveRecords.valve_angle} for record in
                        records]
    elif device.device_type == "Liquid Level Meter":
        records = (
            session.query(LevelRecords, Device)
            .join(Device, LevelRecords.sensor_id == Device.device_id)
            .filter(LevelRecords.sensor_id == sensor_id)
            .order_by(LevelRecords.time.desc())
            .limit(100)
            .all()
        )
        records_data = [{"time": record.LevelRecords.time, "level_state": record.LevelRecords.level_state} for record in
                        records]
    elif device.device_type == "Mixer Motor":
        records = (
            session.query(MotorRecords, Device)
            .join(Device, MotorRecords.sensor_id == Device.device_id)
            .filter(MotorRecords.sensor_id == sensor_id)
            .order_by(MotorRecords.time.desc())
            .limit(100)
            .all()
        )
        records_data = [{"time": record.MotorRecords.time, "motor_state": record.MotorRecords.motor_state} for record in
                        records]
    else:
        return {"error": "Unknown device type"}

    session.close()

    return {
        "sensor_id": sensor_id,
        "ip_address": device.ip_address,
        "device_type": device.device_type,
        "tag": device.tag,
        "place": device.place,
        "description": device.description,
        "records": records_data
    }
