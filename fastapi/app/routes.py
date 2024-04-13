from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from . import models
from .random_generator import RandomNumberGenerator
from .update_user_status import UpdateUserStatus
from .LocationAnalyzer import LocationAnalyzer
from .database import Database
from .bodymodel import *
from apscheduler.schedulers.background import BackgroundScheduler


import json
import datetime

router = APIRouter()
db = Database()
session = next(db.get_session())
sched = BackgroundScheduler(timezone="Asia/Seoul")

'''
성공 = 200
실패 = 400

작성됨 = 201

위치 정보, 키 없음 = 404


정의되지 않은 오류 = 500
'''

# Define API endpoint
@router.post("/noks",status_code=status.HTTP_201_CREATED, responses = {201 : {"model" : ReceiveNokInfoResponse, "description" : "유저 등록 성공" },404: {"model": ErrorResponse, "description": "보호 대상자 키 조회 실패"}}, description="보호자가 보호 대상자의 정보를 등록")
async def receive_nok_info(request: ReceiveNokInfoRequest):

    _key_from_dementia = request.keyFromDementia

    rng = RandomNumberGenerator()

    try:
        existing_dementia = session.query(models.dementia_info).filter(models.dementia_info.dementia_key == _key_from_dementia).first()
        if existing_dementia:
            _nok_name = request.nokName
            _nok_phonenumber = request.nokPhoneNumber
            
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

            return response
            
        else: # 보호 대상자 인증번호가 등록되어 있지 않은 경우

            print(f"[ERROR] Dementia key({_key_from_dementia}) not found")

            raise HTTPException(status_code=404, detail="Dementia key not found")

    finally:
        session.close()

@router.post("/dementias", status_code=status.HTTP_201_CREATED, responses = {201 : {"model" : ReceiveDementiaInfoResponse, "description" : "유저 등록 성공" }}, description="보호 대상자의 정보를 등록")
async def receive_dementia_info(request: ReceiveDementiaInfoRequest):

    rng = RandomNumberGenerator()

    try:
        _dementia_name = request.name
        _dementia_phonenumber = request.phoneNumber

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

@router.post("/connection", status_code=status.HTTP_200_OK, responses = {200 : {"model" : ConnectionResponse, "description" : "연결 확인 성공" }, 400: {"model": ErrorResponse, "description": "연결 실패"}}, description="보호자와 보호 대상자의 연결 확인")
async def is_connected(request: ConnectionRequest):

    _dementia_key = request.dementiaKey

    session = next(db.get_session())
    try:
        existing_nok = session.query(models.nok_info).filter_by(dementia_info_key = _dementia_key).first()
        if existing_nok:
            result = {
                'nokInfoRecord':{
                    'nokKey': existing_nok.nok_key,
                    'nokName': existing_nok.nok_name,
                    'nokPhoneNumber': existing_nok.nok_phonenumber
                }
            }
            response = {
                'status': 'success',
                'message': 'Connection check',
                'result': result
            }

            print(f"[INFO] Connection check from {existing_nok.nok_name}(from {existing_nok.dementia_info_key})")

            return response
        
        else:
            print (f"[ERROR] Connection denied from Dementia key({_dementia_key})")

            raise HTTPException(status_code=400, detail="Connection denied")

    finally:
        session.close()

@router.post("/login", responses = {200 : {"model" : CommonResponse, "description" : "로그인 성공" }, 400: {"model": ErrorResponse, "description": "로그인 실패"}}, description="보호자와 보호 대상자의 로그인 | isDementia : 0(보호자), 1(보호 대상자)")
async def receive_user_login(request: loginRequest):
    _key = request.key
    _isdementia = request.isDementia

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
                print(f"[ERROR] User login failed from NOK key({_key})")

                raise HTTPException(status_code=400, detail="User login failed")

        elif _isdementia == 1: # 보호 대상자인 경우
            existing_dementia = session.query(models.dementia_info).filter_by(dementia_key = _key).first()

            if existing_dementia:
                response = {
                    'status': 'success',
                    'message': 'User login success',
                }
                print(f"[INFO] User login from {existing_dementia.dementia_name}({existing_dementia.dementia_key})")

            else:
                print(f"[ERROR] User login failed from Dementia key({_key})")

                raise HTTPException(status_code=400, detail="User login failed")

        return response
            
    finally:
        session.close()

