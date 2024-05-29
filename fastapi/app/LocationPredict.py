import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf
import json
import math
import folium
import tensorflow.keras.backend as K
from tensorflow import keras
from scipy.spatial import distance
from sklearn.metrics.pairwise import haversine_distances
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import LSTM
from tensorflow.keras.layers import Dropout
from tensorflow.keras.layers import Activation
from tensorflow.keras.models import Sequential
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.losses import MSE
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.callbacks import ModelCheckpoint
from tensorflow.keras.callbacks import ReduceLROnPlateau
from tensorflow.keras.utils import to_categorical
from pyclustering.cluster.gmeans import gmeans
from collections import Counter

import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

class ForecastLSTMClassification:

    def __init__(self, 
                 class_num: int,
                 random_seed: int = 1234):
        self.random_seed = random_seed
        self.class_num = class_num

    def reshape_dataset(self, 
                        df: pd.DataFrame) -> np.array:
        dataset = df.values.reshape(df.shape)
        return dataset
    
    def split_sequences(self, 
                        dataset: np.array, 
                        seq_len: int, 
                        steps: int, 
                        single_output: bool) -> tuple:
    
        # feature와 y 각각 sequential dataset을 반환할 리스트
        X, y = list(), list()
        # sequence length와 step에 따라 생성
        for i, _ in enumerate(dataset):
            idx_in = i + seq_len
            idx_out = idx_in + steps
            if idx_out > len(dataset):
                break
            seq_x = dataset[i:idx_in, :-1]
            if single_output:
                seq_y = dataset[idx_out -1 : idx_out, -1]
            else:
                seq_y = dataset[idx_in:idx_out, -1]

            X.append(seq_x)
            y.append(seq_y)
        X = np.array(X)
        y = np.array(y)
        print(X.shape)
        print(y.shape)
        return X, y
    
    def split_sequences(self, 
                        dataset: np.array, 
                        seq_len: int, 
                        steps: int, 
                        single_output: bool) -> tuple:
        X, y = list(), list()
        for i in range(len(dataset) - seq_len - steps + 1):
            idx_in = i + seq_len
            idx_out = idx_in + steps  # 모델의 출력 길이에 맞춘 고정값 설정

            if idx_out > len(dataset):
                break
        
            seq_x = dataset[i:idx_in, :-1]
            seq_y = dataset[idx_in:idx_out, -1]

            X.append(seq_x)
            y.append(seq_y)
        
        X = np.array(X)
        y = np.array(y)
        print(X.shape)
        print(y.shape)
        return X, y
    
    def split_train_valid_dataset(self, 
                                  df: pd.DataFrame,
                                  seq_len: int,
                                  steps: int,
                                  single_output: bool,
                                  validation_split: float = 0.2,
                                  verbose: bool = True) -> tuple:
        # df -> np.array
        dataset = self.reshape_dataset(df=df)

        # feature, y를 sequential dataset으로 분리
        X, y = self.split_sequences(
            dataset=dataset,
            seq_len=seq_len,
            steps=steps,
            single_output=single_output
        )

        # X, y에서 validation dataset 분리
        dataset_size = len(X)
        train_size = int(dataset_size * (1-validation_split))
        X_train, y_train = X[:train_size, :], y[:train_size, :]
        X_val, y_val = X[train_size:, :], y[train_size:, :]

        # 원핫인코딩
        if not single_output and self.class_num > 1:
            y_train = to_categorical(y_train, num_classes=self.class_num)
            y_val = to_categorical(y_val, num_classes=self.class_num)

        if verbose:
            print(f" >>> X_train: {X_train.shape}")
            print(f" >>> y_train: {y_train.shape}")
            print(f" >>> X_val: {X_val.shape}")
            print(f" >>> y_val: {y_val.shape}")
        return X_train, y_train, X_val, y_val
    
    def build_and_compile_lstm_model(self,
                                     seq_len: int,
                                     n_features: int,
                                     lstm_units: list,
                                     learning_rate: float,
                                     dropout: float,
                                     steps: int,
                                     metrics: list,
                                     single_output: bool,
                                     last_lstm_return_sequences: bool = False,
                                     dense_units: list = None,
                                     activation: str = None):
        tf.random.set_seed(self.random_seed)

        model = Sequential()

        # LSTM 레이어 추가
        model.add(LSTM(64, input_shape=(seq_len, n_features), return_sequences=True))

        # Dense 레이어 추가하여 출력 형태를 변경
        model.add(Dense(self.class_num))  # 출력 레이어의 뉴런 개수를 2로 설정
    
        optimizer = Adam(learning_rate=learning_rate)
        model.compile(optimizer=optimizer, loss='categorical_crossentropy', metrics=metrics)
        return model
    
    def fit_lstm(self,
                df: pd.DataFrame,
                steps: int,
                lstm_units: list,
                activation: str,
                dropout: float = 0,
                seq_len: int = 10,
                single_output: bool = False,
                epochs: int = 50,
                batch_size: int = None,
                steps_per_epoch: int = None,
                learning_rate: float = 0.001,
                patience: int = 10,
                validation_split: float = 0.2,
                last_lstm_return_sequences: bool = False,
                dense_units: list = None,
                metrics: list = ["mse"],
                check_point_path: str = None,
                verbose: bool = False,
                plot: bool = True):
    
        np.random.seed(self.random_seed)
        tf.random.set_seed(self.random_seed)
        (
            self.X_train,
            self.y_train,
            self.X_val,
            self.y_val
        ) = self.split_train_valid_dataset(
            df=df,
            seq_len=seq_len,
            steps=steps,
            validation_split=validation_split,
            single_output=single_output,
            verbose=verbose
        )

        n_features = df.shape[1] - 1
        self.model = self.build_and_compile_lstm_model(
            seq_len=seq_len,
            n_features=n_features,
            lstm_units=lstm_units,
            activation=activation,
            learning_rate=learning_rate,
            dropout=dropout,
            steps=steps,
            last_lstm_return_sequences=last_lstm_return_sequences,
            dense_units=dense_units,
            metrics=metrics,
            single_output=single_output,
        )

        # best model save
        if check_point_path is not None:
            checkpoint_path = f"checkpoint/lstm_{check_point_path}.h5"
            checkpoint = ModelCheckpoint(
                filepath=checkpoint_path,
                save_weights_only=False,
                save_best_only=True,
                monitor="val_loss",
                verbose=verbose,
            )
            rlr = ReduceLROnPlateau(
                monitor="val_loss", factor=0.5, patience=patience, verbose=verbose
            )
            callbacks = [checkpoint, EarlyStopping(patience=patience), rlr]
        else:
            rlr = ReduceLROnPlateau(
                monitor="val_loss", factor=0.5, patience=patience, verbose=verbose
            )
            callbacks = [EarlyStopping(patience=patience), rlr]

        self.history = self.model.fit(
            self.X_train,
            self.y_train,
            batch_size=batch_size,
            steps_per_epoch=steps_per_epoch,
            validation_data=(self.X_val, self.y_val),
            epochs=epochs,
            verbose=verbose,
            callbacks=callbacks,
            shuffle=False,
        )

        if check_point_path is not None: 
            self.model.load_weights(f"checkpoint/lstm_{check_point_path}.h5")

        return self.model
    
    def forecast_validation_dataset(self) -> pd.DataFrame:
        y_pred_list, y_val_list = list(), list()

        for x_val, y_val in zip(self.X_val, self.y_val):
            x_val = np.expand_dims(
                x_val, axis=0
            ) # (seq_len, n_features) -> (1, seq_len, n_features)
            y_pred = self.model.predict(x_val)[0]
            y_pred_list.extend(y_pred.tolist())
            y_val_list.extend(y_val.tolist())
        return pd.DataFrame({"y": y_val_list, "yhat": y_pred_list})
    
    def combine_windows(self, predicted_values, original_length, seq_len):
        # 초기화
        prediction = np.zeros(original_length)
        counts = np.zeros(original_length)
    
        num_predictions = predicted_values.shape[0]

        for i in range(num_predictions):
            start_index = i
            end_index = i + seq_len
            prediction[start_index:end_index] += predicted_values[i]
            counts[start_index:end_index] += 1

        # 중첩된 부분을 평균화
        counts[counts == 0] = 1  # division by zero 방지
        prediction /= counts

        return prediction

    def pred(self,
            df: pd.DataFrame,
            steps: int,
            num_classes: int,  # 클래스 수 추가
            seq_len: int = 10,
            single_output: bool = False):

        np.random.seed(self.random_seed)
        tf.random.set_seed(self.random_seed)
    
        # 데이터셋 변환
        dataset = self.reshape_dataset(df=df)

        # feature, y를 sequential dataset으로 분리
        X_test, y_test = self.split_sequences(
            dataset=dataset,
            seq_len=seq_len,
            steps=steps,
            single_output=single_output
        )

        # 원-핫 인코딩 처리
        y_test_encoded = to_categorical(y_test, num_classes=num_classes)

        # 예측 수행
        y_pred = self.model.predict(X_test)
        y_pred = np.array(y_pred)

        # 성능 평가
        loss, accuracy = self.model.evaluate(X_test, y_test_encoded)

        print(f"y_test: {y_test}")
        print(f"loss: {loss}")
        print(f"acc: {accuracy}")

        y_pred = np.argmax(y_pred, axis=-1)

        y_pred = self.combine_windows(y_pred, len(df), seq_len)

        return y_pred

