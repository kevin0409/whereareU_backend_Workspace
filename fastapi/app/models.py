from sqlalchemy import Column, Integer, String, Boolean, Float, Double
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class nok_info(Base):
    __tablename__ = 'nok_info'

    num = Column(Integer, index=True, primary_key=True)
    nok_key = Column(String)
    nok_name = Column(String)
    nok_phonenumber = Column(String)
    update_rate = Column(String)
    dementia_info_key = Column(String)

class dementia_info(Base):
    __tablename__ = 'dementia_info'

    num = Column(Integer, index = True, primary_key=True)
    dementia_key = Column(String)
    dementia_name = Column(String)
    dementia_phonenumber = Column(String)
    update_rate = Column(String)

class refresh_token_info(Base):
    __tablename__ = 'refresh_token_info'

    key = Column(String, primary_key=True)
    refresh_token = Column(String)

class location_info(Base):
    __tablename__ = 'location_info'

    num = Column(Integer, index=True, primary_key=True)
    dementia_key = Column(String)
    date = Column(String)
    time = Column(String)
    latitude = Column(Double)
    longitude = Column(Double)
    bearing = Column(Float)
    user_status = Column(String)
    accelerationsensor_x = Column(Float)
    accelerationsensor_y = Column(Float)
    accelerationsensor_z = Column(Float)
    directionsensor_x = Column(Float)
    directionsensor_y = Column(Float)
    directionsensor_z = Column(Float)
    gyrosensor_x = Column(Float)
    gyrosensor_y = Column(Float)
    gyrosensor_z = Column(Float)
    lightsensor = Column(Float)
    battery = Column(Integer)
    isInternetOn = Column(Boolean) # Boolean
    isRingstoneOn = Column(Integer)
    isGpsOn = Column(Boolean)
    current_speed = Column(String)

class meaningful_location_info(Base):
    __tablename__ = 'meaningful_location_info'

    num = Column(Integer, index=True, primary_key=True)
    dementia_key = Column(String)
    day_of_the_week = Column(String)
    time = Column(String)
    latitude = Column(Double)
    longitude = Column(Double)
    address = Column(String)
    key = Column(String)

class police_info(Base):
    __tablename__ = 'police_info'

    num = Column(Integer, index=True, primary_key=True)
    key = Column(String)
    policeName = Column(String)
    policeAddress = Column(String)
    policePhoneNumber = Column(String)
    distance = Column(Integer)
    latitude = Column(Double)
    longitude = Column(Double)