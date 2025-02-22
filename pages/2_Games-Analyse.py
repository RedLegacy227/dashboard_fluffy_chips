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

st.set_page_config(page_title="Games Analyser - Fluffy Chips Web Analyser", page_icon="📽️", layout="wide")
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.switch_page("Login.py")  # Redireciona para a página de login
# ✅ Show role-based features in the sidebar
show_role_features()
st.title("📽️ Games Analyser - Fluffy Chips")
st.markdown(f"#### The place where you can Analyse Football Matches!!! ####")
st.markdown(f"Welcome, **{st.session_state['username']}**!")
st.markdown(f"Your role: **{st.session_state['role']}**")
st.divider()
st.markdown(f'#### 📆Games of the Day📆 ####')
# Caminho para a imagem
image_path = os.path.join(os.getcwd(), 'static', 'analises002.png')
# HTML e CSS para centralizar
st.markdown(
    f"""
    <div style="text-align: center;">
        <img src="data:image/png;base64,{base64.b64encode(open(image_path, "rb").read()).decode()}" alt="Analysis" width="100%">
    </div>
    """,
    unsafe_allow_html=True
)
st.divider()
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.switch_page("Login.py")  # Redirect to login page

# URL base do GitHub para os arquivos CSV
github_base_url = "https://raw.githubusercontent.com/RedLegacy227/jogos_do_dia_com_variaveis/main/"

# Escolher uma data
selected_date = st.date_input("Select a date:", value=datetime.today())
formatted_date = selected_date.strftime("%Y-%m-%d")

# Construir a URL do arquivo baseado na data
csv_file_name = f'df_jogos_do_dia_{formatted_date}.csv'
csv_file_url = github_base_url + csv_file_name

