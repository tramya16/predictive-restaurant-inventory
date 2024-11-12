# mocked_process.py
import random
import time

class MockedProcess:
    LOW_STOCK_THRESHOLD = 10
    RESTOCK_AMOUNT = 20

    def __init__(self):
        self.inventory = {
            "pasta": 100,
            "cheese_pizza": 100,
            "garlic_bread": 100,
            "tomato_soup": 100
        }
        self.simulated_food_orders = []
        self.predicted_food_orders = []
        self.model_accuracy = []
        self.current_week = 1
        self.last_update_time = time.time()

    def generate_predicted_food_orders(self):
        return {
            "pasta": random.randint(5, 10),
            "cheese_pizza": random.randint(5, 10),
            "garlic_bread": random.randint(5, 10),
            "tomato_soup": random.randint(5, 10)
        }

    def generate_simulated_food_orders(self, predicted_orders):
        simulated_orders = {}
        for food, predicted_qty in predicted_orders.items():
            deviation = random.randint(-2, 2)
            simulated_orders[food] = max(0, predicted_qty + deviation)
        return simulated_orders

    def update_inventory(self, orders):
        for food, qty in orders.items():
            if food in self.inventory:
                self.inventory[food] -= qty
                if self.inventory[food] < self.LOW_STOCK_THRESHOLD:
                    self.restock_inventory(food)

    def restock_inventory(self, food_item):
        if self.inventory[food_item] < self.LOW_STOCK_THRESHOLD:
            self.inventory[food_item] += self.RESTOCK_AMOUNT
            print(f"Restocked {food_item} with {self.RESTOCK_AMOUNT} items.")

    def generate_order_by_category(self):
        if not self.simulated_food_orders:
            return {'Italian': 0, 'FastFood': 0, 'Soup': 0}

        categories = {'Italian': 0, 'FastFood': 0, 'Soup': 0}
        for food in self.simulated_food_orders[-1]:
            if food in ['pasta', 'cheese_pizza']:
                categories['Italian'] += self.simulated_food_orders[-1][food]
            elif food == 'garlic_bread':
                categories['FastFood'] += self.simulated_food_orders[-1][food]
            elif food == 'tomato_soup':
                categories['Soup'] += self.simulated_food_orders[-1][food]
        return categories

    def calculate_accuracy(self, predicted, actual, tolerance=2):
        correct = 0
        total = len(predicted)
        for food in predicted:
            if abs(predicted[food] - actual.get(food, 0)) <= tolerance:
                correct += 1
        return (correct / total) * 100 if total else 0
