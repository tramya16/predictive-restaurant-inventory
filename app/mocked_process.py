# mocked_process.py
import random
import time

class MockedProcess:
    LOW_STOCK_THRESHOLD = 10
    RESTOCK_AMOUNT = 20  # Fixed restock amount

    def __init__(self):
        self.inventory = {
            "tomato": 40,
            "spaghetti": 40,
            "cheese": 40,
            "basil": 40,
        }
        self.recipes = {
            "Pasta": {
                "ingredients": {
                    "tomato": {"quantity": 2, "unit": "grams"},
                    "spaghetti": {"quantity": 20, "unit": "grams"},
                    "cheese": {"quantity": 20, "unit": "grams"},
                    "basil": {"quantity": 5, "unit": "grams"}
                }
            }
        }
        self.simulated_food_orders = []
        self.predicted_food_orders = []
        self.model_accuracy = []
        self.current_week = 1
        self.last_update_time = time.time()

    def generate_predicted_food_orders(self):
        return {
            "Pasta": random.randint(3, 5)
        }

    def generate_simulated_food_orders(self, predicted_orders):
        simulated_orders = {}
        for food, predicted_qty in predicted_orders.items():
            deviation = random.randint(-2, 2)
            simulated_orders[food] = max(0, predicted_qty + deviation)
        return simulated_orders

    def update_inventory(self, orders):
        restocked_ingredients = {}

        for food, order_qty in orders.items():
            if food in self.recipes:
                for ingredient, details in self.recipes[food]["ingredients"].items():
                    required_qty = details["quantity"] * order_qty
                    if ingredient in self.inventory:
                        # If not enough stock, set the inventory to 0 and restock immediately
                        if self.inventory[ingredient] < required_qty:
                            print(f"Not enough stock for {ingredient}. Restocking...")
                            self.inventory[ingredient] = 0  # Set to 0 since it's out of stock
                            restocked_qty = self.restock_inventory(ingredient)
                            restocked_ingredients[ingredient] = restocked_qty
                        else:
                            # Subtract the required quantity if enough stock is available
                            self.inventory[ingredient] -= required_qty

                        # Check if the inventory falls below the low stock threshold after updating
                        if self.inventory[ingredient] < self.LOW_STOCK_THRESHOLD:
                            restocked_qty = self.restock_inventory(ingredient)
                            if restocked_qty > 0:
                                restocked_ingredients[ingredient] = restocked_qty
            else:
                print(f"No recipe found for {food}. Skipping.")
        
        return restocked_ingredients

        

    def restock_inventory(self, ingredient):
        if self.inventory[ingredient] < self.LOW_STOCK_THRESHOLD:
            # Restock by the fixed amount
            self.inventory[ingredient] += self.RESTOCK_AMOUNT
            print(f"Restocked {ingredient} with {self.RESTOCK_AMOUNT} units. New stock: {self.inventory[ingredient]}")
            return self.RESTOCK_AMOUNT
        return 0

    def calculate_accuracy(self, predicted, actual, tolerance=2):
        correct = 0
        total = len(predicted)
        for food in predicted:
            if abs(predicted[food] - actual.get(food, 0)) <= tolerance:
                correct += 1
        return (correct / total) * 100 if total else 0
