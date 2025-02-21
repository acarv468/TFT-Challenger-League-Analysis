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
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

## Riot Details
api_key = os.getenv('RIOT_API_KEY')
print(f"Loaded API Key: {api_key}")  # Debugging statement
if not api_key:
    raise ValueError("API key must be set in the .env file")

region = 'na1'

# To get PUUID from Riot ID and tagline
# Construct the URL for the endpoint
#url = f"https://{region}.api.riotgames.com/tft/league/v1/challenger?queue=RANKDED_TFT&api_key={api_key}"

# Set the headers with the API key
# headers = {
#     "X-Riot-Token": api_key
# }

def get_challenger_leauge_puuid(region, api_key):
    # Construct the URL for the endpoint
    url = f"https://{region}.api.riotgames.com/tft/league/v1/challenger?queue=RANKED_TFT&api_key={api_key}"
    puuid_list = []
    try:
        # Make the request to the endpoint
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Parse the JSON response
        response_body = response.json()
        entries = response_body['entries']
        puuid_list = [entry['puuid'] for entry in entries]  # Extract the puuid from each entry
        #print(puuid_list)
    except requests.exceptions.HTTPError as err:
        if err.response.status_code == 403:
            print("Error: Forbidden. Check your API key and permissions.")
        elif err.response.status_code == 429:
            print("Error: Rate limit exceeded. Please wait and try again later.")
        else:
            print(f"Error: {err}")
    except Exception as e:
        print(f"An error occurred: {e}")
    
    return puuid_list

#test_list = get_challenger_leauge_puuid(region, api_key)
# print(test_list)