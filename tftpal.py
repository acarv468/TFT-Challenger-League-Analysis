import json
import pandas as pd
import requests
import numpy as np
from riotwatcher import TftWatcher
import main
from collections import defaultdict
import psycopg2
from config import config
from datetime import datetime
from dotenv import load_dotenv
import os
import challenger_search
import time

# Start the timer
start_time = time.time()

# Load environment variables from .env file
load_dotenv()

# Riot Details
api_key = os.getenv('RIOT_API_KEY')
print(f"Loaded API Key: {api_key}")  # Debugging statement
if not api_key:
    raise ValueError("API key must be set in the .env file")


region = 'na1'
print(f"Region: {region}")  # Debugging statement

# Get the puuid list using the imported function
# puuid_list = get_challenger_leauge_puuid(region, api_key)
# print(f"PUUID List: {puuid_list}")  # Debugging statement

# puuid_list = [
#     'IqE3AGiAsBfKo44yi6SDC5N31XSRkQYoDtVNdeVYd6AjZoX0HM-0TdbnhLYP01hVrrEpFZmn1NDL9g',
#     'qiQLis_3Zapl6oxI8oHEbnuivAWoy3uRH06ToRLObMje4IUOKON-YK8TgHhqR-ed-OBQ_6Ei5gCVZg',
#     'COBBLmcIDuaarBHiGr_iFHjaeEw44q94z-sEuW2d-EEmraG3JR4_dxwELOl2qXlIpTwPglfc38zbrg',
#     'AbTNQqyAMULCRJNK5n7DNFwkdl4cMbDWOCN-N4dwno2FPmFhZQL4T7f245YUvpqqJgf7NZrx7vR5LA',
#     'Yw9FTrjrd-ODWl2o4dyAqW9mU_e7SHXzFGOfpRG_JkpMHxqHZpZLHO3pbtQ9b10sRbbCREgaU7A-_A']
#puuid_list = get_challenger_leauge_puuid(api_key, region)
puuid_list = challenger_search.get_challenger_leauge_puuid(region, api_key)
print(f"PUUID List: {puuid_list}")  # Debugging statement

watcher = TftWatcher(api_key)

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

def construct_data_groups(puuid, region):
    me = watcher.summoner.by_puuid(region, puuid)
    matches_ids = watcher.match.by_puuid(region, me['puuid'])
    matches = [watcher.match.by_id(region, item) for item in matches_ids]
    for match in matches:
        match_data = {
            'match_id': match['metadata']['match_id'],
            'game_version': match['info']['game_version'],
            'game_datetime': datetime.fromtimestamp(match['info']['game_datetime'] / 1000.0),
            'queue_id': match['info']['queue_id'],
            'endofgameresult': match['info']['endOfGameResult'],
            'game_length': match['info']['game_length'],
            'tft_game_type': match['info']['tft_game_type'],
            'tft_set_core_name': match['info']['tft_set_core_name'],
            'tft_set_number': match['info']['tft_set_number']
        }

        def insert_match_data(connection):
            insert_data_batch(connection, 'Matches', [match_data], ['match_id'])

        connect(insert_match_data)

        for participant in match['info']['participants']:
            if participant['puuid'] in puuid_list:
                partner_group_id = participant.get('partner_group_id', None)
                participants_data = {
                    'puuid': participant['puuid'],
                    'match_id': match['metadata']['match_id'],
                    'placement': participant['placement'],
                    'level': participant['level'],
                    'total_damage_to_players': participant['total_damage_to_players'],
                    'riotidgamename': participant['riotIdGameName'],
                    'riotidtagline': participant['riotIdTagline'],
                    'partner_group_id': partner_group_id,
                    'gold_left': participant['gold_left'],
                    'last_round': participant['last_round'],
                    'players_eliminated': participant['players_eliminated'],
                    'time_eliminated': participant['time_eliminated'],
                    'win': participant['win']
                }

                def insert_participants_data(connection):
                    insert_data_batch(connection, 'Participants', [participants_data], ['puuid', 'match_id'])

                connect(insert_participants_data)

                # Collect units data for batch insert
                units_data_list = []
                character_counts = defaultdict(int)
                for unit in participant['units']:
                    character_counts[unit['character_id']] += 1

                character_indices = defaultdict(int)
                for unit in participant['units']:
                    character_id = unit['character_id']
                    if character_counts[character_id] > 1:
                        character_indices[character_id] += 1
                        unit['unit_index'] = character_indices[character_id]
                    else:
                        unit['unit_index'] = 0

                    units_data = {
                        'character_id': unit['character_id'],
                        'puuid': participant['puuid'],
                        'unit_name': unit['name'],
                        'tier': unit['tier'],
                        'match_id': match['metadata']['match_id'],
                        'itemnames': unit['itemNames'],
                        'unit_index': unit['unit_index']
                    }
                    units_data_list.append(units_data)

                def insert_units_data(connection):
                    insert_data_batch(connection, 'Units', units_data_list, ['unit_index', 'puuid', 'match_id', 'character_id'])

                connect(insert_units_data)

                # Collect traits data for batch insert
                traits_data_list = []
                for trait in participant['traits']:
                    traits_data = {
                        'puuid': participant['puuid'],
                        'trait_name': trait['name'],
                        'tier_current': trait['tier_current'],
                        'tier_total': trait['tier_total'],
                        'match_id': match['metadata']['match_id'],
                        'num_units': trait['num_units']
                    }
                    traits_data_list.append(traits_data)

                def insert_traits_data(connection):
                    insert_data_batch(connection, 'Traits', traits_data_list, ['trait_name', 'puuid', 'match_id'])

                connect(insert_traits_data)

for puuid in puuid_list:
    construct_data_groups(puuid, region)

# End the timer
end_time = time.time()
elapsed_time = end_time - start_time
print(f"Elapsed time: {elapsed_time:.2f} seconds")