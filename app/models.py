from . import db

class nok_info(db.Model):
    key = db.Column(db.Integer, primary_key=True)
    nok_name = db.Column(db.String(255))
    nok_phonenumber = db.Column(db.String(20))

class dementia_info(db.Model):
    key = db.Column(db.Integer, primary_key=True)
    dementia_name = db.Column(db.String(255))
    dementia_phonenumber = db.Column(db.String(20))