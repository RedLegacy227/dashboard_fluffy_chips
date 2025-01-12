import pandas as pd
import numpy as np
import streamlit as st
from PIL import Image
import os
import base64
from datetime import datetime

# Configuração inicial
st.title('_Fluffy Chips Web Analyzer_')
st.subheader('The place where you can Analyse Football Matches!!!')
st.divider()
st.subheader('_Methods for Today_')
image_path = os.path.join(os.getcwd(), 'static', 'analises001.png')
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
    st.success("Dados carregados com sucesso!")
except Exception as e:
    st.error(f"Erro ao carregar os dados: {e}")
    data = None

# Criação das abas
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(['Lay 0 x 1', 'Lay 1 x 0', 'Over 0,5 HT', 'Over 1,5 FT', 'Lay Home', 'Lay Away', 'Under 1,5 FT'])

with tab1:
    st.subheader('Todays Games for Lay 0 x 1')
    if data is not None:
        # Aplicar os filtros
        lay_0_x_1_flt = data[
            (data["FT_Odd_H"] <= 3) &
            (data["Perc_Scored_at_least_1_Goal_Home"] >= 60) &
            (data["Perc_Over_15_FT_Away"] >= 75) &
            (data["Media_CG_01_Marcados_Home"] >= 3.5) &
            (data["Media_CG_02_Marcados_Home"] >= 0.8) &
            (data["CV_Media_CG_02_Marcados_Home"] <= 0.8) &
            (data["FT_Odd_Ov25"] <= 2.20) &
            (data["FT_Odd_BTTS_Y"] <= 2.20) &
            (data["FT_Odd_A"] >= data["FT_Odd_D"])
        ]
        lay_0_x_1_flt = lay_0_x_1_flt.sort_values(by='Time', ascending=True)

        # Exibir os dados filtrados
        if not lay_0_x_1_flt.empty:
            st.dataframe(lay_0_x_1_flt)
        else:
            st.info("Nenhum jogo encontrado com os critérios especificados.")
    else:
        st.info("Dados indisponíveis para a data selecionada.")

with tab2:
    st.subheader('Todays Games for Lay 1 x 0')
    if data is not None:
        # Aplicar os filtros
        lay_1_x_0_flt = data[
            (data["FT_Odd_A"] <= 3) &
            (data["Perc_Scored_at_least_1_Goal_Away"] >= 60) &
            (data["Perc_Over_15_FT_Home"] >= 75) &
            (data["Media_CG_01_Marcados_Away"] >= 3) &
            (data["Media_CG_02_Marcados_Away"] >= 0.8) &
            (data["CV_Media_CG_02_Marcados_Away"] <= 0.8) &
            (data["FT_Odd_Ov25"] <= 2.20) &
            (data["FT_Odd_BTTS_Y"] <= 2.20) &
            (data["FT_Odd_H"] >= data["FT_Odd_D"])
        ]
        lay_1_x_0_flt = lay_1_x_0_flt.sort_values(by='Time', ascending=True)

        # Exibir os dados filtrados
        if not lay_1_x_0_flt.empty:
            st.dataframe(lay_1_x_0_flt)
        else:
            st.info("Nenhum jogo encontrado com os critérios especificados.")
    else:
        st.info("Dados indisponíveis para a data selecionada.")

with tab3:
    st.subheader('Todays Games for Over 0,5 HT')
    st.markdown('If the Odd is less than 1.54, you must wait for it to reach minimum 1.54')
    if data is not None:
        over_05_ht_flt = data[
            (data["Perc_Over_05_HT_Home"] >= 70) & 
            (data["Perc_Over_05_HT_Away"] >= 70) &
            (data["Media_CG_02_Marcados_Home"] >= 1) &
            (data["Media_CG_02_Marcados_Away"] >= 1) &
            (data["CV_Media_CG_02_Marcados_Home"] <= 0.5)
        ]
        over_05_ht_flt = over_05_ht_flt.sort_values(by='Time', ascending=True)

        # Exibir os dados filtrados
        if not over_05_ht_flt.empty:
            st.dataframe(over_05_ht_flt)
        else:
            st.info("Nenhum jogo encontrado com os critérios especificados.")
    else:
        st.info("Dados indisponíveis para a data selecionada.")

