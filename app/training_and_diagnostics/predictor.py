from typing import Union
import os
import joblib
import pandas as pd
from sklearn.metrics import mean_squared_error
from skforecast.sarimax._sarimax import Sarimax
from statsmodels.tsa.holtwinters.results import HoltWintersResultsWrapper


class Muaddib:

    def __init__(self, model_name: str, base_path: Union[str, None] = None):
        base_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)) \
            if base_path is None else base_path
        model_path = os.path.join(base_path, "models", f"{model_name}.pkl")
        self.model = joblib.load(model_path)

    def predict(self, period: int):
        if isinstance(self.model, Sarimax):
            return self.model.predict(steps=period)['pred'].astype(int)
        elif isinstance(self.model, HoltWintersResultsWrapper):
            return self.model.forecast(steps=period).astype(int)
        else:
            raise Exception(f"Unknown model type: {type(self.model)}")

    @staticmethod
    def calculate_error(predictions: Union[pd.Series, list], actual_values: Union[pd.Series, list]):
        return mean_squared_error(actual_values, predictions)
