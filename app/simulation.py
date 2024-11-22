import dash
from dash import dcc, html
import plotly.graph_objs as go
from dash.dependencies import Input, Output
import pandas as pd
from datetime import timedelta
import joblib
import numpy as np

# Dataset generator
def generate_dates(start_date, end_date):
    """Generate a list of dates between start_date and end_date (inclusive)."""
    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date)
    return [start + timedelta(days=i) for i in range((end - start).days + 1)]

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
    """Generate a simulated dataset with dates and simulated orders."""
    dates = generate_dates(start_date, end_date)
    orders = simulate_orders(dates, base_orders)
    df = pd.DataFrame({
        "date": dates,
        "orders": orders
    })
    return df

# Load the pre-trained model
model_path = "models/holt_winters.pkl"  # Ensure this file is in the correct path
model = joblib.load(model_path)

# Initialize Dash app
app = dash.Dash(__name__)

# Initialize the dataset with a starting date
initial_date = pd.to_datetime("2023-01-01")
initial_end_date = initial_date + timedelta(days=6)
df = create_simulated_dataset(initial_date, initial_end_date)

# Layout of the dashboard
app.layout = html.Div([
    html.H1("Weekly Orders Prediction Dashboard"),
    dcc.Graph(id='orders-graph'),
    dcc.Interval(
        id='graph-update',
        interval=2000,  # Update every 2 seconds
        n_intervals=0
    )
])

# Callback function to update the graph with new data and predictions
@app.callback(
    Output('orders-graph', 'figure'),
    [Input('graph-update', 'n_intervals')]
)
def update_graph(n_intervals):
    global df, model

    # Generate new week's data
    last_date = df['date'].max()
    next_week_dates = generate_dates(last_date + timedelta(days=1), last_date + timedelta(days=7))
    next_week_data = create_simulated_dataset(next_week_dates[0], next_week_dates[-1])

    # Append new data to the dataset
    df = pd.concat([df, next_week_data], ignore_index=True)

    # Forecast the next 7 days
    predictions = model.forecast(steps=7)
    predicted_dates = generate_dates(df['date'].max() + timedelta(days=1), df['date'].max() + timedelta(days=7))
    predicted_data = pd.DataFrame({
        "date": predicted_dates,
        "orders": predictions
    })

    # Append predictions to the dataset
    df = pd.concat([df, predicted_data], ignore_index=True)

    # Keep only predictions for the dashboard
    df = df[df['date'] >= pd.Timestamp("2023-01-01")]

    # Create the plot
    fig = go.Figure()

    # Add trace for predictions
    fig.add_trace(go.Scatter(
        x=df['date'], y=df['orders'],
        mode='lines+markers',
        name='Predicted Orders',
        line=dict(color='royalblue'),
        marker=dict(size=6)
    ))

    # Update layout
    fig.update_layout(
        title="Predicted Orders for Upcoming Weeks",
        xaxis_title="Date",
        yaxis_title="Orders",
        template="plotly_dark"
    )

    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)

