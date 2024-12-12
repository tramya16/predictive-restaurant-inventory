import pandas as pd
from typing import Union
import numpy as np

from settings import HIST_DATA_PATH
from training_and_diagnostics.model_builder import ModelBuilder


class OrderSimulator1:
    def __init__(self, path: Union[str, None] = None):
        path = HIST_DATA_PATH if path is None else path
        self.original_df = pd.read_csv(path)
        model_builder = ModelBuilder(data=self.original_df)
        model_builder.set_time_series_index(col_name="date", frequency="D", method="ffill")
        self.original_df = model_builder.data
        self.day_of_week_data = {i: self.original_df[self.original_df["day_of_week"] == i]["orders"] for i in range(7)}

    def simulate_orders(self, start_dt: str, end_dt: str):
        forecast_dates = pd.date_range(start=start_dt, end=end_dt, freq='D')

        simulated_orders = []
        for date in forecast_dates:
            day_of_week = date.dayofweek
            # Randomly select an order from the historical data for this day of the week
            historical_orders = self.day_of_week_data[day_of_week]
            simulated_order = np.random.choice(historical_orders.values)
            simulated_orders.append(simulated_order)

        # Create the simulated DataFrame
        simulated_data = pd.DataFrame({'orders': simulated_orders}, index=forecast_dates)
        return simulated_data


if __name__ == "__main__":
    order_simulator = OrderSimulator()
    simulated = order_simulator.simulate_orders(start_dt="2024-01-01", end_dt="2024-01-07")
    print(simulated)