# 전처리
class Preprocessing:
    def __init__(self, csv) -> None:
        self.df = pd.DataFrame()
        self.fileReader(csv)

    def convert_day_to_number(self, day):
        weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        return weekdays.index(day)
    
    def custom_parser(self, date_string):
        return pd.to_datetime(date_string, format='%Y-%m-%d')  # 날짜 형식에 맞게 지정
    
    def fileReader(self, csv_path):
        #data = pd.read_csv(csv_path, parse_dates=['date'], date_parser=self.custom_parser)
        data = csv_path
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

        print(self.df)

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
    
    def get_meaningful_df(self):
        return self.gmeans_func()
    
if __name__ =='__main__':
    
    # 전처리
    csv_path = r"C:\Users\sk002\Downloads\138362.csv"
    pr = Preprocessing(csv_path)
    df = pr.run_analysis()

    test_idx = int(len(df) * 0.8)
    df_train = df.iloc[:test_idx]
    df_test = df.iloc[test_idx:]

    # 파라미터 설정
    seq_len = 5  # 150개의 데이터를 feature로 사용
    steps = 5  # 향후 150개 뒤의 y를 예측
    single_output = False
    metrics = ["accuracy"]  # 모델 성능 지표
    lstm_params = {
        "seq_len": seq_len,
        "epochs": 30,  # epochs 반복 횟수
        "patience": 30,  # early stopping 조건
        "steps_per_epoch": 5,  # 1 epochs 시 dataset을 5개로 분할하여 학습
        "learning_rate": 0.03,
        "lstm_units": [64, 32],  # Dense Layer: 2, Unit: (64, 32)
        "activation": "softmax",
        "dropout": 0,
        "validation_split": 0.3,  # 검증 데이터셋 30%
    }
    fl = ForecastLSTMClassification(class_num=len(df['y'].unique()))
    model = fl.fit_lstm(
        df=df_train,
        steps=steps,
        single_output=single_output,
        verbose=True,
        metrics=metrics,
        **lstm_params,
    )

    y_pred = fl.pred(df=df_test, 
                    steps=steps, 
                    num_classes=len(df['y'].unique()),
                    seq_len=seq_len, 
                    single_output=single_output)

    print(y_pred)