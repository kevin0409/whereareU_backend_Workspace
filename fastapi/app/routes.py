from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm, APIKeyHeader

from passlib.context import CryptContext
from haversine import haversine

from . import models
from .random_generator import RandomNumberGenerator
from .update_user_status import UpdateUserStatus
from .database import Database
from .bodymodel import *
from .util import JWTService
from .config import Config
from .schedularFunc import SchedulerFunc

from apscheduler.schedulers.background import BackgroundScheduler

import asyncio
import datetime


router = APIRouter()
db = Database()
session = next(db.get_session())
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
jwt = JWTService()
schedFunc = SchedulerFunc()
sched = BackgroundScheduler(timezone="Asia/Seoul", daemon=True)





'''
성공 = 200
실패 = 400

작성됨 = 201

위치 정보, 키 없음 = 404

정의되지 않은 오류 = 500
'''




@router.get("/test", responses = {200 : {"model" : CommonResponse, "description" : "테스트 성공" }}, description="토큰을 사용했을 때 유저 정보가 반환되면 성공(앞으로 이렇게 바뀔 예정)")
async def protected_route(current_user= Depends(APIKeyHeader(name="Authorization"))):
    return jwt.get_current_user(current_user, session)

"""@router.post("/test/login", responses = {200 : {"model" : TokenResponse, "description" : "로그인 성공" }, 400: {"model": ErrorResponse, "description": "로그인 실패"}}, description="로그인 테스트(앞으로 이렇게 바뀔예정) | username : 이름, password : key -> 이 두개만 채워서 보내면 됨")
async def test_login(from_data: OAuth2PasswordRequestForm = Depends()):
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
        session.close()"""




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
                

            access_token = jwt.create_access_token(_nok_name, _key)
            refresh_token = jwt.create_refresh_token(_nok_name, _key)

            new_token = models.refresh_token_info(key=_key, refresh_token=refresh_token)
            result = {
                'dementiaInfoRecord' : {
                        'dementiaKey' : existing_dementia.dementia_key,
                        'dementiaName': existing_dementia.dementia_name,
                        'dementiaPhoneNumber': existing_dementia.dementia_phonenumber
                },
                'nokKey': _key,
                'accessToken': access_token,
                'refreshToken': refresh_token
            }

            print(f"[INFO] NOK information received from {existing_dementia.dementia_name}({existing_dementia.dementia_key})")

            response = {
                'status': 'success',
                'message': 'NOK information received',
                'result': result
            }
            session.commit()

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

            #_key = pwd_context.hash(unique_key)

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

