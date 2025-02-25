import streamlit as st
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from config import config
import plotly.express as px

# Set the page layout to wide
st.set_page_config(layout="wide")

# Streamlit title
st.title('TFT Challenger Dashboard')

# Database connection parameters
db_params = config()

# Create SQLAlchemy engine
engine = create_engine(f"postgresql://{db_params['user']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/{db_params['database']}")

# Function to get data from PostgreSQL and load into a pandas DataFrame
def get_data_from_db(query):
    try:
        # Execute the query and load data into a DataFrame
        df = pd.read_sql_query(query, engine)
        return df
    except Exception as e:
        st.error(f"Error: {e}")
        return pd.DataFrame()

units_query = '''
    select 
        u.character_id,u.puuid,u.tier, 
        u.match_id,u.itemnames,u.unit_index,
        m.game_datetime
    from units u
    join matches m on m.match_id=u.match_id
    where m.tft_set_number=13;
'''
traits_query = '''
    select 
        t.puuid, t.trait_name, t.tier_current,
        t.tier_total, t.match_id, t.num_units,
        m.game_datetime
    from traits t
    join matches m on m.match_id=t.match_id
    where m.tft_set_number=13;
'''
####
# Need to clean data first
####

# Get data from the database
units_data = get_data_from_db(units_query)
traits_data = get_data_from_db(traits_query)

# Create two columns for filters
filter_col1, filter_col2 = st.columns(2)

# Filter options for game date
min_date = min(units_data['game_datetime'].min(), traits_data['game_datetime'].min())
max_date = max(units_data['game_datetime'].max(), traits_data['game_datetime'].max())
selected_date_range = filter_col1.date_input('Select Game Date Range', [min_date, max_date])

# Filter data based on selected game date range
filtered_units_data = units_data[
    (units_data['game_datetime'] >= pd.to_datetime(selected_date_range[0])) &
    (units_data['game_datetime'] <= pd.to_datetime(selected_date_range[1]))
]

filtered_traits_data = traits_data[
    (traits_data['game_datetime'] >= pd.to_datetime(selected_date_range[0])) &
    (traits_data['game_datetime'] <= pd.to_datetime(selected_date_range[1]))
]

# Count the occurrences of each character_id
character_counts = filtered_units_data['character_id'].value_counts().reset_index()
character_counts.columns = ['character_id', 'count']

# Create bar chart for the count of each character_id
bar_chart1 = px.bar(
    character_counts,
    x='character_id',
    y='count',
    title='Most Used Units',
    labels={'count': 'Count', 'character_id': 'Unit ID'}
)
bar_chart1.update_layout(xaxis_title='Unit ID', yaxis_title='Count', barmode='group')

# Count the occurrences of each trait_name
trait_counts = filtered_traits_data['trait_name'].value_counts().reset_index()
trait_counts.columns = ['trait_name', 'count']

# Create bar chart for the count of each trait_name
bar_chart2 = px.bar(
    trait_counts,
    x='trait_name',
    y='count',
    title='Count of Trait',
    labels={'count': 'Count', 'trait_name': 'Trait'}
)
bar_chart2.update_layout(xaxis_title='Trait', yaxis_title='Count', barmode='group')

# Display the bar charts in two columns
col1, col2 = st.columns(2)
col1.plotly_chart(bar_chart1, use_container_width=True)
col2.plotly_chart(bar_chart2, use_container_width=True)

# Single-select filter for character_id
selected_character = st.selectbox('Select Unit', character_counts['character_id'])

# Filter items_data based on selected character_id
items_data = filtered_units_data.explode('itemnames')
filtered_items_data = items_data[items_data['character_id'] == selected_character]

# Count the occurrences of each item for the selected character_id
items_counts = filtered_items_data['itemnames'].value_counts().reset_index()
items_counts.columns = ['itemnames', 'count']

# Limit to top N items
top_n = 10
top_items_counts = items_counts.head(top_n)

# Create bar chart for the count of each item for the selected character_id
bar_chart3 = px.bar(
    top_items_counts,
    x='itemnames',
    y='count',
    title=f'Top {top_n} Most Often Used Items By Unit: {selected_character}',
    labels={'count': 'Count', 'itemnames': 'Item Names'}
)
bar_chart3.update_layout(xaxis_title='Item Names', yaxis_title='Count', barmode='group', height=600)

# Display the bar chart in Streamlit
st.plotly_chart(bar_chart3, use_container_width=True)

# Display the filtered data in Streamlit
st.write(filtered_units_data)
st.write(filtered_traits_data)

