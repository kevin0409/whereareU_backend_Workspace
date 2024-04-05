from flask import Blueprint, request, jsonify
from .models import db, dementia_info, nok_info, location_info, meaningful_location_info
from .random_generator import RandomNumberGenerator
from .update_user_status import UpdateUserStatus
from .LocationAnalyzer import LocationAnalyzer
from sqlalchemy import and_
from .extentions import scheduler

import datetime
import json



# 블루프린트 생성
nok_info_routes = Blueprint('nok_info_routes', __name__)
dementia_info_routes = Blueprint('dementia_info_routes', __name__)
is_connected_routes = Blueprint('is_connected_routes', __name__)
location_info_routes = Blueprint('location_info_routes', __name__)
send_location_info_routes = Blueprint('send_live_location_info_routes', __name__)
user_login_routes = Blueprint('user_login_routes', __name__)
user_info_modification_routes = Blueprint('user_info_modification_routes', __name__)
caculate_dementia_avarage_walking_speed_routes = Blueprint('caculate_dementia_avarage_walking_speed', __name__)
get_user_info_routes = Blueprint('get_user_info', __name__)
update_rate_routes = Blueprint('update_rate', __name__)
send_meaningful_location_info_routes = Blueprint('send-meaningful-location-info', __name__)
send_location_history_rotues = Blueprint('send-location-history', __name__)

# 상태코드 정의
SUCCESS = 200
WRONG_REQUEST = 400
KEYNOTFOUND = 600
LOCDATANOTFOUND = 650
LOCDATANOTENOUGH = 660
LOGINSUCCESS = 700
LOGINFAILED = 750
UNDEFERR = 500

@nok_info_routes.route('/receive-nok-info', methods=['POST'])
def receive_nok_info():
    try:
        nok_data = request.json
        _keyfromdementia = nok_data.get('keyFromDementia')
        rng = RandomNumberGenerator()
        print(_keyfromdementia)

        # 인증번호 중복 여부 확인
        existing_dementia = dementia_info.query.filter_by(dementia_key=_keyfromdementia).first()
        print('[system] current : {}'.format(existing_dementia))

        if existing_dementia:
            print('[system] dementia key found({:s})'.format(_keyfromdementia))

            # 이미 등록된 인증번호에 해당하는 환자 정보가 있을 경우, 해당 환자의 key 값을 가져옴
            _nok_name = nok_data.get('name')
            _nok_phonenumber = nok_data.get('phoneNumber')

            duplication_check = nok_info.query.filter(and_(nok_info.nok_name == _nok_name, nok_info.nok_phonenumber == _nok_phonenumber, nok_info.dementia_info_key == _keyfromdementia)).first()
            if duplication_check:
                
                _key = duplication_check.nok_key
            
            else:
                for _ in range(10):
                    unique_random_number = rng.generate_unique_random_number(100000, 999999)
            
                _key = str(unique_random_number)  # 키 값을 문자열로 변환
                print('[system] nok_key({:s})', _key)

                new_user = nok_info(nok_key=_key, nok_name=nok_data.get('name'), nok_phonenumber=nok_data.get('phoneNumber'), dementia_info_key = _keyfromdementia)
                db.session.add(new_user)
                db.session.commit()


            result = {
                'dementiaInfoRecord' : {
                        'dementiaKey' : existing_dementia.dementia_key,
                        'dementiaName': existing_dementia.dementia_name,
                        'dementiaPhoneNumber': existing_dementia.dementia_phonenumber
                },
                'nokKey': _key

            } 
            
            
            print('[system] {:s} nok info successfully uploaded'.format(nok_data.get('name')))

            response_data = {'status': 'success', 'message': 'Next of kin data received successfully', 'result': result}\
            
            json_response = jsonify(response_data)
            json_response.headers['Content-Length'] = len(json_response.get_data(as_text=True))

            return json_response, SUCCESS, {'Content-Type': 'application/json; charset = utf-8' }
        
        else:
            # 인증번호가 등록되지 않은 경우, 오류 전송
            print('[system] dementia key not found')

            response_data = {'status': 'error', 'message': 'Certification number not found'}

            json_response = jsonify(response_data)
            json_response.headers['Content-Length'] = len(json_response.get_data(as_text=True))
            
            return json_response, KEYNOTFOUND , {'Content-Type': 'application/json; charset = utf-8' }

    except Exception as e:
        response_data = {'status': 'error', 'message': str(e)}
        return jsonify(response_data), UNDEFERR, {'Content-Type': 'application/json; charset = utf-8' }
    
