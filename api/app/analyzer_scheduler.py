from .models import db, location_info, meaningful_location_info
from .LocationAnalyzer import LocationAnalyzer
from datetime import datetime
from flask import Blueprint

index = 1 # for debugging

analye_schedule = Blueprint('analye_schedule', __name__)

class AnalyzerScheduler:
    def __init__(self):
        pass
    
    @analye_schedule.route('/analyze_meaningful_location')
    def analyze_meaningful_location(self):
        try:
            today = datetime.now().date()
            #날짜를 문자열로 변환
            today = today.strftime('%Y-%m-%d')
            print('[system] {} dementia meaningful location data analysis started'.format(today))

            # 해당일에 저장된 위치 정보를 모두 가져옴
            location_list = location_info.query.filter(location_info.date == today).order_by(location_info.dementia_key.desc(), location_info.time.desc()).first

            print('[system] {}'.format(index)) # for debugging
            index += 1 # for debugging

            errfile = f'error_{today}.txt'
            if location_list:
                # dementia_key 별로 위치 정보를 분류하여 파일 작성 및 분석 수행
                dementia_keys = set([location.dementia_key for location in location_list])
                for key in dementia_keys:
                    key_location_list = [location for location in location_list if location.dementia_key == key]

                    # 만약 key_location_list의 길이가 100보다 작다면 넘어감
                    if len(key_location_list) <= 100:
                        with open(errfile, 'a') as file:
                            file.write(f'{key} dementia location data not enough\n')
                        continue

                    # 파일 작성
                    filename = f'location_data_for_dementia_key_{key}_{today}.txt'
                    with open(filename, 'w') as file:
                        for location in key_location_list:
                            file.write(f'{location.latitude},{location.longitude},{location.date},{location.time}\n')

                    # 분석 수행
                    LA = LocationAnalyzer(filename)
                    predict_meaningful_location_data = LA.gmeansFunc()

                    # 의미 있는 위치 정보 저장
                    new_meaningful_location = meaningful_location_info(
                        dementia_key=key,
                        latitude=predict_meaningful_location_data[0],
                        longitude=predict_meaningful_location_data[1]
                    )
                    db.session.add(new_meaningful_location)
                    db.session.commit()
                    print(f'[system] {key} dementia meaningful location data saved successfully')
            else:
                # 예외 처리 코드
                print("location_list가 비어 있습니다.")

            print('[system] {} dementia meaningful location data analysis finished'.format(today))
        
        except Exception as e:
            return e