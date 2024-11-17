import random
import time

class MockedProcess:
    LOW_STOCK_THRESHOLD = 10  # Threshold below which restocking is triggered
    RESTOCK_AMOUNT = 20  # Restock amount per item when needed
    MARGIN_ERROR = 3  # Additional units added to each restock to account for margin of error

    def __init__(self):
        self.inventory = {
            "tomato": 50,
            "spaghetti": 50,
            "cheese": 50,
            "basil": 50,
        }
        self.recipes = {
            "Pasta": {
                "ingredients": {
                    "tomato": {"quantity": 2, "unit": "grams"},
                    "spaghetti": {"quantity": 2, "unit": "grams"},
                    "cheese": {"quantity": 1, "unit": "grams"},
                    "basil": {"quantity": 2, "unit": "grams"}
                }
            }
        }
        self.simulated_food_orders = []
        self.predicted_food_orders = []
        self.model_accuracy = 100  # Start with initial accuracy as a single value
        self.current_week = 1
        self.last_update_time = time.time()
        self.base_accuracy = 95  # Initial accuracy
        self.max_variation = 2   # Maximum percentage variation

    def generate_predicted_food_orders(self):
        # Simulate predicted orders, for example 3-5 orders of Pasta
        return {
            "Pasta": random.randint(3, 5)
        }

    def generate_simulated_food_orders(self, predicted_orders):
        # Generate simulated food orders with a slight deviation from predicted
        simulated_orders = {}
        for food, predicted_qty in predicted_orders.items():
            deviation = random.randint(-2, 2)  # Small deviation to simulate real conditions
            simulated_orders[food] = max(0, predicted_qty + deviation)  # Ensure non-negative orders
        return simulated_orders

    def update_inventory(self, orders, predicted_orders):
        restocked_ingredients = {}

        # Process the actual orders and update inventory accordingly
        for food, order_qty in orders.items():
            if food in self.recipes:
                for ingredient, details in self.recipes[food]["ingredients"].items():
                    required_qty = details["quantity"] * order_qty
                    if ingredient in self.inventory:
                        if self.inventory[ingredient] < required_qty:
                            print(f"Not enough stock for {ingredient}. Restocking...")
                            self.inventory[ingredient] = 0  # Set to 0 since it's out of stock
                            restocked_qty = self.restock_inventory(ingredient, required_qty)
                            restocked_ingredients[ingredient] = restocked_qty
                        else:
                            self.inventory[ingredient] -= required_qty
                        
                        # After updating the stock, check if it's below the threshold for restocking
                        if self.inventory[ingredient] < self.LOW_STOCK_THRESHOLD:
                            restocked_qty = self.restock_inventory(ingredient, required_qty)
                            if restocked_qty > 0:
                                restocked_ingredients[ingredient] = restocked_qty
            else:
                print(f"No recipe found for {food}. Skipping.")

        # Now, ensure restocking based on predicted food orders and adding the margin of error
        restocked_ingredients.update(self.restock_for_predicted_orders(predicted_orders))
        
        return restocked_ingredients

    def restock_inventory(self, ingredient, required_qty):
        # Restock the ingredient based on required quantity and add margin for error
        restock_qty = required_qty + self.MARGIN_ERROR  # Add margin for error
        self.inventory[ingredient] += restock_qty
        print(f"Restocked {ingredient} with {restock_qty} units. New stock: {self.inventory[ingredient]}")
        return restock_qty

    def restock_for_predicted_orders(self, predicted_orders):
        restocked_ingredients = {}
        for food, predicted_qty in predicted_orders.items():
            if food in self.recipes:
                for ingredient, details in self.recipes[food]["ingredients"].items():
                    required_qty = details["quantity"] * predicted_qty
                    if self.inventory[ingredient] < required_qty:
                        print(f"Predicted shortage of {ingredient}. Restocking with margin...")
                        restocked_qty = self.restock_inventory(ingredient, required_qty)
                        restocked_ingredients[ingredient] = restocked_qty
        return restocked_ingredients

    def calculate_accuracy(self, predicted, actual, tolerance=2):
        correct = 0
        total = len(predicted)
        for food in predicted:
            if abs(predicted[food] - actual.get(food, 0)) <= tolerance:
                correct += 1
        base_accuracy = (correct / total) * 100 if total else 0
        return self.apply_accuracy_variation(base_accuracy)

    def apply_accuracy_variation(self, base_accuracy):
        # Add fluctuation around the base accuracy based on week progression
        time_period_factor = (self.current_week // 16)  # Change every 16 weeks
        fluctuation = random.uniform(-self.max_variation, self.max_variation) * time_period_factor
        varied_accuracy = base_accuracy + fluctuation

        # Keep accuracy within bounds (0–100)
        return max(0, min(95, varied_accuracy))