@dementia_info_routes.route('/receive-dementia-info', methods=['POST'])
def receive_dementia_info():
    try:
        dementia_data = request.json

        rng = RandomNumberGenerator()

        _dementia_name = dementia_data.get('name')
        _dementia_phonenumber = dementia_data.get('phoneNumber')

        duplicate_dementia = dementia_info.query.filter_by(dementia_phonenumber = _dementia_phonenumber).first() # 전화번호는 고유값이므로 전화번호로 중복 확인
        if duplicate_dementia:

            _dementia_key = duplicate_dementia.dementia_key
            
            result = {
                'dementiaKey' : _dementia_key
            }
            response_data = {'status': 'success', 'message': 'Dementia paitient data received successfully', 'result': result}

            print('[system] dementia info {} already exists'.format(_dementia_name))
        else:
            # 인증번호 생성
            for _ in range(10):
                unique_random_numberfordementia = rng.generate_unique_random_number(100000, 999999)
    
            _dementia_key = str(unique_random_numberfordementia)  # 키 값을 문자열로 변환

            new_user = dementia_info(dementia_key=_dementia_key, dementia_name = _dementia_name, dementia_phonenumber=_dementia_phonenumber)
            result = {
                'dementiaKey' : _dementia_key
            }
            db.session.add(new_user)
            db.session.commit()

            print('[system] {:s} dementia info successfully uploaded'.format(_dementia_name))
            response_data = {'status': 'success', 'message': 'Dementia paitient data received successfully', 'result': result}

            
        json_response = jsonify(response_data)
        json_response.headers['Content-Length'] = len(json_response.get_data(as_text=True))
        
        return json_response, SUCCESS, {'Content-Type': 'application/json; charset = utf-8' }
    
    except Exception as e:
        response_data = {'status': 'error', 'message': str(e)}
        return jsonify(response_data), UNDEFERR, {'Content-Type': 'application/json; charset = utf-8' }

@is_connected_routes.route('/is-connected', methods=['POST'])
def is_connected():
    try:
        connection_request = request.json
        _dementia_key = connection_request.get('dementiaKey')

        existing_dementia = nok_info.query.filter_by(dementia_info_key=_dementia_key).first()
        
        if existing_dementia: #조회에 성공한 경우 nok 정보를 가져와 전송
            result = {
                'nokInfoRecord' : {
                    'nokKey': existing_dementia.nok_key,
                    'nokName': existing_dementia.nok_name,
                    'nokPhoneNumber': existing_dementia.nok_phonenumber
                }
            }
            response_data = {'status': 'success', 'message': 'Connected successfully', 'result' : result}

            json_response = jsonify(response_data)
            json_response.headers['Content-Length'] = len(json_response.get_data(as_text=True))

            return json_response, SUCCESS, {'Content-Type': 'application/json; charset = utf-8' }

        else:
            response_data = {'status': 'error', 'message': 'Connection failed'}

            json_response = jsonify(response_data)
            json_response.headers['Content-Length'] = len(json_response.get_data(as_text=True))

            return json_response, KEYNOTFOUND, {'Content-Type': 'application/json; charset = utf-8' }
    
    except Exception as e:
        response_data = {'status': 'error', 'message': str(e)}
        return jsonify(response_data), UNDEFERR, {'Content-Type': 'application/json; charset = utf-8' }
    
