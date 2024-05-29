import numpy as np
import pandas as pd
import json
import math
from scipy.spatial import distance
from sklearn.metrics.pairwise import haversine_distances
from pyclustering.cluster.gmeans import gmeans
from collections import Counter
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning) # FutureWarning 제거
pd.set_option('mode.chained_assignment', None)

class LocationAnalyzer:
    def __init__(self, csv_path) -> None:
        self.df = pd.DataFrame()
        self.fileReader(csv_path)

    def convert_day_to_number(self, day):
        weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        return weekdays.index(day)
    
    def custom_parser(self, date_string):
        return pd.to_datetime(date_string, format='%Y-%m-%d')  # 날짜 형식에 맞게 지정
    
    def fileReader(self, csv_path):
        data = pd.read_csv(csv_path, parse_dates=['date'], date_parser=self.custom_parser)
        index = list(range(len(data)))
        data.index = index
        self.df = data[['date', 'time', 'latitude', 'longitude', 'user_status']]

        self.df['date'] = pd.to_datetime(self.df['date'], format='%Y-%m-%d')
        self.df['time'] = pd.to_datetime(self.df['time'], format='%H:%M:%S')

        self.df['hour_block'] = 'f' + ((self.df['time'].dt.hour) // 4 * 4).astype(str).str.zfill(2) + 't' + ((self.df['time'].dt.hour + 4) // 4 * 4).astype(str).str.zfill(2)
        self.df['day_of_week'] = self.df['date'].dt.day_name()

        new_data = []
        for item in self.df['hour_block']:
            num = int(item[1:-3])
            new_data.append(num)

        self.df['hour_block'] = new_data
        self.df['day_of_week'] = self.df['day_of_week'].apply(self.convert_day_to_number)
        self.df = self.df.drop(['date', 'time'], axis=1)

    def gmeans_fit(self):
        # 두 열을 선택하고 넘파이 배열로 변환
        selected_columns = ['latitude', 'longitude']
        result_list = self.df[selected_columns].values.tolist()

        gmeans_instance = gmeans(result_list).process()

        centers = gmeans_instance.get_centers()
        clusters = gmeans_instance.get_clusters()
        
        return clusters, centers

    def gmeans_func(self):
        clusters, centers = self.gmeans_fit()

        data_df = pd.DataFrame({"clusters": clusters, "centers": centers})

        for k in range(len(data_df.clusters)):
            if len(data_df.clusters[k]) < 10:
                data_df.drop(index=k, inplace=True)
        data_df = data_df.sort_index(axis=1)
        data_df = data_df.reset_index(drop=True)
        
        self.df['cluster_no'] = -1
        for i in range(len(data_df)):
            for j in range(len(data_df['clusters'].iloc[i])):
                k = data_df['clusters'].iloc[i][j]
                self.df['cluster_no'].iloc[k] = i
        
        data_df['hour_block'] = 0
        data_df['day_of_week'] = 0
        for i in range(max(self.df['cluster_no']) + 1):
            counter = Counter(self.df[self.df['cluster_no'] == i]['hour_block'])
            most_hour_value = counter.most_common(1)[0][0]

            counter = Counter(self.df[self.df['cluster_no'] == i]['day_of_week'])
            most_day_value = counter.most_common(1)[0][0]

            data_df['hour_block'].iloc[i] = most_hour_value
            data_df['day_of_week'].iloc[i] = most_day_value

        data_df[['latitude', 'longitude']] = data_df['centers'].apply(lambda x: pd.Series(x))
        data_df.drop('centers', axis=1, inplace=True)
        data_df = data_df[['latitude', 'longitude', 'clusters', 'hour_block', 'day_of_week']]

        meaningful_df = data_df[['latitude', 'longitude', 'hour_block', 'day_of_week']]
        meaningful_df[['latitude', 'longitude']] = meaningful_df[['latitude', 'longitude']].round(4)
        meaningful_df = meaningful_df.drop_duplicates(['latitude', 'longitude'], keep='first', ignore_index=True)

        return meaningful_df
    
    def haversine(self, lat1, lon1, lat2, lon2):
        R = 6371000.0  # 지구 반지름 (미터)
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c
        return distance

    def calculate_bearing(self, lat1, lon1, lat2, lon2):
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        dlon = lon2 - lon1
        x = math.sin(dlon) * math.cos(lat2)
        y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
        initial_bearing = math.atan2(x, y)
        initial_bearing = math.degrees(initial_bearing)
        compass_bearing = (initial_bearing + 360) % 360
        return compass_bearing
    
    def add_movement_features(self):
        self.df['next_lat'] = self.df['latitude'].shift(1)
        self.df['next_lon'] = self.df['longitude'].shift(1)

        self.df['distance'] = self.df.apply(lambda row: self.haversine(row['latitude'], row['longitude'], row['next_lat'], row['next_lon']) if pd.notna(row['next_lat']) else None, axis=1)
        self.df['bearing'] = self.df.apply(lambda row: self.calculate_bearing(row['latitude'], row['longitude'], row['next_lat'], row['next_lon']) if pd.notna(row['next_lat']) else None, axis=1)

        self.df = self.df.drop(['next_lat', 'next_lon'], axis=1)
        self.df = self.df.fillna(0)

    def map_to_meaningful_places(self, meaningful_df):
        y, m_hour_block, m_day_of_week = [], [], []
        for i in range(len(self.df)):
            current_location = (self.df['latitude'].iloc[i], self.df['longitude'].iloc[i])
            min_distance = float('inf')

            for j in range(len(meaningful_df)):
                place_location = (meaningful_df['latitude'].iloc[j], meaningful_df['longitude'].iloc[j])
                dist = distance.euclidean(current_location, place_location)
                if dist < min_distance:
                    min_distance = dist
                    min_distance_index = j

            y.append(min_distance_index)
            m_hour_block.append(meaningful_df['hour_block'].iloc[min_distance_index])
            m_day_of_week.append(meaningful_df['day_of_week'].iloc[min_distance_index])

        self.df['m_hour_block'] = m_hour_block
        self.df['m_day_of_week'] = m_day_of_week
        self.df['y'] = y

    def calculate_additional_features(self):
        self.df['speed'] = self.df['distance'] / (self.df['hour_block'] / 4 + 1)
        self.df['lat_rate_change'] = self.df['latitude'].diff() / self.df['hour_block'].diff().replace(0, 1)
        self.df['lon_rate_change'] = self.df['longitude'].diff() / self.df['hour_block'].diff().replace(0, 1)

        daily_variability = self.df.groupby('day_of_week')[['latitude', 'longitude']].std().add_suffix('_daily_var')
        hourly_variability = self.df.groupby('hour_block')[['latitude', 'longitude']].std().add_suffix('_hourly_var')
        self.df = self.df.join(daily_variability, on='day_of_week')
        self.df = self.df.join(hourly_variability, on='hour_block')

        self.df['max_travel_range'] = self.df.groupby('hour_block')['distance'].transform('max')

        self.df['movement_direction'] = self.df['bearing'].apply(lambda x: 0 if x < 180 else 1)
        self.df = self.df.fillna(0)

    
    def run_analysis(self):
        meaningful_df = self.gmeans_func()
        self.add_movement_features()
        self.map_to_meaningful_places(meaningful_df)
        self.calculate_additional_features()
        
        y = self.df['y']
        self.df = self.df.drop(['y'], axis=1)
        self.df['y'] = y

        return self.df, meaningful_df
    


if __name__ == '__main__':

    # csv 파일 가져오기
    # 필요한 데이터 'date', 'time', 'latitude', 'longitude', 'user_status' : 날짜 시간 위도 경도 이동상태
    csv_path = r"C:\Users\sk002\Downloads\138362.csv"
    la = LocationAnalyzer(csv_path)

    df, meaningful_df = la.run_analysis()
    
    print(df)
    print(meaningful_df)