@router.post("/connection", responses = {200 : {"model" : ConnectionResponse, "description" : "연결 확인 성공" }, 400: {"model": ErrorResponse, "description": "연결 실패"}}, description="보호자와 보호 대상자의 연결 확인")
async def is_connected(request: ConnectionRequest):

    _dementia_key = request.dementiaKey

    try:
        existing_nok = session.query(models.nok_info).filter_by(dementia_info_key = _dementia_key).first()
        if existing_nok:
            dementia_info = session.query(models.dementia_info).filter_by(dementia_key = _dementia_key).first()
            access_token = jwt.create_access_token(dementia_info.dementia_name, dementia_info.dementia_key)
            refresh_token = jwt.create_refresh_token(dementia_info.dementia_name, dementia_info.dementia_key)

            new_token = models.refresh_token_info(key=dementia_info.dementia_key, refresh_token=refresh_token)

            session.add(new_token)
            session.commit()
            result = {
                'nokInfoRecord':{
                    'nokKey': existing_nok.nok_key,
                    'nokName': existing_nok.nok_name,
                    'nokPhoneNumber': existing_nok.nok_phonenumber
                },
                'accessToken': access_token,
                'refreshToken': refresh_token
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

@router.post("/login", responses = {200 : {"model" : TokenResponse, "description" : "로그인 성공" }, 400: {"model": ErrorResponse, "description": "로그인 실패"}}, description="보호자와 보호 대상자의 로그인 | username : 이름, password : key -> 이 두개만 채워서 보내면 됨")
async def receive_user_login(from_data: OAuth2PasswordRequestForm = Depends()):
    try:
        user = jwt.get_user(from_data.username, from_data.password, session)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect key",
                headers={"WWW-Authenticate": "Bearer"},
            )
        # Dict 형태로 반환
        '''def create_access_token(self, data: dict) -> str:
                return self._create_token(data, self.access_token_expire_time)'''
        
        if user[1] == 0:
            access_token = jwt.create_access_token(user[0].nok_name, user[0].nok_key)
            
            #refresh_token_info 테이블 디비에 저장
            if not session.query(models.refresh_token_info).filter_by(key=user[0].nok_key).first():
                refresh_token = jwt.create_refresh_token(user[0].nok_name, user[0].nok_key)
                new_token = models.refresh_token_info(key=user[0].nok_key, refresh_token=refresh_token)
                session.add(new_token)
            else: 
                refresh_token = None


        else:
            access_token = jwt.create_access_token(user[0].dementia_name, user[0].dementia_key)
            
            #refresh_token 디비에 저장
            if not session.query(models.refresh_token_info).filter_by(key=user[0].dementia_key).first():
                refresh_token = jwt.create_refresh_token(user[0].dementia_name, user[0].dementia_key)
                new_token = models.refresh_token_info(key=user[0].dementia_key, refresh_token=refresh_token)
                session.add(new_token)
            else:
                refresh_token = None

        session.commit()

        result = {
            'accessToken': access_token,
            'refreshToken': refresh_token,
            'tokenType': 'bearer'
        }

        response = {
            'status': 'success',
            'message': 'Login success',
            'result': result
        }

        return response
            
    finally:
        session.close()

@router.post("/locations/dementias", responses = {200 : {"model" : TempResponse, "description" : "위치 정보 전송 성공" }, 404: {"model": ErrorResponse, "description": "보호 대상자 키 조회 실패"}}, description="보호 대상자의 위치 정보를 전송 | isRingstoneOn : 0(무음), 1(진동), 2(벨소리)")
async def receive_location_info(request: ReceiveLocationRequest, user_info: int = Depends(APIKeyHeader(name = "Authorization"))):
    try:
        _dementia_key = jwt.get_current_user(user_info, session)[0].dementia_key

        existing_dementia = session.query(models.dementia_info).filter_by(dementia_key = _dementia_key).first()

        user_status_updater = UpdateUserStatus()

        accel = request.accelerationSensor
        gyro = request.gyroSensor
        direction = request.directionSensor

        prediction = user_status_updater.predict(accel, gyro, direction)

        if int(prediction[0]) == 1:
            userStat = "정지"
        elif int(prediction[0]) == 2:
            userStat = "도보"
        elif int(prediction[0]) == 3:
            userStat = "차량"
        elif int(prediction[0]) == 4:
            userStat = "지하철"

        new_location = models.location_info(
            dementia_key = _dementia_key,
            date = request.date,
            time = request.time,
            latitude = request.latitude,
            longitude = request.longitude,
            bearing = request.bearing,
            user_status = userStat,
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
            'message': 'Location data received',
            'result' : int(prediction[0])
        }

        return response
        
    finally:
        session.close()

@router.get("/locations/noks", responses = {200 : {"model" : GetLocationResponse, "description" : "위치 정보 전송 성공" }, 404: {"model": ErrorResponse, "description": "위치 정보 없음"}}, description="보호자에게 보호 대상자의 위치 정보를 전송(쿼리 스트링) | userStatus : 1(정지), 2(도보), 3(차량), 4(지하철) | isRingstoneOn : 0(무음), 1(진동), 2(벨소리)")
async def send_live_location_info(user_info: int = Depends(APIKeyHeader(name = "Authorization"))):

    try:
        _dementia_key = jwt.get_current_user(user_info, session)[0].dementia_info_key

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
            print(f"[ERROR] Location data not found for Dementia key({_dementia_key})")

            raise HTTPException(status_code=404, detail="Location data not found")

        return response
    
    finally:
        session.close()