@user_login_routes.route('/receive-user-login', methods=['POST'])
def receive_user_login():
    response_data = {}
    try:
        data = request.json
        
        _key = data.get('key')
        _isdementia = data.get('isDementia') # 0: NOK, 1: dementia

        if _isdementia == 0: # nok일 경우
            existing_nok = nok_info.query.filter_by(nok_key=_key).first()
            if existing_nok:
                response_data = {'status': 'success', 'message': 'Login success'}

                json_response = jsonify(response_data)
                json_response = json_response.headers.add('Content-Length', str(len(json_response.response)))

                return json_response, LOGINSUCCESS, {'Content-Type': 'application/json; charset = utf-8' }

            else:
                response_data = {'status': 'error', 'message': 'Login failed'}

                json_response = jsonify(response_data)
                json_response = json_response.headers.add('Content-Length', str(len(json_response.response)))

                return json_response, LOGINFAILED, {'Content-Type': 'application/json; charset = utf-8' }

            
        elif _isdementia == 1: # dementia일 경우
            existing_dementia = dementia_info.query.filter_by(dementia_key=_key).first()
            if existing_dementia:
                response_data = {'status': 'success', 'message': 'Login success'}

                json_response = jsonify(response_data)
                json_response.headers['Content-Length'] = len(json_response.get_data(as_text=True))

                return json_response, LOGINSUCCESS, {'Content-Type': 'application/json; charset = utf-8' }

            else:
                response_data = {'status': 'error', 'message': 'Login failed'}

                json_response = jsonify(response_data)
                json_response.headers['Content-Length'] = len(json_response.get_data(as_text=True))

                return json_response, LOGINFAILED, {'Content-Type': 'application/json; charset = utf-8' }
    
    except Exception as e:
        response_data = {'status': 'error', 'message': str(e)}
        return jsonify(response_data), UNDEFERR, {'Content-Type': 'application/json; charset = utf-8' }

@location_info_routes.route('/receive-location-info', methods=['POST'])
def receive_location_info():
    try:
        data = request.json
        json_data = json.dumps(data)
        
        _dementia_key = data.get('dementiaKey')
        
        existing_dementia = dementia_info.query.filter_by(dementia_key=_dementia_key).first()


        if existing_dementia:
            # UpdateUserStatus 클래스의 인스턴스 생성
            user_status_updater = UpdateUserStatus()

            lightsensor = data.get('lightsensor')

            # 예측 수행
            prediction = user_status_updater.predict(json_data)

            # 위치 정보 저장
            new_location = location_info(
                dementia_key=data.get('dementiaKey'),
                date=data.get('date'),
                time=data.get('time'),
                latitude=data.get('latitude'),
                longitude=data.get('longitude'),
                bearing = data.get('bearing'),
                user_status=int(prediction[0]),  # 예측 결과로 업데이트
                accelerationsensor_x = data.get('accelerationsensor')[0],
                accelerationsensor_y = data.get('accelerationsensor')[1],
                accelerationsensor_z = data.get('accelerationsensor')[2],
                directionsensor_x = data.get('directionsensor')[0],
                directionsensor_y = data.get('directionsensor')[1],
                directionsensor_z = data.get('directionsensor')[2],
                gyrosensor_x = data.get('gyrosensor')[0],
                gyrosensor_y = data.get('gyrosensor')[1],
                gyrosensor_z = data.get('gyrosensor')[2],
                lightsensor=lightsensor[0],
                battery=data.get('battery'),
                isInternetOn=data.get('isInternetOn'),
                isGpsOn=data.get('isGpsOn'),
                isRingstoneOn=data.get('isRingstoneOn'),
                current_speed = data.get('currentSpeed')
            )

            db.session.add(new_location)
            db.session.commit()

            print("[system] {} {}".format(data.get("dementiaKey"), int(prediction[0])))

            response_data = {'status': 'success', 'message': 'Location data received successfully'}

            json_response = jsonify(response_data)
            json_response.headers['Content-Length'] = len(json_response.get_data(as_text=True))

            return json_response, SUCCESS, {'Content-Type': 'application/json; charset = utf-8' }
        
        else:
            response_data = {'status': 'error', 'message': 'Certification number not found'}

            json_response = jsonify(response_data)
            json_response.headers['Content-Length'] = len(json_response.get_data(as_text=True))

            return json_response, KEYNOTFOUND, {'Content-Type': 'application/json; charset = utf-8' }
    
    except Exception as e:
        print(e)
        response_data = {'status': 'error', 'message': str(e)}
        return jsonify(response_data), UNDEFERR, {'Content-Type': 'application/json; charset = utf-8' }

