from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os, random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:-----@127.0.0.1:3306/testdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class nok_info(db.Model):
    key = db.Column(db.Integer, primary_key=True)
    nok_name = db.Column(db.String(255))
    certification_number = db.Column(db.String(255))
    nok_phonenumber = db.Column(db.String(20))

class dementia_info(db.Model):
    key = db.Column(db.Integer, primary_key=True)
    dementia_name = db.Column(db.String(255))
    certification_number = db.Column(db.String(255))
    dementia_phonenumber = db.Column(db.String(20))

class RandomNumberGenerator:
    def __init__(self):
        self.used_numbers = set()

    def generate_unique_random_number(self, lower_bound, upper_bound):
        while True:
            random_number = random.randint(lower_bound, upper_bound)
            if random_number not in self.used_numbers:
                self.used_numbers.add(random_number)
                return random_number

@app.route('/receive_nok_info', methods=['POST'])
def receive_nok_info():
    try:
        nok_data = request.json
        Certification_number = nok_data.get('certification_number')

        # 인증번호 중복 여부 확인
        existing_dementia = dementia_info.query.filter_by(certification_number=Certification_number).first()
        if existing_dementia:
            # 이미 등록된 인증번호에 해당하는 환자 정보가 있을 경우, 해당 환자의 key 값을 가져옴
            Key = existing_dementia.key
            new_user = nok_info(key=Key, certification_number=Certification_number, nok_name=nok_data.get('name'), nok_phonenumber=nok_data.get('phone_number'))
            db.session.add(new_user)
            db.session.commit()

            response_data = {'status': 'success', 'message': 'Next of kin data received successfully'}
        else:
            # 인증번호가 등록되지 않은 경우, 오류 전송
            response_data = {'status': 'error', 'message': 'Certification number not found'}

        
        return jsonify(response_data)

    except Exception as e:
        response_data = {'status': 'error', 'message': str(e)}
        return jsonify(response_data), 500
    
@app.route('/receive_dementia_info', methods=['POST'])
def receive_dementia_info():
    try:
        dementia_data = request.json

        rng = RandomNumberGenerator()

        for _ in range(10):
            unique_random_number = rng.generate_unique_random_number(100000, 999999)
        Key = unique_random_number()
        Certification_number = dementia_data.get('certification_number')
        Dementia_name = dementia_data.get('name')
        Dementia_phonenumber = dementia_data.get('phone_number')

        new_user = dementia_info(key=Key, certification_number = Certification_number, dementia_name = Dementia_name, dementia_phonenumber=Dementia_phonenumber)
        db.session.add(new_user)
        db.session.commit()
        
        response_data = {'status': 'success', 'message': 'Dementia paitient data received successfully'}
        return jsonify(response_data)
    
    except Exception as e:
        response_data = {'status': 'error', 'message': str(e)}
        return jsonify(response_data), 500


if __name__ == '__main__':
    from werkzeug.serving import make_ssl_devcert, run_simple

    cert_path = '/Users/parkseungho/Desktop/로컬 웹서버/cert.pem'
    key_path = '/Users/parkseungho/Desktop/로컬 웹서버/key.pem'

    if not (os.path.exists(cert_path) and os.path.exists(key_path)):
        make_ssl_devcert(cert_path, key_path, host='localhost', port=443)

    run_simple('localhost', 433, app, ssl_context=(cert_path, key_path))
