import pandas as pd
import seaborn as sns
import streamlit as st
from PIL import Image
from scipy.stats import poisson
import os
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

# Configuração inicial
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
                        st.subheader("**_Tendency of the H2H_**")
                        st.markdown(f"**Tendency Over 0.5 HT:** {tendency_over_ht:.2f}%")
                        st.markdown(f"**Tendency Over 2.5 Goals:** {tendency_over:.2f}%")
                        st.markdown(f"**Tendency BTTS (Both Teams to Score):** {tendency_btts:.2f}%")
                        st.markdown("**Most Frequent Scores:**")
                        for score, count in top_scores.items():
                            st.markdown(f"- {score}: {count} times")
                            
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
                st.subheader("**_Tendency of Last 7 Games_**")
                st.markdown(f"**Tendency Over 0.5 HT:** {tendency_over_ht_home:.2f}%")
                st.markdown(f"**Tendency Over 2.5 Goals:** {tendency_over_home:.2f}%")
                st.markdown(f"**Tendency BTTS:** {tendency_btts_home:.2f}%")
                st.markdown("**Most Frequent Scores:**")
                for score, count in top_scores_home.items():
                    st.markdown(f"- {score}: {count} times")
                
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
                st.subheader("**_Tendency of Last 7 Games_**")
                st.markdown(f"**Tendency Over 0.5 HT:** {tendency_over_ht_away:.2f}%")
                st.markdown(f"**Tendency Over 2.5 Goals:** {tendency_over_away:.2f}%")
                st.markdown(f"**Tendency BTTS:** {tendency_btts_away:.2f}%")
                st.markdown("**Most Frequent Scores:**")
                for score, count in top_scores_away.items():
                    st.markdown(f"- {score}: {count} times")
                
                
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
                    st.subheader("**_Power Strength Analysis_**")
                    st.markdown('_**Power of Attack > 1**: The Team has a Superior Attack than the League Average (Strong Attack)_')
                    st.markdown('_**Power of Attack < 1**: The Team has an Inferior Attack than the League Average (Weak Attack)_')
                    st.markdown('_**Power of Defense > 1**: The Team has a Superior Defense than the League Average (Strong Defense)_')
                    st.markdown('_**Power of Defense < 1**: The Team has an Inferior Defense than the League Average (Weak Defense)_')
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
                st.subheader("**_Predicted Goals for This Game_**")
                st.markdown(f"- **Predicted Goals Scored for {selected_home}:** {prob_goals_scored_home:.2f}")
                st.markdown(f"- **Predicted Goals Taken for {selected_home}:** {prob_goals_taken_home:.2f}")
                st.markdown(f"- **Predicted Goals Scored for {selected_away}:** {prob_goals_scored_away:.2f}")
                st.markdown(f"- **Predicted Goals Taken for {selected_away}:** {prob_goals_taken_away:.2f}")
            else:
                st.error("As colunas de probabilidades de gols não estão disponíveis nos dados filtrados.")
                
            st.divider()
            
            # Função para calcular o lambda (média esperada de gols) para os times
            def calculate_lambda(filtered_data, home_team, away_team):
                try:
                    # Filtrar os dados do DataFrame para o jogo selecionado
                    match_data = filtered_data[(filtered_data['Home'] == home_team) & (data['Away'] == away_team)]
                    if match_data.empty:
                        raise ValueError(f"Jogo entre {home_team} e {away_team} não encontrado no DataFrame.")
                    
                    # Calcular lambdas
                    home_lambda = (match_data['Media_Golos_Marcados_Home'].values[0] + 
                                match_data['Media_Golos_Sofridos_Away'].values[0])
                    away_lambda = (match_data['Media_Golos_Marcados_Away'].values[0] + 
                                match_data['Media_Golos_Sofridos_Home'].values[0])
                    
                    home_lambda = min(max(home_lambda, 0.1), 2.5)
                    away_lambda = min(max(away_lambda, 0.1), 2.5)                        
                    return home_lambda, away_lambda
                except KeyError as e:
                    raise ValueError(f"Erro ao acessar os dados: {e}")
                except Exception as e:
                    raise ValueError(f"Ocorreu um erro ao calcular os lambdas: {e}")
            
            # Função para prever os resultados com distribuição de Poisson
            def predict_results(filtered_data, home_team, away_team, max_goals=5):
                try:
                    home_lambda, away_lambda = calculate_lambda(filtered_data, home_team, away_team)
                    prob_matrix = np.zeros((max_goals, max_goals))
                    
                    for home_goals in range(max_goals):
                        for away_goals in range(max_goals):
                            prob_matrix[home_goals, away_goals] = (
                                poisson.pmf(home_goals, home_lambda) * poisson.pmf(away_goals, away_lambda)
                            )
                    return prob_matrix
                except Exception as e:
                    raise ValueError(f"Ocorreu um erro ao prever os resultados: {e}")
            
            # Função para exibir a matriz formatada com 4 casas decimais e valores centralizados
            def display_probability_matrix(probabilities, home_team, away_team):
                max_goals = probabilities.shape[0]
                prob_df = pd.DataFrame(
                    probabilities, 
                    index=[f"{i} gols {home_team}" for i in range(max_goals)],
                    columns=[f"{i} gols {away_team}" for i in range(max_goals)]
                )
                
                # Formatar os valores para 4 casas decimais
                styled_df = prob_df.style.format("{:.4f}").set_properties(**{
                    'text-align': 'center'
                }).set_table_styles([{
                    'selector': 'th',
                    'props': [('text-align', 'center')]
                }])
                
                return styled_df
            
            def display_sorted_probabilities(probabilities, home_team, away_team):
                max_goals = probabilities.shape[0]
                prob_list = []
            
                # Criar uma lista com todos os resultados possíveis e suas probabilidades
                for home_goals in range(max_goals):
                    for away_goals in range(max_goals):
                        prob_list.append({
                            'Placar': f"{home_goals}-{away_goals}",
                            'Probabilidade': probabilities[home_goals, away_goals]
                        })
                
                # Converter para DataFrame e ordenar do mais provável para o menos provável
                prob_df = pd.DataFrame(prob_list)
                prob_df = prob_df.sort_values(by='Probabilidade', ascending=False)
                
                return prob_df
            
            # Seleção dos times
            home_team = selected_home
            away_team = selected_away
            
            # Garantir que os times sejam diferentes
            if home_team == away_team:
                st.warning("Selecione times diferentes para a previsão.")
            else:
                try:
                    # Prever os resultados
                    st.subheader(f"_Predict of Correct Score for {home_team} vs {away_team}_")
                    probabilities = predict_results(data, home_team, away_team)
                    
                    # Exibir matriz de probabilidades
                    st.write("_*Probability matrix (Poisson):*_")
                    styled_df = display_probability_matrix(probabilities, home_team, away_team)
                    st.write(styled_df)
                    
                    # Exibir probabilidades ordenadas de cada placar
                    st.write("_*Probability of Scores (sorted):*_")
                    sorted_probabilities = display_sorted_probabilities(probabilities, home_team, away_team)
                    
                    # Exibir as probabilidades ordenadas
                    for _, row in sorted_probabilities.iterrows():
                        st.write(f"{row['Placar']}: {row['Probabilidade']:.4f}")
                    st.divider()
                
                except ValueError as ve:
                    st.error(f"Erro nos cálculos: {ve}")
                except Exception as e:
                    st.error(f"Ocorreu um erro inesperado: {e}")
        except Exception as e:
            st.error(f"Erro ao carregar os dados históricos: {e}")
except Exception as e:
    st.error(f"Erro ao carregar os dados: {e}")