@send_location_info_routes.route('/send-live-location-info', methods=['GET'])
def send_location_info():
    try:
        
        dementia_key = request.args.get('dementiaKey')
        
        latest_location = location_info.query.filter_by(dementia_key=dementia_key).order_by(location_info.date.desc(), location_info.time.desc()).first()

        
        if latest_location:
            result = {
                'status': 'success',
                'message': 'Location data sent successfully',
                'latitude': latest_location.latitude,
                'longitude': latest_location.longitude,
                'bearing': latest_location.bearing,
                'currentSpeed': latest_location.current_speed,
                'userStatus': latest_location.user_status, # 1: 정지, 2: 도보, 3: 차량, 4: 지하철
                'battery': latest_location.battery,
                'isInternetOn': latest_location.isInternetOn,
                'isGpsOn': latest_location.isGpsOn,
                'isRingstoneOn': latest_location.isRingstoneOn # 0 : 무음, 1 : 진동, 2 : 벨소리
            }
            response_data = {'status': 'success', 'message': 'Location data sent successfully', 'result': result}

            json_response = jsonify(response_data)
            json_response.headers['Content-Length'] = len(json_response.get_data(as_text=True))

            return json_response, SUCCESS, {'Content-Type': 'application/json; charset = utf-8' }
        else:
            response_data = {'status': 'error', 'message': 'Certification number not found'}

            json_response = jsonify(response_data)
            json_response.headers['Content-Length'] = len(json_response.get_data(as_text=True))

            return json_response, KEYNOTFOUND, {'Content-Type': 'application/json; charset = utf-8' }
    
    except Exception as e:
        response_data = {'status': 'error', 'message': str(e)}
        return jsonify(response_data), UNDEFERR

@user_info_modification_routes.route('/modify-user-info', methods=['POST'])
def modify_user_info():
    try:
        response_data = {}
        data = request.json

        is_dementia = data.get('isDementia')
        before_name = data.get('name')
        before_phonenumber = data.get('phoneNumber')

        if is_dementia == 0: # 보호자
            existing_nok = nok_info.query.filter_by(nok_key=data.get('key')).first()
            if existing_nok:

                # 수정된 정보를 제외한 나머지 정보들은 기존의 값을 그대로 수신
                if not existing_nok.nok_name == before_name:
                    existing_nok.nok_name = before_name
                
                if not existing_nok.nok_phonenumber == before_phonenumber:
                    existing_nok.nok_phonenumber = before_phonenumber

                db.session.commit()

                print('[system] NOK info modified successfully')

                response_data = {'status': 'success', 'message': 'User info modified successfully'}

                json_response = jsonify(response_data)
                json_response.headers['Content-Length'] = len(json_response.get_data(as_text=True))

                return json_response, SUCCESS, {'Content-Type': 'application/json; charset = utf-8' }
            
            else:
                print('[system] NOK info not found')
                response_data = {'status': 'error', 'message': 'User info not found'}

                json_response = jsonify(response_data)
                json_response.headers['Content-Length'] = len(json_response.get_data(as_text=True))

                return json_response, KEYNOTFOUND, {'Content-Type': 'application/json; charset = utf-8' }
            
        elif is_dementia == 1: # 보호 대상자
            existing_dementia = dementia_info.query.filter_by(dementia_key=data.get('key')).first()
            if existing_dementia:
                if not existing_dementia.dementia_name == before_name:
                    existing_dementia.dementia_name = before_name
                
                if not existing_dementia.dementia_phonenumber == before_phonenumber:
                    existing_dementia.dementia_phonenumber = before_phonenumber
                

                db.session.commit()
                print('[system] Dementia info modified successfully')
                response_data = {'status': 'success', 'message': 'User info modified successfully'}

                json_response = jsonify(response_data)
                json_response.headers['Content-Length'] = len(json_response.get_data(as_text=True))

                return json_response, SUCCESS, {'Content-Type': 'application/json; charset = utf-8' }
            
            else:
                print('[system] Dementia info not found')
                response_data = {'status': 'error', 'message': 'User info not found'}

                json_response = jsonify(response_data)
                json_response.headers['Content-Length'] = len(json_response.get_data(as_text=True))

                return json_response, KEYNOTFOUND, {'Content-Type': 'application/json; charset = utf-8' }
    
    except Exception as e:
        response_data = {'status': 'error', 'message': str(e)}
        return jsonify(response_data), UNDEFERR, {'Content-Type': 'application/json; charset = utf-8' }
    
