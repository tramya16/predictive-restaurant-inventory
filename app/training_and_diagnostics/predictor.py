from typing import Union
import os
import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error
from statsmodels.tsa.holtwinters.results import HoltWintersResults
from statsmodels.tsa.statespace.sarimax import SARIMAXResultsWrapper


class Muaddib:

    def __init__(self, model_name: str, base_path: Union[str, None] = None):
        base_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)) \
            if base_path is None else base_path
        model_path = os.path.join(base_path, "models", f"{model_name}.pkl")
        self.model = joblib.load(model_path)

    def predict(self, start_dt: str, end_dt: str):
        if isinstance(self.model, SARIMAXResultsWrapper):
            return self.model.predict(start=start_dt, end=end_dt).astype(int)
        elif isinstance(self.model, HoltWintersResults):
            return self.model.predict(start=start_dt, end=end_dt).astype(int)
        else:
            raise Exception(f"Unknown model type: {type(self.model)}")

    @staticmethod
    def calculate_rmse(predictions: Union[pd.Series, list], actual_values: Union[pd.Series, list]):
        return np.sqrt(mean_squared_error(actual_values, predictions))

    def calculate_accuracy(self, predictions: Union[pd.Series, list], actual_values: Union[pd.Series, list]):
        rmse = self.calculate_rmse(predictions, actual_values)
        return (1 - (rmse/np.mean(actual_values))) * 100

# if __name__ == "__main__":
#     from app.simultation.order_simulator import OrderSimulator
#
#     oracle = Muaddib("sk_sarima")
#     simulator = OrderSimulator()
#     predicted = oracle.predict("2024-01-01", "2024-01-07")
#     rmse = oracle.calculate_rmse(predicted, simulator.simulate_orders("2024-01-01", "2024-01-07"))
#     mape = oracle.calculate_mape(predicted, simulator.simulate_orders("2024-01-01", "2024-01-07"))
#     print(predicted)
#     print((1 - (rmse / np.mean(simulator.simulate_orders("2024-01-01", "2024-01-07")))) * 100)
#     print(100 - mape)
