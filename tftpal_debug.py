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

# Update with your new API key
api_key = 'RGAPI-a0b2220a-1ebb-4b44-b35f-6e4fbabbbf10'
my_region = 'americas'
summoner_name = 'waxade'
tagline = 'na1'

# To get PUUID from Riot ID and tagline
# Construct the URL for the endpoint
url = f"https://{my_region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{summoner_name}/{tagline}"

# Set the headers with the API key
headers = {
    "X-Riot-Token": api_key
}

try:
    # Make the request to the endpoint
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raise an exception for HTTP errors

    # Parse the JSON response
    account_info = response.json()
    # Extract the puuid
    puuid = account_info['puuid']
    print(f"Summoner Name: {summoner_name}")
    print(f"PUUID: {puuid}")
except requests.exceptions.HTTPError as err:
    if err.response.status_code == 403:
        print("Error: Forbidden. Check your API key and permissions.")
    elif err.response.status_code == 429:
        print("Error: Rate limit exceeded. Please wait and try again later.")
    else:
        print(f"Error: {err}")
except Exception as e:
    print(f"An error occurred: {e}")