with tab4:
    st.subheader('Todays Games for Over 1,5 FT')
    st.markdown('If the Odd is less than 1.42, you must wait for it to reach minimum 1.42')
    if data is not None:
        # Aplicar os filtros
        over_15_ft_flt = data[
            ((data["Perc_Over_15_FT_Home"] + data["Perc_Over_15_FT_Away"]) / 2 > 65) &
            ((data["Perc_of_Games_BTTS_Yes_Home"] + data["Perc_of_Games_BTTS_Yes_Away"]) / 2 > 65) &
            (data["Media_Golos_Marcados_Home"] > 1) &
            (data["CV_Media_Golos_Marcados_Home"] < 1) &
            (data["Media_Golos_Marcados_Away"] > 1) &
            (data["CV_Media_Golos_Marcados_Away"] < 1) &
            (data["Media_Golos_Sofridos_Home"] > 1) &
            (data["CV_Media_Golos_Sofridos_Home"] < 1) &
            (data["Media_Golos_Sofridos_Away"] > 1) &
            (data["CV_Media_Golos_Sofridos_Away"] < 1)
        ]
        over_15_ft_flt = over_15_ft_flt.sort_values(by='Time', ascending=True)

        # Exibir os dados filtrados
        if not over_15_ft_flt.empty:
            st.dataframe(over_15_ft_flt)
        else:
            st.info("Nenhum jogo encontrado com os critérios especificados.")
    else:
        st.info("Dados indisponíveis para a data selecionada.")
        
# URL dos dados de Elo e Tilt
elo_tilt_url = "https://raw.githubusercontent.com/RedLegacy227/elo_tilt/main/df_elo_tilt.csv"

with tab5:
    st.subheader("Todays Games for Lay Home")
    lay_home = data.copy()
    lay_home['VAR1'] = np.sqrt((lay_home['FT_Odd_H'] - lay_home['FT_Odd_A'])**2)
    lay_home['VAR2'] = np.degrees(np.arctan((lay_home['FT_Odd_A'] - lay_home['FT_Odd_H']) / 2))
    lay_home['VAR3'] = np.degrees(np.arctan((lay_home['FT_Odd_D'] - lay_home['FT_Odd_A']) / 2))
    
    if lay_home is not None:
        try:
            # Carregar os dados de Elo e Tilt apenas uma vez
            if 'Elo_Home' not in lay_home.columns or 'Elo_Away' not in lay_home.columns:
                df_elo_tilt = pd.read_csv(elo_tilt_url)
                
                # Merge para adicionar dados de Elo e Tilt
                lay_home = lay_home.merge(df_elo_tilt[['Team', 'Elo', 'Tilt']], left_on='Home', right_on='Team', how='left')
                lay_home = lay_home.rename(columns={'Elo': 'Elo_Home', 'Tilt': 'Tilt_Home'})
                lay_home = lay_home.merge(df_elo_tilt[['Team', 'Elo', 'Tilt']], left_on='Away', right_on='Team', how='left')
                lay_home = lay_home.rename(columns={'Elo': 'Elo_Away', 'Tilt': 'Tilt_Away'})
                
                # Calcular a diferença de Elo
                lay_home['Elo_Difference'] = lay_home['Elo_Home'] - lay_home['Elo_Away']
            
            # Calcular as odds justas
            HFA = 50 * 0.15
            lay_home['dr'] = (lay_home['Elo_Home'] + HFA) - lay_home['Elo_Away']
            lay_home['P_Home'] = 1 / (10 ** (-lay_home['dr'] / 400) + 1)
            lay_home['P_Away'] = 1 - lay_home['P_Home']
            lay_home['Odd_Home_Justa'] = (1 / lay_home['P_Home']).round(2)
            lay_home['Odd_Away_Justa'] = (1 / lay_home['P_Away']).round(2)
            
            # Filtro para Back Home
            lay_home_flt = lay_home[(lay_home['VAR1'] >= 3) & (lay_home["VAR2"] <= -30) & (lay_home["VAR3"] >= 30) & (lay_home['FT_Odd_H'] > 2)]
            
            # Exibir dados filtrados
            if not lay_home_flt.empty:
                st.dataframe(lay_home_flt[['Time', 'League', 'Home', 'Away', 'FT_Odd_H', 'FT_Odd_A', 'FT_Odd_D', 'Odd_Home_Justa', 'Odd_Away_Justa', 'Elo_Home', 'Tilt_Home', 'Elo_Away', 'Tilt_Away', 'Elo_Difference', 'Media_Power_Ranking_Home', 'CV_Media_Power_Ranking_Home', 'Media_Power_Ranking_Away', 'CV_Media_Power_Ranking_Away']])
            else:
                st.info("Nenhum jogo encontrado.")
        except Exception as e:
            st.error(f"Erro ao carregar ou processar os dados para Back Home: {e}")
    else:
        st.info("Dados indisponíveis para a data selecionada.")

