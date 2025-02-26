import json
import pandas as pd
import requests
import numpy as np
from riotwatcher import ApiError
import main
from collections import defaultdict
import psycopg2
from config import config
from datetime import datetime
import challenger_search
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Riot Details
api_key = os.getenv('RIOT_API_KEY')
print(f"Loaded API Key: {api_key}")  # Debugging statement
if not api_key:
    raise ValueError("API key must be set in the .env file")

region = 'na1'

# Function to connect to the database and execute a callback
def connect(callback):
    connection = None
    try:
        params = config()
        print('Connecting to the PostgreSQL database...')
        connection = psycopg2.connect(**params)
        callback(connection)
    except(Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if connection is not None:
            connection.close()
            print('Database connection closed.')

# Function to insert data into the challenger_league table
def insert_data_batch(connection, table_name, data_list, conflict_columns=None):
    cursor = connection.cursor()
    if not data_list:
        return
    placeholders = ', '.join(['%s'] * len(data_list[0]))
    columns = ', '.join(data_list[0].keys())
    if conflict_columns:
        conflict_columns_str = ', '.join(conflict_columns)
        sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders}) ON CONFLICT ({conflict_columns_str}) DO NOTHING"
    else:
        sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
    cursor.executemany(sql, [list(data.values()) for data in data_list])
    connection.commit()
    cursor.close()

# Fetch the challenger league data
entries = challenger_search.get_challenger_league_data(region, api_key)

# Insert the data into the challenger_league table
def insert_challenger_league_data(connection):
    insert_data_batch(connection, 'challenger_league', entries, ['date', 'puuid'])

connect(insert_challenger_league_data)