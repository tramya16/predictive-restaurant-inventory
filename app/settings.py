import os

HIST_DATA_PATH = os.path.join(os.path.expanduser('~'), 'historical_data.csv')
MEAN_WEEKLY_ORDERS = 1544
SD_WEEKLY_ORDERS = 160
START_DATE = "2024-01-01"
db_url = 'mysql+pymysql://admin:admin@localhost/prims?ssl_disabled=true'
csv_dir = './csv'
