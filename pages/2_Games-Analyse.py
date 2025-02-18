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

# Configuração inicial
# Configurar a página para largura total
st.set_page_config(layout="wide")
st.title('_Fluffy Chips Web Analyzer_')
st.subheader('The place where you can Analyse Football Matches!!!')
st.divider()
st.subheader('_Games of the Day_')
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
