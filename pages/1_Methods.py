import pandas as pd
import numpy as np
import streamlit as st
from PIL import Image
import os
import base64
import requests
from datetime import datetime

# Streamlit App Title and Headers
st.title('_Fluffy Chips Web Analyzer_')
st.subheader('The place where you can Analyse Football Matches!!!')
st.divider()
st.subheader('_Methods for Today_')

# Display Image
image_path = os.path.join(os.getcwd(), 'static', 'analises001.png')
if os.path.exists(image_path):
    st.image(image_path, use_container_width=True)
else:
    st.warning("Image not found. Please check the file path.")

st.divider()

# URLs for CSV Files
github_base_url = "https://raw.githubusercontent.com/RedLegacy227/jogos_do_dia_com_variaveis/main/"
historical_data_url = "https://raw.githubusercontent.com/RedLegacy227/main_data_base/main/df_base_original.csv"
leagues_url = "https://raw.githubusercontent.com/RedLegacy227/dados_ligas/main/df_ligas.csv"
elo_tilt_url = "https://raw.githubusercontent.com/RedLegacy227/elo_tilt/main/df_elo_tilt.csv"

# Select Date
selected_date = st.date_input("Select a date:", value=datetime.today())
formatted_date = selected_date.strftime("%Y-%m-%d")

# Construct the CSV File URL
csv_file_name = f'df_jogos_do_dia_{formatted_date}.csv'
csv_file_url = github_base_url + csv_file_name