@router.post("/locations/dementias", responses = {200 : {"model" : CommonResponse, "description" : "위치 정보 전송 성공" }, 404: {"model": ErrorResponse, "description": "보호 대상자 키 조회 실패"}}, description="보호 대상자의 위치 정보를 전송 | isRingstoneOn : 0(무음), 1(진동), 2(벨소리)")
async def receive_location_info(request: ReceiveLocationRequest):

    try:
        _dementia_key = request.dementiaKey

        existing_dementia = session.query(models.dementia_info).filter_by(dementia_key = _dementia_key).first()

        if existing_dementia:

            user_status_updater = UpdateUserStatus()

            accel = request.accelerationSensor
            gyro = request.gyroSensor
            direction = request.directionSensor

            prediction = user_status_updater.predict(accel, gyro, direction)

            new_location = models.location_info(
                dementia_key = _dementia_key,
                date = request.date,
                time = request.time,
                latitude = request.latitude,
                longitude = request.longitude,
                bearing = request.bearing,
                user_status = int(prediction[0]),
                accelerationsensor_x = accel[0],
                accelerationsensor_y = accel[1],
                accelerationsensor_z = accel[2],
                directionsensor_x = direction[0],
                directionsensor_y = direction[1],
                directionsensor_z = direction[2],
                gyrosensor_x = gyro[0],
                gyrosensor_y = gyro[1],
                gyrosensor_z = gyro[2],
                lightsensor = request.lightSensor[0],
                battery = request.battery,
                isInternetOn = request.isInternetOn,
                isRingstoneOn = request.isRingstoneOn,
                isGpsOn = request.isGpsOn,
                current_speed = request.currentSpeed
            )

            session.add(new_location)
            session.commit()

            print(f"[INFO] Location data received from {existing_dementia.dementia_name}({existing_dementia.dementia_key})")

            response = {
                'status': 'success',
                'message': 'Location data received'
            }

        else:
            print(f"[ERROR] Dementia key({_dementia_key}) not found(receive location info)")

            raise HTTPException(status_code=404, detail="Dementia key not found")

        return response
        
    finally:
        session.close()

@router.get("/locations/noks/{dementiaKey}", responses = {200 : {"model" : GetLocationResponse, "description" : "위치 정보 전송 성공" }, 404: {"model": ErrorResponse, "description": "위치 정보 없음"}}, description="보호자에게 보호 대상자의 위치 정보를 전송 | userStatus : 1(정지), 2(도보), 3(차량), 4(지하철) | isRingstoneOn : 0(무음), 1(진동), 2(벨소리)")
async def send_live_location_info(dementiaKey : int):

    try:
        latest_location = session.query(models.location_info).filter_by(dementia_key = dementiaKey).order_by(models.location_info.num.desc()).first()

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
            print(f"[ERROR] Location data not found for Dementia key({dementiaKey})")

            raise HTTPException(status_code=404, detail="Location data not found")

        return response
    
    finally:
        session.close()

@router.post("/users/modification/userInfo", responses = {200 : {"model" : CommonResponse, "description" : "유저 정보 수정 성공" }, 404: {"model": ErrorResponse, "description": "유저 키 조회 실패"}}, description="보호자와 보호대상자의 정보를 수정 | isDementia : 0(보호자), 1(보호대상자) | 변경하지 않는 값은 기존의 값을 그대로 수신할 것")
async def modify_user_info(request: ModifyUserInfoRequest):

    _is_dementia = request.isDementia
    _key = request.key
    _before_name = request.name
    _before_phonenumber = request.phoneNumber

    try:
        if _is_dementia == 0: #보호자
            existing_nok = session.query(models.nok_info).filter_by(nok_key = _key).first()

            if existing_nok:
                # 수정된 정보를 제외한 나머지 정보들은 기존의 값을 그대로 수신받음

                if not existing_nok.nok_name == _before_name:
                    existing_nok.nok_name = _before_name
                
                if not existing_nok.nok_phonenumber == _before_phonenumber:
                    existing_nok.nok_phonenumber = _before_phonenumber
                
                session.commit()

                print(f"[INFO] User information modified by {existing_nok.nok_name}({existing_nok.nok_key})")

                response = {
                    'status': 'success',
                    'message': 'User information modified'
                }
            else:
                print(f"[ERROR] NOK key not found")
                
                raise HTTPException(status_code=404, detail="NOK key not found")

        elif _is_dementia == 1: #보호대상자
            existing_dementia = session.query(models.dementia_info).filter_by(dementia_key = _key).first()

            if existing_dementia:
                # 수정된 정보를 제외한 나머지 정보들은 기존의 값을 그대로 수신받음

                if not existing_dementia.dementia_name == _before_name:
                    existing_dementia.dementia_name = _before_name
                
                if not existing_dementia.dementia_phonenumber == _before_phonenumber:
                    existing_dementia.dementia_phonenumber = _before_phonenumber
                
                session.commit()

                print(f"[INFO] User information modified by {existing_dementia.dementia_name}({existing_dementia.dementia_key})")

                response = {
                    'status': 'success',
                    'message': 'User information modified'
                }

            else:
                print(f"[ERROR] Dementia key not found")

                raise HTTPException(status_code=404, detail="Dementia key not found")

        return response
    
    finally:
        session.close()

