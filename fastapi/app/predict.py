import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf
import json
import math
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
from LocationAnalyzer import LocationAnalyzer

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

    
if __name__ =='__main__':
    
    la = LocationAnalyzer(r"C:\Users\sk002\Downloads\138362.csv")
    df, meaningful_df = la.run_analysis()

    test_idx = int(len(df) * 0.8)
    df_train = df.iloc[:test_idx]
    df_test = df.iloc[test_idx:]

    # 파라미터 설정
    seq_len = 15  # 150개의 데이터를 feature로 사용
    steps = 15  # 향후 150개 뒤의 y를 예측
    single_output = True
    metrics = ["accuracy"]  # 모델 성능 지표
    lstm_params = {
        "seq_len": seq_len,
        "epochs": 10,  # epochs 반복 횟수
        "patience": 30,  # early stopping 조건
        "steps_per_epoch": 5,  # 1 epochs 시 dataset을 5개로 분할하여 학습
        "learning_rate": 0.03,
        "lstm_units": [64, 32],  # Dense Layer: 2, Unit: (64, 32)
        "activation": "softmax",
        "dropout": 0,
        "validation_split": 0.3,  # 검증 데이터셋 30%
    }
    fl = ForecastLSTMClassification(class_num=len(df['y'].unique()))
    fl.fit_lstm(
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