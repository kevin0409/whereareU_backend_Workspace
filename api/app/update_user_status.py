from sklearn.tree import DecisionTreeClassifier
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

    # 전처리 함수
    def preprocessing(self, data):
        # 클라이언트에서 넘어온 데이터를 입력으로 사용
        # ,로 구분된 한 줄 짜리 데이터
        data = pd.read_csv(StringIO(data), header=None, names=['시간', 'x1', 'y1', 'z1', 'x2', 'y2', 'z2', 'x3', 'y3', 'z3'])
        data = data.drop(['시간'], axis=1)

        return data