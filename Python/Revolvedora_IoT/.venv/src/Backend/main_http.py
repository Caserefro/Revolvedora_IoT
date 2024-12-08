import multiprocessing as mp
from flask import Flask, request, jsonify
import json
import time
import threading
import time
from sqlalchemy import *
from sqlalchemy import Column, Integer, Float, String, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from Classes import *
from handlers import *

app = Flask(__name__)


@app.route('/', methods=['POST'])
def ReceivePostRequests():
    if request.method == "POST":
        Package = request.data
        JsonDataReceived = json.loads(Package)
        operation_code = JsonDataReceived["Operation"]
        # Here you can handle the operation and create a response accordingly
        PackagetoSend = Response(operation_code, JsonDataReceived)  # You might need to define this function elsewhere
        return PackagetoSend


# Function to check for offline devices
def check_online_devices(session, timeout=20):
    current_time = time.time()

    # Query only Flowmeter and Liquid Level Meter devices
    devices = session.query(Device).filter(
        or_(
            Device.device_type == "Flowmeter",
            Device.device_type == "Liquid Level Meter"
        )
    ).all()

    for device in devices:
        # Choose the correct records table based on device type
        if device.device_type == "Flowmeter":
            LastReading = session.query(FlowRecords).filter(
                FlowRecords.sensor_id == device.device_id
            ).order_by(FlowRecords.time.desc()).first()

        elif device.device_type == "Liquid Level Meter":
            LastReading = session.query(LevelRecords).filter(
                LevelRecords.sensor_id == device.device_id
            ).order_by(LevelRecords.time.desc()).first()

        # Proceed if we have a last reading for the device
        if LastReading:
            last_reading_time = LastReading.time.timestamp()
            time_difference = current_time - last_reading_time

            # Update OnlineDevices dictionary based on timeout
            if time_difference > timeout:
                OnlineDevices[device.device_id] = False
                print(f"Device {device.device_id} is now offline.")
            else:
                OnlineDevices[device.device_id] = True
                print(f"Device {device.device_id} is online.")

    print("Updated OnlineDevices:", OnlineDevices)
    session.commit()

# Background thread to check devices
def start_device_check():
    while True:
        session = Session()
        check_online_devices(session)
        retrieve_data(session)
        session.close()
        time.sleep(20)  # Check every minute


def retrieve_data(session):
    for device_id, is_online in OnlineDevices.items():
        if is_online:  # Only process devices that are marked as offline
            device_type = session.query(Device).filter_by(device_id=device_id).first()
            if device_type:
                if device_type.device_type == "Flowmeter":
                    last_records = session.query(FlowRecords).filter(
                        FlowRecords.sensor_id == device_id
                    ).order_by(FlowRecords.time.desc()).limit(50).all()

                    # Collect flow values and time values
                    flow_values = [record.flow_value for record in last_records]
                    time_values = [record.time for record in last_records]
                    # OnlineDevicesData[device_id] = [flow_values, time_values]

                elif device_type.device_type == "Liquid Level Meter":
                    last_records = session.query(LevelRecords).filter(
                        LevelRecords.sensor_id == device_id
                    ).order_by(LevelRecords.time.desc()).limit(50).all()

                    # Collect level state values and time values
                    level_state_values = [record.level_state for record in last_records]
                    time_values = [record.time for record in last_records]
                    # OnlineDevicesData[device_id] = [level_state_values, time_values]

                elif device_type.device_type == "Electromechanical Valve":
                    last_records = session.query(ValveRecords).filter(
                        ValveRecords.sensor_id == device_id
                    ).order_by(ValveRecords.time.desc()).limit(50).all()

                    # Collect valve values and time values
                    valve_values = [record.valve_value for record in last_records]
                    time_values = [record.time for record in last_records]
                    # OnlineDevicesData[device_id] = [valve_values, time_values]

                elif device_type.device_type == "Mixer Motor":
                    last_records = session.query(MotorRecords).filter(
                        MotorRecords.sensor_id == device_id
                    ).order_by(MotorRecords.time.desc()).limit(50).all()

                    # Collect motor state values and time values
                    motor_state_values = [record.motor_state for record in last_records]
                    time_values = [record.time for record in last_records]
                    OnlineDevicesData[device_id] = [motor_state_values, time_values]

    print(OnlineDevicesData)
    return


def run_flask():
    """Function to run the Flask app in a separate process."""
    app.run(debug=False, host='0.0.0.0')


if __name__ == '__main__':
    flask_process = None
    try:
        # Start the Flask app in a separate process
        flask_process = mp.Process(target=run_flask)
        flask_process.start()

        # Start a device checking thread
     #   threading.Thread(target=start_device_check, daemon=True).start()

        # Keep the main process running to handle interrupts
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        if flask_process:
            flask_process.terminate()  # Ensure the Flask process is terminated
            flask_process.join()  # Wait for the Flask process to finish
            print("Flask process terminated.")