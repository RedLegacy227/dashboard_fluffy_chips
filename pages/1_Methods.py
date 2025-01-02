import pandas as pd
import streamlit as st
from PIL import Image
import os
from datetime import datetime

# Configuração inicial
st.title('_Fluffy Chips Web Analyzer_')
st.subheader('The place where you can Analyse Football Matches!!!')
st.divider()
st.subheader('_Methods for Today_')
st.image(os.path.join(os.getcwd(), 'static', 'analises001.png'))
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
tab1, tab2, tab3 = st.tabs(['Lay 0 x 1', 'Lay 1 x 0', 'Over 1,5 FT'])

with tab1:
    st.subheader('Todays Games for Lay 0 x 1')
    if data is not None:
        # Aplicar os filtros
        lay_0_x_1_flt = data[
            (data["Probabilidade_Goals_Scored_Home"] >= 1.4) &
            (data["Probabilidade_Goals_Taken_Away"] >= 1.3) &
            (data["Media_CG_01_Marcados_Home"] >= 3) &
            (data["Media_CG_02_Marcados_Home"] >= 0.8) &
            (data["CV_Media_CG_02_Marcados_Home"] <= 0.8) &
            (data["FT_Odd_Ov25"] <= 2.3) &
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
            (data["Probabilidade_Goals_Scored_Away"] >= 1.4) &
            (data["Probabilidade_Goals_Taken_Home"] >= 1.3) &
            (data["Media_CG_01_Marcados_Away"] >= 3) &
            (data["Media_CG_02_Marcados_Away"] >= 0.8) &
            (data["CV_Media_CG_02_Marcados_Away"] <= 0.8) &
            (data["FT_Odd_Ov25"] <= 2.3) &
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
