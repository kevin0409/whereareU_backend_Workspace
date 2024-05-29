from app import models
from fastapi import Depends

from . import models
from .random_generator import RandomNumberGenerator
from .update_user_status import UpdateUserStatus
from .LocationAnalyzer import LocationAnalyzer
from .database import Database
from .config import Config

from PyKakao import Local

from datetime import datetime, timedelta
from pytz import timezone




kakao = Local(service_key=Config.kakao_service_key)


class SchedulerFunc:
    def __init__(self):
        pass

    async def load_analyze_location_data(self, session = Depends(Database().get_session)):
        await self.analyze_location_data(session)
    
    async def load_kakao_api(self, session = Depends(Database().get_session)):
        await self.kakao_api(session)

    async def kakao_api(self, session = Depends(Database().get_session)):
        try:
            print(f"[INFO] Start geocoding")
            # db 에서 의미장소 정보 가져오기
            meaningful_location_list = session.query(models.meaningful_location_info).filter_by(address = None).all()

            # dementia_key 별로 분류
            dementia_keys = set([location.dementia_key for location in meaningful_location_list])

            rng = RandomNumberGenerator()

            # dementia_key별 의미장소 위경도 값으로 주소 변환 후 의미 장소 테이블에 address란에 추가
            address_list = []
            key_dict = {}
            for key in dementia_keys:
                key_location_list = [location for location in meaningful_location_list if location.dementia_key == key]
                for location in key_location_list:
                    geo = kakao.geo_coord2address(location.longitude, location.latitude)
                    if not geo['documents'][0]['road_address'] == None:
                        xy2addr = geo['documents'][0]['road_address']['address_name'] + " " + geo['documents'][0]['road_address']['building_name']
                    
                    else:
                        xy2addr = geo['documents'][0]['address']['address_name']
                
                    location.address = xy2addr

                    if xy2addr not in address_list:
                        address_list.append(xy2addr)
                        new_key = rng.generate_unique_random_number(100000, 999999)
                        key_dict[xy2addr] = str(new_key)
                        location.key = str(new_key)
                        police = kakao.search_keyword("경찰서", x = location.longitude, y = location.latitude, sort = 'distance')

                        police_list = []
                        if police['meta']['total_count'] == 0:
                            print(f"[INFO] No police station found near {xy2addr}")
                        else:
                            for pol in police['documents']:
                                if not pol['road_address_name'] == None:
                                    poladdr = pol['address_name'] + " " + pol['place_name']

                                else:
                                    poladdr = pol['road_address_name'] + " " + pol['place_name']

                                if not pol['phone'] == '':
                                    new_police = models.police_info(
                                        policeName =  pol['place_name'],
                                        policeAddress = poladdr,
                                        policePhoneNumber = pol['phone'],
                                        distance = pol['distance'],
                                        latitude = pol['y'],
                                        longitude = pol['x'],
                                        key = str(new_key)
                                    )
                                    police_list.append(new_police)
                                else:
                                    pass
                    
                        session.add_all(police_list)
                    else:
                        location.key = key_dict[xy2addr]

            session.commit()
            print(f"[INFO] Geocoding completed")

        except Exception as e:
            print(f"[ERROR] Geocoding failed: {e}")
            raise e
    
        finally:
            session.close()

    async def analyze_location_data(self, session = Depends(Database().get_session)):
        seoul_timezone = timezone('Asia/Seoul')
        now = datetime.now(seoul_timezone)

        # 어제의 날짜 계산하고 포맷팅
        yesterday = now - timedelta(days=1)
        yesterday_str = yesterday.strftime('%Y-%m-%d')

        print(f"[INFO] Start analyzing location data at {yesterday_str}")

        try:
            location_list = session.query(models.location_info).filter(models.location_info.date == yesterday_str).all()

            print(f"[INFO] {len(location_list)} location data found")

            errfile = f'error_{yesterday_str}.txt'
            if location_list:
                dementia_keys = set([location.dementia_key for location in location_list])
                for key in dementia_keys:
                    key_location_list = [location for location in location_list if location.dementia_key == key]

                    if len(key_location_list) <= 100:
                        with open(errfile, 'a') as file:
                            file.write(f'{key} dementia location data not enough\n')
                        continue

                    filename = f'location_data_for_dementia_key_{key}_{yesterday_str}.txt'
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

            #session.commit()
            print(f"[INFO] Location data analysis completed at {yesterday_str}")

        finally:
            session.close()