with tab6:
    st.subheader("Todays Games for Lay Away")
    lay_away = data.copy()
    lay_away['VAR1'] = np.sqrt((lay_away['FT_Odd_H'] - lay_away['FT_Odd_A'])**2)
    lay_away['VAR2'] = np.degrees(np.arctan((lay_away['FT_Odd_A'] - lay_away['FT_Odd_H']) / 2))
    lay_away['VAR3'] = np.degrees(np.arctan((lay_away['FT_Odd_D'] - lay_away['FT_Odd_A']) / 2))
    
    if lay_away is not None:
        try:
            # Carregar os dados de Elo e Tilt apenas uma vez
            if 'Elo_Home' not in lay_away.columns or 'Elo_Away' not in lay_away.columns:
                df_elo_tilt = pd.read_csv(elo_tilt_url)
                
                # Merge para adicionar dados de Elo e Tilt
                lay_away = lay_away.merge(df_elo_tilt[['Team', 'Elo', 'Tilt']], left_on='Home', right_on='Team', how='left')
                lay_away = lay_away.rename(columns={'Elo': 'Elo_Home', 'Tilt': 'Tilt_Home'})
                lay_away = lay_away.merge(df_elo_tilt[['Team', 'Elo', 'Tilt']], left_on='Away', right_on='Team', how='left')
                lay_away = lay_away.rename(columns={'Elo': 'Elo_Away', 'Tilt': 'Tilt_Away'})
                
                # Calcular a diferença de Elo
                lay_away['Elo_Difference'] = lay_away['Elo_Home'] - lay_away['Elo_Away']
                
            # Calcular as odds justas, caso ainda não estejam calculadas
            HFA = 50 * 0.15
            lay_away['dr'] = (lay_away['Elo_Home'] + HFA) - lay_away['Elo_Away']
            lay_away['P_Home'] = 1 / (10 ** (-lay_away['dr'] / 400) + 1)
            lay_away['P_Away'] = 1 - lay_away['P_Home']
            lay_away['Odd_Home_Justa'] = (1 / lay_away['P_Home']).round(2)
            lay_away['Odd_Away_Justa'] = (1 / lay_away['P_Away']).round(2)
            
            # Filtro para Lay Away
            lay_away_flt = lay_away[(lay_away['VAR1'] >=4) & (lay_away["VAR2"] >= 60) & (lay_away["VAR3"] <= -60) & (lay_away['FT_Odd_A'] > 2)]
            
            # Exibir dados filtrados
            if not lay_away_flt.empty:
                st.dataframe(lay_away_flt[['Time', 'League', 'Home', 'Away', 'FT_Odd_H', 'FT_Odd_A', 'FT_Odd_D', 'Odd_Home_Justa', 'Odd_Away_Justa', 'Elo_Home', 'Tilt_Home', 'Elo_Away', 'Tilt_Away', 'Elo_Difference', 'Media_Power_Ranking_Home', 'CV_Media_Power_Ranking_Home', 'Media_Power_Ranking_Away', 'CV_Media_Power_Ranking_Away']])
            else:
                st.info("Nenhum jogo encontrado.")
        except Exception as e:
            st.error(f"Erro ao processar os dados para Back Away: {e}")
    else:
        st.info("Dados indisponíveis para a data selecionada.")
        