# Function to Load Data with Caching
@st.cache_data
def load_data(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return pd.read_csv(url)
        else:
            st.error(f"File not found: {url}")
            return None
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

# Load Data
with st.spinner("Fetching data..."):
    data = load_data(csv_file_url)
    historical_data = load_data(historical_data_url)
    leagues_data = load_data(leagues_url)
    elo_tilt_data = load_data(elo_tilt_url)

# Display Success Messages
if data is not None:
    st.success("Jogos do Dia loaded successfully!")
if historical_data is not None:
    st.success("Historical Data loaded successfully!")
if leagues_data is not None:
    st.success("Leagues Data loaded successfully!")
if elo_tilt_data is not None:
    st.success("Elo & Tilt Data loaded successfully!")

# Create Tabs
tabs = ['Lay 0 x 1', 'Goleada Home', 'Over 1,5 FT', 'Lay Home', 'Lay Away', 'Under 1,5 FT', 'Back Home', 'Lay 1x1']
tab_views = st.tabs(tabs)

# Exibir dados para cada liga
with tab_views[0]:
    def parse_interval(interval):
        """Converte uma string de intervalo ('<=X', '>=X', 'A - B') para um par de valores numéricos."""
        interval = interval.strip().replace(" ", "")  # Remover espaços extras
    
        if interval.startswith("<="):
            return (-float('inf'), float(interval[2:]))  # Exemplo: '<=0.2000' → (-inf, 0.2000)
        elif interval.startswith(">="):
            return (float(interval[2:]), float('inf'))  # Exemplo: '>=0.4001' → (0.4001, inf)
        elif "-" in interval:
            limites = [float(x) for x in interval.split("-")]
            return (limites[0], limites[1])  # Exemplo: '0.2001 - 0.4000' → (0.2001, 0.4000)
        else:
            raise ValueError(f"Formato de intervalo desconhecido: {interval}")
    
    def obter_referencia(cv_match_odds, ft_odd_h, df_referencias):
        """Determina a referência com base nos intervalos de CV_Match_Odds e FT_Odd_H."""
        try:
            # Garantir que os valores sejam numéricos
            cv_match_odds = float(cv_match_odds) if not pd.isna(cv_match_odds) else None
            ft_odd_h = float(ft_odd_h) if not pd.isna(ft_odd_h) else None
    
            if cv_match_odds is None or ft_odd_h is None:
                return None  # Se os valores estiverem ausentes, retorna None
    
            # Determinar a linha correta baseada no intervalo de CV_Match_Odds
            linha = None
            for i, intervalo in enumerate(df_referencias.index):
                min_val, max_val = parse_interval(intervalo)
    
                if min_val <= cv_match_odds <= max_val:
                    linha = i
                    break
    
            if linha is None:
                return None  # Caso não encontre um intervalo correspondente
    
            # Determinar a coluna correta baseada no intervalo de FT_Odd_H
            for coluna in df_referencias.columns:
                min_val, max_val = parse_interval(coluna)
    
                if min_val <= ft_odd_h <= max_val:
                    return df_referencias.iloc[linha][coluna]
    
            return None  # Retorna None se não houver correspondência
        except Exception as e:
            st.error(f"Erro ao obter referência: {e}")
            return None

    # Configurações de ligas e seus filtros
    leagues_config = {
        "EUROPE - CHAMPIONS LEAGUE": {
            "prob_filter": ("Probability_Away", "Media_Bigger"),
            "additional_filters": [
                ("Prob_H", ">=", 0.4001),
                ("Prob_D", "<=", 0.30)
            ],
            "df_referencias": pd.DataFrame({
                "Intervalo CV": ["<=0.5000", "0.5001 - 0.8000", ">=0.8001"],
                "<=1.2500": ["0", "0", "<1000"],
                "1.2501 - 1.4500": ["0", "<43", "<51"],
                "1.4501 - 1.7000": ["<11", "<18", "0"],
                ">=1.7001": ["<13", "0", "0"]
            }).set_index("Intervalo CV")
        },
        "ARGENTINA - TORNEO BETANO": {
            "prob_filter": ("Probability_Home", "p_Bigger"),
            "additional_filters": [
                ("Prob_Un25_FT", "<=", 0.75),
                ("Poisson_2_GM_Home", ">=", 0.1501)
            ],
            "df_referencias": pd.DataFrame({
                "Intervalo CV": ["<=0.3000", "0.3001 - 0.5000", ">=0.5001"],
                "<=1.6500": ["0", "<17", "<21"],
                "1.6501 - 1.8500": ["0", "<20", "<6"],
                "1.8501 - 2.1000": ["<14", "<13", "0"],
                ">=2.1001": ["<13", "<15", "0"]
            }).set_index("Intervalo CV")
        },
        "AUSTRALIA - A-LEAGUE": {
            "prob_filter": ("Goal_Difference", "Bigger_Home"),
            "additional_filters": [
                ("Poisson_1_GS_Away", ">=", 0.1501),
                ("Poisson_1_GM_Home", ">=", 0.2001),
                ("Prob_A", "<=", 0.45)
                ],
            "df_referencias": pd.DataFrame({
                "Intervalo CV": ["<=0.2000", "0.2001 - 0.4000", ">=0.4001"],
                "<=1.6500": ["0", "0", "<37"],
                "1.6501 - 1.9500": ["0", "<28", "<12"],
                "1.9501 - 2.3000": ["<39", "<29", "0"],
                ">=2.3001": ["<13", "<31", "0"]
                }).set_index("Intervalo CV")
        },
        "CROATIA - HNL": {
            "prob_filter": ("Probability_Away", "Media_Bigger"),
            "additional_filters": [
                ("Prob_BTTS_N_FT", ">=", 0.5001),
                ("Poisson_0_GM_Home", "<=", 0.30),
                ],
            "df_referencias": pd.DataFrame({
                "Intervalo CV": ["<=0.5000", "0.5001 - 0.8000", ">=0.8001"],
                "<=1.2500": ["0", "< 105", "< 100"],
                "1.2501 - 1.5500": ["0", "< 88", "< 22"],
                ">=1.5501": ["< 20", "< 60", "0"]
                }).set_index("Intervalo CV")
        },
        "COSTA RICA - PRIMERA DIVISION": {
            "prob_filter": ("Conceded_Goals", "Bigger_Away"),
            "additional_filters": [
                ("Prob_Un25_FT", ">=", 0.5001),
                ("Prob_H", ">=", 0.4001)
                ],
            "df_referencias": pd.DataFrame({
                "Intervalo CV": ["<=0.3000", "0.3001 - 0.5500", ">=0.5501"],
                "<=1.4500": ["0", "0", "<38"],
                "1.4501 - 1.7000": ["0", "<23", "<35"],
                "1.7001 - 2.0000": ["<19", "<31", "0"],
                ">=2.0001": ["<17", "0", "0"]
                }).set_index("Intervalo CV")
        },
        "EGYPT - PREMIER LEAGUE": {
            "prob_filter": ("Probability_Away", "Media_Bigger"),
            "additional_filters": [
                ("Prob_Ov25_FT", ">=", 0.4001),
                ("Prob_BTTS_N_FT", ">=", 0.5001)
                ],
            "df_referencias": pd.DataFrame({
                "Intervalo CV": ["<=0.3000", "0.3001 - 0.6000", ">=0.6001"],
                "<=1.4500": ["0", "0", "<160"],
                "1.4501 - 1.8000": ["0", "<33", "<36"],
                "1.8001 - 2.3000": ["<26", "<9", "0"],
                ">=2.3001": ["<22", "<17", "<5"]
                }).set_index("Intervalo CV")
        },
        "ENGLAND - PREMIER LEAGUE": {
            "prob_filter": ("Probability_Home", "p_Bigger"),
            "additional_filters": [
                ("Poisson_1_GM_Home", "<=", 0.40),
                ("Prob_D", "<=", 0.40)
                ],
            "df_referencias": pd.DataFrame({
                "Intervalo CV": ["<=0.4500", "0.4501 - 0.6500", ">=0.6501"],
                "<=1.3400": ["0", "0", "<33"],
                "1.3401 - 1.6000": ["0", "<27", "<25"],
                "1.6001 - 1.9800": ["<31", "<20", "0"],
                ">=1.9801": ["<27", "<26", "0"]
                }).set_index("Intervalo CV")
        },
        "ENGLAND - CHAMPIONSHIP": {
            "prob_filter": ("Probability_Home", "p_Bigger"),
            "additional_filters": [
                ("Poisson_1_GM_Home", "<=", 0.40),
                ("Prob_D", "<=", 0.30)
                ],
            "df_referencias": pd.DataFrame({
                "Intervalo CV": ["<=0.3500", "0.3501 - 0.5500", ">=0.5501"],
                "<=1.5500": ["0", "0", "<29"],
                "1.5501 - 1.7500": ["0", "<25", "<38"],
                "1.7501 - 2.0000": ["<8", "<22", "0"],
                ">=2.0001": ["<19", "0", "0"]
                }).set_index("Intervalo CV")
        },
        "ENGLAND - LEAGUE ONE": {
            "prob_filter": ("Probability_Away", "Media_Bigger"),
            "additional_filters": [
                ("Prob_A", "<=", 0.30),
                ("Prob_D", "<=", 0.30)
                ],
            "df_referencias": pd.DataFrame({
                "Intervalo CV": ["<=0.4000", "0.4001 - 0.5500", ">=0.5501"],
                "<=1.5000": ["0", "0", "<35"],
                "1.5001 - 1.6500": ["0", "<21", "<19"],
                "1.6501 - 1.8000": ["<30", "<33", "0"],
                ">=1.8001": ["<16", "0", "0"]
                }).set_index("Intervalo CV")
        },
        "FRANCE - LIGUE 1": {
            "prob_filter": ("Probability_Away", "Media_Bigger"),
            "additional_filters": [
                ("Prob_Ov25_FT", ">=", 0.4501),
                ("Prob_H", ">=", 0.3501)
                ],
            "df_referencias": pd.DataFrame({
                "Intervalo CV": ["<=0.4000", "0.4001 - 0.6500", ">=0.6501"],
                "<=1.4000": ["0", "0", "<51"],
                "1.4001 - 1.6000": ["0", "<24", "<16"],
                "1.6001 - 2.0000": ["<17", "<18", "0"],
                ">=2.0001": ["<18", "<19", "<31"]
                }).set_index("Intervalo CV")
        },
        "FRANCE - LIGUE 2": {
            "prob_filter": ("Probability_Home", "p_Bigger"),
            "additional_filters": [
                ("Poisson_1_GS_Away", ">=", 0.3001),
                ("Prob_H", ">=", 0.4001)
                ],
            "df_referencias": pd.DataFrame({
                "Intervalo CV": ["<=0.2500", "0.2501 - 0.4500", ">=0.4501"],
                "<=1.6500": ["0", "0", "<20"],
                "1.6501 - 1.8500": ["0", "<28", "<16"],
                "1.8501 - 2.0500": ["<8", "<11", "0"],
                ">=2.0501": ["<17", "<17", "0"]
                }).set_index("Intervalo CV")
        },
        "GERMANY - BUNDESLIGA": {
            "prob_filter": ("Probability_Away", "Media_Bigger"),
            "additional_filters": [
                ("Poisson_2_GS_Away", ">=", 0.1501),
                ("Prob_H", ">=", 0.5501),
                ("Prob_H", "<=", 0.95)
                ],
            "df_referencias": pd.DataFrame({
                "Intervalo CV": ["<=0.5000", "0.5001 - 0.7500", ">=0.7501"],
                "<=1.3000": ["0", "0", "< 50"],
                "1.3001 - 1.5000": ["0", "< 18", "< 50"],
                "1.5001 - 1.7900": ["< 100", "< 96", "0"],
                ">=1.7901": ["< 30", "0", "0"]
                }).set_index("Intervalo CV")
        },
        "GERMANY - 2. BUNDESLIGA": {
            "prob_filter": ("Probability_Away", "Media_Bigger"),
            "additional_filters": [
                ("Prob_D", "<=", 0.3000),
                ("Media_CG_02_Sofridos_Home", ">=", 0.2001),
                ("Media_CG_02_Sofridos_Home", "<=", 1.0000)
                ],
            "df_referencias": pd.DataFrame({
                "Intervalo CV": ["<=0.2500", "0.2501 - 0.4500", ">=0.4501"],
                "<=1.6500": ["0", "<38", "<48"],
                "1.6501 - 1.9000": ["0", "<24", "<17"],
                "1.9001 - 2.2500": ["<96", "<30", "0"],
                ">=2.2501": ["<33", "<42", "<39"]
                }).set_index("Intervalo CV")
        },
        "GREECE - SUPER LEAGUE": {
            "prob_filter": ("Goal_Difference", "Bigger_Home"),
            "additional_filters": [
                ("Media_CG_02_Sofridos_Away", ">=", 0.6001),
                ("Prob_H", ">=", 0.4001)
                ],
            "df_referencias": pd.DataFrame({
                "Intervalo CV": ["<=0.4000", "0.4001 - 0.8000", ">=0.8001"],
                "<=1.2000": ["0", "0", "<109"],
                "1.2001 - 1.4500": ["0", "<14", "<90"],
                "1.4501 - 1.9000": ["<11", "<13", "0"],
                ">=1.9001": ["<28", "0", "0"]
                }).set_index("Intervalo CV")
        },
        "INDIA - ISL": {
            "prob_filter": ("Probability_Home", "p_Bigger"),
            "additional_filters": [
                ("Poisson_2_GS_Away", ">=", 0.2501)
                ],
            "df_referencias": pd.DataFrame({
                "Intervalo CV": ["<=0.3000", "0.3001 - 0.5000", ">=0.5001"],
                "<=1.5000": ["0", "0", "<21"],
                "1.5001 - 1.7000": ["0", "<30", "<36"],
                "1.7001 - 2.0000": ["<14", "<40", "0"],
                ">=2.0001": ["<49", "0", "0"]
                }).set_index("Intervalo CV")
        },
        "INDONESIA - LIGA 1": {
            "prob_filter": ("Probability_Away", "Media_Bigger"),
            "additional_filters": [
                ("Prob_BTTS_Y_FT", ">=", 0.5001),
                ("Prob_BTTS_Y_FT", "<=", 0.6500),
                ("Prob_H", ">=", 0.4001),
                ("Prob_H", "<=", 0.8000)
                ],
            "df_referencias": pd.DataFrame({
                "Intervalo CV": ["<=0.3000", "0.3001 - 0.5500", ">=0.5501"],
                "<=1.4500": ["0", "0", "<37"],
                "1.4501 - 1.6500": ["0", "<31", "<51"],
                "1.6501 - 1.9500": ["<19", "<27", "0"],
                ">=1.9501": ["<13", "0", "0"]
                }).set_index("Intervalo CV")
        },
        "ISRAEL - LIGAT HA'AL": {
            "prob_filter": ("Probability_Away", "Media_Bigger"),
            "additional_filters": [
                ("Prob_Un25_FT", "<=", 0.6000),
                ("Prob_Ov25_FT", ">=", 0.4501)
                ],
            "df_referencias": pd.DataFrame({
                "Intervalo CV": ["<=0.4000", "0.4001 - 0.7000", ">=0.7001"],
                "<=1.3500": ["0", "0", "<58"],
                "1.3501 - 1.6000": ["0", "<45", "<52"],
                "1.6001 - 2.0000": ["<20", "<52", "0"],
                ">=2.0001": ["<15", "<48", "0"]
                }).set_index("Intervalo CV")
        },
        "ITALY - SERIE A": {
            "prob_filter": ("Probability_Away", "Media_Bigger"),
            "additional_filters": [
                ("Poisson_3_GS_Away", ">=", 0.1001),
                ("Prob_H", ">=", 0.3501)
                ],
            "df_referencias": pd.DataFrame({
                "Intervalo CV": ["<=0.5000", "0.5001 - 0.7500", ">=0.7501"],
                "<=1.3200": ["0", "<40", "<27"],
                "1.3201 - 1.5000": ["0", "<33", "<35"],
                "1.5001 - 1.7500": ["<51", "<62", "0"],
                ">=1.7501": ["<14", "0", "0"]
                }).set_index("Intervalo CV")
        },
        "ITALY - SERIE B": {
            "prob_filter": ("Goal_Difference", "Bigger_Home"),
            "additional_filters": [
                ("Poisson_2_GM_Home", ">=", 0.1501),
                ("Prob_A", ">=", 0.1001),
                ("Prob_A", "<=", 0.3500)
                ],
            "df_referencias": pd.DataFrame({
                "Intervalo CV": ["<=0.2000", "0.2001 - 0.4000", ">=0.4001"],
                "<=1.7500": ["0", "<21", "<22"],
                "1.7501 - 2.0000": ["0", "<20", "<20"],
                "2.0001 - 2.2500": ["<18", "<19", "0"],
                ">=2.2501": ["<15", "0", "0"]
                }).set_index("Intervalo CV")
        },
        "MEXICO - LIGA MX": {
            "prob_filter": ("Conceded_Goals", "Bigger_Away"),
            "additional_filters": [
                ("Poisson_0_GM_Home", "<=", 0.3500),
                ("Prob_H", ">=", 0.4501)
                ],
            "df_referencias": pd.DataFrame({
                "Intervalo CV": ["<=0.3500", "0.3501 - 0.5500", ">=0.5501"],
                "<=1.5000": ["0", "0", "<36"],
                "1.5001 - 1.7000": ["0", "<24", "<50"],
                "1.7001 - 1.9500": ["<27", "<33", "0"],
                ">=1.9501": ["<16", "0", "0"]
                }).set_index("Intervalo CV")
        },
        "NETHERLANDS - EREDIVISIE": {
            "prob_filter": ("Probability_Away", "Media_Bigger"),
            "additional_filters": [
                ("Prob_Un25_FT", "<=", 0.5000),
                ("Prob_H", ">=", 0.4001)
                ],
            "df_referencias": pd.DataFrame({
                "Intervalo CV": ["<=0.5500", "0.5501 - 0.8500", ">=0.8501"],
                "<=1.2000": ["0", "0", "<160"],
                "1.2001 - 1.3800": ["0", "<95", "<32"],
                "1.3801 - 1.6500": ["<20", "<62", "0"],
                ">=1.6501": ["<79", "0", "0"]
                }).set_index("Intervalo CV")
        },
        "NETHERLANDS - EERSTE DIVISIE": {
            "prob_filter": ("Conceded_Goals", "Bigger_Away"),
            "additional_filters": [
                ("Poisson_2_GS_Away", ">=", 0.2001),
                ("Prob_H", ">=", 0.4501)
                ],
            "df_referencias": pd.DataFrame({
                "Intervalo CV": ["<=0.3500", "0.3501 - 0.6000", ">=0.6001"],
                "<=1.3500": ["0", "0", "<54"],
                "1.3501 - 1.6000": ["0", "<16", "<30"],
                "1.6001 - 1.9000": ["<17", "<24", "0"],
                ">=1.9001": ["<19", "0", "0"]
                }).set_index("Intervalo CV")
        },
        "PORTUGAL - LIGA PORTUGAL": {
            "prob_filter": ("Probability_Away", "Media_Bigger"),
            "additional_filters": [
                ("Poisson_3_GM_Away", "<=", 0.1000),
                ("Prob_H", ">=", 0.4501)
                ],
            "df_referencias": pd.DataFrame({
                "Intervalo CV": ["<=0.5500", "0.5501 - 0.9000", ">=0.9001"],
                "<=1.1800": ["0", "0", "< 50"],
                "1.1801 - 1.3600": ["0", "< 18", "< 50"],
                "1.3601 - 1.6500": ["< 100", "< 96", "0"],
                ">=1.6501": ["< 30", "0", "0"]
                }).set_index("Intervalo CV")
        },
        "PORTUGAL - LIGA PORTUGAL 2": {
            "prob_filter": ("Conceded_Goals", "Bigger_Away"),
            "additional_filters": [
                ("Poisson_2_GM_Away", ">=", 0.0501),
                ("Poisson_2_GM_Away", "<=", 0.2500),
                ("Poisson_2_GS_Away", ">=", 0.2001),
                ("Prob_H", ">=", 0.3501)
                ],
            "df_referencias": pd.DataFrame({
                "Intervalo CV": ["<=0.2000", "0.2001 - 0.4000", ">=0.4001"],
                "<=1.6500": ["0", "0", "<58"],
                "1.6501 - 1.9500": ["0", "<31", "<8"],
                "1.9501 - 2.2000": ["<14", "<16", "0"],
                ">=2.2001": ["<22", "0", "0"]
                }).set_index("Intervalo CV")
        },
        "QATAR - QSL": {
            "prob_filter": ("Probability_Away", "Media_Bigger"),
            "additional_filters": [
                ("Poisson_1_GM_Home", ">=", 0.1001),
                ("Prob_D", "<=", 0.3000)
                ],
            "df_referencias": pd.DataFrame({
                "Intervalo CV": ["<=0.4000", "0.4001 - 0.6000", ">=0.6001"],
                "<=1.4000": ["0", "0", "<66"],
                "1.4001 - 1.6500": ["0", "<51", "<15"],
                "1.6501 - 2.0000": ["<44", "<69", "0"],
                ">=2.0001": ["<17", "<50", "<9"]
                }).set_index("Intervalo CV")
        },
        "ROMANIA - SUPERLIGA": {
            "prob_filter": ("Probability_Home", "p_Bigger"),
            "additional_filters": [
                ("Prob_Ov25_FT", ">=", 0.4001),
                ("Prob_H", ">=", 0.4501)
                ],
            "df_referencias": pd.DataFrame({
                "Intervalo CV": ["<=0.4000", "0.4001 - 0.6000", ">=0.6001"],
                "<=1.4000": ["0", "0", "<33"],
                "1.4001 - 1.6000": ["0", "<7", "<25"],
                "1.6001 - 1.8000": ["<23", "<19", "0"],
                ">=1.8001": ["<21", "0", "0"]
                }).set_index("Intervalo CV")
        },
        "SAUDI ARABIA - SAUDI PROFESSIONAL LEAGUE": {
            "prob_filter": ("Scored_Goals", "Bigger_Home"),
            "additional_filters": [
                ("Poisson_2_GS_Away", ">=", 0.1501),
                ("Poisson_2_GS_Away", "<=", 0.3000),
                ("Prob_H", ">=", 0.3001)
                ],
            "df_referencias": pd.DataFrame({
                "Intervalo CV": ["<=0.2000", "0.2001 - 0.5000", ">=0.5001"],
                "<=1.4000": ["0", "0", "<48"],
                "1.4001 - 1.8000": ["0", "<25", "<18"],
                "1.8001 - 2.2500": ["<18", "<31", "0"],
                ">=2.2501": ["<13", "<11", "0"]
                }).set_index("Intervalo CV")
        },
        "SPAIN - LALIGA": {
            "prob_filter": ("Probability_Home", "p_Bigger"),
            "additional_filters": [
                ("Poisson_2_GM_Away", "<=", 0.2500),
                ("Poisson_0_GS_Away", "<=", 0.3500),
                ("Prob_H", ">=", 0.4001)
                ],
            "df_referencias": pd.DataFrame({
                "Intervalo CV": ["<=0.3500", "0.3501 - 0.6000", ">=0.6001"],
                "<=1.4300": ["0", "0", "<36"],
                "1.4301 - 1.7000": ["0", "<33", "<13"],
                "1.7001 - 1.9500": ["<43", "<19", "0"],
                ">=1.9501": ["<17", "0", "0"]
                }).set_index("Intervalo CV")
        },
        "SPAIN - LALIGA2": {
            "prob_filter": ("Probability_Home", "p_Bigger"),
            "additional_filters": [
                ("Media_CG_02_Marcados_Home", ">=", 0.7501),
                ("Media_CG_02_Marcados_Home", "<=", 1.2000)
                ],
            "df_referencias": pd.DataFrame({
                "Intervalo CV": ["<=0.3000", "0.3001 - 0.4500", ">=0.4501"],
                "<=1.6600": ["0", "0", "<21"],
                "1.6601 - 1.8000": ["0", "<11", "<12"],
                "1.8001 - 2.0000": ["<10", "<21", "0"],
                ">=2.0001": ["<19", "0", "0"]
                }).set_index("Intervalo CV")
        },
        "THAILAND - THAI LEAGUE 1": {
            "prob_filter": ("Probability_Home", "p_Bigger"),
            "additional_filters": [
                ("Media_CG_02_Marcados_Away", ">=", 0.3001),
                ("Media_CG_02_Marcados_Away", "<=", 0.9500),
                ("Media_CG_02_Sofridos_Away", ">=", 0.5001),
                ("Media_CG_02_Sofridos_Away", "<=", 1.6000)
                ],
            "df_referencias": pd.DataFrame({
                "Intervalo CV": ["<=0.2500", "0.2501 - 0.5000", ">=0.5001"],
                "<=1.4000": ["0", "0", "<69"],
                "1.4001 - 1.6500": ["0", "<41", "<41"],
                "1.6501 - 2.0000": ["<14", "<15", "0"],
                ">=2.0001": ["<80", "0", "0"]
                }).set_index("Intervalo CV")
        },
        "TURKEY - SUPER LIG": {
            "prob_filter": ("Goal_Difference", "Bigger_Home"),
            "additional_filters": [
                ("Poisson_2_GM_Away", ">=", 0.1001),
                ("Poisson_2_GM_Away", "<=", 0.2500),
                ("Media_CG_02_Marcados_Home", ">=", 0.4501),
                ("Media_CG_02_Marcados_Home", "<=", 1.0500),
                ("Prob_BTTS_N_FT", "<=", 0.6000)
                ],
            "df_referencias": pd.DataFrame({
                "Intervalo CV": ["<=0.2500", "0.2501 - 0.5500", ">=0.5501"],
                "<=1.5500": ["0", "0", "<51"],
                "1.5501 - 1.9500": ["0", "<24", "<16"],
                "1.9501 - 2.3500": ["<17", "<18", "0"],
                ">=2.3501": ["<18", "<19", "<31"]
                }).set_index("Intervalo CV")
        },
        "TURKEY - 1. LIG": {
            "prob_filter": ("Probability_Home", "p_Bigger"),
            "additional_filters": [
                ("Poisson_2_GM_Home", ">=", 0.1501),
                ],
            "df_referencias": pd.DataFrame({
                "Intervalo CV": ["<=0.3500", "0.3501 - 0.6000", ">=0.6001"],
                "<=1.4000": ["0", "0", "<28"],
                "1.4001 - 1.6500": ["0", "<21", "<29"],
                "1.6501 - 1.9000": ["<21", "<11", "0"],
                ">=1.9001": ["<12", "0", "0"]
                }).set_index("Intervalo CV")
        }
    }
    st.subheader("Today's Games for Lay 0X1 - Fluffy Method")
    
    if data is not None:
        for league, config in leagues_config.items():
            st.markdown(f"### {league}")
            prob_filter_col, prob_filter_val = config["prob_filter"]
            df_referencias = config["df_referencias"]
            
            # Aplicar filtros
            filtered_data = data[data["League"] == league]
            filtered_data = filtered_data[filtered_data[prob_filter_col] == prob_filter_val]
            
            for col, op, val in config["additional_filters"]:
                if op == ">=":
                    filtered_data = filtered_data[filtered_data[col] >= val]
                elif op == "<=":
                    filtered_data = filtered_data[filtered_data[col] <= val]
            
            filtered_data = filtered_data.sort_values(by='Time', ascending=True)
            
            # Aplicar a função para calcular 'Odd_Justa_Lay_0x1'
            filtered_data["Odd_Justa_Lay_0x1"] = filtered_data.apply(
                lambda row: obter_referencia(row["CV_Match_Odds"], row["FT_Odd_H"], df_referencias),
                axis=1
            )
            
            # Exibir os dados filtrados
            if not filtered_data.empty:
                st.dataframe(filtered_data[['Time', 'League', 'Home', 'Away', 'Odd_Justa_Lay_0x1',
                                        'FT_Odd_H', 'FT_Odd_D', 'FT_Odd_A', 'CV_Match_Odds',
                                        'CV_Match_Type', 'Perc_Over_15_FT_Home', 'Perc_Over_15_FT_Away']])
            else:
                st.info("Nenhum jogo encontrado com os critérios especificados.")
    else:
        st.info("Dados indisponíveis para a data selecionada.")

with tab_views[1]:
    st.subheader('Todays Games for Lay Any Other Home Win')
    st.markdown('If you Get 2 Goals on the First Half, You must Exit the Operation')

    # Verificar se 'data' está disponível e contém as colunas necessárias
    required_columns = ["League", "Time", "Home", "Away", "FT_Odd_H", "FT_Odd_Ov25", "FT_Odd_BTTS_Y"]

    if data is not None and all(col in data.columns for col in required_columns):
        
        # Aplicar filtros
        flt = (
            (data["FT_Odd_H"] >= 1.50) & 
            (data["FT_Odd_Ov25"] >= 1.50) & 
            (data["FT_Odd_BTTS_Y"] <= 2.50) 
        )
        df_LGP = data[flt].dropna().reset_index(drop=True)  # Filtrar e resetar índice

        def LayGoleada(df_LGP, historical_data):
            """ 
            Filtra jogos onde as equipes têm alto potencial de gols marcados e sofridos.
            """

            required_cols = ["League", "Home", "Away", "FT_Goals_H", "FT_Goals_A"]
            
            if historical_data is None or not all(col in historical_data.columns for col in required_cols):
                st.warning("Os dados históricos estão incompletos ou ausentes.")
                return

            results = []  # Lista para armazenar os resultados

            try:
                for league in df_LGP["League"].unique():
                    df_league_hist = historical_data[historical_data["League"] == league]

                    if df_league_hist.empty:
                        continue  # Pula ligas sem histórico suficiente

                    # Contar quantas equipes existem na liga
                    unique_teams = set(df_league_hist["Home"]).union(set(df_league_hist["Away"]))
                    num_teams = len(unique_teams)

                    if num_teams < 6:
                        continue  # Pula ligas muito pequenas

                    # 🔹 Voltar ao método original de cálculo de gols
                    Gols_Marcados_Home = df_league_hist.groupby("Home")["FT_Goals_H"].sum()
                    Gols_Marcados_Away = df_league_hist.groupby("Away")["FT_Goals_A"].sum()
                    Gols_Marcados = pd.concat([Gols_Marcados_Home, Gols_Marcados_Away], axis=1).fillna(0)
                    Gols_Marcados["Gols_Marcados"] = Gols_Marcados.sum(axis=1)
                    Gols_Marcados = Gols_Marcados[["Gols_Marcados"]].sort_values("Gols_Marcados", ascending=False)

                    Gols_Sofridos_Home = df_league_hist.groupby("Home")["FT_Goals_A"].sum()
                    Gols_Sofridos_Away = df_league_hist.groupby("Away")["FT_Goals_H"].sum()
                    Gols_Sofridos = pd.concat([Gols_Sofridos_Home, Gols_Sofridos_Away], axis=1).fillna(0)
                    Gols_Sofridos["Gols_Sofridos"] = Gols_Sofridos.sum(axis=1)
                    Gols_Sofridos = Gols_Sofridos[["Gols_Sofridos"]].sort_values("Gols_Sofridos", ascending=True)

                    # 🔹 Ajuste nos limites para ligas pequenas e grandes
                    if num_teams > 10:
                        # Critério original para ligas grandes
                        top_scoring_teams = set(Gols_Marcados.iloc[5:min(15, num_teams)].index)
                        weak_defense_teams = set(Gols_Sofridos.iloc[:min(15, num_teams)].index)
                    else:
                        # Critério adaptado para ligas pequenas (top/bottom 50%)
                        top_scoring_teams = set(Gols_Marcados.iloc[:max(1, num_teams // 2)].index)
                        weak_defense_teams = set(Gols_Sofridos.iloc[:max(1, num_teams // 2)].index)

                    # 🔹 Filtrar jogos da liga que atendem aos critérios
                    df_matches_league = df_LGP[df_LGP["League"] == league]

                    for _, row in df_matches_league.iterrows():
                        home, away, match_time = row["Home"], row["Away"], row["Time"]

                        if home in top_scoring_teams and away in top_scoring_teams and \
                            home in weak_defense_teams and away in weak_defense_teams:
                            results.append([league, home, away, match_time])

                # Verificar se há resultados antes de exibir
                if results:
                    df_results = pd.DataFrame(results, columns=["League", "Home", "Away", "Time"])

                    # Verificar formato da coluna 'Time' antes de converter
                    try:
                        df_results["Time"] = pd.to_datetime(df_results["Time"], format="%H:%M").dt.time
                    except Exception:
                        st.error("Erro ao converter a coluna 'Time'. Verifique o formato dos dados.")

                    df_results = df_results.sort_values(by="Time").reset_index(drop=True)
                    st.dataframe(df_results, use_container_width=True)
                else:
                    st.warning("Nenhum jogo atende aos critérios.")

            except KeyError as e:
                st.error(f"Coluna ausente nos dados históricos: {e}")

        # Chamar a função
        LayGoleada(df_LGP, historical_data)

    else:
        st.warning("Os dados principais estão ausentes ou incompletos.")

with tab_views[2]:
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

with tab_views[3]:
    st.subheader("Todays Games for Lay Home")
    lay_home = data.copy()
    lay_home['VAR1'] = np.sqrt((lay_home['FT_Odd_H'] - lay_home['FT_Odd_A'])**2)
    lay_home['VAR2'] = np.degrees(np.arctan((lay_home['FT_Odd_A'] - lay_home['FT_Odd_H']) / 2))
    lay_home['VAR3'] = np.degrees(np.arctan((lay_home['FT_Odd_D'] - lay_home['FT_Odd_A']) / 2))
    
    if lay_home is not None:
        try:
            # Carregar os dados de Elo e Tilt apenas uma vez
            if 'Elo_Home' not in lay_home.columns or 'Elo_Away' not in lay_home.columns:
                df_elo_tilt = elo_tilt_data
                
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

with tab_views[4]:
    st.subheader("Todays Games for Lay Away")
    lay_away = data.copy()
    lay_away['VAR1'] = np.sqrt((lay_away['FT_Odd_H'] - lay_away['FT_Odd_A'])**2)
    lay_away['VAR2'] = np.degrees(np.arctan((lay_away['FT_Odd_A'] - lay_away['FT_Odd_H']) / 2))
    lay_away['VAR3'] = np.degrees(np.arctan((lay_away['FT_Odd_D'] - lay_away['FT_Odd_A']) / 2))
    
    if lay_away is not None:
        try:
            # Carregar os dados de Elo e Tilt apenas uma vez
            if 'Elo_Home' not in lay_away.columns or 'Elo_Away' not in lay_away.columns:
                df_elo_tilt = elo_tilt_data
                
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
        
with tab_views[5]:
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
        
with tab_views[6]:
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
    st.markdown('England - Premier League - Method 1')
    if data is not None:
        # Aplicar os filtros
        back_home_eng_01_01_ft_flt = data[
            (data["League"] == 'ENGLAND - PREMIER LEAGUE') &
            (data["Media_CG_02_Marcados_Home"] > 0.1910) &
            (data["Media_CG_02_Marcados_Home"] < 0.5580) &
            (data["Media_Golos_Sofridos_Away"] > 0.1980) &
            (data["Media_Golos_Sofridos_Away"] < 1.6000)
        ]
        back_home_eng_01_01_ft_flt = back_home_eng_01_01_ft_flt.sort_values(by='Time', ascending=True)

        # Exibir os dados filtrados
        if not back_home_eng_01_01_ft_flt.empty:
            st.dataframe(back_home_eng_01_01_ft_flt)
        else:
            st.info("Nenhum jogo encontrado com os critérios especificados.")
    else:
        st.info("Dados indisponíveis para a data selecionada.")
with tab_views[7]:
    st.subheader('Todays Games for Lay 1x1 Based on Home Team')
    st.markdown('Keep The Operation until Green or close at 60 min. At Half Time if you have Profit Close the Operation')
    if data is not None:
        # Aplicar os filtros
        lay_1x1_home_flt = data[
            (data["FT_Odd_H"] < 1.75) &
            (data["FT_Odd_Ov25"] < 1.65)
        ]
        lay_1x1_home_flt = lay_1x1_home_flt.sort_values(by='Time', ascending=True)

        # Exibir os dados filtrados
        if not lay_1x1_home_flt.empty:
            st.dataframe(lay_1x1_home_flt)
        else:
            st.info("Nenhum jogo encontrado com os critérios especificados.")
    st.subheader('Todays Games for Lay 1x1 Based on Away Team')
    st.markdown('Keep The Operation until Green or close at 60 min. At Half Time if you have Profit Close the Operation')
    if data is not None:
        # Aplicar os filtros
        lay_1x1_away_flt = data[
            (data["FT_Odd_A"] < 1.75) &
            (data["FT_Odd_Ov25"] < 1.65)
        ]
        lay_1x1_away_flt = lay_1x1_away_flt.sort_values(by='Time', ascending=True)

        # Exibir os dados filtrados
        if not lay_1x1_away_flt.empty:
            st.dataframe(lay_1x1_away_flt)
        else:
            st.info("Nenhum jogo encontrado com os critérios especificados.")
    else:
        st.info("Dados indisponíveis para a data selecionada.")
        