@router.post("/users/modification/userInfo", responses = {200 : {"model" : TokenResponse, "description" : "유저 정보 수정 성공" }, 404: {"model": ErrorResponse, "description": "유저 키 조회 실패"}}, description="보호자와 보호대상자의 정보를 수정 | 정보 수정 시 새로운 토큰 전송 | 변경하지 않는 값은 기존의 값을 그대로 수신할 것")
async def modify_user_info(request: ModifyUserInfoRequest, user_info : int = Depends(APIKeyHeader(name = "Authorization"))):

    _new_name = request.name
    _new_phonenumber = request.phoneNumber

    try:
        user = jwt.get_current_user(user_info, session)

        if user[1] == 0: #보호자
            existing_nok = session.query(models.nok_info).filter_by(nok_key = user[0].nok_key).first()

            if not existing_nok.nok_name == _new_name:
                existing_nok.nokname = _new_name
            if not existing_nok.nok_phonenumber == _new_phonenumber:
                existing_nok.nok_phonenumber = _new_phonenumber

            print(f"[INFO] User information modified by {existing_nok.nok_name}({existing_nok.nok_key})")

            new_access_token = jwt.create_access_token(existing_nok.nok_name, existing_nok.nok_key)
            new_refresh_token = jwt.create_refresh_token(existing_nok.nok_name, existing_nok.nok_key)

            update_refresh_token = models.refresh_token_info(key=existing_nok.nok_key, refresh_token=new_refresh_token)
            session.add(update_refresh_token)


        elif user[1] == 1: #보호대상자
            existing_dementia = session.query(models.dementia_info).filter_by(dementia_key = user[0].dementia_key).first()

            if not existing_dementia.dementia_name == _new_name:
                existing_dementia.dementia_name = _new_name
            if not existing_dementia.dementia_phonenumber == _new_phonenumber:
                existing_dementia.dementia_phonenumber = _new_phonenumber

            print(f"[INFO] User information modified by {existing_dementia.dementia_name}({existing_dementia.dementia_key})")

            new_access_token = jwt.create_access_token(existing_dementia.dementia_name, existing_dementia.dementia_key)
            new_refresh_token = jwt.create_refresh_token(existing_dementia.dementia_name, existing_dementia.dementia_key)

            update_refresh_token = models.refresh_token_info(key=existing_dementia.dementia_key, refresh_token=new_refresh_token)
            session.add(update_refresh_token)



        result = {
            'accessToken': new_access_token,
            'refreshToken': new_refresh_token
        }

        response = {
            'status': 'success',
            'message': 'User information modified',
            'result': result
        }

        session.commit()


        return response
    
    finally:
        session.close()

@router.post("/users/modification/updateRate", responses = {200 : {"model" : CommonResponse, "description" : "업데이트 주기 수정 성공" }, 404: {"model": ErrorResponse, "description": "유저 키 조회 실패"}}, description="보호자와 보호대상자의 업데이트 주기를 수정")
async def modify_updatint_rate(request: ModifyUserUpdateRateRequest, user_info : int = Depends(APIKeyHeader(name = "Authorization"))):

    _update_rate = request.updateRate

    #보호자와 보호대상자 모두 업데이트
    try:
        user = jwt.get_current_user(user_info, session)
        if user[1] == 0: #보호자
            existing_nok = session.query(models.nok_info).filter_by(nok_key = user[0].nok_key).first()

            connected_dementia = session.query(models.dementia_info).filter_by(dementia_key = existing_nok.dementia_info_key).first()
            existing_nok.update_rate = _update_rate
            connected_dementia.update_rate = _update_rate

            print(f"[INFO] Update rate modified by {existing_nok.nok_name}, {connected_dementia.dementia_name}")

            response = {
                'status': 'success',
                'message': 'User update rate modified'
            }

        elif user[1] == 1:
            existing_dementia = session.query(models.dementia_info).filter_by(dementia_key = user[0].dementia_key).first()

            connected_nok = session.query(models.nok_info).filter_by(dementia_info_key = existing_dementia.dementia_key).first()
            existing_dementia.update_rate = _update_rate
            connected_nok.update_rate = _update_rate

            print(f"[INFO] Update rate modified by {existing_dementia.dementia_name}, {connected_nok.nok_name}")

            response = {
                'status': 'success',
                'message': 'User update rate modified'
            }
        
        session.commit()
    
        return response
    
    finally:
        session.close()

