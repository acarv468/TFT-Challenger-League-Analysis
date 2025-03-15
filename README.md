# TFT Challenger League Dashboard

This project provides a comprehensive dashboard for analyzing data from the TFT (Teamfight Tactics) Challenger League using Riot Games' Developer API. The dashboard is built using Streamlit and includes various visualizations and metrics to help users gain insights into the top players, units, traits, and items used in the Challenger League.

## Features

- **Player Leaderboard**: Displays the top 10 players in the Challenger League based on league points.
- **Unit Analysis**: Provides visualizations of the most used units, including a stacked bar chart showing the count of each unit by tier.
- **Trait Analysis**: Displays the count of each trait used by players.
- **Item Analysis**: Shows the most often used items for selected units.
- **Team Composition**: Visualizes the team composition for selected units, showing the highest count of other characters that have the same `puuid` and `match_id` as the selected character.
- **KPI Metrics**: Displays key performance indicators such as average placement, win percentage, average damage to players, average gold left, and average players eliminated.

## Project Structure

- `challenger_dashboard.py`: Main Streamlit application file that creates the dashboard.
- `puuid_finder.py`: Script to get PUUID from Riot ID and tagline.
- `challenger_search.py`: Script to fetch Challenger League data from Riot Games' API.
- `tftpal.py`: Gets all necessary data from the Riot Games API to the PostgreSQL DB
- `config.py`: DB connection, parsing, and authorization handling
- `requirements.txt`: List of required Python packages.
- `README.md`: Project documentation.

<!-- ## Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/your-username/TFT_Challenger_League.git
   cd TFT_Challenger_League
   ```
2. Create and activate a virtual environment:
    ```sh
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .\.venv\Scripts\activate
    ```
3. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```
4. Set up the environment variables:
    - create a .env file in the project root directory.
    - Add your Riot API key to the .env file:
      ```sh
      RIOT_API_KEY=your_riot_api_key
      ``` -->