@update_rate_routes.route('/update-rate', methods=['POST'])
def modify_updating_rate():
    try:
        data = request.json

        is_dementia = data.get('isDementia')
        _key = data.get('key')
        _update_rate = data.get('updateRate')

        # 보호자와 보호대상자 테이블 모두 업데이트

        if is_dementia == 0: # 보호자
            existing_nok = nok_info.query.filter_by(nok_key=_key).first()
            if existing_nok:

                connected_dementia = dementia_info.query.filter_by(dementia_key = existing_nok.dementia_info_key).first()
                existing_nok.update_rate = _update_rate
                connected_dementia.update_rate = _update_rate
                
            else:
                response_data = {'status': 'error', 'message': 'User info not found'}
                return jsonify(response_data), KEYNOTFOUND, {'Content-Type': 'application/json; charset = utf-8' }
            
        elif is_dementia == 1: # 보호 대상자
            existing_dementia = dementia_info.query.filter_by(dementia_key=_key).first()
            if existing_dementia:   
                
                connected_nok = nok_info.query.filter_by(dementia_info_key = existing_dementia.dementia_key).all()
                existing_dementia.update_rate = _update_rate
                for nok in connected_nok:
                    nok.update_rate = _update_rate
        
            else:
                response_data = {'status': 'error', 'message': 'User info not found'}
                return jsonify(response_data), KEYNOTFOUND, {'Content-Type': 'application/json; charset = utf-8' }
            
        db.session.commit()

        response_data = {'status': 'success', 'message': 'Update rate successfully'}
        
        json_response = jsonify(response_data)
        json_response.headers['Content-Length'] = len(json_response.get_data(as_text=True))

        return json_response, SUCCESS, {'Content-Type': 'application/json; charset = utf-8' }
    
    except Exception as e:
        response_data = {'status': 'error', 'message': str(e)}
        return jsonify(response_data), UNDEFERR, {'Content-Type': 'application/json; charset = utf-8' }
    
