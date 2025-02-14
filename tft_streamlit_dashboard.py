import streamlit as st
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from config import config
import altair as alt
import plotly.express as px

# Streamlit title
st.title('TFT Stats Dashboard')

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

# Example query to get data from a table
query = '''
    SELECT p.puuid, p.match_id AS p_match_id, p.placement, p.level, p.total_damage_to_players, 
           p.riotidgamename, p.riotidtagline, p.partner_group_id, p.gold_left, p.last_round, 
           p.players_eliminated, p.time_eliminated, p.win, 
           m.match_id AS m_match_id, m.game_version, m.game_datetime, m.queue_id, 
           m.endofgameresult, m.game_length, m.tft_game_type, m.tft_set_core_name, 
           m.tft_set_number
    FROM Participants p
    JOIN Matches m ON p.match_id = m.match_id
    WHERE p.riotidgamename = 'waxade'
    OR p.riotidgamename = 'LittleHuman'
    OR p.riotidgamename = 'Sonariq'
    OR p.riotidgamename = 'MiniButt'
    OR p.riotidgamename = 'WizardHatDave';
'''

# Get data from the database
data = get_data_from_db(query)

# Display the data in Streamlit
st.write(data)

# Check for data issues
st.write("Data types:")
st.write(data.dtypes)

# Create a custom scatter chart with altair
scatter_chart = alt.Chart(data).mark_circle(size=60).encode(
    x=alt.X('total_damage_to_players', scale=alt.Scale(domain=[0, 100])),
    y=alt.Y('placement', scale=alt.Scale(domain=[1, 8])),
    color='riotidgamename',
    tooltip=['riotidgamename', 'total_damage_to_players', 'placement', 'p_match_id']
).properties(
    width=600,
    height=400
).interactive()

# Simplified bar chart for debugging with Altair
bar_chart_altair = alt.Chart(data).mark_bar().encode(
    x='game_datetime:T',
    y='placement:Q',
    color='riotidgamename'
).properties(
    width=600,
    height=400
).interactive()

# Create a custom bar chart with Plotly
bar_chart_plotly = px.bar(
    data,
    x='game_datetime',
    y='placement',
    color='riotidgamename',
    title='Bar Chart of Placement over Time'
)
bar_chart_plotly.update_layout(
    xaxis_title='Game Date',
    yaxis_title='Placement',
    yaxis=dict(range=[8, 1])  # Reverse the y-axis to have 1 at the top
)

# Display the custom scatter chart in Streamlit
st.altair_chart(scatter_chart, use_container_width=True)

# Display the custom bar chart with Altair in Streamlit
st.altair_chart(bar_chart_altair, use_container_width=True)

# Display the custom bar chart with Plotly in Streamlit
st.plotly_chart(bar_chart_plotly, use_container_width=True)
