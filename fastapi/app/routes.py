from fastapi import APIRouter, Request, HTTPException, status
from . import models
from .random_generator import RandomNumberGenerator
from .update_user_status import UpdateUserStatus
from .LocationAnalyzer import LocationAnalyzer
from .database import Database
from apscheduler.schedulers.background import BackgroundScheduler

import json
import datetime

router = APIRouter()
db = Database()
session = next(db.get_session())
sched = BackgroundScheduler(timezone="Asia/Seoul")


'''SUCCESS = 200
WRONG_REQUEST = 400
KEYNOTFOUND = 600
LOCDATANOTFOUND = 650
LOCDATANOTENOUGH = 660
LOGINSUCCESS = 700
LOGINFAILED = 750
UNDEFERR = 500'''

@router.post("/receive-nok-info")
async def receive_nok_info(request: Request):
    data = await request.json()

    _key_from_dementia = data.get("keyFromDementia")
    rng = RandomNumberGenerator()

    try:
        existing_dementia = session.query(models.dementia_info).filter(models.dementia_info.dementia_key == _key_from_dementia).first()
        if existing_dementia:
            _nok_name = data.get("nokName")
            _nok_phonenumber = data.get("nokPhoneNumber")
            
            duplication_check = session.query(models.nok_info).filter(models.nok_info.nok_name == _nok_name, models.nok_info.nok_phonenumber == _nok_phonenumber, models.nok_info.dementia_info_key == _key_from_dementia).first()

            if duplication_check:
                _key = duplication_check.nok_key
            else:
                unique_key = None
                for _ in range(10):
                    unique_key = rng.generate_unique_random_number(100000, 999999)
                
                _key = str(unique_key)

            new_nok = models.nok_info(nok_key=_key, nok_name=_nok_name, nok_phonenumber=_nok_phonenumber, dementia_info_key=_key_from_dementia)
            session.add(new_nok)
            session.commit()
            result = {
                'dementiaInfoRecord' : {
                        'dementiaKey' : existing_dementia.dementia_key,
                        'dementiaName': existing_dementia.dementia_name,
                        'dementiaPhoneNumber': existing_dementia.dementia_phonenumber
                },
                'nokKey': _key
            }

            print(f"[INFO] NOK information received from {existing_dementia.dementia_name}({existing_dementia.dementia_key})")

            response = {
                'status': 'success',
                'message': 'NOK information received',
                'result': result
            }
            
        else: # 보호 대상자 인증번호가 등록되어 있지 않은 경우

            print(f"[ERROR] Dementia key({_key_from_dementia}) not found")

            response = {
                'status': 'error',
                'message': 'Dementia information not found'
            }

        return response
    
    finally:
        session.close()

@router.post("/receive-dementia-info")
async def receive_dementia_info(request: Request):
    data = await request.json()

    rng = RandomNumberGenerator()

    try:
        _dementia_name = data.get("name")
        _dementia_phonenumber = data.get("phoneNumber")

        duplication_check = session.query(models.dementia_info).filter(models.dementia_info.dementia_name == _dementia_name, models.dementia_info.dementia_phonenumber == _dementia_phonenumber).first()

        if duplication_check: # 기존의 인증번호를 가져옴
            _key = duplication_check.dementia_key
        else: # 새로운 인증번호 생성
            unique_key = None
            for _ in range(10):
                unique_key = rng.generate_unique_random_number(100000, 999999)
            
            _key = str(unique_key)

            new_dementia = models.dementia_info(dementia_key=_key, dementia_name=_dementia_name, dementia_phonenumber=_dementia_phonenumber)
            session.add(new_dementia)
            session.commit()

        result = {
            'dementiaKey': _key
        }

        response = {
            'status': 'success',
            'message' : 'Dementia information received',
            'result': result
        }

        print(f"[INFO] Dementia information received from {_dementia_name}({_key})")

        return response
    
    finally:
        session.close()

@router.post("/is-connected")
async def is_connected(request: Request):
    data = await request.json()
    _dementia_key = data.get("dementiaKey")

    session = next(db.get_session())
    try:
        existing_dementia = session.query(models.nok_info).filter_by(dementia_info_key = _dementia_key).first()
        if existing_dementia:
            result = {
                'nokInfoRecord':{
                    'nokKey': existing_dementia.nok_key,
                    'nokName': existing_dementia.nok_name,
                    'nokPhoneNumber': existing_dementia.nok_phonenumber
                }
            }
            response = {
                'status': 'success',
                'message': 'Connection check',
                'result': result
            }

            print(f"[INFO] Connection check from {existing_dementia.dementia_name}({existing_dementia.dementia_key})")
        
        else:
            print (f"[ERROR] Connection denied from Dementia key({_dementia_key})")

            response = {
                'status': 'error',
                'message': 'Dementia information not found'
            }

        return response
    finally:
        session.close()