@caculate_dementia_avarage_walking_speed_routes.route('/caculate-dementia-avarage-walking-speed', methods=['POST'])
def caculate_dementia_average_walking_speed():
    try:
        data = request.json
        _dementia_key = data.get('dementiaKey')

        if _dementia_key is None:
            return jsonify({'status': 'error', 'message': 'Certification number not found'}), KEYNOTFOUND

        # dementia_key에 해당하고 이동상태가 도보(2)인 환자의 최근 10개의 위치 정보를 가져옴
        location_info_list = location_info.query.filter(and_(location_info.dementia_key == _dementia_key, location_info.user_status == 2)).order_by(location_info.date.desc()).limit(10).all()
        if location_info_list:
            # 최근 10개의 위치 정보를 이용하여 평균 속도 계산
            total_speed = 0
            for loc_info in location_info_list:  # 루프 변수의 이름을 loc_info로 변경
                total_speed += loc_info.current_speed
            average_speed = round(total_speed / len(location_info_list),2)
            result = {
                'averageSpeed' : average_speed,
                'lastLatitude' : location_info_list[-1].latitude,
                'lastLongitude' : location_info_list[-1].longitude
            }
            print('[system] {} dementia average walking speed : {}'.format(_dementia_key, average_speed))
            response_data = {'status': 'success', 'message': 'Average walking speed calculated successfully', 'result': result}

            return jsonify(response_data), SUCCESS, {'Content-Type': 'application/json; charset = utf-8' }
        else:
            print('[system] {} dementia info not found'.format(_dementia_key))
            response_data = {'status': 'error', 'message': 'Location data not found'}

            return jsonify(response_data), LOCDATANOTFOUND, {'Content-Type': 'application/json; charset = utf-8' }
    
    except Exception as e:
        response_data = {'status': 'error', 'message': str(e)}
        return jsonify(response_data), UNDEFERR
    
@get_user_info_routes.route('/get-user-info', methods=['GET']) 
def get_user_info():
    try:
        dementia_key = request.args.get('dementiaKey')

        dementia_info_record = dementia_info.query.filter_by(dementia_key=dementia_key).first()
        nok_info_record = nok_info.query.filter_by(dementia_info_key=dementia_key).order_by(nok_info.num.desc()).first()
        
        if dementia_info_record is None or nok_info_record is None:
            response_data = {'status': 'error', 'message': 'User info not found'}
            return jsonify(response_data), KEYNOTFOUND, {'Content-Type': 'application/json; charset = utf-8' }
        else:

            result = {
                'dementiaInfoRecord': {
                    'dementiaKey': dementia_info_record.dementia_key,
                    'dementiaName': dementia_info_record.dementia_name,
                    'dementiaPhoneNumber': dementia_info_record.dementia_phonenumber,
                    'updateRate' : dementia_info_record.update_rate
                },
                'nokInfoRecord': {
                    'nokKey': nok_info_record.nok_key,
                    'nokName': nok_info_record.nok_name,
                    'nokPhoneNumber': nok_info_record.nok_phonenumber,
                    'updateRate' : nok_info_record.update_rate
                }
            }

            response_data = {'status': 'success', 'message': 'User info sent successfully', 'result': result}
            json_response = jsonify(response_data)
            json_response.headers['Content-Length'] = len(json_response.get_data(as_text=True))

            return json_response, SUCCESS, {'Content-Type': 'application/json; charset = utf-8' }

    
    except Exception as e:
        response_data = {'status': 'error', 'message': str(e)}
        return jsonify(response_data), UNDEFERR, {'Content-Type': 'application/json; charset = utf-8' }
    
@send_meaningful_location_info_routes.route('/send-meaningful-location-info', methods=['GET'])
def send_meaningful_location_info():
    try:
        

        _key = request.args.get('dementiaKey')

        meaningful_location_list = meaningful_location_info.query.filter_by(dementia_key=_key).all()

        if meaningful_location_list:
            result = []
            for location in meaningful_location_list:
                result.append({
                    'latitude': location.latitude,
                    'longitude': location.longitude,
                    'date' : location.day_of_the_week,
                    "time" : location.time
                })
            response_data = {'status': 'success', 'message': 'Meaningful location data sent successfully', 'result': result}

            json_response = jsonify(response_data)
            json_response.headers['Content-Length'] = len(json_response.get_data(as_text=True))

            return json_response, SUCCESS, {'Content-Type': 'application/json; charset = utf-8' }
        else:
            response_data = {'status': 'error', 'message': 'Meaningful location data not found'}

            json_response = jsonify(response_data)
            json_response.headers['Content-Length'] = len(json_response.get_data(as_text=True))

            return json_response, LOCDATANOTFOUND, {'Content-Type': 'application/json; charset = utf-8' }
        
    except Exception as e:
        response_data = {'status': 'error', 'message': str(e)}
        return jsonify(response_data), UNDEFERR, {'Content-Type': 'application/json; charset = utf-8' }
    
