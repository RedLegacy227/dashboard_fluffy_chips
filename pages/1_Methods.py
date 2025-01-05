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
        
# URL dos dados de Elo e Tilt
elo_tilt_url = "https://raw.githubusercontent.com/RedLegacy227/elo_tilt/main/df_elo_tilt.csv"

with tab4:
    st.subheader("Todays Games for Back Home")
    
    if data is not None:
        try:
            # Carregar os dados de Elo e Tilt
            df_elo_tilt = pd.read_csv(elo_tilt_url)
            
            # Garantir que os nomes de colunas estão consistentes
            if 'Team' in df_elo_tilt.columns and 'Elo' in df_elo_tilt.columns and 'Tilt' in df_elo_tilt.columns:
                # Fazer o merge para adicionar os dados de Elo e Tilt das equipes
                data = data.merge(df_elo_tilt[['Team', 'Elo', 'Tilt']], left_on='Home', right_on='Team', how='left', suffixes=('', '_Home'))
                data = data.rename(columns={'Elo': 'Elo_Home', 'Tilt': 'Tilt_Home'})
                
                data = data.merge(df_elo_tilt[['Team', 'Elo', 'Tilt']], left_on='Away', right_on='Team', how='left', suffixes=('', '_Away'))
                data = data.rename(columns={'Elo': 'Elo_Away', 'Tilt': 'Tilt_Away'})
                
                # Calcular a diferença de Elo
                data['Elo_Difference'] = data['Elo_Home'] - data['Elo_Away']
                
                # Aplicar o filtro
                back_home_flt = data[data['Elo_Difference'] > 100]
                
                # Ordenar os dados
                back_home_flt = back_home_flt.sort_values(by='Time', ascending=True)
                
                # Exibir os dados filtrados
                if not back_home_flt.empty:
                    # Selecionar as colunas relevantes para exibição
                    st.dataframe(back_home_flt[['Time', 'Home', 'Away', 'FT_Odd_H', 'FT_Odd_A', 'FT_Odd_D', 'Elo_Home', 'Tilt_Home', 'Elo_Away', 'Tilt_Away',  'Elo_Difference', 'Media_SG_H', 'Media_SG_A', 'Media_Ptos_H', 'CV_Ptos_H', 'Media_Ptos_A', 'CV_Ptos_A', 'Media_CGM_H_02', 'CV_CGM_H_02', 'Media_CGM_A_02', 'CV_CGM_A_02' ]])
                else:
                    st.info("Nenhum jogo encontrado com diferença de Elo superior a 100.")
            else:
                st.error("Dados de Elo e Tilt não estão no formato esperado. Verifique se as colunas 'Team', 'Elo' e 'Tilt' estão presentes.")
        except Exception as e:
            st.error(f"Erro ao carregar os dados de Elo e Tilt: {e}")
    else:
        st.info("Dados indisponíveis para a data selecionada.")
        
with tab5:
    st.subheader("Todays Games for Back Away")
    
    if data is not None:
        try:
            # Verificar se as colunas Elo e Tilt já estão no dataframe
            if {'Elo_Home', 'Tilt_Home', 'Elo_Away', 'Tilt_Away'}.issubset(data.columns):
                # Aplicar o filtro para Back Away (diferença de Elo <= -100)
                back_away_flt = data[data['Elo_Difference'] <= -100]
                
                # Ordenar os dados
                back_away_flt = back_away_flt.sort_values(by='Time', ascending=True)
                
                # Exibir os dados filtrados
                if not back_away_flt.empty:
                    # Selecionar as colunas relevantes para exibição
                    st.dataframe(back_away_flt[['Time', 'Home', 'Away', 'FT_Odd_H', 'FT_Odd_A', 'FT_Odd_D', 'Elo_Home', 'Tilt_Home', 'Elo_Away', 'Tilt_Away',  'Elo_Difference', 'Media_SG_H', 'Media_SG_A', 'Media_Ptos_H', 'CV_Ptos_H', 'Media_Ptos_A', 'CV_Ptos_A', 'Media_CGM_H_02', 'CV_CGM_H_02', 'Media_CGM_A_02', 'CV_CGM_A_02' ]])
                else:
                    st.info("Nenhum jogo encontrado com diferença de Elo menor ou igual a -100.")
            else:
                st.error("As colunas de Elo e Tilt não estão disponíveis no dataframe. Verifique a execução do tab4.")
        except Exception as e:
            st.error(f"Erro ao processar os dados para Back Away: {e}")
    else:
        st.info("Dados indisponíveis para a data selecionada.")
