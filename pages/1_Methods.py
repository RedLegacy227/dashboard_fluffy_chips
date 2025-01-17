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
tab1, tab2, tab3, tab4, tab5, tab6, tab7,tab8 = st.tabs(['Lay 0 x 1', 'Lay 1 x 0', 'Over 0,5 HT', 'Over 1,5 FT', 'Lay Home', 'Lay Away', 'Under 1,5 FT', 'Back Home'])

with tab1:
    st.subheader('Todays Games for Lay 0X1 - Fluffy Method ')
    st.markdown('Croatia - HNL - 97,58%')
    if data is not None:
        # DataFrame de referências
        df_referencias = pd.DataFrame({
            "Intervalo CV": ["<0.5000", "0.5001 - 0.8000", ">0.8001"],
            "<1.2500": ["0", "< 105", "< 100"],
            "1.2501 - 1.5500": ["0", "< 88", "< 22"],
            ">1.5501": ["< 20", "< 60", "0"]
        })
        # Função para determinar a referência com base nos intervalos
        def obter_referencia(cv_match_odds, ft_odd_h):
            # Determinar a linha (intervalo de CV_Match_Odds)
            if cv_match_odds < 0.5000:
                linha = 0
            elif 0.5001 <= cv_match_odds <= 0.8000:
                linha = 1
            elif cv_match_odds > 0.8001:
                linha = 2
            else:
                return "Sem valores"
            # Determinar a coluna (intervalo de FT_Odd_H)
            if ft_odd_h < 1.2500:
                coluna = "<1.2500"
            elif 1.2501 <= ft_odd_h <= 1.5500:
                coluna = "1.2501 - 1.5500"
            elif ft_odd_h > 1.5501:
                coluna = ">1.5501"
            else:
                return "Sem valores"
            # Buscar e retornar o valor correspondente no DataFrame de referências
            return df_referencias.at[linha, coluna]
        # Aplicar os filtros
        lay_0x1_hr_flt = data[
            (data["League"] == 'CROATIA - HNL') &
            (data["Probability_Away"] == 'Media_Bigger') &
            (data["Prob_BTTS_N_FT"] >= 0.5001) &
            (data['Poisson_0_GM_Home'] <= 0.30)
        ]
        lay_0x1_hr_flt = lay_0x1_hr_flt.sort_values(by='Time', ascending=True)
        # Aplicar a função para calcular 'Odd_Justa_Lay_0x1'
        lay_0x1_hr_flt['Odd_Justa_Lay_0x1'] = lay_0x1_hr_flt.apply(
            lambda row: obter_referencia(row['CV_Match_Odds'], row['FT_Odd_H']),
            axis=1
        )
        # Exibir os dados filtrados
        if not lay_0x1_hr_flt.empty:
            st.dataframe(lay_0x1_hr_flt[['Time', 'League', 'Home', 'Away', 'Odd_Justa_Lay_0x1',
                                            'FT_Odd_H', 'FT_Odd_D', 'FT_Odd_A', 'CV_Match_Odds',
                                            'CV_Match_Type', 'Perc_Over_15_FT_Home', 'Perc_Over_15_FT_Away']])
        else:
            st.info("Nenhum jogo encontrado com os critérios especificados.")
    else:
        st.info("Dados indisponíveis para a data selecionada.")
    st.markdown('PORTUGAL - LIGA PORTUGAL - 97,07%')
    if data is not None:
        # DataFrame de referências
        df_referencias = pd.DataFrame({
            "Intervalo CV": ["<0.5500", "0.5501 - 0.9000", ">0.9001"],
            "<1.1800": ["0", "0", "< 50"],
            "1.1801 - 1.3600": ["0", "< 18", "< 50"],
            "1.3601 - 1.6500": ["< 100", "< 96", "0"],
            ">1.6501": ["< 30", "0", "0"]
        })
        # Função para determinar a referência com base nos intervalos
        def obter_referencia(cv_match_odds, ft_odd_h):
            # Determinar a linha (intervalo de CV_Match_Odds)
            if cv_match_odds < 0.5500:
                linha = 0
            elif 0.5501 <= cv_match_odds <= 0.9000:
                linha = 1
            elif cv_match_odds > 0.9001:
                linha = 2
            else:
                return "Sem valores"
            # Determinar a coluna (intervalo de FT_Odd_H)
            if ft_odd_h < 1.1800:
                coluna = "<1.1800"
            elif 1.1801 <= ft_odd_h <= 1.3600:
                coluna = "1.1801 - 1.3600"
            elif 1.3601 <= ft_odd_h <= 1.6500:
                coluna = "1.3601 - 1.6500"
            elif ft_odd_h > 1.6501:
                coluna = ">1.6501"
            else:
                return "Sem valores"
            # Buscar e retornar o valor correspondente no DataFrame de referências
            return df_referencias.at[linha, coluna]
        # Aplicar os filtros
        lay_0x1_pt1_flt = data[
            (data["League"] == 'PORTUGAL - LIGA PORTUGAL') &
            (data["Probability_Away"] == 'Media_Bigger') &
            (data["Prob_H"] >= 0.4501) &
            (data['Poisson_3_GM_Away'] <= 0.10)
        ]
        lay_0x1_pt1_flt = lay_0x1_pt1_flt.sort_values(by='Time', ascending=True)
        # Aplicar a função para calcular 'Odd_Justa_Lay_0x1'
        lay_0x1_pt1_flt['Odd_Justa_Lay_0x1'] = lay_0x1_pt1_flt.apply(
            lambda row: obter_referencia(row['CV_Match_Odds'], row['FT_Odd_H']),
            axis=1
        )
        # Exibir os dados filtrados
        if not lay_0x1_pt1_flt.empty:
            st.dataframe(lay_0x1_pt1_flt[['Time', 'League', 'Home', 'Away', 'Odd_Justa_Lay_0x1',
                                            'FT_Odd_H', 'FT_Odd_D', 'FT_Odd_A', 'CV_Match_Odds',
                                            'CV_Match_Type', 'Perc_Over_15_FT_Home', 'Perc_Over_15_FT_Away']])
        else:
            st.info("Nenhum jogo encontrado com os critérios especificados.")
    else:
        st.info("Dados indisponíveis para a data selecionada.")
    st.markdown('PORTUGAL - LIGA PORTUGAL 2 - 95,37%')
    if data is not None:
        # DataFrame de referências
        df_referencias = pd.DataFrame({
            "Intervalo CV": ["<0.2000", "0.2001 - 0.4000", ">0.4001"],
            "<1.6500": ["0", "0", "<58"],
            "1.6501 - 1.9500": ["0", "<31", "<8"],
            "1.9501 - 2.2000": ["<14", "<16", "0"],
            ">2.2001": ["<22", "0", "0"]
        })
        # Função para determinar a referência com base nos intervalos
        def obter_referencia(cv_match_odds, ft_odd_h):
            # Determinar a linha (intervalo de CV_Match_Odds)
            if cv_match_odds < 0.2000:
                linha = 0
            elif 0.2001 <= cv_match_odds <= 0.4000:
                linha = 1
            elif cv_match_odds > 0.4001:
                linha = 2
            else:
                return "Sem valores"
            # Determinar a coluna (intervalo de FT_Odd_H)
            if ft_odd_h < 1.6500:
                coluna = "<1.6500"
            elif 1.6501 <= ft_odd_h <= 1.9500:
                coluna = "1.6501 - 1.9500"
            elif 1.3601 <= ft_odd_h <= 1.6500:
                coluna = "1.9501 - 2.2000"
            elif ft_odd_h > 2.2001:
                coluna = ">2.2001"
            else:
                return "Sem valores"
            # Buscar e retornar o valor correspondente no DataFrame de referências
            return df_referencias.at[linha, coluna]
        # Aplicar os filtros
        lay_0x1_pt2_flt = data[
            (data["League"] == 'PORTUGAL - LIGA PORTUGAL 2') &
            (data["Conceded_Goals"] == 'Bigger_Away') &
            (data["Prob_H"] >= 0.3501) &
            (data['Poisson_2_GM_Away'] >= 0.0501) &
            (data['Poisson_2_GM_Away'] <= 0.25) &
            (data['Poisson_2_GS_Away'] >= 0.2001)
            
        ]
        lay_0x1_pt2_flt = lay_0x1_pt2_flt.sort_values(by='Time', ascending=True)
        # Aplicar a função para calcular 'Odd_Justa_Lay_0x1'
        lay_0x1_pt2_flt['Odd_Justa_Lay_0x1'] = lay_0x1_pt2_flt.apply(
            lambda row: obter_referencia(row['CV_Match_Odds'], row['FT_Odd_H']),
            axis=1
        )
        # Exibir os dados filtrados
        if not lay_0x1_pt2_flt.empty:
            st.dataframe(lay_0x1_pt2_flt[['Time', 'League', 'Home', 'Away', 'Odd_Justa_Lay_0x1',
                                            'FT_Odd_H', 'FT_Odd_D', 'FT_Odd_A', 'CV_Match_Odds',
                                            'CV_Match_Type', 'Perc_Over_15_FT_Home', 'Perc_Over_15_FT_Away']])
        else:
            st.info("Nenhum jogo encontrado com os critérios especificados.")
    else:
        st.info("Dados indisponíveis para a data selecionada.")
    st.markdown('GERMANY - BUNDESLIGA - 98,11%')
    if data is not None:
        # DataFrame de referências
        df_referencias = pd.DataFrame({
            "Intervalo CV": ["<0.5000", "0.5001 - 0.7500", ">0.7501"],
            "<1.3000": ["0", "0", "< 50"],
            "1.3001 - 1.5000": ["0", "< 18", "< 50"],
            "1.5001 - 1.7900": ["< 100", "< 96", "0"],
            ">1.7901": ["< 30", "0", "0"]
        })
        # Função para determinar a referência com base nos intervalos
        def obter_referencia(cv_match_odds, ft_odd_h):
            # Determinar a linha (intervalo de CV_Match_Odds)
            if cv_match_odds < 0.5000:
                linha = 0
            elif 0.5001 <= cv_match_odds <= 0.7500:
                linha = 1
            elif cv_match_odds > 0.7501:
                linha = 2
            else:
                return "Sem valores"
            # Determinar a coluna (intervalo de FT_Odd_H)
            if ft_odd_h < 1.3000:
                coluna = "<1.3000"
            elif 1.3001 <= ft_odd_h <= 1.5000:
                coluna = "1.3001 - 1.5000"
            elif 1.5001 <= ft_odd_h <= 1.7900:
                coluna = "1.5001 - 1.7900"
            elif ft_odd_h > 1.7901:
                coluna = ">1.7901"
            else:
                return "Sem valores"
            # Buscar e retornar o valor correspondente no DataFrame de referências
            return df_referencias.at[linha, coluna]
        # Aplicar os filtros
        lay_0x1_ger1_flt = data[
            (data["League"] == 'GERMANY - BUNDESLIGA') &
            (data["Probability_Away"] == 'Media_Bigger') &
            (data["Poisson_2_GS_Away"] >= 0.1501) &
            (data["Prob_H"] >= 0.4501) &
            (data["Prob_H"] <= 0.95)
        ]
        lay_0x1_ger1_flt = lay_0x1_ger1_flt.sort_values(by='Time', ascending=True)
        # Aplicar a função para calcular 'Odd_Justa_Lay_0x1'
        lay_0x1_ger1_flt['Odd_Justa_Lay_0x1'] = lay_0x1_ger1_flt.apply(
            lambda row: obter_referencia(row['CV_Match_Odds'], row['FT_Odd_H']),
            axis=1
        )
        # Exibir os dados filtrados
        if not lay_0x1_ger1_flt.empty:
            st.dataframe(lay_0x1_ger1_flt[['Time', 'League', 'Home', 'Away', 'Odd_Justa_Lay_0x1',
                                            'FT_Odd_H', 'FT_Odd_D', 'FT_Odd_A', 'CV_Match_Odds',
                                            'CV_Match_Type', 'Perc_Over_15_FT_Home', 'Perc_Over_15_FT_Away']])
        else:
            st.info("Nenhum jogo encontrado com os critérios especificados.")
    else:
        st.info("Dados indisponíveis para a data selecionada.")    
    st.markdown('ENGLAND - PREMIER LEAGUE - 96,43%')
    if data is not None:
        # DataFrame de referências
        df_referencias = pd.DataFrame({
            "Intervalo CV": ["<0.4500", "0.4501 - 0.6500", ">0.6501"],
            "<1.3400": ["0", "0", "<33"],
            "1.3401 - 1.6000": ["0", "<27", "<25"],
            "1.6001 - 1.9800": ["<31", "<20", "0"],
            ">1.9801": ["<27", "<26", "0"]
        })
        # Função para determinar a referência com base nos intervalos
        def obter_referencia(cv_match_odds, ft_odd_h):
            # Determinar a linha (intervalo de CV_Match_Odds)
            if cv_match_odds < 0.4500:
                linha = 0
            elif 0.4501 <= cv_match_odds <= 0.6500:
                linha = 1
            elif cv_match_odds > 0.6501:
                linha = 2
            else:
                return "Sem valores"
            # Determinar a coluna (intervalo de FT_Odd_H)
            if ft_odd_h < 1.3400:
                coluna = "<1.3400"
            elif 1.3401 <= ft_odd_h <= 1.6000:
                coluna = "1.3401 - 1.6000"
            elif 1.6001 <= ft_odd_h <= 1.9800:
                coluna = "1.6001 - 1.9800"
            elif ft_odd_h > 1.9801:
                coluna = ">1.9801"
            else:
                return "Sem valores"
            # Buscar e retornar o valor correspondente no DataFrame de referências
            return df_referencias.at[linha, coluna]
        # Aplicar os filtros
        lay_0x1_eng1_flt = data[
            (data["League"] == 'ENGLAND - PREMIER LEAGUE') &
            (data["Probability_Home"] == 'p_Bigger') &
            (data["Poisson_1_GM_Home"] <= 0.40) &
            (data["Prob_D"] <= 0.30)
        ]
        lay_0x1_eng1_flt = lay_0x1_eng1_flt.sort_values(by='Time', ascending=True)
        # Aplicar a função para calcular 'Odd_Justa_Lay_0x1'
        lay_0x1_eng1_flt['Odd_Justa_Lay_0x1'] = lay_0x1_eng1_flt.apply(
            lambda row: obter_referencia(row['CV_Match_Odds'], row['FT_Odd_H']),
            axis=1
        )
        # Exibir os dados filtrados
        if not lay_0x1_eng1_flt.empty:
            st.dataframe(lay_0x1_eng1_flt[['Time', 'League', 'Home', 'Away', 'Odd_Justa_Lay_0x1',
                                            'FT_Odd_H', 'FT_Odd_D', 'FT_Odd_A', 'CV_Match_Odds',
                                            'CV_Match_Type', 'Perc_Over_15_FT_Home', 'Perc_Over_15_FT_Away']])
        else:
            st.info("Nenhum jogo encontrado com os critérios especificados.")
    else:
        st.info("Dados indisponíveis para a data selecionada.")
    st.markdown('ITALY - SERIE A - 96,15%')
    
    if data is not None:
        df_referencias = pd.DataFrame({
            "Intervalo CV": ["<0.5000", "0.5001 - 0.7500", ">0.7501"],
            "<1.3200": ["0", "<40", "<27"],
            "1.3201 - 1.5000": ["0", "<33", "<35"],
            "1.5001 - 1.7500": ["<51", "<62", "0"],
            ">1.7501": ["<14", "0", "0"]
        })
        # Função para determinar a referência com base nos intervalos
        def obter_referencia(cv_match_odds, ft_odd_h):
            # Determinar a linha (intervalo de CV_Match_Odds)
            if cv_match_odds < 0.5000:
                linha = 0
            elif 0.5001 <= cv_match_odds <= 0.7500:
                linha = 1
            elif cv_match_odds > 0.7501:
                linha = 2
            else:
                return "Sem valores"
            # Determinar a coluna (intervalo de FT_Odd_H)
            if ft_odd_h < 1.3200:
                coluna = "<1.3200"
            elif 1.3201 <= ft_odd_h <= 1.5000:
                coluna = "1.3201 - 1.5000"
            elif 1.5001 <= ft_odd_h <= 1.7500:
                coluna = "1.5001 - 1.7500"
            elif ft_odd_h > 1.7501:
                coluna = ">1.7501"
            else:
                return "Sem valores"
            # Buscar e retornar o valor correspondente no DataFrame de referências
            return df_referencias.at[linha, coluna]
        # Aplicar os filtros
        lay_0x1_ita1_flt = data[
            (data["League"] == 'ITALY - SERIE A') &
            (data["Probability_Away"] == 'Media_Bigger') &
            (data["Poisson_3_GS_Away"] >= 0.1001) &
            (data["Prob_H"] >= 0.3501)
        ]
        lay_0x1_ita1_flt = lay_0x1_ita1_flt.sort_values(by='Time', ascending=True)
        # Aplicar a função para calcular 'Odd_Justa_Lay_0x1'
        lay_0x1_ita1_flt['Odd_Justa_Lay_0x1'] = lay_0x1_ita1_flt.apply(
            lambda row: obter_referencia(row['CV_Match_Odds'], row['FT_Odd_H']),
            axis=1
        )
        # Exibir os dados filtrados
        if not lay_0x1_ita1_flt.empty:
            st.dataframe(lay_0x1_ita1_flt[['Time', 'League', 'Home', 'Away', 'Odd_Justa_Lay_0x1',
                                            'FT_Odd_H', 'FT_Odd_D', 'FT_Odd_A', 'CV_Match_Odds',
                                            'CV_Match_Type', 'Perc_Over_15_FT_Home', 'Perc_Over_15_FT_Away']])
        else:
            st.info("Nenhum jogo encontrado com os critérios especificados.")
    else:
        st.info("Dados indisponíveis para a data selecionada.")
    st.markdown('SPAIN - LALIGA - 95,44%')
    
    if data is not None:
        df_referencias = pd.DataFrame({
            "Intervalo CV": ["<0.3500", "0.3501 - 0.6000", ">0.6001"],
            "<1.4300": ["0", "0", "<36"],
            "1.4301 - 1.7000": ["0", "<33", "<13"],
            "1.7001 - 1.9500": ["<43", "<19", "0"],
            ">1.9501": ["<17", "0", "0"]
        })
        # Função para determinar a referência com base nos intervalos
        def obter_referencia(cv_match_odds, ft_odd_h):
            # Determinar a linha (intervalo de CV_Match_Odds)
            if cv_match_odds < 0.3500:
                linha = 0
            elif 0.3501 <= cv_match_odds <= 0.6000:
                linha = 1
            elif cv_match_odds > 0.6001:
                linha = 2
            else:
                return "Sem valores"
            # Determinar a coluna (intervalo de FT_Odd_H)
            if ft_odd_h < 1.4300:
                coluna = "<1.4300"
            elif 1.4301 <= ft_odd_h <= 1.7000:
                coluna = "1.4301 - 1.7000"
            elif 1.7001 <= ft_odd_h <= 1.9500:
                coluna = "1.7001 - 1.9500"
            elif ft_odd_h > 1.9501:
                coluna = ">1.9501"
            else:
                return "Sem valores"
            # Buscar e retornar o valor correspondente no DataFrame de referências
            return df_referencias.at[linha, coluna]
        # Aplicar os filtros
        lay_0x1_spa1_flt = data[
            (data["League"] == 'SPAIN - LALIGA') &
            (data["Probability_Home"] == 'p_Bigger') &
            (data["Poisson_2_GM_Away"] <=0.25) &
            (data["Poisson_0_GS_Away"] <=0.35) &
            (data["Prob_H"] >= 0.4001)
        ]
        lay_0x1_spa1_flt = lay_0x1_spa1_flt.sort_values(by='Time', ascending=True)
        # Aplicar a função para calcular 'Odd_Justa_Lay_0x1'
        lay_0x1_spa1_flt['Odd_Justa_Lay_0x1'] = lay_0x1_spa1_flt.apply(
            lambda row: obter_referencia(row['CV_Match_Odds'], row['FT_Odd_H']),
            axis=1
        )
        # Exibir os dados filtrados
        if not lay_0x1_spa1_flt.empty:
            st.dataframe(lay_0x1_spa1_flt[['Time', 'League', 'Home', 'Away', 'Odd_Justa_Lay_0x1',
                                            'FT_Odd_H', 'FT_Odd_D', 'FT_Odd_A', 'CV_Match_Odds',
                                            'CV_Match_Type', 'Perc_Over_15_FT_Home', 'Perc_Over_15_FT_Away']])
        else:
            st.info("Nenhum jogo encontrado com os critérios especificados.")
    else:
        st.info("Dados indisponíveis para a data selecionada.")
    st.markdown('TURKEY - SUPER LIG - 95,54%')
    
    if data is not None:
        df_referencias = pd.DataFrame({
            "Intervalo CV": ["<0.2500", "0.2501 - 0.5500", ">0.5501"],
            "<1.5500": ["0", "0", "<51"],
            "1.5501 - 1.9500": ["0", "<24", "<16"],
            "1.9501 - 2.3500": ["<17", "<18", "0"],
            ">2.3501": ["<18", "<19", "<31"]
        })
        # Função para determinar a referência com base nos intervalos
        def obter_referencia(cv_match_odds, ft_odd_h):
            # Determinar a linha (intervalo de CV_Match_Odds)
            if cv_match_odds < 0.2500:
                linha = 0
            elif 0.2501 <= cv_match_odds <= 0.5500:
                linha = 1
            elif cv_match_odds > 0.5501:
                linha = 2
            else:
                return "Sem valores"
            # Determinar a coluna (intervalo de FT_Odd_H)
            if ft_odd_h < 1.5500:
                coluna = "<1.5500"
            elif 1.5501 <= ft_odd_h <= 1.9500:
                coluna = "1.5501 - 1.9500"
            elif 1.9501 <= ft_odd_h <= 2.3500:
                coluna = "1.9501 - 2.3500"
            elif ft_odd_h > 2.3501:
                coluna = ">2.3501"
            else:
                return "Sem valores"
            # Buscar e retornar o valor correspondente no DataFrame de referências
            return df_referencias.at[linha, coluna]
        # Aplicar os filtros
        lay_0x1_tur1_flt = data[
            (data["League"] == 'TURKEY - SUPER LIG') &
            (data["Goal_Difference"] == 'Bigger_Home') &
            (data["Poisson_2_GM_Away"] >=0.1001) &
            (data["Poisson_2_GM_Away"] <=0.25) &
            (data["Media_CG_02_Marcados_Home"] >=0.4501) &
            (data["Media_CG_02_Marcados_Home"] <= 1.05) &
            (data["Prob_BTTS_N_FT"] <= 0.60) 
            
        ]
        lay_0x1_tur1_flt = lay_0x1_tur1_flt.sort_values(by='Time', ascending=True)
        # Aplicar a função para calcular 'Odd_Justa_Lay_0x1'
        lay_0x1_tur1_flt['Odd_Justa_Lay_0x1'] = lay_0x1_tur1_flt.apply(
            lambda row: obter_referencia(row['CV_Match_Odds'], row['FT_Odd_H']),
            axis=1
        )
        # Exibir os dados filtrados
        if not lay_0x1_tur1_flt.empty:
            st.dataframe(lay_0x1_spa1_flt[['Time', 'League', 'Home', 'Away', 'Odd_Justa_Lay_0x1',
                                            'FT_Odd_H', 'FT_Odd_D', 'FT_Odd_A', 'CV_Match_Odds',
                                            'CV_Match_Type', 'Perc_Over_15_FT_Home', 'Perc_Over_15_FT_Away']])
        else:
            st.info("Nenhum jogo encontrado com os critérios especificados.")
    else:
        st.info("Dados indisponíveis para a data selecionada.")

