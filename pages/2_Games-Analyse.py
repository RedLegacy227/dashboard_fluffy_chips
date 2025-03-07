import pandas as pd
import math
import seaborn as sns
import streamlit as st
from PIL import Image
from scipy.stats import poisson
import os
import base64
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
from auth import logout
from sidebar_menu import show_role_features
import ast

# Set up the Streamlit page configuration
st.set_page_config(page_title="Games Analyser - Fluffy Chips Web Analyser", page_icon="📽️", layout="wide")

# Check if the user is logged in
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.switch_page("Login.py")  # Redirect to login page

# Show role-based features in the sidebar
show_role_features()

# Title and welcome message
st.title("📽️ Games Analyser - Fluffy Chips")
st.markdown(f"#### The place where you can Analyse Football Matches!!! ####")
st.markdown(f"Welcome, **{st.session_state['username']}**!")
st.markdown(f"Your role: **{st.session_state['role']}**")
st.divider()

# Display the image
image_path = os.path.join(os.getcwd(), 'static', 'analises002.png')
st.markdown(
    f"""
    <div style="text-align: center;">
        <img src="data:image/png;base64,{base64.b64encode(open(image_path, "rb").read()).decode()}" alt="Analysis" width="100%">
    </div>
    """,
    unsafe_allow_html=True
)
st.divider()

# Base URL for GitHub CSV files
github_base_url = "https://raw.githubusercontent.com/RedLegacy227/jogos_do_dia_com_variaveis/main/"

# Function to load data from a URL
def load_data(url):
    try:
        data = pd.read_csv(url)
        return data
    except Exception as e:
        st.error(f"Failed to load data from {url}: {e}")
        return None

# Function to filter data based on date and league
def filter_data(data, date, league):
    try:
        filtered_data = data[
            (data['Date'] < pd.to_datetime(date)) &
            (data['League'] == league)
        ]
        if filtered_data.empty:
            raise ValueError("No historical data available for the selected date and league.")
        return filtered_data
    except Exception as e:
        st.error(f"Error filtering data: {e}")
        return None

# Function to count goals per time segment
def count_goals(goals_list):
    time_segments = {"0-15": 0, "15-30": 0, "30-45": 0, "45-60": 0, "60-75": 0, "75-90": 0}
    for goals in goals_list:
        if isinstance(goals, str):
            goal_times = ast.literal_eval(goals)
            for minute in goal_times:
                if 0 <= minute < 15:
                    time_segments["0-15"] += 1
                elif 15 <= minute < 30:
                    time_segments["15-30"] += 1
                elif 30 <= minute < 45:
                    time_segments["30-45"] += 1
                elif 45 <= minute < 60:
                    time_segments["45-60"] += 1
                elif 60 <= minute < 75:
                    time_segments["60-75"] += 1
                elif 75 <= minute < 90:
                    time_segments["75-90"] += 1
    return time_segments

# Function to plot goal distribution
def plot_goal_distribution(team_name, goals, conceded):
    fig, ax = plt.subplots(figsize=(10, 6))
    x_labels = list(goals.keys())
    x = np.arange(len(x_labels))
    width = 0.35

    ax.bar(x - width/2, goals.values(), width, label='Scored', color='green')
    ax.bar(x + width/2, conceded.values(), width, label='Conceded', color='red')
    ax.set_xticks(x)
    ax.set_xticklabels(x_labels, rotation=45)
    ax.set_ylabel("Goals")
    ax.set_title(f"Goal Distribution - {team_name}")
    ax.legend()
    st.pyplot(fig)

# Function to count first goal occurrences
def count_first_goal(goals_scored_list, goals_conceded_list):
    count_scored_first = 0
    count_conceded_first = 0

    for goals_scored, goals_conceded in zip(goals_scored_list, goals_conceded_list):
        try:
            scored_times = ast.literal_eval(goals_scored) if isinstance(goals_scored, str) else []
            conceded_times = ast.literal_eval(goals_conceded) if isinstance(goals_conceded, str) else []
        except (SyntaxError, ValueError):
            continue  # Skip invalid entries

        if scored_times and conceded_times:  # Both teams scored
            if min(scored_times) < min(conceded_times):
                count_scored_first += 1  # Team scored first
            else:
                count_conceded_first += 1  # Team conceded first
        elif scored_times:  # Only this team scored
            count_scored_first += 1
        elif conceded_times:  # Only the opponent scored
            count_conceded_first += 1

    return count_scored_first, count_conceded_first

