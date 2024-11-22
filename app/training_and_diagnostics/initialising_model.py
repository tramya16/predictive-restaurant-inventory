from app.training_and_diagnostics.model_builder import ModelBuilder
import pandas as pd
from app.settings import HIST_DATA_PATH
import matplotlib.pyplot as plt
import os


def main():
    original_df = pd.read_csv(HIST_DATA_PATH)
    model_builder = ModelBuilder(data=original_df)
    model_builder.set_time_series_index(col_name="date", frequency="D", method="ffill")
    df = model_builder.data[["orders"]]
    model_builder.set_training_testing_split(training_end_dt="2023-03-31", testing_start_dt="2023-04-01")
    plot_df = pd.DataFrame()
    plot_df["orders"] = model_builder.testing_data["orders"]
    print("original dataframe: ")
    print(df)

    # Best model: ARIMA(0, 0, 0)(3, 0, 0)[7]
    model_builder.build_sarima_model(col_name="orders", order=(0, 0, 0), seasonal_order=(3, 0, 0, 7))
    test_result = model_builder.test_model(col_name="orders")
    plot_df["auto_sarima_values"] = test_result[0]
    plot_df["auto_sarima_rmse"] = test_result[1]

    # Best Parameters: (2, 0, 1, 3, 0, 3, 7)
    model_builder.build_sarima_model(col_name="orders", order=(2, 0, 1), seasonal_order=(3, 0, 3, 7))
    test_result = model_builder.test_model(col_name="orders")
    plot_df["sk_sarima_values"] = test_result[0]
    plot_df["sk_sarima_rmse"] = test_result[1]

    model_builder.build_holt_winters_model(col_name="orders", seasonality="add", seasonal_periods=7, trend="add")
    test_result = model_builder.test_model(col_name="orders")
    plot_df["holt_winters_values"] = test_result[0]
    plot_df["holt_winters_rmse"] = test_result[1]
    print(plot_df)

    plot_df[:100].plot(y=["orders", "sk_sarima_values", "holt_winters_values", "auto_sarima_values"], figsize=(16, 9),
                       legend=True)
    plt.grid()
    plt.show()

    parent_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))
    path = os.path.join(parent_dir, "models")

    model_builder.train_complete_holt_winters_model(col_name="orders", seasonality="add", seasonal_periods=7,
                                                    trend="add")
    model_builder.save_model(path=path, filename="holt_winters")

    order = (0, 0, 0)
    seasonal_order = (3, 0, 0, 7)
    model_builder.train_complete_sarima_model(col_name="orders", order=order, seasonal_order=seasonal_order)
    model_builder.save_model(path=path, filename="auto_sarima")

    order = (2, 0, 1)
    seasonal_order = (3, 0, 3, 7)
    model_builder.train_complete_sarima_model(col_name="orders", order=order, seasonal_order=seasonal_order)
    model_builder.save_model(path=path, filename="sk_sarima")


if __name__ == "__main__":
    main()
