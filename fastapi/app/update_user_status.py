import json
import pandas as pd
import pickle
from .bodymodel import ReceiveLocationRequest

class UpdateUserStatus:
    def __init__(self):

        model_filename = 'app/random_forest_model_mk2.pkl'
        with open(model_filename, 'rb') as model_file:
            self.model = pickle.load(model_file)

    def predict(self, accel, gyro, direction):
        # 전처리 함수 호출
        preprocessed_data = self.preprocessing(accel, gyro, direction)
        
        # 모델 예측
        prediction = self.model.predict(preprocessed_data)
        return prediction

    def preprocessing(self, accel, gyro, direction):

        processed_data = [{
            'x1': accel[0],
            'y1': accel[1],
            'z1': accel[2],
            'x2': gyro[0],
            'y2': gyro[1],
            'z2': gyro[2],
            'x3': direction[0],
            'y3': direction[1],
            'z3': direction[2],
        }]

        df = pd.DataFrame(processed_data)

        return df