@router.post("/users/modification/updateRate", responses = {200 : {"model" : CommonResponse, "description" : "업데이트 주기 수정 성공" }, 404: {"model": ErrorResponse, "description": "유저 키 조회 실패"}}, description="보호자와 보호대상자의 업데이트 주기를 수정 | isDementia : 0(보호자), 1(보호대상자)")
async def modify_updatint_rate(request: ModifyUserUpdateRateRequest):
    _is_dementia = request.isDementia
    _key = request.key
    _update_rate = request.updateRate

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

                raise HTTPException(status_code=404, detail="NOK key not found")

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

                raise HTTPException(status_code=404, detail="Dementia key not found")
        
        session.commit()
    
        return response
    
    finally:
        session.close()

@router.post("/dementias/averageWalkingSpeed", responses = {200 : {"model" : AverageWalkingSpeedResponse, "description" : "평균 걷기 속도 계산 성공" }, 404: {"model": ErrorResponse, "description": "보호 대상자 키 조회 실패 or 위치 정보 부족"}}, description="보호 대상자의 평균 걷기 속도를 계산")
async def caculate_dementia_average_walking_speed(requset: AverageWalkingSpeedRequest):

    _dementia_key = requset.dementiaKey

    if _dementia_key is None:
        print(f"[ERROR] Dementia key not found(calculate dementia average walking speed)")
        
        raise HTTPException(status_code=404, detail="Dementia key not found")
    
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
            print(f"[ERROR] Not enough location data for Dementia key({_dementia_key})")

            raise HTTPException(status_code=404, detail="Not enough location data")

        return response
    
    finally:
        session.close()

@router.get("/users/info/{nokKey}", responses = {200 : {"model" : GetUserInfoResponse, "description" : "유저 정보 전송 성공" }, 404: {"model": ErrorResponse, "description": "유저 정보 없음"}}, description="보호자와 보호 대상자 정보 전달")
async def get_user_info(nokKey : int):
    _nok_key = nokKey

    try:
        nok_info_record = session.query(models.nok_info).filter_by(nok_key = _nok_key).first()
        

        if nok_info_record:
            dementia_info_record = session.query(models.dementia_info).filter_by(dementia_key = nok_info_record.dementia_info_key).first()
            if not dementia_info_record:
                print(f"[ERROR] Dementia information not found for nok key({_nok_key})")

                raise HTTPException(status_code=404, detail="Dementia information not found")
            
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
            print(f"[ERROR] User information not found for nok key({_nok_key})")

            raise HTTPException(status_code=404, detail="User information not found")

        return response
    
    finally:
        session.close()

@router.get("/locatoins/meaningful/{dementiaKey}", responses = {200 : {"model" : MeaningfulLocResponse, "description" : "의미장소 전송 성공" }, 404: {"model": ErrorResponse, "description": "의미 장소 없음"}}, description="보호 대상자의 의미 장소 정보 전달")
async def send_meaningful_location_info(dementiaKey : int):
    _key = dementiaKey

    try:
        meaningful_location_list = session.query(models.meaningful_location_info).filter_by(dementia_key = _key).all()

        if meaningful_location_list:
            meaningful_locations = []

            for location in meaningful_location_list:
                meaningful_locations.append({
                    'dayOfTheWeek': location.day_of_the_week,
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
            print(f"[ERROR] Meaningful location data not found for {_key}")

            raise HTTPException(status_code=404, detail="Meaningful location data not found")
        
        return response
    
    finally:
        session.close()

@router.get("/locations/history/{date}/{dementiaKey}", responses = {200 : {"model" : LocHistoryResponse, "description" : "위치 이력 전송 성공" }, 404: {"model": ErrorResponse, "description": "위치 이력 없음"}}, description="보호 대상자의 위치 이력 정보 전달")
async def send_location_history(date : str, dementiaKey : int):
    _key = dementiaKey

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
                'locationHistory': locHistory,
            }

            response = {
                'status': 'success',
                'message': 'Location history data sent',
                'result': result
            }

            print(f"[INFO] Location history data sent to {_key}")

        else:
            print(f"[ERROR] Location history data not found for {_key}")

            raise HTTPException(status_code=404, detail="Location history data not found")

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