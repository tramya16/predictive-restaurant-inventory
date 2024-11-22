import pandas as pd
from sqlalchemy import create_engine, Table, MetaData, Column, Integer, String, ForeignKey, Float, inspect, text, insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy_utils import database_exists, create_database
import random
import numpy as np
import time
from settings import *


class PRIMSDatabase:
    def __init__(self, db_url, csv_dir):
        # Initialize database connection and metadata
        self.engine = create_engine(db_url)
        if not database_exists(self.engine.url):
            create_database(self.engine.url)
        self.metadata = MetaData()
        self.csv_dir = csv_dir
        self.current_week = 0
        self.last_update_time = time.time()
        # Define tables and load data into them
        self.create_tables()
        self.load_all_data()
        self.simulated_food_orders = []
        self.predicted_food_orders = []
        self.model_accuracy = []
        self.restocked_ingredients = dict()
        self.sd = SD_WEEKLY_ORDERS 
        self.start_date= pd.to_datetime(START_DATE)  

    def create_tables(self):
        # Inventory table
        self.inventory = Table('inventory', self.metadata,
                               Column('ingredient_id', Integer, primary_key=True),
                               Column('quantity', Float)
                               )

        # Ingredient table
        self.ingredient = Table('ingredient', self.metadata,
                                Column('ingredient_id', Integer, primary_key=True),
                                Column('ingredient_name', String(255))
                                )

        # Recipes table (composite primary key)
        self.recipes = Table('recipes', self.metadata,
                             Column('recipe_id', Integer, primary_key=True),
                             Column('recipe_name', String(255)),
                             Column('ingredient_id', Integer, ForeignKey('ingredient.ingredient_id'), primary_key=True),
                             Column('quantity', Float)
                             )

        # Orders table
        self.orders = Table('orders', self.metadata,
                            Column('week', Integer, primary_key=True),
                            Column('recipe_id', Integer, ForeignKey('recipes.recipe_id'), primary_key=True),
                            Column('num_orders', Integer)
                            )

        # Performance Parameters table
        self.performance_parameters = Table('performance_parameters', self.metadata,
                                            Column('parameter_id', Integer, primary_key=True),
                                            Column('parameter_name', String(255))
                                            )

        # Performance Matrix table
        self.performance_matrix = Table('performance_matrix', self.metadata,
                                        Column('week', Integer, primary_key=True),
                                        Column('parameter_id', Integer,
                                               ForeignKey('performance_parameters.parameter_id'), primary_key=True),
                                        Column('value', Float)
                                        )

        # Predicted Orders table
        self.predicted_orders = Table('predicted_orders', self.metadata,
                                      Column('week', Integer, primary_key=True),
                                      Column('recipe_id', Integer, ForeignKey('recipes.recipe_id'), primary_key=True),
                                      Column('num_orders', Integer)
                                      )

        # Create all tables in the database
        self.metadata.create_all(self.engine)

    def load_all_data(self):
        self.load_and_insert_data("ingredients.csv", "ingredient", ["ingredient_id"])
        self.load_and_insert_data("recipes.csv", "recipes", ["recipe_id", "ingredient_id"])
        self.load_and_insert_data("orders.csv", "orders", ["week", "recipe_id"])
        self.load_and_insert_data("inventory.csv", "inventory", ["ingredient_id"])
        self.load_and_insert_data("predicted_orders.csv", "predicted_orders", ["week", "recipe_id"])
        self.load_and_insert_data("performance_parameters.csv", "performance_parameters", ["parameter_id"])
        self.load_and_insert_data("performance_matrix.csv", "performance_matrix", ["week", "parameter_id"])

    def load_and_insert_data(self, file_name, table_name, unique_id_columns):
        # Load CSV into a DataFrame
        file_path = f"{self.csv_dir}/{file_name}"
        df = pd.read_csv(file_path, sep=',', quotechar='\'', encoding='utf8')
        df_filtered = df

        # Check if the table exists, then filter for new records
        if table_name in inspect(self.engine).get_table_names():
            existing_ids_query = f"SELECT {', '.join(unique_id_columns)} FROM {table_name}"
            existing_ids = pd.read_sql(existing_ids_query, con=self.engine)
            existing_ids_set = set(tuple(x) for x in existing_ids[unique_id_columns].values)
            df_filtered = df[~df[unique_id_columns].apply(tuple, axis=1).isin(existing_ids_set)]

        # Insert new records into the table
        try:
            df_filtered.to_sql(table_name, con=self.engine, index=False, if_exists='append')
            print(f"Data inserted into '{table_name}' successfully.")
        except IntegrityError as e:
            print(f"Error inserting data into '{table_name}': {e}")

    def get_predicted_ingredients(self, week):
        query = f'''
            SELECT a.week, a.num_orders, b.recipe_id, b.recipe_name, d.ingredient_name, d.ingredient_id,
                   b.quantity AS 'ingredient_qty', c.quantity AS 'inventory_qty' 
            FROM predicted_orders a
            INNER JOIN recipes b ON a.recipe_id = b.recipe_id
            INNER JOIN inventory c ON b.ingredient_id = c.ingredient_id
            INNER JOIN ingredient d ON c.ingredient_id = d.ingredient_id
            WHERE a.week = {week}
            ORDER BY d.ingredient_name
        '''
        predicted_ingredients = pd.read_sql(query, con=self.engine)
        predicted_ingredients['stock_update'] = predicted_ingredients.inventory_qty - (
                    predicted_ingredients.num_orders * predicted_ingredients.ingredient_qty) - self.sd
        return predicted_ingredients

    def get_predicted_ingredients_json(self, week):
        predicted_ingredients_df = self.get_predicted_ingredients(week)

        predicted_ingredients_dict = dict()

        for index, row in predicted_ingredients_df.iterrows():
            if predicted_ingredients_df.loc[index, 'stock_update'] < 0:
                predicted_ingredients_dict[predicted_ingredients_df.loc[index, 'ingredient_name']] = int(
                    -1 * predicted_ingredients_df.loc[index, 'stock_update'])

        return predicted_ingredients_dict

    def get_inventory(self):
        inventory = pd.read_sql(
            '''SELECT b.ingredient_name, a.quantity FROM inventory a INNER JOIN ingredient b ON a.ingredient_id = b.ingredient_id ORDER BY b.ingredient_name''',
            con=self.engine
        )
        return inventory

    def get_inventory_json(self):
        inventory_df = self.get_inventory()

        inventory_dict = dict()

        for index, row in inventory_df.iterrows():
            inventory_dict[inventory_df.loc[index, 'ingredient_name']] = int(inventory_df.loc[index, 'quantity'])

        return inventory_dict

    def update_inventory(self, week):
        # Fetch predicted ingredient data
        predicted_ingredients = self.get_predicted_ingredients(week)

        # Store updates for the inventory in a dictionary
        inventory_updates = {}

        # Loop through predicted ingredients to calculate inventory changes
        for _, row in predicted_ingredients.iterrows():
            num_orders = row['num_orders']
            ingredient_qty = row['ingredient_qty'] * num_orders  # Total quantity needed for actual orders

            # Start by calculating the quantity decrease based on predicted orders
            if row['ingredient_id'] not in inventory_updates:
                inventory_updates[row['ingredient_id']] = 0

            # Decrease inventory based on predicted orders
            inventory_updates[row['ingredient_id']] -= ingredient_qty

            # Restocking logic: If inventory goes below 10, restock to 10 units
            current_quantity = row['inventory_qty']

            # Apply predicted stock updates (if stock_update < 0)
            if row['stock_update'] < 0:
                predicted_update_qty = -1 * row['stock_update']  # Apply the predicted stock update (can be negative)
                inventory_updates[row['ingredient_id']] += predicted_update_qty
                restock_qty = predicted_update_qty  # Calculate how much to restock
                inventory_updates[row['ingredient_id']] += restock_qty  # Restock to 10 units
                self.restocked_ingredients[row['ingredient_name']] = restock_qty
                print(f"Restocked ingredient {row['ingredient_name']} to 10 units from {current_quantity}.")

        # Perform the inventory update in one batch if there are any updates
        if inventory_updates:
            with self.engine.begin() as conn:
                # Set session timeout for long-running operations
                sql = text("SET SESSION innodb_lock_wait_timeout = 500;")
                conn.execute(sql)

                # Loop through the inventory updates and execute them one by one
                for ingredient_id, update_qty in inventory_updates.items():
                    update_sql = text(
                        f"UPDATE inventory SET quantity = quantity + {update_qty} WHERE ingredient_id = {ingredient_id}")
                    conn.execute(update_sql)
                    print(f"Executed update for ingredient {ingredient_id} with change of {update_qty}.")

    def get_performance_parameter(self, week, parameter_name):
        query = f'''
            SELECT a.value 
            FROM performance_matrix a
            INNER JOIN performance_parameters b ON a.parameter_id = b.parameter_id
            WHERE b.parameter_name="{parameter_name}" AND a.week = {week}
        '''

        parameter = pd.read_sql(query, con=self.engine)

        if not parameter.empty:
            return parameter['value'].iloc[0]
        else:
            return None

    def update_performance_parameter(self, week, parameter_name, value):
        parameter = pd.read_sql(
            f"SELECT parameter_id FROM performance_parameters WHERE parameter_name='{parameter_name}'", con=self.engine)

        with self.engine.begin() as conn:
            if self.get_performance_parameter(week, parameter_name) is None:
                sql = text(
                    f"INSERT INTO performance_matrix (week, parameter_id, value) VALUES ({week}, {parameter['parameter_id'].iloc[0]}, {round(value, 2)})")
            else:
                sql = text(
                    f"UPDATE performance_matrix SET value = {round(value, 2)} WHERE week = {week} AND parameter_id = {parameter['parameter_id'].iloc[0]}")
            conn.execute(sql)

    def get_orders(self, week):
        orders = pd.read_sql(
            f'''SELECT a.week, b.recipe_name, a.num_orders FROM orders a INNER JOIN recipes b ON a.recipe_id = b.recipe_id WHERE a.week = {week}''',
            con=self.engine
        )

        if not orders.empty:
            return orders
        else:
            return None
    
    def update_orders(self, df):
        orders = df[['week', 'recipe_id', 'num_orders']]

        print(orders)

        with self.engine.begin() as conn:
            for _, row in orders.iterrows():
                if self.get_orders(row.week) is None:
                    sql = text(
                        f"INSERT INTO orders (week, recipe_id, num_orders) VALUES ({row.week}, {row.recipe_id}, {row.num_orders})")
                else:
                    sql = text(
                        f"UPDATE orders SET num_orders = {row.num_orders} WHERE week = {row.week} AND recipe_id = {row.recipe_id}")
                conn.execute(sql)

    def get_predicted_orders(self, week):
        predicted_orders = pd.read_sql(
            f'''SELECT a.week, b.recipe_name, a.num_orders FROM predicted_orders a INNER JOIN recipes b ON a.recipe_id = b.recipe_id WHERE a.week = {week}''',
            con=self.engine
        )

        if not predicted_orders.empty:
            return predicted_orders
        else:
            return None

    def get_predicted_orders_json(self, week):
        predicted_orders_df = self.get_predicted_orders(week)

        predicted_orders_dict = dict()

        for index, row in predicted_orders_df.iterrows():
            predicted_orders_dict[predicted_orders_df.loc[index, 'recipe_name']] = int(
                predicted_orders_df.loc[index, 'num_orders'])

        return predicted_orders_dict

    def update_predicted_orders(self, df):

        predicted_orders = df[['week', 'recipe_id', 'num_orders']]

        with self.engine.begin() as conn:
            for _, row in predicted_orders.iterrows():
                if self.get_predicted_orders(row.week) is None:
                    sql = text(
                        f"INSERT INTO predicted_orders (week, recipe_id, num_orders) VALUES ({row.week}, {row.recipe_id}, {row.num_orders})")
                else:
                    sql = text(
                        f"UPDATE predicted_orders SET num_orders = {row.num_orders} WHERE week = {row.week} AND recipe_id = {row.recipe_id}")
                conn.execute(sql)

    def generate_simulated_food_orders(self, week, num_orders):
        recipe_ids = pd.read_sql(
            "SELECT DISTINCT b.recipe_id, b.recipe_name FROM recipes b",
            con=self.engine)
        simulated_orders = pd.DataFrame()
        simulated_orders['week'] = [week]
        simulated_orders['num_orders'] = num_orders
        simulated_orders['recipe_id'] = [recipe_ids["recipe_id"][0]]
        simulated_orders['recipe_name'] = [recipe_ids["recipe_name"][0]]

        print(simulated_orders)

        if not simulated_orders.empty:
            self.update_orders(simulated_orders)
            return simulated_orders
        else:
            return None

    def generate_simulated_food_orders_json(self, week, num_orders):
        simulated_orders_df = self.generate_simulated_food_orders(week, num_orders)

        simulated_orders_dict = dict()

        if simulated_orders_df is not None:
            for index, row in simulated_orders_df.iterrows():
                simulated_orders_dict[simulated_orders_df.loc[index, 'recipe_name']] = int(
                    simulated_orders_df.loc[index, 'num_orders'])

        return simulated_orders_dict

    def predict_random_orders(self, week):
        recipe_ids = pd.read_sql(
            "SELECT DISTINCT a.recipe_id, b.recipe_name FROM orders a INNER JOIN recipes b ON a.recipe_id = b.recipe_id",
            con=self.engine)
        recipe_ids['week'] = week
        chosen_idx = np.random.choice(recipe_ids.index, replace=True, size=random.randint(100, 150))
        predicted_orders = recipe_ids.loc[chosen_idx]

        # print(predicted_orders)

        predicted_orders_df = pd.DataFrame(columns=['week', 'recipe_id', 'num_orders'])

        recipe_counts = predicted_orders['recipe_id'].value_counts()

        count = 0

        for recipe_id, num_orders in recipe_counts.items():
            predicted_orders_df.loc[count] = [week, recipe_id, num_orders]
            count += 1

        self.update_predicted_orders(predicted_orders_df)

        return predicted_orders_df

# # Instantiate the class and pass in the database URL and CSV directory path
# db_url = 'mysql+pymysql://{}:{}@{}/{}?ssl_disabled=true'.format(DB_USERNAME, DB_PASSWORD, DB_HOST, DB_NAME)
# prims_db = PRIMSDatabase(db_url, CSV_DIR)
# prims_db.generate_simulated_food_orders_json(0)
# prims_db.get_predicted_orders_json(0)