# Tentar carregar o CSV
try:
    data = pd.read_csv(csv_file_url)
    if "Home" in data.columns and "Away" in data.columns:
        games_list = data.apply(lambda row: f"{row['Home']} x {row['Away']}", axis=1).tolist()

        # Menu dropdown para selecionar um jogo
        selected_game = st.selectbox("Select a game:", games_list)

        st.markdown(f"#### Selected Game ➡️ ***{selected_game}*** ####")
        st.divider()

        # Dividir o jogo em Home e Away
        selected_home, selected_away = selected_game.split(" x ")
        
        # Escolher a liga baseada na seleção do jogo
        selected_league = data[data['Home'] == selected_home].iloc[0]['League']

        # Carregar dados históricos
        historical_data_url = "https://raw.githubusercontent.com/RedLegacy227/main_data_base/refs/heads/main/df_base_original.csv"
        
        historical_data = pd.read_csv(historical_data_url)
        historical_data['Date'] = pd.to_datetime(historical_data["Date"])
        # Filtrar dados históricos por data e liga
        filtered_data = historical_data[(historical_data['Date'] < pd.to_datetime(selected_date)) & (historical_data['League'] == selected_league)]
        try:
            required_columns = [
                'Date', 'League', 'Season', 'Home', 'Away', 'HT_Goals_H', 'HT_Goals_A', 'FT_Goals_H', 'FT_Goals_A', 'FT_Odd_H', 'FT_Odd_D', 'FT_Odd_A','FT_Odd_Over25', 'Odd_BTTS_Yes'
            ]

            if all(col in filtered_data.columns for col in required_columns):
                filtered_data = filtered_data[
                    (filtered_data["Home"] == selected_home) & (filtered_data["Away"] == selected_away) & (filtered_data['League'] == selected_league)
                    ][required_columns]
                
                if not filtered_data.empty:
                    st.markdown(f"#### Past Games Between ***{selected_home}*** and ***{selected_away}*** ####")
                    st.dataframe(filtered_data)

                    # **Gráfico de Pizza e Barras lado a lado**
                    col1, col2 = st.columns(2)

                    with col1:
                        # Gráfico de Pizza
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
                        ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
                        ax1.set_title("Final Result", fontsize=20)
                        ax1.legend(
                            wedges, labels, title="Results", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1), fontsize=20
                        )
                        st.pyplot(fig1)
                        
                        # Gráfico de Linhas (Odds)
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
                        # Gráfico de Barras
                        games = filtered_data["Date"]
                        home_goals = filtered_data["FT_Goals_H"]
                        away_goals = filtered_data["FT_Goals_A"]

                        fig2, ax2 = plt.subplots(figsize=(10, 6.2))
                        bar_width = 0.35
                        x = np.arange(len(games))

                        # Barras lado a lado para gols por jogo
                        ax2.bar(x - bar_width / 2, home_goals, bar_width, label="Home Goals", color='darkgreen', alpha=0.7)
                        ax2.bar(x + bar_width / 2, away_goals, bar_width, label="Away Goals", color='orange', alpha=0.7)

                        # Configurar o gráfico
                        ax2.set_xticks(x)
                        ax2.set_xticklabels(games, rotation=45)
                        ax2.set_ylabel("Goals")
                        ax2.set_ylim(0, max(max(home_goals), max(away_goals)) + 1)
                        ax2.set_title("Goals Scored", fontsize=20)
                        ax2.legend(fontsize=20)

                        st.pyplot(fig2)
                        
                        # Estatísticas adicionais
                        total_games = len(filtered_data)
                        
                        # Tendency Over 0.5 HT
                        tendency_over_ht = len(filtered_data[
                            (filtered_data["HT_Goals_H"] + filtered_data["HT_Goals_A"]) > 0
                            ]) / total_games * 100
                        
                        # Tendency Over 2.5 FT
                        tendency_over = len(filtered_data[
                            (filtered_data["FT_Goals_H"] + filtered_data["FT_Goals_A"]) > 2
                            ]) / total_games * 100
                        
                        # Tendency BTTS
                        tendency_btts = len(filtered_data[
                            (filtered_data["FT_Goals_H"] > 0) & (filtered_data["FT_Goals_A"] > 0)
                            ]) / total_games * 100
                        
                        # Contar os resultados mais frequentes
                        filtered_data["Score"] = filtered_data["FT_Goals_H"].astype(int).astype(str) + "x" + filtered_data["FT_Goals_A"].astype(int).astype(str)
                        top_scores = filtered_data["Score"].value_counts().head(7)
                        
                        # Exibir informações adicionais
                        st.divider() 
                        st.markdown(f"#### Tendency of the H2H ####")
                        st.markdown(f"Tendency Over 0.5 HT: **{tendency_over_ht:.2f}%**")
                        st.markdown(f"Tendency Over 2.5 Goals: **{tendency_over:.2f}%**")
                        st.markdown(f"Tendency BTTS (Both Teams to Score): **{tendency_btts:.2f}%**")
                        st.markdown("Most Frequent Scores:")
                        for score, count in top_scores.items():
                            st.markdown(f"- **{score}**: **{count}** times")
                            
                else:
                    st.info(f"Não foram encontrados jogos passados entre {selected_home} e {selected_away} no mesmo mando de campo.")
            else:
                st.error("Os dados históricos não contêm todas as colunas necessárias.")
        except Exception as e:
            st.error(f"Erro ao carregar os dados históricos: {e}")
            
        # Carregar dados do CSV e preparar análises
        try:
            data_7 = historical_data
            # Converter a coluna "Date" para datetime
            data_7["Date"] = pd.to_datetime(data_7["Date"])
            # Filtrar os últimos 7 jogos da equipe da casa (jogando em casa) até a data selecionada
            home_last_7 = data_7[(data_7["Home"] == selected_home) & (data_7['League'] == selected_league) & (data_7["Date"] <= pd.to_datetime(selected_date))
                            ].sort_values(by="Date", ascending=False).head(7)
            # Filtrar os últimos 7 jogos da equipe visitante (jogando fora) até a data selecionada
            away_last_7 = data_7[(data_7["Away"] == selected_away) & (data_7['League'] == selected_league) & (data_7["Date"] <= pd.to_datetime(selected_date))
                            ].sort_values(by="Date", ascending=False).head(7)
            st.divider()
            # **Análises para a equipe da casa**
            if not home_last_7.empty:
                st.markdown(f"#### Last 7 Games of ***{selected_home}*** - Playing @Home ####")
                st.dataframe(home_last_7)
            
            # Estatísticas e gráficos
            col1, col2 = st.columns(2)
            
            with col1:
                # Gráfico de Pizza
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
                
                # Estatísticas para os últimos 7 jogos da casa
                total_games_home = len(home_last_7)
                tendency_over_ht_home = len(home_last_7[(home_last_7["HT_Goals_H"] + home_last_7["HT_Goals_A"]) > 0
                    ]) / total_games_home * 100
                tendency_over_home = len(home_last_7[(home_last_7["FT_Goals_H"] + home_last_7["FT_Goals_A"]) > 2
                                                     ]) / total_games_home * 100
                
                tendency_btts_home = len(home_last_7[(home_last_7["FT_Goals_H"] > 0) & (home_last_7["FT_Goals_A"] > 0)
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
                # Gráfico de Barras
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
                
            st.divider()                    
            # **Análises para a equipe visitante**
            if not away_last_7.empty:
                st.markdown(f"#### Last 7 Games of ***{selected_away}*** - Playing @Away ####")
                st.dataframe(away_last_7)
                
            # Estatísticas e gráficos
            col1, col2 = st.columns(2)
            
            with col1:
                # Gráfico de Pizza
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
                
                # Estatísticas para os últimos 7 jogos de fora
                total_games_away = len(away_last_7)
                tendency_over_ht_away = len(away_last_7[(away_last_7["HT_Goals_H"] + away_last_7["HT_Goals_A"]) > 0
                    ]) / total_games_away * 100
                tendency_over_away = len(away_last_7[(away_last_7["FT_Goals_H"] + away_last_7["FT_Goals_A"]) > 2
                                                     ]) / total_games_away * 100
                
                tendency_btts_away = len(away_last_7[(away_last_7["FT_Goals_H"] > 0) & (away_last_7["FT_Goals_A"] > 0)
                                                     ]) / total_games_home * 100
                
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
                # Gráfico de Barras
                home_goals = away_last_7["FT_Goals_H"]
                away_goals = away_last_7["FT_Goals_A"]
                
                fig7, ax7 = plt.subplots(figsize=(10, 6))
                bar_width = 0.35
                x = np.arange(len(home_last_7))
                
                
                ax7.bar(x - bar_width / 2, home_goals, bar_width, label="Home Goals", color='darkgreen', alpha=0.7)
                ax7.bar(x + bar_width / 2, away_goals, bar_width, label="Away Goals", color='orange', alpha=0.7)
                ax7.set_xticks(x)
                ax7.set_xticklabels(away_last_7["Date"].dt.strftime('%Y-%m-%d'), rotation=45)
                ax7.set_ylim(0, max(max(home_goals), max(away_goals)) + 1)
                ax7.set_ylabel("Goals")
                ax7.set_title("Goals Scored - Away Games", fontsize=20)
                ax7.legend(fontsize=20)
                st.pyplot(fig7)
                
        except Exception:
            st.error(f"Not enough Data Available")
            
        st.divider()
        with col2:
            
            # Adicionar cálculo de poder de ataque e defesa
            leagues_url = "https://raw.githubusercontent.com/RedLegacy227/dados_ligas/refs/heads/main/df_ligas.csv"
            try:
                leagues_data = pd.read_csv(leagues_url)
                
                if "League" in filtered_data.columns:
                    selected_league = filtered_data["League"].iloc[0]
                    league_stats = leagues_data[leagues_data["League"] == selected_league]
                    
                if not league_stats.empty:
                    # Média de gols da liga correspondente
                    league_avg_gm_home = league_stats["Media_GM_Home_Teams"].iloc[0]
                    league_avg_gs_away = league_stats["Media_GS_Away_Teams"].iloc[0]
                    league_avg_gm_away = league_stats["Media_GM_Away_Teams"].iloc[0]
                    league_avg_gs_home = league_stats["Media_GS_Home_Teams"].iloc[0]
                    
                    # Filtrar dados históricos apenas da liga e do time da casa
                    home_league_data = historical_data[(historical_data["League"] == selected_league) & (historical_data["Home"] == selected_home)]
                    home_goals_scored = home_league_data["FT_Goals_H"].mean()
                    home_goals_conceded = home_league_data["FT_Goals_A"].mean()
            
                    # Filtrar dados históricos apenas da liga e do time visitante
                    away_league_data = historical_data[(historical_data["League"] == selected_league) & (historical_data["Away"] == selected_away)]
                    away_goals_scored = away_league_data["FT_Goals_A"].mean()
                    away_goals_conceded = away_league_data["FT_Goals_H"].mean()
                    
                    # Calcular poderes de ataque e defesa
                    attack_power_home = home_goals_scored / league_avg_gm_home
                    defense_power_home = home_goals_conceded / league_avg_gs_home
                    
                    attack_power_away = away_goals_scored / league_avg_gm_away
                    defense_power_away = away_goals_conceded / league_avg_gs_away
                    
                    # Exibir os resultados no Streamlit
                    st.divider() 
                    st.markdown(f"#### Power Strength Analysis ####")
                    st.markdown(f'Power of Attack > 1: The Team has a Superior Attack than the League Average (Strong Attack)')
                    st.markdown(f'Power of Attack < 1: The Team has an Inferior Attack than the League Average (Weak Attack)')
                    st.markdown(f'Power of Defense > 1: The Team has a Inferior Defense than the League Average (Weak Defense)')
                    st.markdown(f'Power of Defense < 1: The Team has an Superior Defense than the League Average (Strong Defense)')
                    st.markdown(f"⚽ Power of Attack for ***{selected_home}*** ➡️ **{attack_power_home:.2f}**")
                    st.markdown(f"⚽ Power of Attack for ***{selected_away}*** ➡️ **{attack_power_away:.2f}**")
                    st.markdown(f"⚽ Power of Defense for ***{selected_home}*** ➡️ **{defense_power_home:.2f}**")
                    st.markdown(f"⚽ Power of Defense for ***{selected_away}*** ➡️ **{defense_power_away:.2f}**")
                    
                    st.divider()
                    if defense_power_away == 0 or defense_power_home == 0:
                        st.error("Division by zero detected in xG calculation.")
                    else:
                        # Expected Goals (xG) para o time da casa
                        xg_home = home_goals_scored * attack_power_home / defense_power_away
                        # Expected Goals (xG) para o time visitante
                        xg_away = away_goals_scored * attack_power_away / defense_power_home
                    
                    # Exibindo os Expected Goals (xG) e Expected Goals Against (xGA)
                    st.markdown(f"#### Expected Goals (xG) ####")
                    st.markdown(f"🥅 Expected Goals for ***{selected_home}*** ➡️ **{xg_home:.2f}**")
                    st.markdown(f"🥅 Expected Goals for ***{selected_away}*** ➡️ **{xg_away:.2f}**")
                else:
                    st.error("Liga do jogo selecionado não encontrada nos dados de ligas.")
            except Exception as e:
                st.error(f"Erro ao carregar os dados de ligas: {e}")
            
        with col1:
            st.divider() 
            filtered_data = historical_data[(historical_data['Date'] < pd.to_datetime(selected_date)) & (historical_data['League'] == selected_league)]
            past_games_home = filtered_data[(filtered_data['Home'] == selected_home)].tail(21)
            past_games_away = filtered_data[(filtered_data['Away'] == selected_away)].tail(21)
        
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
    
            # Get goal statistics
            home_goals_scored = count_goals(past_games_home['Goals_Minutes_Home'])
            home_goals_conceded = count_goals(past_games_home['Goals_Minutes_Away'])
            away_goals_scored = count_goals(past_games_away['Goals_Minutes_Away'])
            away_goals_conceded = count_goals(past_games_away['Goals_Minutes_Home'])
    
            # Function to plot goal distribution
            def plot_goal_distribution(team_name, goals, conceded):
                fig21, ax = plt.subplots(figsize=(10, 6))
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
                st.pyplot(fig21)
                
            st.markdown(f"#### Time of Goals of ***{selected_home}*** on the last 21 Games ####")
            plot_goal_distribution(selected_home, home_goals_scored, home_goals_conceded)
            st.divider()             
            st.markdown(f"#### Time of Goals of ***{selected_away}*** on the last 21 Games ####")
            plot_goal_distribution(selected_away, away_goals_scored, away_goals_conceded)
            st.divider() 
            def summarize_half_goals(goals, half_segments):
                return sum([goals[segment] for segment in half_segments])
        
            st.markdown(f"#### First Half & Second Half Goals Distribution on the Last 21 Games ####")
            
            # Definir rótulos apenas para os tempos de jogo
            half_labels = ["First Half", "Second Half"]
            
            # Criar listas de gols com 4 categorias dentro de cada tempo
            home_scored = [
                summarize_half_goals(home_goals_scored, ['0-15', '15-30', '30-45']),
                summarize_half_goals(home_goals_scored, ['45-60', '60-75', '75-90'])
            ]
            home_conceded = [
                summarize_half_goals(home_goals_conceded, ['0-15', '15-30', '30-45']),
                summarize_half_goals(home_goals_conceded, ['45-60', '60-75', '75-90'])
            ]
            away_scored = [
                summarize_half_goals(away_goals_scored, ['0-15', '15-30', '30-45']),
                summarize_half_goals(away_goals_scored, ['45-60', '60-75', '75-90'])
            ]
            away_conceded = [
                summarize_half_goals(away_goals_conceded, ['0-15', '15-30', '30-45']),
                summarize_half_goals(away_goals_conceded, ['45-60', '60-75', '75-90'])
            ]
            
            # Criar o gráfico com 2 grupos ("First Half" e "Second Half"), mas 4 colunas dentro de cada um
            fig22, ax = plt.subplots(figsize=(10, 6))
            x = np.arange(len(half_labels))  # Posições para "First Half" e "Second Half"
            width = 0.2  # Largura das barras
            
            # Adicionar as barras deslocadas dentro de cada tempo
            ax.bar(x - 1.5 * width, home_scored, width, label=f'{selected_home} Scored', color='green')
            ax.bar(x - 0.5 * width, home_conceded, width, label=f'{selected_home} Conceded', color='darkgreen')
            ax.bar(x + 0.5 * width, away_scored, width, label=f'{selected_away} Scored', color='red')
            ax.bar(x + 1.5 * width, away_conceded, width, label=f'{selected_away} Conceded', color='darkred')
            
            # Configurar rótulos do gráfico
            ax.set_xticks(x)
            ax.set_xticklabels(half_labels)
            ax.set_ylabel("Goals")
            ax.set_title("First & Second Half Goals")
            ax.legend()
            ax.grid(axis="y", linestyle="--", alpha=0.7)
            
            # Exibir gráfico no Streamlit
            st.pyplot(fig22)
        
        with col2:
            def count_first_goal(goals_scored_list, goals_conceded_list):
                count_scored_first = 0
                count_conceded_first = 0
                
                for goals_scored, goals_conceded in zip(goals_scored_list, goals_conceded_list):
                    try:
                        scored_times = ast.literal_eval(goals_scored) if isinstance(goals_scored, str) else []
                        conceded_times = ast.literal_eval(goals_conceded) if isinstance(goals_conceded, str) else []
                    except (SyntaxError, ValueError):
                        continue  # Ignorar entradas inválidas
                    
                    if scored_times and conceded_times:  # Ambos marcaram
                        if min(scored_times) < min(conceded_times):
                            count_scored_first += 1  # Time marcou primeiro
                        else:
                            count_conceded_first += 1  # Time sofreu primeiro
                    elif scored_times:  # Só esse time marcou
                        count_scored_first += 1
                    elif conceded_times:  # Só o adversário marcou
                        count_conceded_first += 1
            
                return count_scored_first, count_conceded_first
            
            # Verificar se os dados têm o tamanho esperado
            if len(past_games_home) < 5 or len(past_games_away) < 5:
                st.write("No Sufficient Data Available")
            else:
                # Contar gols para cada time separadamente
                home_first_goal, home_conceded_first = count_first_goal(
                    past_games_home['Goals_Minutes_Home'], past_games_home['Goals_Minutes_Away']
                )
            
                away_first_goal, away_conceded_first = count_first_goal(
                    past_games_away['Goals_Minutes_Away'], past_games_away['Goals_Minutes_Home']
                )
            
                # Exibir resultados com negrito e itálico
                st.markdown(f"#### Who Scored and Conceded First in the Last 21 Games? ####")
                st.markdown(f"***{selected_home}*** Scored First **{home_first_goal}** times")
                st.markdown(f"***{selected_home}*** Conceded First **{home_conceded_first}** times")
                st.markdown(f"***{selected_away}*** Scored First **{away_first_goal}** times")
                st.markdown(f"***{selected_away}*** Conceded First **{away_conceded_first}**")
                st.divider() 
        
except Exception as e:
    st.error(f"Erro Geral: {e}")                   