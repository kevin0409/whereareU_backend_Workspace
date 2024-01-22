from . import db
from geoalchemy2 import Geometry
#db 구조 변경 예정
class nok_info(db.Model):
    num = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nok_key = db.Column(db.Integer, unique=True)
    nok_name = db.Column(db.String(255))
    nok_phonenumber = db.Column(db.String(20))
    dementia_info_key = db.Column(db.Integer, db.ForeignKey('dementia_info.dementia_key'))
    dementia_info = db.relationship('dementia_info', back_populates='nok_info')

class dementia_info(db.Model):
    num = db.Column(db.Integer, primary_key=True, autoincrement=True)
    dementia_key = db.Column(db.Integer, unique=True)
    dementia_name = db.Column(db.String(255))
    dementia_phonenumber = db.Column(db.String(20))
    nok_info = db.relationship('nok_info', back_populates='dementia_info')


class location_info(db.Model):
    num = db.Column(db.Integer, primary_key=True, autoincrement=True)
    dementia_key = db.Column(db.Integer)
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