@router.post("/receive-user-login")
async def receive_user_login(request: Request):
    data = await request.json()

    _key = data.get("key")
    _isdementia = data.get("isDementia")

    try:
        if _isdementia == 0: # 보호자인 경우
            existing_nok = session.query(models.nok_info).filter_by(nok_key = _key).first()

            if existing_nok:
                response = {
                    'status': 'success',
                    'message': 'User login success',
                }
                print(f"[INFO] User login from {existing_nok.nok_name}({existing_nok.nok_key})")

            else:
                response = {
                    'status': 'error',
                    'message': 'User login failed'
                }
                print(f"[ERROR] User login failed from NOK key({_key})")

        elif _isdementia == 1: # 보호 대상자인 경우
            existing_dementia = session.query(models.dementia_info).filter_by(dementia_key = _key).first()

            if existing_dementia:
                response = {
                    'status': 'success',
                    'message': 'User login success',
                }
                print(f"[INFO] User login from {existing_dementia.dementia_name}({existing_dementia.dementia_key})")

            else:
                response = {
                    'status': 'error',
                    'message': 'User login failed'
                }
                print(f"[ERROR] User login failed from Dementia key({_key})")

        return response
            
    finally:
        session.close()

@router.post("/receive-location-info")
async def receive_location_info(request: Request):
    data = await request.json()

    json_data = json.dumps(data)

    _dementia_key = data.get("dementiaKey")

    try:
        existing_dementia = session.query(models.dementia_info).filter_by(dementia_key = _dementia_key).first()

        if existing_dementia:

            user_status_updater = UpdateUserStatus()

            lightsensor = data.get("lightsensor")

            prediction = user_status_updater.predict(json_data)

            new_location = models.location_info(
                dementia_key = data.get("dementiaKey"),
                date = data.get("date"),
                time = data.get("time"),
                latitude = data.get("latitude"),
                longitude = data.get("longitude"),
                bearing = data.get("bearing"),
                user_status = int(prediction[0]),
                accelerationsensor_x = data.get("accelerationsensor")[0],
                accelerationsensor_y = data.get("accelerationsensor")[1],
                accelerationsensor_z = data.get("accelerationsensor")[2],
                directionsensor_x = data.get("directionsensor")[0],
                directionsensor_y = data.get("directionsensor")[1],
                directionsensor_z = data.get("directionsensor")[2],
                gyrosensor_x = data.get("gyrosensor")[0],
                gyrosensor_y = data.get("gyrosensor")[1],
                gyrosensor_z = data.get("gyrosensor")[2],
                lightsensor = lightsensor[0],
                battery = data.get("battery"),
                isInternetOn = data.get("isInternetOn"),
                isRingstoneOn = data.get("isRingstoneOn"),
                isGpsOn = data.get("isGpsOn"),
                current_speed = data.get("currentSpeed")
            )

            session.add(new_location)
            session.commit()

            print(f"[INFO] Location data received from {existing_dementia.dementia_name}({existing_dementia.dementia_key})")

            response = {
                'status': 'success',
                'message': 'Location data received'
            }

        else:
            response = {
                'status': 'error',
                'message': 'Dementia key not found'
            }
            print(f"[ERROR] Dementia key({_dementia_key}) not found(receive location info)")

        return response
        
    finally:
        session.close()