@router.post("/dementias/averageWalkingSpeed", responses = {200 : {"model" : AverageWalkingSpeedResponse, "description" : "평균 걷기 속도 계산 성공" }, 404: {"model": ErrorResponse, "description": "보호 대상자 키 조회 실패 or 위치 정보 부족"}}, description="보호 대상자의 평균 걷기 속도를 계산 및 마지막 정보 전송")
async def caculate_dementia_average_walking_speed(user_info : int = Depends(APIKeyHeader(name = "Authorization"))): 
    try:
        _dementia_key = jwt.get_current_user(user_info, session)[0].dementia_info_key

        #최근 10개의 정보를 가져와 평균 속도 계산(임시)
        location_info_list = session.query(models.location_info).filter_by(dementia_key = _dementia_key).order_by(models.location_info.num.desc()).limit(10).all()
        
        if location_info_list:
            sum_speed = 0
            for location_info in location_info_list:
                sum_speed += float(location_info.current_speed)
            
            average_speed = round(sum_speed / len(location_info_list), 2)
            
            geo = kakao.geo_coord2address(location_info_list[0].longitude, location_info_list[0].latitude)

            if not geo['documents'][0]['road_address'] == None:
                xy2addr = geo['documents'][0]['road_address']['address_name'] + " " + geo['documents'][0]['road_address']['building_name']
                    
            else:
                xy2addr = geo['documents'][0]['address']['address_name']

            response = {
                'status': 'success',
                'message': 'Dementia average walking speed calculated',
                'result': {
                    'averageSpeed': average_speed,
                    'lastLatitude': location_info_list[0].latitude,
                    'lastLongitude': location_info_list[0].longitude,
                    'addressName' : xy2addr
                }
            }
            print(f"[INFO] Dementia average walking speed calculated for {location_info_list[0].dementia_key}")

        else:
            print(f"[ERROR] Not enough location data for Dementia key({_dementia_key})")

            raise HTTPException(status_code=404, detail="Not enough location data")

        return response
    
    finally:
        session.close()

@router.get("/users/info", responses = {200 : {"model" : GetUserInfoResponse, "description" : "유저 정보 전송 성공" }, 404: {"model": ErrorResponse, "description": "유저 정보 없음"}}, description="보호자와 보호 대상자 정보 전달(쿼리 스트링)")
async def get_user_info(user_info : int = Depends(APIKeyHeader(name = "Authorization"))):
    try:
        user = jwt.get_current_user(user_info, session)

        nok_info_record = session.query(models.nok_info).filter_by(nok_key = user[0].nok_key).first()
        

        if nok_info_record:
            dementia_info_record = session.query(models.dementia_info).filter_by(dementia_key = nok_info_record.dementia_info_key).first()
            if not dementia_info_record:
                print(f"[ERROR] Dementia information not found for nok key({user[0].nok_key})")

                raise HTTPException(status_code=404, detail="Dementia information not found")
            
            result = {
                'dementiaInfoRecord': {
                    'dementiaKey': dementia_info_record.dementia_key,
                    'dementiaName': dementia_info_record.dementia_name,
                    'dementiaPhoneNumber': dementia_info_record.dementia_phonenumber,
                    'updateRate': dementia_info_record.update_rate
                },
                'nokInfoRecord': {
                    'nokKey': nok_info_record.nok_key,
                    'nokName': nok_info_record.nok_name,
                    'nokPhoneNumber': nok_info_record.nok_phonenumber,
                    'updateRate': nok_info_record.update_rate
                }
            }

            response = {
                'status': 'success',
                'message': 'User information sent',
                'result': result
            }

            print(f"[INFO] User information sent to {dementia_info_record.dementia_name}({dementia_info_record.dementia_key})")

        else:
            print(f"[ERROR] User information not found for nok key({user[0].nok_key})")

            raise HTTPException(status_code=404, detail="User information not found")

        return response
    
    finally:
        session.close()