with tab2:
    st.subheader('Todays Games for Lay 1X0 - Fluffy Method ')
    st.markdown('Croatia - HNL - 93,35%')
    if data is not None:
        # DataFrame de referências
        df_referencias = pd.DataFrame({
            "Intervalo CV": ["<0.2000", "0.2001 - 0.4500", ">0.4501"],
            "<1.7900": ["0", "< 20", "< 19"],
            "1.7901 - 2.7000": ["< 8.5", "< 12", "< 0"],
            ">1.7901": ["< 43", "< 14.5", "< 6"]
        })
        # Função para determinar a referência com base nos intervalos
        def obter_referencia(cv_match_odds, ft_odd_a):
            # Determinar a linha (intervalo de CV_Match_Odds)
            if cv_match_odds < 0.2000:
                linha = 0
            elif 0.2001 <= cv_match_odds <= 0.4500:
                linha = 1
            elif cv_match_odds > 0.4501:
                linha = 2
            else:
                return "Sem valores"
            # Determinar a coluna (intervalo de FT_Odd_A)
            if ft_odd_a < 1.7900:
                coluna = "<1.7900"
            elif 1.7901 <= ft_odd_a <= 2.7000:
                coluna = "1.7901 - 2.7000"
            elif ft_odd_a > 2.7001:
                coluna = ">2.7001"
            else:
                return "Sem valores"
            # Buscar e retornar o valor correspondente no DataFrame de referências
            return df_referencias.at[linha, coluna]
        # Aplicar os filtros
        lay_1x0_hr_flt = data[
            (data["League"] == 'CROATIA - HNL') &
            (data["Probability_Away"] == 'p_Bigger') &
            (data["Poisson_1_GM_Home"] >= 0.3501) &
            (data["Poisson_0_GM_Home"] >= 0.2501) &
            (data['Poisson_0_GM_Home'] <= 0.50)
        ]
        lay_1x0_hr_flt = lay_1x0_hr_flt.sort_values(by='Time', ascending=True)
        # Aplicar a função para calcular 'Odd_Justa_Lay_1x0'
        lay_1x0_hr_flt['Odd_Justa_Lay_1x0'] = lay_1x0_hr_flt.apply(
            lambda row: obter_referencia(row['CV_Match_Odds'], row['FT_Odd_A']),
            axis=1
        )
        # Exibir os dados filtrados
        if not lay_1x0_hr_flt.empty:
            st.dataframe(lay_1x0_hr_flt[['Time', 'League', 'Home', 'Away', 'Odd_Justa_Lay_1x0',
                                            'FT_Odd_H', 'FT_Odd_D', 'FT_Odd_A', 'CV_Match_Odds',
                                            'CV_Match_Type', 'Perc_Over_15_FT_Home', 'Perc_Over_15_FT_Away']])
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
        
