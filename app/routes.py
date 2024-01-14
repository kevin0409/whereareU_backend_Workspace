from flask import Blueprint, request, jsonify
from .models import db, dementia_info, nok_info, location_info
from .random_generator import RandomNumberGenerator
from sqlalchemy import text

# 블루프린트 생성
nok_info_routes = Blueprint('nok_info_routes', __name__)
dementia_info_routes = Blueprint('dementia_info_routes', __name__)
location_info_routes = Blueprint('location_info_routes', __name__)


@nok_info_routes.route('/receive_nok_info', methods=['POST'])
def receive_nok_info():
    try:
        nok_data = request.json
        keyfromnok = nok_data.get('keyfromnok')

        # 인증번호 중복 여부 확인
        existing_dementia = dementia_info.query.filter_by(key=keyfromnok).first()
        if existing_dementia:
            # 이미 등록된 인증번호에 해당하는 환자 정보가 있을 경우, 해당 환자의 key 값을 가져옴
            Key = keyfromnok
            new_user = nok_info(key=Key, nok_name=nok_data.get('name'), nok_phonenumber=nok_data.get('phone_number'))
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
    
@dementia_info_routes.route('/receive_dementia_info', methods=['POST'])
def receive_dementia_info():
    try:
        dementia_data = request.json

        rng = RandomNumberGenerator()

        for _ in range(10):
            unique_random_number = rng.generate_unique_random_number(100000, 999999)
        Key = str(unique_random_number)  # 키 값을 문자열로 변환
        Dementia_name = dementia_data.get('name')
        Dementia_phonenumber = dementia_data.get('phone_number')

        new_user = dementia_info(key=Key, dementia_name = Dementia_name, dementia_phonenumber=Dementia_phonenumber)
        db.session.add(new_user)
        db.session.commit()
        
        response_data = {'status': 'success', 'message': 'Dementia paitient data received successfully', 'key': Key}
        return jsonify(response_data)
    
    except Exception as e:
        response_data = {'status': 'error', 'message': str(e)}
        return jsonify(response_data), 500
    
@location_info_routes.route('/receive_location_info', methods=['POST'])
def receive_location_info():
    try:
        data = request.json
        
        # Convert latitude and longitude to POINT format
        point_string = "POINT({} {})".format(data.get('latitude'), data.get('longitude'))

        new_location = location_info(
            key=data.get('key'),
            date=data.get('date'),
            time=data.get('time'),
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            user_status=text("ST_GeomFromText(:point_string)").params(point_string=point_string),
            accelerationsensor_x=data.get('accelerationsensor_x'),
            accelerationsensor_y=data.get('accelerationsensor_y'),
            accelerationsensor_z=data.get('accelerationsensor_z'),
            gyrosensor_x=data.get('gyrosensor_x'),
            gyrosensor_y=data.get('gyrosensor_y'),
            gyrosensor_z=data.get('gyrosensor_z'),
            directionsensor_x=data.get('directionsensor_x'),
            directionsensor_y=data.get('directionsensor_y'),
            directionsensor_z=data.get('directionsensor_z'),
            lightsensor=data.get('lightsensor'),
            battery=data.get('battery'),
            isInternetOn=data.get('isInternetOn'),
            isGpsOn=data.get('isGpsOn'),
            isRingstoneOn=data.get('isRingstoneOn')
        )
        
        db.session.add(new_location)
        db.session.commit()
        
        response_data = {'status': 'success', 'message': 'Location data received successfully'}
        return jsonify(response_data)
    
    except Exception as e:
        print(e)
        response_data = {'status': 'error', 'message': str(e)}
        return jsonify(response_data), 500