@router.get("/locations/meaningful", responses = {200 : {"model" : MeaningfulLocResponse, "description" : "의미장소 전송 성공" }, 404: {"model": ErrorResponse, "description": "의미 장소 없음"}}, description="보호 대상자의 의미 장소 정보 및 주변 경찰서 정보 전달(쿼리 스트링)")
async def send_meaningful_location_info(user_info : int = Depends(APIKeyHeader(name = "Authorization"))):

    try:
        _key = jwt.get_current_user(user_info, session)[0].dementia_info_key

        meaningful_location_list = session.query(models.meaningful_location_info).filter_by(dementia_key=_key).all()

        if meaningful_location_list:
            meaningful_places_dict = {}


            for location in meaningful_location_list:
                address = location.address
                day_of_week = location.day_of_the_week
                time = location.time

                # 주소가 이미 존재하는지 확인하고, 없으면 새로운 딕셔너리 엔트리 생성
                if address not in meaningful_places_dict:
                    # 해당 주소의 경찰서 정보 가져오기(distance 순으로 정렬)
                    police_list = session.query(models.police_info).filter_by(key = location.key).order_by(models.police_info.distance).limit(3).all()

                    #police_list의 num 속성 제거
                    for police in police_list:
                        del police.num
                        del police.key

                    meaningful_places_dict[address] = {
                        'address': address,
                        'timeInfo': [],
                        'latitude': location.latitude,
                        'longitude': location.longitude,
                        'policeStationInfo' : police_list
                    }

                # 해당 주소의 시간 정보 리스트에 현재 시간 정보가 없으면 추가
                time_info_list = meaningful_places_dict[address]['timeInfo']
                if {'dayOfTheWeek': day_of_week, 'time': time} not in time_info_list:
                    time_info_list.append({'dayOfTheWeek': day_of_week, 'time': time})

            # 결과를 리스트 형태로 변환
            meaningful_places = list(meaningful_places_dict.values())

            result = {
                'meaningfulPlaces': meaningful_places
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

@router.get("/locations/history", responses = {200 : {"model" : LocHistoryResponse, "description" : "위치 이력 전송 성공" }, 404: {"model": ErrorResponse, "description": "위치 이력 없음"}}, description="보호 대상자의 위치 이력 정보 전달(쿼리 스트링) | date : YYYY-MM-DD")
async def send_location_history(_date : str, user_info : int = Depends(APIKeyHeader(name = "Authorization"))):
    _key = jwt.get_current_user(user_info, session)[0].dementia_key
    try:
        location_list = session.query(models.location_info).filter_by(dementia_key=_key, date=_date).all()

        if not location_list:
            print(f"[ERROR] Location history data not found for {_key}")
            raise HTTPException(status_code=404, detail="Location history data not found")

        locHistory = []
        prev_location = None

        for location in location_list:
            current_location = (location.latitude, location.longitude)
            distance = 0

            if prev_location:
                distance = round(haversine(current_location, prev_location, unit='m'), 2)

            if not locHistory or location.user_status != "정지" or locHistory[-1]['userStatus'] != "정지":
                locHistory.append({
                    'latitude': location.latitude,
                    'longitude': location.longitude,
                    'time': location.time,
                    'userStatus': location.user_status,
                    'distance': distance
                })
            else:
                locHistory[-1]['time'] = locHistory[-1]['time'][:8] + ',' + location.time

            prev_location = current_location

        result = {
        'locationHistory': locHistory,
        }

        response = {
            'status': 'success',
            'message': 'Location history data sent',
            'result': result
        }
        

        print(f"[INFO] Location history data sent to {_key}")
    
    finally:
        session.close()

        return response





'''#스케줄러 비활성화
@sched.scheduled_job('cron', hour=1, minute=0, id = 'geocoding')
def geocoding():
    asyncio.run(schedFunc.load_kakao_api(session))

@sched.scheduled_job('cron', hour=0, minute=0, id = 'analyze_location_data')
def analyzing_location_data():
    asyncio.run(schedFunc.load_analyze_location_data(session))'''


