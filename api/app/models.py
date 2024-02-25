from . import db
from geoalchemy2 import Geometry

class nok_info(db.Model):
    num = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nok_key = db.Column(db.String(20), unique=True)
    nok_name = db.Column(db.String(255))
    nok_phonenumber = db.Column(db.String(20))
    dementia_info_key = db.Column(db.String(20), db.ForeignKey('dementia_info.dementia_key'))
    dementia_info = db.relationship('dementia_info', back_populates='nok_info')

class dementia_info(db.Model):
    num = db.Column(db.Integer, primary_key=True, autoincrement=True)
    dementia_key = db.Column(db.String(20), unique=True)
    dementia_name = db.Column(db.String(255))
    dementia_phonenumber = db.Column(db.String(20))
    nok_info = db.relationship('nok_info', back_populates='dementia_info')


class location_info(db.Model):
    num = db.Column(db.Integer, primary_key=True, autoincrement=True)
    dementia_key = db.Column(db.String(20))
    date = db.Column(db.Date)
    time = db.Column(db.Time)
    latitude = db.Column(db.Double)
    longitude = db.Column(db.Double)
    user_status = db.Column(db.Integer) # 1: 정지, 2: 도보, 3: 차량, 4: 지하철
    current_speed = db.Column(db.Float)
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