with tab7:
    st.subheader('Todays Games for Under 1,5 FT')
    st.markdown('Croatia Method 1')
    if data is not None:
        # Aplicar os filtros
        under_15_croatia_01_ft_flt = data[
            (data["League"] == 'CROATIA - HNL') &
            (data["Points"] == 'Points_Home') &
            (data["RPS_OVUnd"] == 'Bigger_Away') &
            (data["Poisson_2_GS_Home"] > 0.1660) &
            (data["Poisson_2_GS_Home"] < 0.2610) &
            (data["Media_CG_02_Marcados_Away"] > 0.5550) &
            (data["Media_CG_02_Marcados_Away"] < 0.8390)
        ]
        under_15_croatia_01_ft_flt = under_15_croatia_01_ft_flt.sort_values(by='Time', ascending=True)

        # Exibir os dados filtrados
        if not under_15_croatia_01_ft_flt.empty:
            st.dataframe(under_15_croatia_01_ft_flt)
        else:
            st.info("Nenhum jogo encontrado com os critérios especificados.")
    else:
        st.info("Dados indisponíveis para a data selecionada.")
    st.markdown('Croatia Method 2')
    if data is not None:
        # Aplicar os filtros
        under_15_croatia_02_ft_flt = data[
            (data["League"] == 'CROATIA - HNL') &
            (data["Points"] == 'Points_Home') &
            (data["RPS_OVUnd"] == 'Bigger_Away') &
            (data["Poisson_2_GS_Home"] > 0.1660) &
            (data["Poisson_2_GS_Home"] < 0.2610) &
            (data["Media_CG_02_Sofridos_Home"] > 0.7080) &
            (data["Media_CG_02_Sofridos_Home"] < 0.9270)
        ]
        under_15_croatia_02_ft_flt = under_15_croatia_02_ft_flt.sort_values(by='Time', ascending=True)

        # Exibir os dados filtrados
        if not under_15_croatia_02_ft_flt.empty:
            st.dataframe(under_15_croatia_02_ft_flt)
        else:
            st.info("Nenhum jogo encontrado com os critérios especificados.")
    else:
        st.info("Dados indisponíveis para a data selecionada.")
    st.markdown('Croatia Method 3')
    if data is not None:
        # Aplicar os filtros
        under_15_croatia_03_ft_flt = data[
            (data["League"] == 'CROATIA - HNL') &
            (data["Points"] == 'Points_Home') &
            (data["RPS_OVUnd"] == 'Bigger_Away') &
            (data["Probabilidade_Goals_Scored_Home"] > 0.9020) &
            (data["Probabilidade_Goals_Scored_Home"] < 1.5720) &
            (data["Probabilidade_Goals_Taken_Home"] > 0.9370) &
            (data["Probabilidade_Goals_Taken_Home"] < 1.3880)
        ]
        under_15_croatia_03_ft_flt = under_15_croatia_03_ft_flt.sort_values(by='Time', ascending=True)

        # Exibir os dados filtrados
        if not under_15_croatia_03_ft_flt.empty:
            st.dataframe(under_15_croatia_03_ft_flt)
        else:
            st.info("Nenhum jogo encontrado com os critérios especificados.")
    else:
        st.info("Dados indisponíveis para a data selecionada.")