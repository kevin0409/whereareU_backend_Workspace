from . import db
from geoalchemy2 import Geometry

class nok_info(db.Model):
    key = db.Column(db.Integer, primary_key=True)
    nok_name = db.Column(db.String(255))
    nok_phonenumber = db.Column(db.String(20))

class dementia_info(db.Model):
    key = db.Column(db.Integer, primary_key=True)
    dementia_name = db.Column(db.String(255))
    dementia_phonenumber = db.Column(db.String(20))

class location_info(db.Model):
    key = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    time = db.Column(db.Time)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    user_status = db.Column(Geometry(geometry_type='POINT'))  # LINESTRING 형식에 대한 처리 필요
    accelerationsensor_x = db.Column(db.Float)
    accelerationsensor_y = db.Column(db.Float)
    accelerationsensor_z = db.Column(db.Float)
    directionsensor_x = db.Column(db.Float)
    directionsensor_y = db.Column(db.Float)
    directionsensor_z = db.Column(db.Float)
    gyrosensor_x = db.Column(db.Float)
    gyrosensor_y = db.Column(db.Float)
    gyrosensor_z = db.Column(db.Float)
    lightsensor = db.Column(db.Float)
    battery = db.Column(db.Integer)
    isInternetOn = db.Column(db.Boolean)
    isRingstoneOn = db.Column(db.Boolean)
    isGpsOn = db.Column(db.Boolean)
