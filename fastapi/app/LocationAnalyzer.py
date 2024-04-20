from pyclustering.cluster.gmeans import gmeans
from collections import Counter
import numpy as np
import pandas as pd
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning) # FutureWarning 제거

pd.set_option('mode.chained_assignment', None)

class LocationAnalyzer:
    def __init__(self, filename):
        self.df = self.fileReader(filename)

    # 파일 읽기
    # 데이터 예시 (39.984702,116.318417,0,492,39744.1201851852,2008-10-23,02:53:04)
    # (위도, 경도, 0, 고도, 1899년 이후 경과한 시간, 날짜, 시간)
    def fileReader(self, filename):

        latitude = []   # 위도
        longitude = []  # 경도
        date = []       # 날짜
        time = []       # 시간

        with open(filename, 'r') as file:
            data = file.read()

        # 데이터에 불필요한 부분 제거
        # 추후 데이터 형식에 따라 수정 필요 *
        data = data.split('\n')[:-1]
        # data = data.split('\n')[6:-1]
        for i in range(len(data)):
            line = data[i].split(',')
            latitude.append(line[0])    # 위도
            longitude.append(line[1])   # 경도
            date.append(line[2])        # 날짜
            time.append(line[3])        # 시간
            # date.append(line[5])
            # time.append(line[6])
        df = pd.DataFrame({"latitude":latitude, "longitude":longitude, "date":date, "time":time})

    
        df['latitude'] = df['latitude'].astype(float)
        df['longitude'] = df['longitude'].astype(float)
        df['datetime'] = pd.to_datetime(df['date'] + ' ' + df['time'], format='%Y-%m-%d %H:%M:%S')
        df['datetime'] = df['datetime'].dt.floor('T')
        # 시간대와 요일 추가
        # 시간대 형식 : f00t04 f20t24
        # 4시간 단위로 분리
        df['hour_block'] = ((df['datetime'].dt.hour) // 4 * 4).astype(str).str.zfill(2) + ((df['datetime'].dt.hour + 4) // 4 * 4).astype(str).str.zfill(2)
        df['day_of_week'] = df['datetime'].dt.day_name()
        df = df.drop(['date', 'time'], axis=1)
        df = df.drop_duplicates(['datetime'], ignore_index=True)

        return df

    # 의미장소 추출
    def gmeansFit(self, df):
        # 두 열을 선택하고 넘파이 배열로 변환
        selectedColumns = ['latitude', 'longitude']
        resultList = df[selectedColumns].values.tolist()    # 리스트로 변환
    
        gmeansInstance = gmeans(resultList).process()       # 클러스터링

        centers = gmeansInstance.get_centers()              # 클러스터의 중심 (의미장소)
        clusters = gmeansInstance.get_clusters()            # 분류된 클러스터


        return clusters, centers
    
    # 호출 함수
    def gmeansFunc(self):


        clusters, centers = self.gmeansFit(self.df)

        data_df = pd.DataFrame({"clusters":clusters, "centers":centers})
        
        for k in range(len(data_df.clusters)):
            if (len(data_df.clusters[k]) < 10):
                data_df.drop(index=k, inplace=True)
        data_df = data_df.sort_index(axis=1)
        data_df = data_df.reset_index(drop=True)
    
        self.df['clusterNo'] = -1
        for i in range(len(data_df)):
            for j in range(len(data_df['clusters'].iloc[i])):
                k = data_df['clusters'].iloc[i][j]
                self.df['clusterNo'].iloc[k] = i

        self.df = self.df[self.df['clusterNo'] != -1]


        data_df['hour_block'] = 0
        data_df['day_of_week'] = 0
        for i in range(max(self.df['clusterNo'])+1):
        
            counter = Counter(self.df[self.df['clusterNo'] == i]['hour_block'])
            most_hour_value = counter.most_common(1)[0][0]

            counter = Counter(self.df[self.df['clusterNo'] == i]['day_of_week'])
            most_day_value = counter.most_common(1)[0][0]

            data_df['hour_block'].iloc[i] = most_hour_value
            data_df['day_of_week'].iloc[i] = most_day_value

        data_list = data_df.values.tolist()
        return data_list
