import pandas as pd
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
tab1, tab2, tab3, tab4, tab5 = st.tabs(['Lay 0 x 1', 'Lay 1 x 0', 'Over 1,5 FT', 'Back Home', 'Back Away'])

with tab1:
    st.subheader('Todays Games for Lay 0 x 1')
    if data is not None:
        # Aplicar os filtros
        lay_0_x_1_flt = data[
            (data["FT_Odd_H"] <= 3) &
            (data["Perc_Over_15_FT_Away"] >= 80) &
            (data["Media_CG_01_Marcados_Home"] <= 4) &
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
            (data["Perc_Over_15_FT_Home"] >= 80) &
            (data["Media_CG_01_Marcados_Away"] <= 4) &
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
    st.subheader('Todays Games for Over 1,5 FT')
    st.markdown('If the Odd is less than 1.42, you must wait for it to reach minimum 1.42')
    if data is not None:
        # Aplicar os filtros
        over_15_ft_flt = data[
            (data["Perc_Over_15_FT_Home"] > 57) &
            (data["Perc_Over_15_FT_Away"] > 57) &
            (data["Perc_of_Games_BTTS_Yes_Home"] > 57) &
            (data["Perc_of_Games_BTTS_Yes_Away"] > 57) &
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

with tab4:
    st.subheader("Todays Games for Back Home")
    
    if data is not None:
        try:
            # Carregar os dados de Elo e Tilt apenas uma vez
            if 'Elo_Home' not in data.columns or 'Elo_Away' not in data.columns:
                df_elo_tilt = pd.read_csv(elo_tilt_url)
                
                # Merge para adicionar dados de Elo e Tilt
                data = data.merge(df_elo_tilt[['Team', 'Elo', 'Tilt']], left_on='Home', right_on='Team', how='left')
                data = data.rename(columns={'Elo': 'Elo_Home', 'Tilt': 'Tilt_Home'})
                data = data.merge(df_elo_tilt[['Team', 'Elo', 'Tilt']], left_on='Away', right_on='Team', how='left')
                data = data.rename(columns={'Elo': 'Elo_Away', 'Tilt': 'Tilt_Away'})
                
                # Calcular a diferença de Elo
                data['Elo_Difference'] = data['Elo_Home'] - data['Elo_Away']
            
            # Calcular as odds justas
            HFA = 60
            data['dr'] = (data['Elo_Home'] + HFA) - data['Elo_Away']
            data['P_Home'] = 1 / (10 ** (-data['dr'] / 400) + 1)
            data['P_Away'] = 1 - data['P_Home']
            data['Odd_Home_Justa'] = (1 / data['P_Home']).round(2)
            data['Odd_Away_Justa'] = (1 / data['P_Away']).round(2)
            
            # Filtro para Back Home
            back_home_flt = data[(data['Elo_Difference'] > 75) & (data["Perc_Wins_FT_Home"] >= 80)& (data["FT_Odd_H"] <= 3.00) & (data['Tilt_Home'] < data['Tilt_Home'])]
            
            # Exibir dados filtrados
            if not back_home_flt.empty:
                st.dataframe(back_home_flt[['Time', 'Home', 'Away', 'FT_Odd_H', 'FT_Odd_A', 'FT_Odd_D', 'Odd_Home_Justa', 'Odd_Away_Justa', 'Elo_Home', 'Tilt_Home', 'Elo_Away', 'Tilt_Away', 'Elo_Difference']])
            else:
                st.info("Nenhum jogo encontrado.")
        except Exception as e:
            st.error(f"Erro ao carregar ou processar os dados para Back Home: {e}")
    else:
        st.info("Dados indisponíveis para a data selecionada.")

with tab5:
    st.subheader("Todays Games for Back Away")
    
    if data is not None:
        try:
            # Verificar se as colunas já foram calculadas
            if 'Odd_Home_Justa' not in data.columns:
                # Calcular as odds justas, caso ainda não estejam calculadas
                HFA = 60
                data['dr'] = (data['Elo_Home'] + HFA) - data['Elo_Away']
                data['P_Home'] = 1 / (10 ** (-data['dr'] / 400) + 1)
                data['P_Away'] = 1 - data['P_Home']
                data['Odd_Home_Justa'] = (1 / data['P_Home']).round(2)
                data['Odd_Away_Justa'] = (1 / data['P_Away']).round(2)
            
            # Filtro para Back Away
            back_away_flt = data[(data['Elo_Difference'] < -75) & (data["Perc_Wins_FT_Away"] >= 80) & (data["FT_Odd_A"] <= 3.00) & (data['Tilt_Away'] < data['Tilt_Home'])]
            
            # Exibir dados filtrados
            if not back_away_flt.empty:
                st.dataframe(back_away_flt[['Time', 'Home', 'Away', 'FT_Odd_H', 'FT_Odd_A', 'FT_Odd_D', 'Odd_Home_Justa', 'Odd_Away_Justa', 'Elo_Home', 'Tilt_Home', 'Elo_Away', 'Tilt_Away', 'Elo_Difference']])
            else:
                st.info("Nenhum jogo encontrado.")
        except Exception as e:
            st.error(f"Erro ao processar os dados para Back Away: {e}")
    else:
        st.info("Dados indisponíveis para a data selecionada.")