# Main application logic
try:
    # Select a date
    selected_date = st.date_input("Select a date:", value=datetime.today())
    formatted_date = selected_date.strftime("%Y-%m-%d")

    # Build the CSV file URL based on the selected date
    csv_file_name = f'df_jogos_do_dia_{formatted_date}.csv'
    csv_file_url = github_base_url + csv_file_name

    # Load the CSV data
    data = load_data(csv_file_url)
    if data is None:
        st.stop()  # Stop the app if data loading fails

    if "Home" not in data.columns or "Away" not in data.columns:
        raise ValueError("CSV file is missing required columns 'Home' or 'Away'.")

    # Create a dropdown menu to select a game
    games_list = data.apply(lambda row: f"{row['Home']} x {row['Away']}", axis=1).tolist()
    selected_game = st.selectbox("Select a game:", games_list)

    st.markdown(f"#### Selected Game ➡️ ***{selected_game}*** ####")
    st.divider()

    # Split the selected game into home and away teams
    selected_home, selected_away = selected_game.split(" x ")

    # Determine the league based on the selected game
    selected_league = data[data['Home'] == selected_home].iloc[0]['League']

    # Load historical data
    historical_data_url = "https://raw.githubusercontent.com/RedLegacy227/main_data_base/refs/heads/main/df_base_original.csv"
    historical_data = load_data(historical_data_url)
    if historical_data is None:
        st.stop()  # Stop the app if historical data loading fails

    historical_data['Date'] = pd.to_datetime(historical_data["Date"])

    # Filter historical data by date and league
    filtered_data = filter_data(historical_data, selected_date, selected_league)
    if filtered_data is None:
        st.stop()  # Stop the app if filtering fails

    required_columns = [
        'Date', 'League', 'Season', 'Home', 'Away', 'HT_Goals_H', 'HT_Goals_A', 'FT_Goals_H', 'FT_Goals_A', 'FT_Odd_H', 'FT_Odd_D', 'FT_Odd_A', 'FT_Odd_Over25', 'Odd_BTTS_Yes', 'Goals_Minutes_Home', 'Goals_Minutes_Away'
    ]

    if not all(col in filtered_data.columns for col in required_columns):
        raise ValueError("Historical data is missing required columns.")

    filtered_data = filtered_data[
        (filtered_data["Home"] == selected_home) & (filtered_data["Away"] == selected_away) & (filtered_data['League'] == selected_league)
    ][required_columns]

    if not filtered_data.empty:
        st.markdown(f"#### Past Games Between ***{selected_home}*** and ***{selected_away}*** ####")
        st.dataframe(filtered_data)

        # Plot pie chart and bar chart side by side
        col1, col2 = st.columns(2)

        with col1:
            # Pie chart
            home_wins = len(filtered_data[filtered_data["FT_Goals_H"] > filtered_data["FT_Goals_A"]])
            away_wins = len(filtered_data[filtered_data["FT_Goals_A"] > filtered_data["FT_Goals_H"]])
            draws = len(filtered_data[filtered_data["FT_Goals_H"] == filtered_data["FT_Goals_A"]])

            labels = ['Home Wins', 'Draws', 'Away Wins']
            sizes = [home_wins, draws, away_wins]
            colors = ['darkgreen', 'cyan', 'orange']

            fig1, ax1 = plt.subplots(figsize=(10, 10))
            wedges, texts, autotexts = ax1.pie(
                sizes,
                autopct='%1.1f%%',
                startangle=90,
                colors=colors,
                textprops=dict(color="white", weight="bold", fontsize=40)
            )
            ax1.axis('equal')
            ax1.set_title("Final Result", fontsize=20)
            ax1.legend(
                wedges, labels, title="Results", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1), fontsize=20
            )
            st.pyplot(fig1)

            # Line chart (Odds)
            fig3, ax3 = plt.subplots(figsize=(10, 6))
            ax3.plot(filtered_data["Date"], filtered_data["FT_Odd_H"], color='darkgreen', label='FT_Odd_H')
            ax3.plot(filtered_data["Date"], filtered_data["FT_Odd_D"], color='cyan', label='FT_Odd_D')
            ax3.plot(filtered_data["Date"], filtered_data["FT_Odd_A"], color='orange', label='FT_Odd_A')
            ax3.set_xlabel('Date')
            ax3.set_ylabel('Odds')
            ax3.legend(fontsize=20)
            ax3.set_title('Odds Trends', fontsize=20)
            ax3.grid(True)
            st.pyplot(fig3)

        with col2:
            # Bar chart
            games = filtered_data["Date"]
            home_goals = filtered_data["FT_Goals_H"]
            away_goals = filtered_data["FT_Goals_A"]

            fig2, ax2 = plt.subplots(figsize=(10, 6.2))
            bar_width = 0.35
            x = np.arange(len(games))

            ax2.bar(x - bar_width / 2, home_goals, bar_width, label="Home Goals", color='darkgreen', alpha=0.7)
            ax2.bar(x + bar_width / 2, away_goals, bar_width, label="Away Goals", color='orange', alpha=0.7)

            ax2.set_xticks(x)
            ax2.set_xticklabels(games, rotation=45)
            ax2.set_ylabel("Goals")
            ax2.set_ylim(0, max(max(home_goals), max(away_goals)) + 1)
            ax2.set_title("Goals Scored", fontsize=20)
            ax2.legend(fontsize=20)

            st.pyplot(fig2)

            # Additional statistics
            total_games = len(filtered_data)

            tendency_over_ht = len(filtered_data[
                (filtered_data["HT_Goals_H"] + filtered_data["HT_Goals_A"]) > 0
            ]) / total_games * 100

            tendency_over = len(filtered_data[
                (filtered_data["FT_Goals_H"] + filtered_data["FT_Goals_A"]) > 2
            ]) / total_games * 100

            tendency_btts = len(filtered_data[
                (filtered_data["FT_Goals_H"] > 0) & (filtered_data["FT_Goals_A"] > 0)
            ]) / total_games * 100

            filtered_data["Score"] = filtered_data["FT_Goals_H"].astype(int).astype(str) + "x" + filtered_data["FT_Goals_A"].astype(int).astype(str)
            top_scores = filtered_data["Score"].value_counts().head(7)

            st.divider()
            st.markdown(f"#### Tendency of the H2H ####")
            st.markdown(f"Tendency Over 0.5 HT: **{tendency_over_ht:.2f}%**")
            st.markdown(f"Tendency Over 2.5 Goals: **{tendency_over:.2f}%**")
            st.markdown(f"Tendency BTTS (Both Teams to Score): **{tendency_btts:.2f}%**")
            st.markdown("Most Frequent Scores:")
            for score, count in top_scores.items():
                st.markdown(f"- **{score}**: **{count}** times")

    else:
        st.info(f"No past games found between {selected_home} and {selected_away} in the same home field.")

except Exception as e:
    st.error(f"General Error: {e}")