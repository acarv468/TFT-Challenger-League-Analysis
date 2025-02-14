import streamlit as st
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from config import config
import plotly.express as px

# Set the page layout to wide
st.set_page_config(layout="wide")

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

# Calculate KPIs
average_placement = data['placement'].mean()
total_damage = data['total_damage_to_players'].mean()
average_gold_left = data['gold_left'].mean()
total_players_eliminated = data['players_eliminated'].mean()
average_win_pct = (data['win'].sum() / len(data)) * 100

# Display KPI callout cards in columns
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric(label="Average Placement", value=f"{average_placement:.2f}")
col2.metric(label="Win Percentage", value=f"{average_win_pct:.2f}%")
col3.metric(label="Average Damage to Players", value=f"{total_damage:.2f}")
col4.metric(label="Average Gold Left", value=f"{average_gold_left:.2f}")
col5.metric(label="Average Players Eliminated", value=f"{total_players_eliminated:.2f}")

# Create a custom scatter plot with Plotly
scatter_plot1 = px.scatter(
    data,
    x='total_damage_to_players',
    y='placement',
    color='riotidgamename',
    hover_data=['riotidgamename', 'total_damage_to_players', 'placement', 'p_match_id'],
    title='Scatter Plot of Total Damage to Players vs Placement'
)
scatter_plot1.update_layout(
    xaxis_title='Total Damage to Players',
    yaxis_title='Placement',
    yaxis=dict(range=[8, 1])  # Reverse the y-axis to have 1 at the top
)

# Create a custom scatter plot with Plotly
scatter_plot2 = px.scatter(
    data,
    x='gold_left',
    y='placement',
    color='riotidgamename',
    hover_data=['riotidgamename', 'gold_left', 'placement', 'p_match_id'],
    title='Scatter Plot of Gold Left vs Placement'
)
scatter_plot2.update_layout(
    xaxis_title='Gold Remaining',
    yaxis_title='Placement',
    yaxis=dict(range=[8, 1])  # Reverse the y-axis to have 1 at the top
)

# Create a custom scatter plot with Plotly
scatter_plot3 = px.scatter(
    data,
    x='last_round',
    y='placement',
    color='riotidgamename',
    hover_data=['riotidgamename', 'last_round', 'placement', 'p_match_id'],
    title='Scatter Plot of Last Round vs Placement'
)
scatter_plot3.update_layout(
    xaxis_title='Last Round',
    yaxis_title='Placement',
    yaxis=dict(range=[8, 1])  # Reverse the y-axis to have 1 at the top
)

# Create a custom scatter plot with Plotly
scatter_plot4 = px.scatter(
    data,
    x='players_eliminated',
    y='placement',
    color='riotidgamename',
    hover_data=['riotidgamename', 'players_eliminated', 'placement', 'p_match_id'],
    title='Scatter Plot of Players Eliminated vs Placement'
)
scatter_plot4.update_layout(
    xaxis_title='Players Eliminated',
    yaxis_title='Placement',
    yaxis=dict(range=[8, 1])  # Reverse the y-axis to have 1 at the top
)

# Create two columns for scatter plots
scatter_col1, scatter_col2 = st.columns(2)

# Display the custom scatter plots with Plotly in Streamlit
scatter_col1.plotly_chart(scatter_plot1, use_container_width=True)
scatter_col1.plotly_chart(scatter_plot2, use_container_width=True)
scatter_col2.plotly_chart(scatter_plot3, use_container_width=True)
scatter_col2.plotly_chart(scatter_plot4, use_container_width=True)

# Display the data in Streamlit
st.write(data)

