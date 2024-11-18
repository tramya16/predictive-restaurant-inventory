from flask import Flask, render_template, jsonify
from datetime import datetime
from mocked_process import MockedProcess
import time
from db_config import *

app = Flask(__name__)
# process = MockedProcess()
db_url = 'mysql+pymysql://admin:admin@localhost/prims?ssl_disabled=true'
csv_dir = './csv'
db = PRIMSDatabase(db_url, csv_dir)
MAX_HISTORY = 10  # Limit for historical data

@app.route('/mocked-data')
def get_mocked_data():
    current_time = time.time()

    # Generate new data only if 5 seconds have passed
    if current_time - db.last_update_time >= 5:
        # predicted_food = process.generate_predicted_food_orders()
        # actual_food = process.generate_simulated_food_orders(predicted_food)
        
        # Append new food order data
        # process.predicted_food_orders.append(predicted_food)
        # process.simulated_food_orders.append(actual_food)

        # Limit the history size
        # if len(process.predicted_food_orders) > MAX_HISTORY:
        #     process.predicted_food_orders.pop(0)
        # if len(process.simulated_food_orders) > MAX_HISTORY:
        #     process.simulated_food_orders.pop(0)
        # if len(process.model_accuracy) > MAX_HISTORY:
        #     process.model_accuracy.pop(0)

        db.update_performance_parameter(db.current_week, "model_accuracy", random.uniform(80.0, 95.0))
        db.predict_random_orders(db.current_week)

        accuracy = db.get_performance_parameter(db.current_week, "model_accuracy")
        db.model_accuracy.append(accuracy)

        db.predicted_food_orders = db.get_predicted_orders_json(db.current_week)
        db.simulated_food_orders = db.generate_simulated_food_orders_json(db.current_week)

        # Update the ingredient inventory and track how much was restocked
        db.update_inventory(db.current_week)
        restocked_ingredients = {} # process.update_inventory(actual_food)
        db.current_week += 1
        db.last_update_time = current_time

    else:
        restocked_ingredients = {}
        

    # print("predicted_food_orders: ", process.predicted_food_orders)
    # print("simulated_food_orders: ", process.simulated_food_orders)
    # print("process.model_accuracy: ", process.model_accuracy)
    # print("process.inventory: ", process.inventory)
    # print("restocked_ingredients: ", restocked_ingredients)
    # print("db.current_week: ", db.current_week)
    # print('datetime.now().strftime("%H:%M:%S"): ', datetime.now().strftime("%H:%M:%S"))

    # Prepare data to send to frontend
    data = {
        "predicted_food_orders": db.predicted_food_orders, # Currently predicted randomly using function
        "food_orders_this_week": db.simulated_food_orders,  # Currently simulated randomly 
        "model_accuracy": db.model_accuracy,
        "inventory": db.get_inventory_json(),
        "restocked_ingredients": restocked_ingredients,  # New data for restocked ingredients
        "current_week": db.current_week,
        "current_time": datetime.now().strftime("%H:%M:%S")
    }

    return jsonify(data)



@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