@router.get("/send-live-location-info")
async def send_live_location_info(request: Request):
    _dementia_key = request.query_params.get("dementiaKey")

    try:
        latest_location = session.query(models.location_info).filter_by(dementia_key = _dementia_key).order_by(models.location_info.num.desc()).first()

        if latest_location:
            result = {
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
            response = {
                'status': 'success',
                'message': 'Live location data sent',
                'result': result
            }
            print(f"[INFO] Live location data sent to {latest_location.dementia_key}")

        else:
            response = {
                'status': 'error',
                'message': 'Location data not found'
            }
            print(f"[ERROR] Location data not found for Dementia key({_dementia_key})")

        return response
    
    finally:
        session.close()

@router.post("/modify-user-info")
async def modify_user_info(request: Request):
    data = await request.json()

    _is_dementia = data.get("isDementia")
    _before_name = data.get("name")
    _before_phonenumber = data.get("phoneNumber")

    try:
        if _is_dementia == 0: #보호자
            existing_nok = session.query(models.nok_info).filter_by(nok_key = data.get("key")).first()

            if existing_nok:
                # 수정된 정보를 제외한 나머지 정보들은 기존의 값을 그대로 수신받음

                if not existing_nok.nok_name == _before_name:
                    existing_nok.nok_name = data.get("name")
                
                if not existing_nok.nok_phonenumber == _before_phonenumber:
                    existing_nok.nok_phonenumber = data.get("phoneNumber")
                
                session.commit()

                print(f"[INFO] User information modified by {existing_nok.nok_name}({existing_nok.nok_key})")

                response = {
                    'status': 'success',
                    'message': 'User information modified'
                }
            else:
                print(f"[ERROR] NOK key not found")

                response = {
                    'status': 'error',
                    'message': 'User key not found'
                }

        elif _is_dementia == 1: #보호대상자
            existing_dementia = session.query(models.dementia_info).filter_by(dementia_key = data.get("key")).first()

            if existing_dementia:
                # 수정된 정보를 제외한 나머지 정보들은 기존의 값을 그대로 수신받음

                if not existing_dementia.dementia_name == _before_name:
                    existing_dementia.dementia_name = data.get("name")
                
                if not existing_dementia.dementia_phonenumber == _before_phonenumber:
                    existing_dementia.dementia_phonenumber = data.get("phoneNumber")
                
                session.commit()

                print(f"[INFO] User information modified by {existing_dementia.dementia_name}({existing_dementia.dementia_key})")

                response = {
                    'status': 'success',
                    'message': 'User information modified'
                }

            else:
                print(f"[ERROR] Dementia key not found")

                response = {
                    'status': 'error',
                    'message': 'User key not found'
                }

        return response
    
    finally:
        session.close()

@router.post("/update-rate")
async def modify_updatint_rate(request: Request):
    data = await request.json()

    _is_dementia = data.get("isDementia")
    _key = data.get("key")
    _update_rate = data.get("updateRate")

    #보호자와 보호대상자 모두 업데이트
    try:
        if _is_dementia == 0: #보호자
            existing_nok = session.query(models.nok_info).filter_by(nok_key = _key).first()

            if existing_nok:
                connected_dementia = session.query(models.dementia_info).filter_by(dementia_key = existing_nok.dementia_info_key).first()
                existing_nok.update_rate = _update_rate
                connected_dementia.update_rate = _update_rate

                print(f"[INFO] Update rate modified by {existing_nok.nok_name}, {connected_dementia.dementia_name}")

                response = {
                    'status': 'success',
                    'message': 'User update rate modified'
                }
            else:
                print(f"[ERROR] NOK key not found(update rate)")

                response = {
                    'status': 'error',
                    'message': 'User key not found'
                }
        elif _is_dementia == 1:
            existing_dementia = session.query(models.dementia_info).filter_by(dementia_key = _key).first()

            if existing_dementia:
                connected_nok = session.query(models.nok_info).filter_by(dementia_info_key = existing_dementia.dementia_key).first()
                existing_dementia.update_rate = _update_rate
                connected_nok.update_rate = _update_rate

                print(f"[INFO] Update rate modified by {existing_dementia.dementia_name}, {connected_nok.nok_name}")

                response = {
                    'status': 'success',
                    'message': 'User update rate modified'
                }
            else:
                print(f"[ERROR] Dementia key not found(update rate)")

                response = {
                    'status': 'error',
                    'message': 'User key not found'
                }
        
        session.commit()
    
        return response
    
    finally:
        session.close()

@router.post("/caculate-dementia-avarage-walking-speed")
async def caculate_dementia_average_walking_speed(requset: Request):
    data = await requset.json()

    _dementia_key = data.get("dementiaKey")

    if _dementia_key is None:
        print(f"[ERROR] Dementia key not found(calculate dementia average walking speed)")
        response = {
            'status': 'error',
            'message': 'Dementia key not found'
        }
        return response
    
    try:
        #최근 10개의 정보를 가져와 평균 속도 계산(임시)
        location_info_list = session.query(models.location_info).filter_by(dementia_key = _dementia_key).order_by(models.location_info.num.desc()).limit(10).all()
        
        if location_info_list:
            sum_speed = 0
            for location_info in location_info_list:
                sum_speed += float(location_info.current_speed)
            
            average_speed = round(sum_speed / len(location_info_list), 2)

            response = {
                'status': 'success',
                'message': 'Dementia average walking speed calculated',
                'result': {
                    'averageSpeed': average_speed,
                    'lastLatitude': location_info_list[0].latitude,
                    'lastLongitude': location_info_list[0].longitude
                }
            }
            print(f"[INFO] Dementia average walking speed calculated for {location_info_list[0].dementia_key}")

        else:
            response = {
                'status': 'error',
                'message': 'Not enough location data'
            }
            print(f"[ERROR] Not enough location data for Dementia key({_dementia_key})")

        return response
    
    finally:
        session.close()

@router.get("/get-user-info")
async def get_user_info(request: Request):
    _nok_key = request.query_params.get("nokKey")

    try:
        nok_info_record = session.query(models.nok_info).filter_by(nok_key = _nok_key).first()
        

        if nok_info_record:
            dementia_info_record = session.query(models.dementia_info).filter_by(dementia_key = nok_info_record.dementia_info_key).first()
            if not dementia_info_record:
                response = {
                    'status': 'error',
                    'message': 'Dementia information not found'
                }

                print(f"[ERROR] Dementia information not found for nok key({_nok_key})")

                return response
            
            result = {
                'dementiaInfoRecord': {
                    'dementiaKey': dementia_info_record.dementia_key,
                    'dementiaName': dementia_info_record.dementia_name,
                    'dementiaPhoneNumber': dementia_info_record.dementia_phonenumber
                },
                'nokInfoRecord': {
                    'nokKey': nok_info_record.nok_key,
                    'nokName': nok_info_record.nok_name,
                    'nokPhoneNumber': nok_info_record.nok_phonenumber
                }
            }

            response = {
                'status': 'success',
                'message': 'User information sent',
                'result': result
            }

            print(f"[INFO] User information sent to {dementia_info_record.dementia_name}({dementia_info_record.dementia_key})")
        else:
            response = {
                'status': 'error',
                'message': 'User information not found'
            }

            print(f"[ERROR] User information not found for nok key({_nok_key})")

        return response
    
    finally:
        session.close()

@router.get("/send-meaningful-location-info")
async def send_meaningful_location_info(request: Request):
    _key = request.query_params.get("dementiaKey")

    try:
        meaningful_location_list = session.query(models.meaningful_location_info).filter_by(dementia_key = _key).all()

        if meaningful_location_list:
            meaningful_locations = []

            for location in meaningful_location_list:
                meaningful_locations.append({
                    'date': location.day_of_the_week,
                    'time': location.time,
                    'latitude': location.latitude,
                    'longitude': location.longitude
                })
            
            result = {
                'meaningfulLocations': meaningful_locations
            }
            
            response = {
                'status': 'success',
                'message': 'Meaningful location data sent',
                'result': result
            }

            print(f"[INFO] Meaningful location data sent to {_key}")

        else:
            response = {
                'status': 'error',
                'message': 'Meaningful location data not found'
            }

            print(f"[ERROR] Meaningful location data not found for {_key}")
        
        return response
    
    finally:
        session.close()

@router.get("/send-location-history")
async def send_location_history(request: Request):
    _key = request.query_params.get("dementiaKey")
    date = request.query_params.get("date")

    try:
        location_list = session.query(models.location_info).filter_by(dementia_key = _key, date = date).all()

        if location_list:
            locHistory = []

            for location in location_list:
                locHistory.append({
                    'latitude': location.latitude,
                    'longitude': location.longitude,
                    'time': location.time
                })

            result = {
                'locationHistory': locHistory
            }

            response = {
                'status': 'success',
                'message': 'Location history data sent',
                'result': result
            }

            print(f"[INFO] Location history data sent to {_key}")

        else:
            response = {
                'status': 'error',
                'message': 'Location history data not found'
            }

            print(f"[ERROR] Location history data not found for {_key}")

        return response
    
    finally:
        session.close()

#스케줄러 비활성화
"""@sched.scheduled_job('cron', hour=0, minute=18, id = 'analyze_location_data')
def analyze_location_data():
    today = datetime.datetime.now()
    today = today - datetime.timedelta(days=1) # 어제 날짜의 위치 정보를 분석

    today = today.strftime('%Y-%m-%d')

    print(f"[INFO] Start analyzing location data at {today}")

    try:
        location_list = session.query(models.location_info).filter(models.location_info.date == today).all()

        print(f"[INFO] {len(location_list)} location data found")

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
                prediction = LA.gmeansFunc()

                meaningful_location_list = []
                for i in range(len(prediction) - 1):
                    new_meaningful_location = models.meaningful_location_info(
                        dementia_key=key,
                        latitude = prediction[i][0][0],
                        longitude = prediction[i][0][1],
                        time = prediction[i][2],
                        day_of_the_week = prediction[i][3]
                    )
                    meaningful_location_list.append(new_meaningful_location)

                session.add_all(meaningful_location_list)

                print(f"[INFO] Meaningful location data saved for {key}")
            
        else:
            print("[ERROR] Location data not found")
            pass

        session.commit()
        print(f"[INFO] Location data analysis completed at {today}")

    finally:
        session.close()"""