@send_location_history_rotues.route('/send-location-history', methods=['GET'])
def send_location_history():
    try:
        dementia_key = request.args.get('dementiaKey')
        date = request.args.get('date')

        location_list = location_info.query.filter(and_(location_info.dementia_key == dementia_key, location_info.date == date)).all()

        if location_list:
            result = []
            for location in location_list:
                result.append({
                    'latitude': location.latitude,
                    'longitude': location.longitude,
                    'time': location.time
                })
            response_data = {'status': 'success', 'message': 'Location history data sent successfully', 'result': result}

            json_response = jsonify(response_data)
            json_response.headers['Content-Length'] = len(json_response.get_data(as_text=True))

            return json_response, SUCCESS, {'Content-Type': 'application/json; charset = utf-8' }
        else:
            response_data = {'status': 'error', 'message': 'Location history data not found'}

            json_response = jsonify(response_data)
            json_response.headers['Content-Length'] = len(json_response.get_data(as_text=True))

            return json_response, LOCDATANOTFOUND, {'Content-Type': 'application/json; charset = utf-8' }


    except Exception as e:
        response_data = {'status': 'error', 'message': str(e)}
        return jsonify(response_data), UNDEFERR, {'Content-Type': 'application/json; charset = utf-8' }


# 스케줄러 비활성화
''' 
@scheduler.task('cron', id='analyze_meaningful_location', hour=17, minute=14, second=0, timezone='Asia/Seoul', misfire_grace_time=120)
def analyze_meaningful_location():
    try:
        with scheduler.app.app_context():
            today = datetime.datetime.now()
            today = today - datetime.timedelta(days = 9)
            #print(today)
            today = today.strftime('%Y-%m-%d')

            print('[system] {} dementia meaningful location data analysis started'.format(today))
            
            location_list = location_info.query.filter(location_info.date == today).all()

            print('[system] {} dementia location data loaded successfully'.format(today))
            errfile = f'error_{today}.txt'
            if location_list:
                dementia_keys = set([location.dementia_key for location in location_list])
                for key in dementia_keys:
                    key_location_list = [location for location in location_list if location.dementia_key == key]
                    
                    if len(key_location_list) <= 100:
                        with open(errfile, 'a') as file:
                            file.write(f'{key} dementia location data not enough\n')
                        continue

                    filename = f'location_data_for_dementia_key_{key}_{today}.txt'
                    with open(filename, 'w') as file:
                        for location in key_location_list:
                            file.write(f'{location.latitude},{location.longitude},{location.date},{location.time}\n')

                    LA = LocationAnalyzer(filename)
                    predict_meaningful_location_data = LA.gmeansFunc()

                    meaningful_location_record = []
                    for i in range(len(predict_meaningful_location_data)-1):
                        new_meaningful_location = meaningful_location_info(
                            dementia_key=key,
                            latitude=predict_meaningful_location_data[i][0][0],
                            longitude=predict_meaningful_location_data[i][0][1],
                            time = predict_meaningful_location_data[i][2],
                            day_of_the_week = predict_meaningful_location_data[i][3]
                        )
                        meaningful_location_record.append(new_meaningful_location)

                    #print(meaningful_location_record)
                    
                    db.session.bulk_save_objects(meaningful_location_record)

                    print(f'[system] {key} dementia meaningful location data saved successfully')

            else:
                print("location_list가 비어 있습니다.")
                pass

            db.session.commit()
            print('[system] {} dementia meaningful location data analysis finished'.format(today))
            
    except Exception as e:
        print(e)
        return str(e)
'''