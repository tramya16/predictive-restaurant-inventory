# mocked_process.py
import random
import time

class MockedProcess:
    LOW_STOCK_THRESHOLD = 10
    RESTOCK_AMOUNT = 20

    def __init__(self):
        self.inventory = {
            "eggs": 100,
            "spaghetti": 100,
            "bread": 100,
            "tomato_sauce": 100
        }
        self.simulated_food_orders = []
        self.predicted_food_orders = []
        self.model_accuracy = []
        self.current_week = 1
        self.last_update_time = time.time()

    def generate_predicted_food_orders(self):
        return {
            "eggs": random.randint(5, 10),
            "spaghetti": random.randint(5, 10),
            "bread": random.randint(5, 10),
            "tomato_sauce": random.randint(5, 10)
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
            return {'Pasta': 0, 'Omlette': 0, 'GarlicBread': 0}

        categories = {'Pasta': 0, 'Omlette': 0, 'GarlicBread': 0}
        for food in self.simulated_food_orders[-1]:
            if food in ['spaghetti', 'tomato_sauce']:
                categories['Pasta'] += self.simulated_food_orders[-1][food]
            elif food == 'bread':
                categories['GarlicBread'] += self.simulated_food_orders[-1][food]
            elif food == 'eggs':
                categories['Omlette'] += self.simulated_food_orders[-1][food]
        return categories

    def calculate_accuracy(self, predicted, actual, tolerance=2):
        correct = 0
        total = len(predicted)
        for food in predicted:
            if abs(predicted[food] - actual.get(food, 0)) <= tolerance:
                correct += 1
        return (correct / total) * 100 if total else 0
