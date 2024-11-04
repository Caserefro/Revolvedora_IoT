from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()
engine = create_engine('sqlite:///test.db')  # Use an in-memory SQLite database for testing
Base.metadata.create_all(engine)  # Create all tables
Session = sessionmaker(bind=engine)


class Device(Base):
    __tablename__ = 'devices'

    device_id = Column(Integer, primary_key=True)
    ip_address = Column(String(26), nullable=False, default="")
    device_type = Column(String(61), nullable=False, default="")
    tag = Column(String(51), nullable=False, default="")
    place = Column(String(51), nullable=False, default="")
    description = Column(String(256), nullable=False, default="")

    def __init__(self, device_id, ip_address, device_type, tag, place, description,):
        self.device_id = device_id
        self.ip_address = ip_address
        self.device_type = device_type
        self.tag = tag
        self.place = place
        self.description = description

    def __repr__(self):
        return (f"<E_Device(device_id={self.device_id}, ip_address={self.ip_address}, device_type={self.device_type}, "
                f"description={self.description})>")


# Types of devices
# Flowmeter
# Electromechanical Valve
# Liquid Level Meter
# Mixer Motor


class BaseRecord(Base):
    __abstract__ = True
    ar_id = Column(Integer, primary_key=True, autoincrement=True)
    sensor_id = Column(Integer, ForeignKey('devices.device_id'), nullable=True)
    time = Column(DateTime, nullable=False, default=datetime.utcnow)
    tag = Column(String(51), nullable=False, default="")

class FlowRecords(BaseRecord):
    __tablename__ = 'flow_records'
    flow_value = Column(Integer, nullable=True)

class ValveRecords(BaseRecord):
    __tablename__ = 'valve_records'
    valve_value = Column(Integer, nullable=True)

class LevelRecords(BaseRecord):
    __tablename__ = 'level_records'
    level_state = Column(Integer, nullable=True)

class MotorRecords(BaseRecord):
    __tablename__ = 'motor_records'
    motor_state = Column(String(30), nullable=True)




# Assuming Base is declared somewhere before these class definitions
engine = create_engine('sqlite:///test.db')  # Use an in-memory SQLite database for testing
Base.metadata.create_all(engine)  # Create all tables
Session = sessionmaker(bind=engine)
