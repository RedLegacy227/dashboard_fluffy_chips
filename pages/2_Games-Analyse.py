import pandas as pd
import math
import seaborn as sns
import streamlit as st
from PIL import Image
from scipy.stats import poisson
import os
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

# Configuração inicial
# Configurar a página para largura total
st.set_page_config(layout="wide")
st.title('_Fluffy Chips Web Analyzer_')
st.subheader('The place where you can Analyse Football Matches!!!')
st.divider()
st.subheader('_Games of the Day_')
st.image(os.path.join(os.getcwd(), 'static', 'analises002.png'))
st.divider()

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

        st.write(f"**Selected Game:** {selected_game}")
        st.divider()

        # Dividir o jogo em Home e Away
        selected_home, selected_away = selected_game.split(" x ")

        # Carregar dados históricos
        historical_data_url = "https://raw.githubusercontent.com/RedLegacy227/main_data_base/refs/heads/main/df_base_original.csv"
        
        historical_data = pd.read_csv(historical_data_url)
        historical_data['Date'] = pd.to_datetime(historical_data["Date"])
        filtered_data = historical_data[(historical_data['Date'] < pd.to_datetime(selected_date))]
        try:
            required_columns = [
                'Date', 'League', 'Season', 'Home', 'Away', 'HT_Goals_H', 'HT_Goals_A', 'FT_Goals_H', 'FT_Goals_A', 'FT_Odd_H', 'FT_Odd_D', 'FT_Odd_A','FT_Odd_Over25', 'Odd_BTTS_Yes'
            ]

            if all(col in filtered_data.columns for col in required_columns):
                filtered_data = filtered_data[
                    (filtered_data["Home"] == selected_home) & (filtered_data["Away"] == selected_away)
                    ][required_columns]
                
                if not filtered_data.empty:
                    st.write(f"**Past Games Between {selected_home} and {selected_away}:**")
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

                        fig1, ax1 = plt.subplots(figsize=(10, 9))
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
                        fig3, ax3 = plt.subplots(figsize=(10, 9))
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

                        fig2, ax2 = plt.subplots(figsize=(10, 9))
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
                        top_scores = filtered_data["Score"].value_counts().head(3)
                        
                        # Exibir informações adicionais
                        st.subheader("**Tendency of the H2H**")
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
            data_7 = pd.read_csv(historical_data_url)
            # Converter a coluna "Date" para datetime
            data_7["Date"] = pd.to_datetime(data_7["Date"])
            # Filtrar os últimos 7 jogos da equipe da casa (jogando em casa) até a data selecionada
            home_last_7 = data_7[(data_7["Home"] == selected_home) & (data_7["Date"] <= pd.to_datetime(selected_date))
                            ].sort_values(by="Date", ascending=False).head(7)
            # Filtrar os últimos 7 jogos da equipe visitante (jogando fora) até a data selecionada
            away_last_7 = data_7[(data_7["Away"] == selected_away) & (data_7["Date"] <= pd.to_datetime(selected_date))
                            ].sort_values(by="Date", ascending=False).head(7)
            st.divider()
            # **Análises para a equipe da casa**
            if not home_last_7.empty:
                st.subheader(f"Last 7 Games of {selected_home} - Playing @Home:")
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
                
                fig4, ax4 = plt.subplots(figsize=(10, 9))
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
                st.subheader("**Tendency of Last 7 Games**")
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
                
                fig5, ax5 = plt.subplots(figsize=(10, 8))
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
                st.subheader(f"Last 7 Games of {selected_away} - Playing @Away:")
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
                
                fig6, ax6 = plt.subplots(figsize=(10, 9))
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
                st.subheader("**Tendency of Last 7 Games**")
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
                
                fig7, ax7 = plt.subplots(figsize=(10, 8))
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
        
            st.divider()
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
                    
                    # Filtrar jogos do Home apenas em casa
                    home_filtered_data = filtered_data[filtered_data["Home"] == selected_home]
                    home_goals_scored = home_filtered_data["FT_Goals_H"].mean()  # Média de gols marcados pelo Home em casa
                    home_goals_conceded = home_filtered_data["FT_Goals_A"].mean()  # Média de gols sofridos pelo Home em casa
                    
                    # Filtrar jogos do Away apenas fora
                    away_filtered_data = filtered_data[filtered_data["Away"] == selected_away]
                    away_goals_scored = away_filtered_data["FT_Goals_A"].mean()  # Média de gols marcados pelo Away fora
                    away_goals_conceded = away_filtered_data["FT_Goals_H"].mean()  # Média de gols sofridos pelo Away fora
                    
                    # Calcular poderes de ataque e defesa
                    attack_power_home = home_goals_scored / league_avg_gs_away
                    defense_power_home = home_goals_conceded / league_avg_gm_away
                    
                    attack_power_away = away_goals_scored / league_avg_gs_home
                    defense_power_away = away_goals_conceded / league_avg_gm_home
                    
                    
                    # Exibir os resultados no Streamlit
                    st.subheader("**Power Strength Analysis**")
                    st.markdown('**Power of Attack > 1**: The Team has a Superior Attack than the League Average (Strong Attack)')
                    st.markdown('**Power of Attack < 1**: The Team has an Inferior Attack than the League Average (Weak Attack)')
                    st.markdown('**Power of Defense > 1**: The Team has a Inferior Defense than the League Average (Weak Defense)')
                    st.markdown('**Power of Defense < 1**: The Team has an Superior Defense than the League Average (Strong Defense)')
                    st.markdown(f"- **Power of Attack for {selected_home}:** {attack_power_home:.2f}")
                    st.markdown(f"- **Power of Attack for {selected_away}:** {attack_power_away:.2f}")
                    st.markdown(f"- **Power of Defense for {selected_home}:** {defense_power_home:.2f}")
                    st.markdown(f"- **Power of Defense for {selected_away}:** {defense_power_away:.2f}")
                else:
                    st.error("Liga do jogo selecionado não encontrada nos dados de ligas.")
            except Exception as e:
                st.error(f"Erro ao carregar os dados de ligas: {e}")
                st.divider()                    
            
            # Exibir as previsões de gols marcados e sofridos
            if all(col in data.columns for col in [
                'Probabilidade_Goals_Scored_Home', 'Probabilidade_Goals_Taken_Home',
                'Probabilidade_Goals_Scored_Away', 'Probabilidade_Goals_Taken_Away'
                ]):
                # Obter as probabilidades agregadas (média, por exemplo)
                prob_goals_scored_home = data['Probabilidade_Goals_Scored_Home'].mean()
                prob_goals_taken_home = data['Probabilidade_Goals_Taken_Home'].mean()   
                prob_goals_scored_away = data['Probabilidade_Goals_Scored_Away'].mean()
                prob_goals_taken_away = data['Probabilidade_Goals_Taken_Away'].mean()
                
                # Exibir os resultados no Streamlit
                st.subheader("**Predicted Goals for This Game**")
                st.markdown(f"- Predicted Goals Scored for {selected_home}: **{prob_goals_scored_home:.2f}**")
                st.markdown(f"- Predicted Goals Taken for {selected_home}: **{prob_goals_taken_home:.2f}**")
                st.markdown(f"- Predicted Goals Scored for {selected_away}: **{prob_goals_scored_away:.2f}**")
                st.markdown(f"- Predicted Goals Taken for {selected_away}: **{prob_goals_taken_away:.2f}**")
            else:
                st.error("As colunas de probabilidades de gols não estão disponíveis nos dados filtrados.")
                
            st.divider()
            
            def calculate_probabilities(home_elo, away_elo):
                """
                Calcula as probabilidades de vitória, empate e derrota com base nos Elos.
                """
                # Diferença de Elo
                elo_diff = home_elo - away_elo
            
                # Probabilidade base de empate e fator de ajuste
                base_draw_chance = 0.25  # 25% como base
                adjustment_factor = 0.005
            
                # Calcular probabilidade de empate
                p_draw = base_draw_chance * math.exp(-adjustment_factor * abs(elo_diff))
            
                # Calcular probabilidades de vitória
                p_home = 1 / (10 ** (-elo_diff / 400) + 1)
                p_away = 1 - p_home
            
                # Ajustar probabilidades para incluir empate
                p_home -= p_draw / 2
                p_away -= p_draw / 2
            
                # Garantir que as probabilidades somem 1 (100%)
                p_home = max(0, min(p_home, 1))
                p_away = max(0, min(p_away, 1))
                p_draw = max(0, min(p_draw, 1))
            
                return {
                    "Home_Win": round(p_home * 100, 2),
                    "Draw": round(p_draw * 100, 2),
                    "Away_Win": round(p_away * 100, 2)
                }
            
            # URL dos dados de Elo e Tilt
            elo_tilt_url = "https://raw.githubusercontent.com/RedLegacy227/elo_tilt/refs/heads/main/df_elo_tilt.csv"
            
            try:
                # Carregar os dados de Elo e Tilt
                elo_tilt_data = pd.read_csv(elo_tilt_url)
                
                if selected_home and selected_away:
                    # Filtro para os times
                    home_team_data = elo_tilt_data[elo_tilt_data['Team'] == selected_home]
                    away_team_data = elo_tilt_data[elo_tilt_data['Team'] == selected_away]
                    
                    # Verifica se os dados dos times foram encontrados
                    if not home_team_data.empty and not away_team_data.empty:
                        # Obtém valores de Elo e Tilt
                        home_elo = home_team_data.iloc[0]['Elo']
                        home_tilt = home_team_data.iloc[0]['Tilt']
                        away_elo = away_team_data.iloc[0]['Elo']
                        away_tilt = away_team_data.iloc[0]['Tilt']
                        
                        # Exibe os valores no Streamlit
                        st.markdown(f"_The Elo for *{selected_home}* is *{home_elo}*_")
                        st.markdown(f"_The Tilt for *{selected_home}* is *{home_tilt}*_")
                        st.markdown(f"_The Elo for *{selected_away}* is *{away_elo}*_")
                        st.markdown(f"_The Tilt for *{selected_away}* is *{away_tilt}*_")
                        
                        # Calcular as probabilidades de vitória, empate e derrota
                        probabilities = calculate_probabilities(home_elo, away_elo)
                        
                        # Exibir as previsões
                        st.markdown("### Predictions:")
                        st.markdown(f"Prediction for *{selected_home}* to win is **{probabilities['Home_Win']}%**")
                        st.markdown(f"Prediction for *{selected_away}* to win is **{probabilities['Away_Win']}%**")
                        st.markdown(f"Prediction for *Draw* is **{probabilities['Draw']}%**")
                        
                        # Interpretation of Tilt
                        st.markdown("### Interpretation of Tilt:")
                        st.markdown("""
                                    - **Low Tilt Values (< 1.0):**
                                    - Indicate that the matches of this team have fewer goals than expected, based on Elo and goal expectations.
                                    - Example: Teams with solid defenses or that play more conservatively may have low Tilt values.
                                        
                                    - **Values Around 1.0:**
                                    - Indicate that the team aligns with the average expected offensive and defensive performance in terms of goals scored and conceded.
                                            
                                    - **High Tilt Values (> 1.0):**
                                    - Represent teams whose matches frequently have more goals than expected.
                                    - Example: Offensive teams or teams with weak defenses, leading to more open matches with many goals.
                                    """)
                    else:
                        st.error("The data for one or both teams could not be found.")
            except Exception as e:
                st.error(f"Error loading or processing Elo and Tilt data: {e}")
            
            st.divider()


            
            # Função para calcular o lambda (média esperada de gols) para os times
            def drop_reset_index(df):
                df = df.dropna()
                df = df.reset_index(drop=True)
                df.index += 1
                return df
            
            def simulate_match(home_goals_for, home_goals_against,away_goals_for,away_goals_against,num_simulations=10000,random_seed=42):
                np.random.seed(random_seed)
                estimated_home_goals = (home_goals_for + away_goals_against) / 2
                estimated_away_goals = (away_goals_for + home_goals_against) / 2
                
                home_goals = poisson(estimated_home_goals).rvs(num_simulations)
                away_goals = poisson(estimated_away_goals).rvs(num_simulations)
                
                results = pd.DataFrame({
                    'Home_Goals':home_goals,
                    'Away_Goals': away_goals
                })
                return results
            
            def top_results_df(simulated_results, top_n):
                # Criar uma coluna para representar o resultado como string ou tupla
                simulated_results['Result'] = simulated_results.apply(
                    lambda row: (row['Home_Goals'], row['Away_Goals']), axis=1
                    )
                # Contar as ocorrências de cada combinação única
                result_counts = simulated_results['Result'].value_counts().head(top_n).reset_index()
                result_counts.columns = ['Home_Goals_Away_Goals', 'Count']
                
                # Separar a coluna de tupla novamente em duas colunas para clareza
                result_counts[['Home_Goals', 'Away_Goals']] = pd.DataFrame(result_counts['Home_Goals_Away_Goals'].tolist())
                result_counts = result_counts.drop(columns=['Home_Goals_Away_Goals'])
                
                # Calcular probabilidades
                sum_top_counts = result_counts['Count'].sum()
                result_counts['Probability'] = result_counts['Count'] / sum_top_counts
                return result_counts
            
            # Seleção dos times
            home_team = selected_home
            away_team = selected_away
            
            home_goals_for = data['Media_Golos_Marcados_Home'].iloc[0]
            home_goals_against = data['Media_Golos_Sofridos_Home'].iloc[0]
            away_goals_for = data['Media_Golos_Marcados_Away'].iloc[0]
            away_goals_against = data['Media_Golos_Sofridos_Away'].iloc[0]
            
            simulated_results = simulate_match(home_goals_for,home_goals_against,away_goals_scored,away_goals_against)
            simulated_results = drop_reset_index(simulated_results)
            
            results = top_results_df(simulated_results,100)
            results = drop_reset_index(results)
            
            results['Score_Board'] = results.apply(
                lambda row: 'Any_Other_Home_Win' if (row['Home_Goals'] >= 4 and row['Home_Goals'] > row['Away_Goals'])
                else 'Any_Other_Away_Win' if (row['Away_Goals'] >= 4 and row['Away_Goals'] > row['Home_Goals'])
                else 'Any_Other_Draw' if (row['Home_Goals'] >= 4 and row['Away_Goals'] >= 4 and row['Home_Goals'] == row['Away_Goals'])
                else f'{int(row['Home_Goals'])}X{int(row['Away_Goals'])}', axis=1
            )
            
            # Aplicar CSS para garantir que a tabela seja exibida completamente
            st.markdown(
                """
                <style>
                .dataframe tbody tr th, .dataframe tbody tr td {
                    text-align: center !important;
                    }
                    .dataframe {
                        width: 100% !important;
                        }
                        </style>
                        """,
                        unsafe_allow_html=True
                        )
            
            # Exibir os resultados
            results = results.head(19)
            
            # Manter apenas as colunas desejadas
            results = results[['Score_Board', 'Probability']]
            
            ## Consolidar valores repetidos na coluna `Score_Board`
            results = results.groupby('Score_Board', as_index=False).agg({'Probability': 'sum'})
            
            # Ordenar pelo valor da probabilidade em ordem decrescente
            results = results.sort_values(by='Probability', ascending=False).reset_index(drop=True)
            
            # Formatar a coluna Probability com 4 casas decimais
            results['Probability'] = results['Probability'].apply(lambda x: f"{x:.4f}")
            
            # Centralizar e estilizar os resultados
            styled_results = results.style.set_properties(**{
                'text-align': 'center'
                }).set_table_styles([
                    dict(selector='th', props=[('text-align', 'center')])
                    ])
            # Configuração do Streamlit
            st.subheader(f"Correct Score Simulation for **{home_team}** vs **{away_team}**")
            # Exibir a tabela completa estilizada no Streamlit
            st.write(styled_results.to_html(), unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"Erro ao carregar os dados históricos: {e}")
except Exception as e:
    st.error(f"Erro ao carregar os dados: {e}")
