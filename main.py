import psycopg2
from config import config
from datetime import datetime

def connect(callback):
    connection = None
    try:
        params = config()
        print('Connecting to the PostgreSQL database...')
        connection = psycopg2.connect(**params)
        callback(connection)
    except(Exception, psycopg2.DatabaseError) as error:
        print('Error:', error)
    finally:
        if connection is not None:
            connection.close()
            print('Database connection closed.')

def insert_data(connection, table_name, data, conflict_columns=None):
    cursor = connection.cursor()
    placeholders = ', '.join(['%s'] * len(data))
    columns = ', '.join(data.keys())
    if conflict_columns:
        conflict_columns_str = ', '.join(conflict_columns)
        sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders}) ON CONFLICT ({conflict_columns_str}) DO NOTHING"
    else:
        sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
    cursor.execute(sql, list(data.values()))
    connection.commit()
    cursor.close()

if __name__ == '__main__':
    match_data = {
        'match_id': 'NA1_5208689472',
        'game_version': 'Linux Version 14.24.644.2327 (Dec 16 2024/12:53:39) [PUBLIC] <Releases/14.24>',
        'game_datetime': datetime.fromtimestamp(1736360384613 / 1000.0),
        'queue_id': 1090,
        'endofgameresult': 'GameComplete',
        'game_length': 2256.497802734375,
        'tft_game_type': 'standard',
        'tft_set_core_name': 'TFTSet13',
        'tft_set_number': 13
    }

    participants_data = {
        'puuid': 'IqE3AGiAsBfKo44yi6SDC5N31XSRkQYoDtVNdeVYd6AjZoX0HM-0TdbnhLYP01hVrrEpFZmn1NDL9g',
        'match_id': 'NA1_5208689472',
        'placement': 5,
        'level': 9,
        'total_damage_to_players': 58,
        'riotidgamename': 'waxade',
        'riotidtagline': 'NA1',
        'partner_group_id': 1,
        'gold_left': 4,
        'last_round': 34,
        'players_eliminated': 0,
        'time_eliminated': 2208.0849609375,
        'win': False
    }

    traits_data = {
        'puuid': 'IqE3AGiAsBfKo44yi6SDC5N31XSRkQYoDtVNdeVYd6AjZoX0HM-0TdbnhLYP01hVrrEpFZmn1NDL9g',
        'trait_name': 'Set13_Augment',
        'tier_current': 2,
        'tier_total': 3,
        'match_id': 'NA1_5208689472',
        'num_units': 4
    }

    units_data = {
        'character_id': 'TFT4_Brand',
        'puuid': 'paEkTNPxBM1MdjKIGocIyv_BcNvhM9JF6WWdaD5tyclDFExOkKvd_7OyQ-rXL987GMWy4ifVXCYmzQ',
        'unit_name': '',
        'tier': 3,
        'match_id': 'NA1_5219325260',
        'itemnames': ['TFT_Item_ThiefsGloves','TFT_Item_SteraksGage','TFT_Item_RapidFireCannon'],
        'unit_index': 0
    }

    def insert_match_data(connection):
        insert_data(connection, 'Matches', match_data, ['match_id'])

    def insert_participants_data(connection):
        insert_data(connection, 'Participants', participants_data, ['puuid', 'match_id'])

    def insert_traits_data(connection):
        insert_data(connection, 'Traits', traits_data, ['trait_name', 'puuid', 'match_id'])

    def insert_units_data(connection):
        insert_data(connection, 'Units', units_data['unit_index', 'puuid', 'match_id'])

    # connect(insert_match_data)
    # connect(insert_participants_data)
    # connect(insert_traits_data)
    connect(insert_units_data)
