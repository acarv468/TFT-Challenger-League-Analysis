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
    WHERE p.riotidgamename IN ('waxade', 'LittleHuman', 'Sonariq', 'MiniButt', 'WizardHatDave');
'''

# Get data from the database
data = get_data_from_db(query)

# Create two columns for filters
filter_col1, filter_col2 = st.columns(2)

# Filter options for riotidgamename
riotidgamename_options = data['riotidgamename'].unique()
selected_riotidgamename = filter_col1.multiselect('Select Riot ID Game Name(s)', riotidgamename_options, default=riotidgamename_options)

# Filter options for game date
min_date = data['game_datetime'].min()
max_date = data['game_datetime'].max()
selected_date_range = filter_col2.date_input('Select Game Date Range', [min_date, max_date])

# Filter data based on selected riotidgamename and game date range
filtered_data = data[
    (data['riotidgamename'].isin(selected_riotidgamename)) &
    (data['game_datetime'] >= pd.to_datetime(selected_date_range[0])) &
    (data['game_datetime'] <= pd.to_datetime(selected_date_range[1]))
]

# Calculate KPIs
average_placement = filtered_data['placement'].mean()
total_damage = filtered_data['total_damage_to_players'].mean()
average_gold_left = filtered_data['gold_left'].mean()
total_players_eliminated = filtered_data['players_eliminated'].mean()
average_win_pct = (filtered_data['win'].sum() / len(filtered_data)) * 100

# Display KPI callout cards in columns
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric(label="Average Placement", value=f"{average_placement:.2f}")
col2.metric(label="Win Percentage", value=f"{average_win_pct:.2f}%")
col3.metric(label="Average Damage to Players", value=f"{total_damage:.2f}")
col4.metric(label="Average Gold Left", value=f"{average_gold_left:.2f}")
col5.metric(label="Average Players Eliminated", value=f"{total_players_eliminated:.2f}")

# Aggregate data by week
filtered_data['week'] = filtered_data['game_datetime'].dt.to_period('W').apply(lambda r: r.start_time)

# Create bar chart for average placement by riotidgamename aggregated by week
bar_chart1 = px.bar(
    filtered_data.groupby(['week', 'riotidgamename']).agg({'placement': 'mean'}).reset_index(),
    x='week',
    y='placement',
    color='riotidgamename',
    title='Average Placement by Riot ID Game Name (Weekly)',
    labels={'placement': 'Average Placement', 'week': 'Week'}
)
bar_chart1.update_layout(xaxis_title='Week', yaxis_title='Average Placement', barmode='group')

# Create bar chart for average damage to players by riotidgamename aggregated by week
bar_chart2 = px.bar(
    filtered_data.groupby(['week', 'riotidgamename']).agg({'total_damage_to_players': 'mean'}).reset_index(),
    x='week',
    y='total_damage_to_players',
    color='riotidgamename',
    title='Average Damage to Players by Riot ID Game Name (Weekly)',
    labels={'total_damage_to_players': 'Average Damage to Players', 'week': 'Week'}
)
bar_chart2.update_layout(xaxis_title='Week', yaxis_title='Average Damage to Players', barmode='group')

# Display the bar charts in columns
bar_col1, bar_col2 = st.columns(2)
bar_col1.plotly_chart(bar_chart1, use_container_width=True)
bar_col2.plotly_chart(bar_chart2, use_container_width=True)

# Create a custom scatter plot with Plotly
scatter_plot1 = px.scatter(
    filtered_data,
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
    filtered_data,
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
    filtered_data,
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
    filtered_data,
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

# Display the filtered data in Streamlit
st.write(filtered_data)

