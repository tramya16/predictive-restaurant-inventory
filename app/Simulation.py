import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_dates(start_date, end_date):
    """Generate a list of dates between start_date and end_date (inclusive)."""
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    return [start + timedelta(days=i) for i in range((end - start).days + 1)]

def derive_day_and_month(dates):
    """Extract day of the week and month for each date."""
    return [(date, date.strftime("%A"), date.strftime("%B")) for date in dates]

def simulate_orders(dates, base_orders=100):
    """
    Simulate daily orders with fixed multipliers:
    - Weekends: 1.5
    - Holidays (December): 2.0
    - Weekdays: 1.0
    """
    orders = []
    for date in dates:
        if date.strftime("%B") == "December":
            multiplier = 2.0
        elif date.weekday() in [5, 6]:  # Weekend
            multiplier = 1.5
        else:  # Weekday
            multiplier = 1.0
        
        daily_orders = np.random.poisson(base_orders * multiplier)
        orders.append(daily_orders)
    return orders

def create_simulated_dataset(start_date, end_date, base_orders=100):
    """
    Generate a simulated dataset with dates, weekdays, months, and simulated orders.
    """
    dates = generate_dates(start_date, end_date)
    derived_data = derive_day_and_month(dates)
    orders = simulate_orders(dates, base_orders)
    df = pd.DataFrame(derived_data, columns=["date", "day_of_week", "month"])
    df["orders"] = orders
    return df

def main():
    start_date = "2023-01-01"
    end_date = "2026-01-01"
    return create_simulated_dataset(start_date, end_date)
    
if __name__ == "__main__":
    main()
