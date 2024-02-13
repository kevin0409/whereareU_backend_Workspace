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
        
        #column_names = ['x1', 'y1', 'z1', 'x2', 'y2', 'z2', 'x3', 'y3', 'z3']
        #df = pd.DataFrame(data, columns=column_names)

        #df['x1'] = data.get('accelerometer_x')
        #df['y1'] = data.get('accelerometer_y')
        #df['z1'] = data.get('accelerometer_z')
        #df['x2'] = data.get('gyroscope_x')
        #df['y2'] = data.get('gyroscope_y')
        #df['z2'] = data.get('gyroscope_z')
        #df['x3'] = data.get('magnetometer_x')
        #df['y3'] = data.get('magnetometer_y')
        #df['z3'] = data.get('magnetometer_z')

        json_data = json.loads(data)

        processed_data = [{
            'x1': json_data.get('accelerationsensor_x'),
            'y1': json_data.get('accelerationsensor_y'),
            'z1': json_data.get('accelerationsensor_z'),
            'x2': json_data.get('gyrosensor_x'),
            'y2': json_data.get('gyrosensor_y'),
            'z2': json_data.get('gyrosensor_z'),
            'x3': json_data.get('directionsensor_x'),
            'y3': json_data.get('directionsensor_y'),
            'z3': json_data.get('directionsensor_z'),
        }]

        df = pd.DataFrame(processed_data)

        return df