with tab8:
    st.subheader('Todays Games for Back_Home')
    st.markdown('Portugal - Liga Portugal 1 - Method 1')
    if data is not None:
        # Aplicar os filtros
        back_home_Port_01_01_ft_flt = data[
            (data["League"] == 'PORTUGAL - LIGA PORTUGAL') &
            (data["Home_Score_Take"] == 'No') &
            (data["Away_Score_Take"] == 'Yes') &
            (data["Media_Saldo_Golos_Away"] > -0.0900) &
            (data["Media_Saldo_Golos_Away"] < 0.0250)
        ]
        back_home_Port_01_01_ft_flt = back_home_Port_01_01_ft_flt.sort_values(by='Time', ascending=True)

        # Exibir os dados filtrados
        if not back_home_Port_01_01_ft_flt.empty:
            st.dataframe(back_home_Port_01_01_ft_flt)
        else:
            st.info("Nenhum jogo encontrado com os critérios especificados.")
    else:
        st.info("Dados indisponíveis para a data selecionada.")
    st.markdown('Portugal - Liga Portugal 1 - Method 2')
    if data is not None:
        # Aplicar os filtros
        back_home_Port_01_02_ft_flt = data[
            (data["League"] == 'PORTUGAL - LIGA PORTUGAL') &
            (data["Home_Score_Take"] == 'No') &
            (data["Away_Score_Take"] == 'Yes') &
            (data["Poisson_2_GS_Away"] > 0.2520) &
            (data["Poisson_2_GS_Away"] < 0.2710) &
            (data["Media_Ptos_Away"] > 0.9780) &
            (data["Media_Ptos_Away"] < 1.6950)
        ]
        back_home_Port_01_02_ft_flt = back_home_Port_01_02_ft_flt.sort_values(by='Time', ascending=True)

        # Exibir os dados filtrados
        if not back_home_Port_01_02_ft_flt.empty:
            st.dataframe(back_home_Port_01_02_ft_flt)
        else:
            st.info("Nenhum jogo encontrado com os critérios especificados.")
    else:
        st.info("Dados indisponíveis para a data selecionada.")
    st.markdown('Portugal - Liga Portugal 1 - Method 3')
    if data is not None:
        # Aplicar os filtros
        back_home_Port_01_03_ft_flt = data[
            (data["League"] == 'PORTUGAL - LIGA PORTUGAL') &
            (data["Home_Score_Take"] == 'No') &
            (data["Away_Score_Take"] == 'Yes') &
            (data["Media_Ptos_Away"] > 0.9780) &
            (data["Media_Ptos_Away"] < 1.6950) &
            (data["Media_Golos_Sofridos_Away"] > 1.5120) &
            (data["Media_Golos_Sofridos_Away"] < 4.0670)
        ]
        back_home_Port_01_03_ft_flt = back_home_Port_01_03_ft_flt.sort_values(by='Time', ascending=True)

        # Exibir os dados filtrados
        if not back_home_Port_01_03_ft_flt.empty:
            st.dataframe(back_home_Port_01_03_ft_flt)
        else:
            st.info("Nenhum jogo encontrado com os critérios especificados.")
    else:
        st.info("Dados indisponíveis para a data selecionada.")