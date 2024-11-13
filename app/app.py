from flask import Flask, render_template, jsonify
from datetime import datetime
from mocked_process import MockedProcess
import time

app = Flask(__name__)
process = MockedProcess()

MAX_HISTORY = 10  # Limit for historical data

@app.route('/mocked-data')
def get_mocked_data():
    current_time = time.time()
    
    # Generate new data only if 5 seconds have passed
    if current_time - process.last_update_time >= 5:
        predicted_food = process.generate_predicted_food_orders()
        actual_food = process.generate_simulated_food_orders(predicted_food)
        accuracy = process.calculate_accuracy(predicted_food, actual_food)

        # Append new food order data
        process.predicted_food_orders.append(predicted_food)  # Correctly appending to the list
        process.simulated_food_orders.append(actual_food)  # Correctly appending to the list
        process.model_accuracy.append(accuracy)  # Correctly appending to the list

        # Limit the history size
        if len(process.predicted_food_orders) > MAX_HISTORY:
            process.predicted_food_orders.pop(0)
        if len(process.simulated_food_orders) > MAX_HISTORY:
            process.simulated_food_orders.pop(0)
        if len(process.model_accuracy) > MAX_HISTORY:
            process.model_accuracy.pop(0)

        # Update the ingredient inventory based on food orders
        process.update_inventory(actual_food)
        process.current_week += 1
        process.last_update_time = current_time

    # Check for last available values or generate defaults
    predicted_food_orders = process.predicted_food_orders[-1] if process.predicted_food_orders else process.generate_predicted_food_orders()
    simulated_food_orders = process.simulated_food_orders[-1] if process.simulated_food_orders else process.generate_simulated_food_orders(predicted_food_orders)

    # Prepare data to send to frontend
    data = {
        "predicted_food_orders": predicted_food_orders,
        "simulated_food_orders": simulated_food_orders,
        "model_accuracy": process.model_accuracy,
        "inventory": process.inventory,
        "food_orders_this_week": simulated_food_orders,
        "orders_by_category": process.generate_order_by_category(),
        "current_week": process.current_week,
        "current_time": datetime.now().strftime("%H:%M:%S")
    }

    return jsonify(data)


@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
