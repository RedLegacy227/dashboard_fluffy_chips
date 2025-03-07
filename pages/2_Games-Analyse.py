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

    # Load data for the last 7 games of the home team
    home_last_7 = historical_data[
        (historical_data["Home"] == selected_home) &
        (historical_data['League'] == selected_league) &
        (historical_data["Date"] <= pd.to_datetime(selected_date))
    ].sort_values(by="Date", ascending=False).head(7)

    if not home_last_7.empty:
        st.markdown(f"#### Last 7 Games of ***{selected_home}*** - Playing @Home ####")
        columns_to_show = [
            'Date', 'League', 'Season', 'Home', 'Away', 'HT_Goals_H', 'HT_Goals_A', 'FT_Goals_H', 'FT_Goals_A',
            'FT_Odd_H', 'FT_Odd_D', 'FT_Odd_A', 'FT_Odd_Over25', 'Odd_BTTS_Yes', 'Goals_Minutes_Home', 'Goals_Minutes_Away'
        ]
        home_last_7_filt = home_last_7[columns_to_show]
        st.dataframe(home_last_7_filt)

        # Plot pie chart and bar chart side by side for home team
        col1, col2 = st.columns(2)

        with col1:
            # Pie chart
            home_wins = len(home_last_7[home_last_7["FT_Goals_H"] > home_last_7["FT_Goals_A"]])
            away_wins = len(home_last_7[home_last_7["FT_Goals_A"] > home_last_7["FT_Goals_H"]])
            draws = len(home_last_7[home_last_7["FT_Goals_H"] == home_last_7["FT_Goals_A"]])

            labels = ['Home Wins', 'Draws', 'Away Wins']
            sizes = [home_wins, draws, away_wins]
            colors = ['darkgreen', 'cyan', 'orange']

            fig4, ax4 = plt.subplots(figsize=(10, 9.1))
            wedges, texts, autotexts = ax4.pie(
                sizes,
                autopct='%1.1f%%',
                startangle=90,
                colors=colors,
                textprops=dict(color="white", weight="bold", fontsize=40)
            )
            ax4.axis('equal')
            ax4.set_title(f"{selected_home} - Last 7 Games @Home", fontsize=20)
            ax4.legend(
                wedges, labels, title="Results", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1), fontsize=20
            )
            st.pyplot(fig4)

            # Statistics for the last 7 home games
            total_games_home = len(home_last_7)
            tendency_over_ht_home = len(home_last_7[
                (home_last_7["HT_Goals_H"] + home_last_7["HT_Goals_A"]) > 0
            ]) / total_games_home * 100

            tendency_over_home = len(home_last_7[
                (home_last_7["FT_Goals_H"] + home_last_7["FT_Goals_A"]) > 2
            ]) / total_games_home * 100

            tendency_btts_home = len(home_last_7[
                (home_last_7["FT_Goals_H"] > 0) & (home_last_7["FT_Goals_A"] > 0)
            ]) / total_games_home * 100

            home_last_7["Score"] = home_last_7["FT_Goals_H"].astype(int).astype(str) + "x" + home_last_7["FT_Goals_A"].astype(int).astype(str)
            top_scores_home = home_last_7["Score"].value_counts().head(7)

            st.divider()
            st.markdown(f"#### Tendency of Last 7 Games ####")
            st.markdown(f"Tendency Over 0.5 HT: **{tendency_over_ht_home:.2f}%**")
            st.markdown(f"Tendency Over 2.5 Goals: **{tendency_over_home:.2f}%**")
            st.markdown(f"Tendency BTTS: **{tendency_btts_home:.2f}%**")
            st.markdown("Most Frequent Scores:")
            for score, count in top_scores_home.items():
                st.markdown(f"- **{score}**: **{count}** times")

        with col2:
            # Bar chart
            home_goals = home_last_7["FT_Goals_H"]
            away_goals = home_last_7["FT_Goals_A"]

            fig5, ax5 = plt.subplots(figsize=(10, 6))
            bar_width = 0.35
            x = np.arange(len(home_last_7))

            ax5.bar(x - bar_width / 2, home_goals, bar_width, label="Home Goals", color='darkgreen', alpha=0.7)
            ax5.bar(x + bar_width / 2, away_goals, bar_width, label="Away Goals", color='orange', alpha=0.7)
            ax5.set_xticks(x)
            ax5.set_xticklabels(home_last_7["Date"].dt.strftime('%Y-%m-%d'), rotation=45)
            ax5.set_ylim(0, max(max(home_goals), max(away_goals)) + 1)
            ax5.set_ylabel("Goals")
            ax5.set_title("Goals Scored - Home Games", fontsize=20)
            ax5.legend(fontsize=20)
            st.pyplot(fig5)

    # Load data for the last 7 games of the away team
    away_last_7 = historical_data[
        (historical_data["Away"] == selected_away) &
        (historical_data['League'] == selected_league) &
        (historical_data["Date"] <= pd.to_datetime(selected_date))
    ].sort_values(by="Date", ascending=False).head(7)

    if not away_last_7.empty:
        st.markdown(f"#### Last 7 Games of ***{selected_away}*** - Playing @Away ####")
        columns_to_show = [
            'Date', 'League', 'Season', 'Home', 'Away', 'HT_Goals_H', 'HT_Goals_A', 'FT_Goals_H', 'FT_Goals_A',
            'FT_Odd_H', 'FT_Odd_D', 'FT_Odd_A', 'FT_Odd_Over25', 'Odd_BTTS_Yes', 'Goals_Minutes_Home', 'Goals_Minutes_Away'
        ]
        away_last_7_filt = away_last_7[columns_to_show]
        st.dataframe(away_last_7_filt)

        # Plot pie chart and bar chart side by side for away team
        col1, col2 = st.columns(2)

        with col1:
            # Pie chart
            home_wins = len(away_last_7[away_last_7["FT_Goals_H"] > away_last_7["FT_Goals_A"]])
            away_wins = len(away_last_7[away_last_7["FT_Goals_A"] > away_last_7["FT_Goals_H"]])
            draws = len(away_last_7[away_last_7["FT_Goals_H"] == away_last_7["FT_Goals_A"]])

            labels = ['Home Wins', 'Draws', 'Away Wins']
            sizes = [home_wins, draws, away_wins]
            colors = ['darkgreen', 'cyan', 'orange']

            fig6, ax6 = plt.subplots(figsize=(10, 9.1))
            wedges, texts, autotexts = ax6.pie(
                sizes,
                autopct='%1.1f%%',
                startangle=90,
                colors=colors,
                textprops=dict(color="white", weight="bold", fontsize=40)
            )
            ax6.axis('equal')
            ax6.set_title(f"{selected_away} - Last 7 Games @Away", fontsize=20)
            ax6.legend(
                wedges, labels, title="Results", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1), fontsize=20
            )
            st.pyplot(fig6)

            # Statistics for the last 7 away games
            total_games_away = len(away_last_7)
            tendency_over_ht_away = len(away_last_7[
                (away_last_7["HT_Goals_H"] + away_last_7["HT_Goals_A"]) > 0
            ]) / total_games_away * 100

            tendency_over_away = len(away_last_7[
                (away_last_7["FT_Goals_H"] + away_last_7["FT_Goals_A"]) > 2
            ]) / total_games_away * 100

            tendency_btts_away = len(away_last_7[
                (away_last_7["FT_Goals_H"] > 0) & (away_last_7["FT_Goals_A"] > 0)
            ]) / total_games_away * 100

            away_last_7["Score"] = away_last_7["FT_Goals_H"].astype(int).astype(str) + "x" + away_last_7["FT_Goals_A"].astype(int).astype(str)
            top_scores_away = away_last_7["Score"].value_counts().head(7)

            st.divider()
            st.markdown(f"#### Tendency of Last 7 Games ####")
            st.markdown(f"Tendency Over 0.5 HT: **{tendency_over_ht_away:.2f}%**")
            st.markdown(f"Tendency Over 2.5 Goals: **{tendency_over_away:.2f}%**")
            st.markdown(f"Tendency BTTS: **{tendency_btts_away:.2f}%**")
            st.markdown("Most Frequent Scores:")
            for score, count in top_scores_away.items():
                st.markdown(f"- **{score}**: **{count}** times")

        with col2:
            # Bar chart
            home_goals = away_last_7["FT_Goals_H"]
            away_goals = away_last_7["FT_Goals_A"]

            fig7, ax7 = plt.subplots(figsize=(10, 6))
            bar_width = 0.35
            x = np.arange(len(away_last_7))

            ax7.bar(x - bar_width / 2, home_goals, bar_width, label="Home Goals", color='darkgreen', alpha=0.7)
            ax7.bar(x + bar_width / 2, away_goals, bar_width, label="Away Goals", color='orange', alpha=0.7)
            ax7.set_xticks(x)
            ax7.set_xticklabels(away_last_7["Date"].dt.strftime('%Y-%m-%d'), rotation=45)
            ax7.set_ylim(0, max(max(home_goals), max(away_goals)) + 1)
            ax7.set_ylabel("Goals")
            ax7.set_title("Goals Scored - Away Games", fontsize=20)
            ax7.legend(fontsize=20)
            st.pyplot(fig7)

    # Load league statistics
    leagues_url = "https://raw.githubusercontent.com/RedLegacy227/dados_ligas/refs/heads/main/df_ligas.csv"
    leagues_data = load_data(leagues_url)
    if leagues_data is None:
        st.stop()  # Stop the app if league data loading fails

    if "League" in filtered_data.columns:
        selected_league = filtered_data["League"].iloc[0]
        league_stats = leagues_data[leagues_data["League"] == selected_league]

    if not league_stats.empty:
        # Average goals scored and conceded for the league
        league_avg_gm_home = league_stats["Avg_G_Scored_Home_Teams"].iloc[0]
        league_avg_gs_away = league_stats["Avg_G_Conceded_Home_Teams"].iloc[0]
        league_avg_gm_away = league_stats["Avg_G_Scored_Away_Teams"].iloc[0]
        league_avg_gs_home = league_stats["Avg_G_Conceded_Away_Teams"].iloc[0]

        # Filter historical data for the home team
        home_league_data = historical_data[
            (historical_data["League"] == selected_league) &
            (historical_data["Home"] == selected_home)
        ]
        home_goals_scored = home_league_data["FT_Goals_H"].mean()
        home_goals_conceded = home_league_data["FT_Goals_A"].mean()

        # Filter historical data for the away team
        away_league_data = historical_data[
            (historical_data["League"] == selected_league) &
            (historical_data["Away"] == selected_away)
        ]
        away_goals_scored = away_league_data["FT_Goals_A"].mean()
        away_goals_conceded = away_league_data["FT_Goals_H"].mean()

        # Calculate attack and defense powers
        attack_power_home = home_goals_scored / league_avg_gm_home
        defense_power_home = home_goals_conceded / league_avg_gs_home

        attack_power_away = away_goals_scored / league_avg_gm_away
        defense_power_away = away_goals_conceded / league_avg_gs_away

        # Display the results
        st.divider()
        st.markdown(f"#### Power Strength Analysis ####")
        st.markdown(f'Power of Attack > 1: The Team has a Superior Attack than the League Average (Strong Attack)')
        st.markdown(f'Power of Attack < 1: The Team has an Inferior Attack than the League Average (Weak Attack)')
        st.markdown(f'Power of Defense > 1: The Team has an Inferior Defense than the League Average (Weak Defense)')
        st.markdown(f'Power of Defense < 1: The Team has a Superior Defense than the League Average (Strong Defense)')
        st.markdown(f"⚽ Power of Attack for ***{selected_home}*** ➡️ ***{attack_power_home:.2f}***")
        st.markdown(f"⚽ Power of Attack for ***{selected_away}*** ➡️ ***{attack_power_away:.2f}***")
        st.markdown(f"🛡️ Power of Defense for ***{selected_home}*** ➡️ ***{defense_power_home:.2f}***")
        st.markdown(f"🛡️ Power of Defense for ***{selected_away}*** ➡️ ***{defense_power_away:.2f}***")

        # Expected Goals (xG) calculation
        xg_home = home_goals_scored * attack_power_home / defense_power_away
        xg_away = away_goals_scored * attack_power_away / defense_power_home

        st.divider()
        st.markdown(f"#### Expected Goals (xG) ####")
        st.markdown(f"🥅 Expected Goals for ***{selected_home}*** ➡️ ***{xg_home:.2f}***")
        st.markdown(f"🥅 Expected Goals for ***{selected_away}*** ➡️ ***{xg_away:.2f}***")

    else:
        st.error("League statistics not found for the selected league.")

    # Load additional statistics for the teams
    team_data = data[
        (data['Home'] == selected_home) |
        (data['Away'] == selected_away)
    ]

    if not team_data.empty:
        stats_crn_IF_home = team_data['Avg_Corners_InFavor_H'].iloc[0]
        stats_crn_Ag_home = team_data['Avg_Corners_Against_H'].iloc[0]
        stats_crn_IF_away = team_data['Avg_Corners_InFavor_A'].iloc[0]
        stats_crn_Ag_away = team_data['Avg_Corners_Against_A'].iloc[0]
        stats_shots_ot_IF_home = team_data['Avg_Shots_OnTarget_InFavor_H'].iloc[0]
        stats_shots_ot_Ag_home = team_data['Avg_Shots_OnTarget_Against_H'].iloc[0]
        stats_shots_ot_IF_away = team_data['Avg_Shots_OnTarget_InFavor_A'].iloc[0]
        stats_shots_ot_Ag_away = team_data['Avg_Shots_OnTarget_Against_A'].iloc[0]
        stats_shots_ot_pG_IF_home = team_data['Avg_Shots_OnTarget_per_Goal_InFavor_H'].iloc[0]
        stats_shots_ot_pG_Ag_home = team_data['Avg_Shots_OnTarget_per_Goal_Against_H'].iloc[0]
        stats_shots_ot_pG_IF_away = team_data['Avg_Shots_OnTarget_per_Goal_InFavor_A'].iloc[0]
        stats_shots_ot_pG_Ag_away = team_data['Avg_Shots_OnTarget_per_Goal_Against_A'].iloc[0]
        stats_G_Attempts_pG_IF_home = team_data['Avg_Goal_Attempt_per_Goal_InFavor_H'].iloc[0]
        stats_G_Attempts_pG_Ag_home = team_data['Avg_Goal_Attempts_per_Goal_Against_H'].iloc[0]
        stats_G_Attempts_pG_IF_away = team_data['Avg_Goal_Attempt_per_Goal_InFavor_A'].iloc[0]
        stats_G_Attempts_pG_Ag_away = team_data['Avg_Goal_Attempts_per_Goal_Against_A'].iloc[0]
        stats_yellow_cards_home = team_data['Avg_Yellow_Cards_H'].iloc[0]
        stats_yellow_cards_away = team_data['Avg_Yellow_Cards_A'].iloc[0]
        stats_red_cards_home = team_data['Avg_Red_Cards_H'].iloc[0]
        stats_red_cards_away = team_data['Avg_Red_Cards_A'].iloc[0]

        st.divider()
        st.markdown(f"#### Average Stats on the Last 7 Games ####")
        st.markdown(f"🎯 Shots On Target In Favor ***{selected_home}*** ➡️ ***{stats_shots_ot_IF_home:.2f}***")
        st.markdown(f"🎯 Shots On Target Against ***{selected_home}*** ➡️ ***{stats_shots_ot_Ag_home:.2f}***")
        st.markdown(f"🎯 Shots On Target In Favor ***{selected_away}*** ➡️ ***{stats_shots_ot_IF_away:.2f}***")
        st.markdown(f"🎯 Shots On Target Against ***{selected_away}*** ➡️ ***{stats_shots_ot_Ag_away:.2f}***")

        st.markdown(f"⚽ Shots On Target per Goal In Favor ***{selected_home}*** ➡️ ***{stats_shots_ot_pG_IF_home:.2f}***")
        st.markdown(f"⚽ Shots On Target per Goal Against ***{selected_home}*** ➡️ ***{stats_shots_ot_pG_Ag_home:.2f}***")
        st.markdown(f"⚽ Shots On Target per Goal In Favor ***{selected_away}*** ➡️ ***{stats_shots_ot_pG_IF_away:.2f}***")
        st.markdown(f"⚽ Shots On Target per Goal Against ***{selected_away}*** ➡️ ***{stats_shots_ot_pG_Ag_away:.2f}***")

        st.markdown(f"🥅 Goal Attempt per Goal In Favor ***{selected_home}*** ➡️ ***{stats_G_Attempts_pG_IF_home:.2f}***")
        st.markdown(f"🥅 Goal Attempt per Goal Against ***{selected_home}*** ➡️ ***{stats_G_Attempts_pG_Ag_home:.2f}***")
        st.markdown(f"🥅 Goal Attempt per Goal In Favor ***{selected_away}*** ➡️ ***{stats_G_Attempts_pG_IF_away:.2f}***")
        st.markdown(f"🥅 Goal Attempt per Goal Against ***{selected_away}*** ➡️ ***{stats_G_Attempts_pG_Ag_away:.2f}***")

        st.markdown(f"🚩 Corners Average In Favor ***{selected_home}*** ➡️ ***{stats_crn_IF_home:.2f}***")
        st.markdown(f"🚩 Corners Average Against ***{selected_home}*** ➡️ ***{stats_crn_Ag_home:.2f}***")
        st.markdown(f"🚩 Corners Average In Favor ***{selected_away}*** ➡️ ***{stats_crn_IF_away:.2f}***")
        st.markdown(f"🚩 Corners Average Against ***{selected_away}*** ➡️ ***{stats_crn_Ag_away:.2f}***")
        
        st.markdown(f"🟨 Yellow Cards Taken ***{selected_home}*** ➡️ ***{stats_yellow_cards_home:.2f}***")
        st.markdown(f"🟨 Yellow Cards Taken ***{selected_home}*** ➡️ ***{stats_yellow_cards_away:.2f}***")
        st.markdown(f"🟥 Red Cards Taken ***{selected_away}*** ➡️ ***{stats_red_cards_home:.2f}***")
        st.markdown(f"🟥 Red Cards Taken ***{selected_away}*** ➡️ ***{stats_red_cards_away:.2f}***")

    else:
        st.error("Not enough data available for the selected teams.")

    # Load data for the last 21 games of the home team
    past_games_home = historical_data[
        (historical_data['Home'] == selected_home) &
        (historical_data['Date'] < pd.to_datetime(selected_date))
    ].tail(21)
    
    # Load data for the last 21 games of the away team
    past_games_away = historical_data[
        (historical_data['Away'] == selected_away) &
        (historical_data['Date'] < pd.to_datetime(selected_date))
    ].tail(21)
    
    # Function to summarize goals in time segments
    def summarize_half_goals(goals, half_segments):
        return sum([goals[segment] for segment in half_segments])
    
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
        return fig
    
    # Plot goal distribution for the home team
    st.divider()
    st.markdown(f"#### Time of Goals of ***{selected_home}*** and ***{selected_away}*** on the last 21 Games ####")
    home_goals_scored = count_goals(past_games_home['Goals_Minutes_Home'])
    home_goals_conceded = count_goals(past_games_home['Goals_Minutes_Away'])
    fig_home = plot_goal_distribution(selected_home, home_goals_scored, home_goals_conceded)
    
    # Plot goal distribution for the away team
    away_goals_scored = count_goals(past_games_away['Goals_Minutes_Away'])
    away_goals_conceded = count_goals(past_games_away['Goals_Minutes_Home'])
    fig_away = plot_goal_distribution(selected_away, away_goals_scored, away_goals_conceded)
    
    # Display the plots side by side
    col1, col2 = st.columns(2)
    with col1:
        st.pyplot(fig_home)
    with col2:
        st.pyplot(fig_away)
    
    # Calculate first half and second half goals for both teams
    home_first_half_goals = sum([home_goals_scored[segment] for segment in ['0-15', '15-30', '30-45']])
    home_second_half_goals = sum([home_goals_scored[segment] for segment in ['45-60', '60-75', '75-90']])
    away_first_half_goals = sum([away_goals_scored[segment] for segment in ['0-15', '15-30', '30-45']])
    away_second_half_goals = sum([away_goals_scored[segment] for segment in ['45-60', '60-75', '75-90']])
    
    # Calculate first half and second half goals conceded for both teams
    home_first_half_conceded = sum([home_goals_conceded[segment] for segment in ['0-15', '15-30', '30-45']])
    home_second_half_conceded = sum([home_goals_conceded[segment] for segment in ['45-60', '60-75', '75-90']])
    away_first_half_conceded = sum([away_goals_conceded[segment] for segment in ['0-15', '15-30', '30-45']])
    away_second_half_conceded = sum([away_goals_conceded[segment] for segment in ['45-60', '60-75', '75-90']])
    
    # Plot the data side by side
    fig22, ax = plt.subplots(figsize=(10, 6))
    half_labels = ["First Half", "Second Half"]
    home_goals = [home_first_half_goals, home_first_half_conceded, home_second_half_goals, home_second_half_conceded]
    away_goals = [away_first_half_goals, away_first_half_conceded, away_second_half_goals, away_second_half_conceded]
    
    x = np.arange(len(half_labels))
    width = 0.35
    
    # Create the bar chart with 2 groups and 4 columns within each group
    fig22, ax = plt.subplots(figsize=(10, 6))
    half_labels = ["First Half", "Second Half"]
    x = np.arange(len(half_labels))  # Positions for "First Half" and "Second Half"
    width = 0.2  # Width of the bars
    
    # Add the bars with offsets within each half
    ax.bar(x - 1.5 * width, [home_first_half_goals, home_second_half_goals], width, label=f'{selected_home} Scored', color='green')
    ax.bar(x - 0.5 * width, [home_first_half_conceded, home_second_half_conceded], width, label=f'{selected_home} Conceded', color='darkgreen')
    ax.bar(x + 0.5 * width, [away_first_half_goals, away_second_half_goals], width, label=f'{selected_away} Scored', color='blue')
    ax.bar(x + 1.5 * width, [away_first_half_conceded, away_second_half_conceded], width, label=f'{selected_away} Conceded', color='darkblue')
    
    # Configure the labels of the chart
    ax.set_xticks(x)
    ax.set_xticklabels(half_labels)
    ax.set_ylabel("Goals")
    ax.set_title("First & Second Half Goals")
    ax.legend()
    ax.grid(axis="y", linestyle="--", alpha=0.7)
    
    with col1:
        st.markdown(f"#### First Half & Second Half Goals Distribution on the Last 21 Games ####")
        # Display the plot
        st.pyplot(fig22)
    
    home_first_goal, home_conceded_first = count_first_goal(
    past_games_home['Goals_Minutes_Home'], past_games_home['Goals_Minutes_Away']
    )
    
    away_first_goal, away_conceded_first = count_first_goal(
        past_games_away['Goals_Minutes_Away'], past_games_away['Goals_Minutes_Home']
    )
    
    # Create a bar chart to display the first goal occurrences
    fig27, ax = plt.subplots(figsize=(10, 6))
    
    # Labels and data for the bar chart
    labels = [f'{selected_home} Scored First', f'{selected_home} Conceded First', f'{selected_away} Scored First', f'{selected_away} Conceded First']
    values = [home_first_goal, home_conceded_first, away_first_goal, away_conceded_first]
    colors = ['green', 'darkgreen', 'red', 'darkred']
    
    # Create the bar chart
    ax.bar(labels, values, color=colors)
    
    # Configure the labels of the chart
    ax.set_ylabel("Number of Times")
    ax.set_title("First Goal Occurrences in the Last 21 Games")
    ax.grid(axis="y", linestyle="--", alpha=0.7)
    
    with col2:
        st.markdown(f"#### Who Scored and Conceded First in the Last 21 Games? ####")
        # Display the chart in Streamlit
        st.pyplot(fig27)

except Exception as e:
    st.error(f"General Error: {e}")