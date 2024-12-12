from flask import Flask, render_template, jsonify, request
from datetime import datetime
from db_config import *
from settings import DB_USERNAME, DB_PASSWORD, DB_HOST, DB_NAME, CSV_DIR
from training_and_diagnostics.predictor import Muaddib
import pandas as pd
from order_simulator import OrderSimulator1

app = Flask(__name__)
db_url = 'mysql+pymysql://{}:{}@{}/{}?ssl_disabled=true'.format(DB_USERNAME, DB_PASSWORD, DB_HOST, DB_NAME)
db = PRIMSDatabase(db_url, CSV_DIR)

# Variable to store the currently selected model
current_model_name = "sk_sarima"  # Default model


@app.route('/mocked-data')
def get_mocked_data():
    current_time = time.time()

    # Generate new data only if 5 seconds have passed
    if current_time - db.last_update_time >= 5:

        oracle = Muaddib(model_name=current_model_name)
        predictions = oracle.predict(start_dt=db.start_date, end_dt=db.start_date + pd.Timedelta(days=6))
        weekly_predictions = predictions.sum()
        print(str(predictions))

        simulate_orders = OrderSimulator1()
        print(str(simulate_orders))
        simulated_orders = simulate_orders.simulate_orders(start_dt=db.start_date,
                                                           end_dt=db.start_date + pd.Timedelta(days=6))
        weekly_simulations = simulated_orders['orders'].sum()
        print(weekly_simulations)

        error = oracle.calculate_rmse(predictions, simulated_orders)
        accuracy = oracle.calculate_accuracy(predictions, simulated_orders)
        print(accuracy, error)

        db.update_performance_parameter(db.current_week, "model_accuracy", accuracy)
        # db.predict_random_orders(db.current_week )

        prediction_df = pd.DataFrame()
        prediction_df['week'] = [db.current_week]
        prediction_df['num_orders'] = weekly_predictions
        prediction_df['recipe_id'] = [1]
        db.update_predicted_orders(prediction_df)

        accuracy = db.get_performance_parameter(db.current_week, "model_accuracy")
        db.model_accuracy.append(accuracy)
        print(f"Week {db.current_week}")
        print(f"Predictions: {predictions}")
        print(f"Simulated Orders: {simulated_orders}")
        print(f"Accuracy: {accuracy}, RMSE: {error}")

        db.predicted_food_orders = db.get_predicted_orders_json(db.current_week)
        db.simulated_food_orders = db.generate_simulated_food_orders_json(db.current_week, weekly_simulations)

        # Update the ingredient inventory and track how much was restocked
        db.update_inventory(db.current_week)
        restocked_ingredients = db.restocked_ingredients
        db.current_week += 1
        db.last_update_time = current_time
        db.start_date = db.start_date + pd.Timedelta(days=7)
        print("start date updated: ", db.start_date)

    else:
        restocked_ingredients = db.restocked_ingredients

    # Prepare data to send to frontend
    data = {
        "predicted_food_orders": db.predicted_food_orders,  # Currently predicted randomly using function
        "food_orders_this_week": db.simulated_food_orders,  # Currently simulated randomly 
        "model_accuracy": db.model_accuracy,
        "inventory": db.get_inventory_json(),
        "restocked_ingredients": restocked_ingredients,  # New data for restocked ingredients
        "current_week": db.current_week,
        "current_time": datetime.now().strftime("%H:%M:%S")
    }
    print(data)
    return jsonify(data)


@app.route('/update-model', methods=['POST'])
def update_model():
    global current_model_name
    data = request.get_json()
    model_name = data.get("model_name")

    if model_name in ("sk_sarima", "holt_winters", "auto_sarima"):  # Validate input
        current_model_name = model_name
        return jsonify({"success": True, "model_name": current_model_name})
    else:
        return jsonify({"success": False, "error": "Invalid model name"}), 400


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
