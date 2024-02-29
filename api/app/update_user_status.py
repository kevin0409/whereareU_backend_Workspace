from sklearn.tree import DecisionTreeClassifier
import json
import pandas as pd
from io import StringIO
import pickle

class UpdateUserStatus:
    def __init__(self):

        model_filename = 'app/random_forest_model.pkl'
        with open(model_filename, 'rb') as model_file:
            self.model = pickle.load(model_file)

    def predict(self, data):
        # 전처리 함수 호출
        preprocessed_data = self.preprocessing(data)
        
        # 모델 예측
        prediction = self.model.predict(preprocessed_data)
        return prediction

    def preprocessing(self, data):

        json_data = json.loads(data)

        accel = json_data.get('accelerationsensor')
        gyro = json_data.get('gyrosensor')
        direction = json_data.get('directionsensor')

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
