import pandas as pd
import numpy as np
import streamlit as st
from PIL import Image
import os
import base64
import requests
from datetime import datetime
from auth import logout
from sidebar_menu import show_role_features

# Streamlit App Title and Headers
st.set_page_config(page_title="Methods - Fluffy Chips Web Analyser", page_icon="🔋", layout="wide")
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.switch_page("Login.py")  # Redireciona para a página de login
# ✅ Show role-based features in the sidebar
show_role_features()
def drop_reset_index(df):
    df = df.dropna()
    df = df.reset_index(drop=True)
    df.index += 1
    return df
st.title("🔋 Methods - Fluffy Chips")
st.subheader('The place where you can Analyse Football Matches!!!')
st.write(f"Welcome, **{st.session_state['username']}**!")
st.write(f"Your role: **{st.session_state['role']}**")
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
@st.cache_data(ttl=0)
def load_data(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return pd.read_csv(url)
        else:
            st.error(f"No Games Available for the Chosen Date: {formatted_date}")
            return None
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

# Function to check head-to-head results
def check_h2h_lay_0x1(home_team, away_team, historical_data):
    h2h_games = historical_data[
        (historical_data['Home'] == home_team) & (historical_data['Away'] == away_team)
    ]
    return int(any((h2h_games['FT_Goals_H'] == 0) & (h2h_games['FT_Goals_A'] == 1)))

# Function to check head-to-head results for Lay 1x1
def check_h2h_lay_1x1(home_team, away_team, historical_data):
    h2h_games = historical_data[
        (historical_data['Home'] == home_team) & (historical_data['Away'] == away_team)
    ]
    return int(any((h2h_games['FT_Goals_H'] == 1) & (h2h_games['FT_Goals_A'] == 1)))

# Function to check head-to-head results
def check_h2h_lay_1x3(home_team, away_team, historical_data):
    h2h_games = historical_data[
        (historical_data['Home'] == home_team) & (historical_data['Away'] == away_team)
    ]
    return int(any((h2h_games['FT_Goals_H'] == 1) & (h2h_games['FT_Goals_A'] == 3)))

# Load Data
with st.spinner("Fetching data..."):
    try:
        data = load_data(csv_file_url)
        if data is not None:
            data_Ov25_FT = data.copy()
            data_btts = data.copy()
            lay_home = data.copy()
            lay_away = data.copy()
            lay_1x3 = data.copy()
        else:
            data_Ov25_FT = None
            data_btts = None
            lay_home = None
            lay_away = None
            lay_1x3 = None
            
    except Exception as e:
        st.error("No Data Available for the Chosen Date")
        data = None
        data_Ov25_FT = None
        data_btts = None
        lay_home = None
        lay_away = None
        lay_1x3 = None

    try:
        historical_data = load_data(historical_data_url)
    except Exception as e:
        st.error("No Historical Data Available for the Chosen Date")
        historical_data = None

    try:
        leagues_data = load_data(leagues_url)
    except Exception as e:
        st.error("No Leagues Data Available for the Chosen Date")
        leagues_data = None

    try:
        elo_tilt_data = load_data(elo_tilt_url)
    except Exception as e:
        st.error("No Elo & Tilt Data Available for the Chosen Date")
        elo_tilt_data = None

# Display Success Messages
if data is not None:
    st.success("Jogos do Dia loaded successfully!")
else:
    st.error("No Data Available for the Chosen Date")

if historical_data is not None:
    st.success("Historical Data loaded successfully!")
else:
    st.error("No Historical Data Available for the Chosen Date")

if leagues_data is not None:
    st.success("Leagues Data loaded successfully!")
else:
    st.error("No Leagues Data Available for the Chosen Date")

if elo_tilt_data is not None:
    st.success("Elo & Tilt Data loaded successfully!")
else:
    st.error("No Elo & Tilt Data Available for the Chosen Date")

# Create Tabs
tabs = ['Lay 0 x 1', 'Lay 1x1', 'Lay 1x3', 'Goleada Home', 'Any Other Win']
tab_views = st.tabs(tabs)

# Exibir dados para cada liga
with tab_views[0]:
    # Função para parsear intervalos
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
    
    # Função para obter referência
    def obter_referencia(cv_mo_ft, ft_odd_h, df_referencias):
        """Determina a referência com base nos intervalos de CV_Match_Odds e FT_Odd_H."""
        try:
            # Garantir que os valores sejam numéricos
            cv_mo_ft = float(cv_mo_ft) if not pd.isna(cv_mo_ft) else None
            ft_odd_h = float(ft_odd_h) if not pd.isna(ft_odd_h) else None
    
            if cv_mo_ft is None or ft_odd_h is None:
                return None  # Se os valores estiverem ausentes, retorna None
    
            # Determinar a linha correta baseada no intervalo de CV_Match_Odds
            linha = None
            for i, intervalo in enumerate(df_referencias.index):
                min_val, max_val = parse_interval(intervalo)
    
                if min_val <= cv_mo_ft <= max_val:
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
        "Old_Europe UEFA Champions League": {
            "prob_filter": ("Probability_Away", "Avg_Bigger"),
            "additional_filters": [
                ("prob_H", ">=", 0.4001),
                ("prob_D", "<=", 0.30)
            ],
            "df_referencias": pd.DataFrame({
                "Intervalo CV": ["<=0.5000", "0.5001 - 0.8000", ">=0.8001"],
                "<=1.2500": ["0", "0", "<1000"],
                "1.2501 - 1.4500": ["0", "<43", "<51"],
                "1.4501 - 1.7000": ["<11", "<18", "0"],
                ">=1.7001": ["<13", "0", "0"]
            }).set_index("Intervalo CV")
        },
        "South America Copa Libertadores": {
            "prob_filter": ("Conceded_Goals", "Bigger_Away"),
            "additional_filters": [
                ("prob_H", ">=", 0.5501),
                ("prob_BTTS_No_FT", ">=", 0.5501)
            ],
            "df_referencias": pd.DataFrame({
                "Intervalo CV": ["<=0.6000", "0.6001 - 0.8000", ">=0.8001"],
                "<=1.1500": ["0", "G-7 <22 - 99,00%", "G-38 < 100 - 99,00%"],
                "1.1501 - 1.3000": ["G-10 <25 - 99,00%", "G-14 <19 - 99,0%", "G-42 <100 - 99,00%"],
                "1.3001 - 1.5000": ["G-12 <24 - 99,00%", "G-43 <14 - 93,02%", "G-3 < 19 - 99,00%"],
                ">=1.5001": ["G-54 <17 - 94,44%", "G-3 <19 - 99,00%", "0"]
            }).set_index("Intervalo CV")
        },
        "Argentina Primera División": {
            "prob_filter": ("Probability_Home", "p_Bigger"),
            "additional_filters": [
                ("prob_Over_25_FT", ">=", 0.3001),
                ("prob_Over_15_FT", ">=", 0.6001)
            ],
            "df_referencias": pd.DataFrame({
                "Intervalo CV": ["<=0.2000", "0.2001 - 0.4000", ">=0.4001"],
                "<=1.7000": ["0", "G-6 <20 - 99,00%", "G-161 <22 - 95,65%"],
                "1.7001 - 1.9500": ["0", "G-140 <15 - 93,57%", "G-81 <40 - 97,53%"],
                "1.9501 - 2.2500": ["G-36 <11 - 91,67%", "G-138 <12 - 92,75%", "0"],
                ">=2.2501": ["G-185 <13 - 92,43%", "G-4 <14 - 99,00%", "0"]
            }).set_index("Intervalo CV")
        },
        "Old_Australia A-League": {
            "prob_filter": ("Goal_Difference", "Bigger_Home"),
            "additional_filters": [
                ("Poisson_GS_A_1", ">=", 0.1501),
                ("Poisson_GM_H_1", ">=", 0.2001),
                ("prob_A", "<=", 0.45)
                ],
            "df_referencias": pd.DataFrame({
                "Intervalo CV": ["<=0.2000", "0.2001 - 0.4000", ">=0.4001"],
                "<=1.6500": ["0", "0", "<37"],
                "1.6501 - 1.9500": ["0", "<28", "<12"],
                "1.9501 - 2.3000": ["<39", "<29", "0"],
                ">=2.3001": ["<13", "<31", "0"]
                }).set_index("Intervalo CV")
        },
        "Brazil Serie A": {
            "prob_filter": ("Probability_Away", "Avg_Bigger"),
            "additional_filters": [
                ("Poisson_GS_H_2", ">=", 0.0501),
                ("Poisson_GS_H_2", "<=", 0.2500),
                ("prob_H", ">=", 0.4501)
                ],
            "df_referencias": pd.DataFrame({
                "Intervalo CV": ["<=0.4000", "0.4001 - 0.6000", ">=0.6001"],
                "<=1.5000": ["0", "G-6 <6 - 83,33%", "G-199 <66 - 98,49%"],
                "1.5001 - 1.6500": ["0", "G-150 <21 - 95,33%", "G-23 <11 - 91,30%"],
                "1.6501 - 1.9000": ["G-62 <17 - 95,16%", "G-132 <21 - 95,45%", "0"],
                ">=1.9001": ["G-189 <12 - 92,06%", "0", "0"]
                }).set_index("Intervalo CV")
        },
        "Brazil Serie B": {
            "prob_filter": ("Probability_Away", "Avg_Bigger"),
            "additional_filters": [
                ("prob_A", "<=", 0.3000),
                ("prob_H", ">=", 0.5001)
                ],
            "df_referencias": pd.DataFrame({
                "Intervalo CV": ["<=0.4000", "0.4001 - 0.5500", ">=0.5501"],
                "<=1.5000": ["0", "G-1 <15 - 99,00%", "G-140 <46 - 97,86%"],
                "1.5001 - 1.6500": ["0", "G-122 <15 - 93,44%", "G-40 <19 - 95,00%"],
                "1.6501 - 1.8000": ["G-40 <15 - 95,00%", "G-121 <11 - 91,74%", "G-40 <19 - 95,00%"],
                ">=1.8001": ["G-156 <17 - 94,23%", "G-13 <16 - 99,00%", "0"]
                }).set_index("Intervalo CV")
        },
        "Brazil Serie C": {
            "prob_filter": ("Probability_Away", "Avg_Bigger"),
            "additional_filters": [
                ("prob_Under_25_FT", ">=", 0.5501),
                ("Poisson_GM_H_1", ">=", 0.3001)
                ],
            "df_referencias": pd.DataFrame({
                "Intervalo CV": ["<=0.2000", "0.2001 - 0.3500", ">=0.3501"],
                "<=1.7000": ["0", "0", "G-86 <42 - 97,67%"],
                "1.7001 - 1.9000": ["0", "G-36 <17 - 94,44%", "G-60 <11 - 91,67%"],
                "1.9001 - 2.1000": ["G-7 <18 - 99,00%", "G-105 <17 - 94,29%", "0"],
                ">=2.1001": ["G-109 <17 - 94,50%", "G-6 <5 - 83,33%", "0"]
                }).set_index("Intervalo CV")
        },
        "Belarus Vysheyshaya Liga": {
            "prob_filter": ("Conceded_Goals", "Bigger_Away"),
            "additional_filters": [
                ("prob_Over_15_FT", ">=", 0.7501),
                ("Poisson_GS_H_3", "<=", 0.1500)
                ],
            "df_referencias": pd.DataFrame({
                "Intervalo CV": ["<=0.3000", "0.3001 - 0.6000", ">=0.6001"],
                "<=1.4000": ["0", "0", "G-114 <28 - 96,49%"],
                "1.4001 - 1.7000": ["0", "G-72 <71 - 98,61%", "G-26 <12 - 92,31%"],
                "1.7001 - 2.2500": ["G-58 <28 - 96,55%", "G-40 <6 - 85,00%", "0"],
                ">=2.2501": ["G-81 <11 - 91,36%", "G-27 <13 - 92,59%", "G-6 <24 - 99,00%"]
                }).set_index("Intervalo CV")
        },
        "China Chinese Super League": {
            "prob_filter": ("Probability_Away", "Avg_Bigger"),
            "additional_filters": [
                ("prob_H", ">=", 0.4001),
                ("prob_A", "<=", 0.40),
                ],
            "df_referencias": pd.DataFrame({
                "Intervalo CV": ["<=0.4500", "0.4501 - 0.8000", ">=0.8001"],
                "<=1.2500": ["0", "G-4 <27 - 99,00%", "G-104 <104 - 99,04%"],
                "1.2501 - 1.4500": ["0", "G-83 <27 - 99,00%", "G-27 <100 - 99,00%"],
                "1.4501 - 1.8500": ["G-42 <13 - 92,86%", "G-76 <12 - 92,11%", "0"],
                ">=1.8501": ["G-118 <14 - 93,22%", "G-1 <19 - 99,00%", "0"]
                }).set_index("Intervalo CV")
        },
        "Old_COSTA RICA - PRIMERA DIVISION": {
            "prob_filter": ("Conceded_Goals", "Bigger_Away"),
            "additional_filters": [
                ("prob_Under_25_FT", ">=", 0.5001),
                ("prob_H", ">=", 0.4001)
                ],
            "df_referencias": pd.DataFrame({
                "Intervalo CV": ["<=0.3000", "0.3001 - 0.5500", ">=0.5501"],
                "<=1.4500": ["0", "0", "<38"],
                "1.4501 - 1.7000": ["0", "<23", "<35"],
                "1.7001 - 2.0000": ["<19", "<31", "0"],
                ">=2.0001": ["<17", "0", "0"]
                }).set_index("Intervalo CV")
        },
        "Old_Egypt Egyptian Premier League": {
            "prob_filter": ("Probability_Away", "Avg_Bigger"),
            "additional_filters": [
                ("prob_Over_25_FT", ">=", 0.4001),
                ("prob_BTTS_No_FT", ">=", 0.5001)
                ],
            "df_referencias": pd.DataFrame({
                "Intervalo CV": ["<=0.3000", "0.3001 - 0.6000", ">=0.6001"],
                "<=1.4500": ["0", "0", "<160"],
                "1.4501 - 1.8000": ["0", "<33", "<36"],
                "1.8001 - 2.3000": ["<26", "<9", "0"],
                ">=2.3001": ["<22", "<17", "<5"]
                }).set_index("Intervalo CV")
        },
        "Old_England Premier League": {
            "prob_filter": ("Probability_Home", "p_Bigger"),
            "additional_filters": [
                ("Poisson_GM_H_1", "<=", 0.40),
                ("prob_D", "<=", 0.40)
                ],
            "df_referencias": pd.DataFrame({
                "Intervalo CV": ["<=0.4500", "0.4501 - 0.6500", ">=0.6501"],
                "<=1.3400": ["0", "0", "<33"],
                "1.3401 - 1.6000": ["0", "<27", "<25"],
                "1.6001 - 1.9800": ["<31", "<20", "0"],
                ">=1.9801": ["<27", "<26", "0"]
                }).set_index("Intervalo CV")
        },
        "Old_England Championship": {
            "prob_filter": ("Probability_Home", "p_Bigger"),
            "additional_filters": [
                ("Poisson_GM_H_1", "<=", 0.40),
                ("prob_D", "<=", 0.30)
                ],
            "df_referencias": pd.DataFrame({
                "Intervalo CV": ["<=0.3500", "0.3501 - 0.5500", ">=0.5501"],
                "<=1.5500": ["0", "0", "<29"],
                "1.5501 - 1.7500": ["0", "<25", "<38"],
                "1.7501 - 2.0000": ["<8", "<22", "0"],
                ">=2.0001": ["<19", "0", "0"]
                }).set_index("Intervalo CV")
        },
        "Finland Veikkausliiga": {
            "prob_filter": ("Conceded_Goals", "Bigger_Away"),
            "additional_filters": [
                ("prob_Under_25_FT", "<=", 0.6000),
                ("Poisson_GS_H_1", ">=", 0.3001)
                ],
            "df_referencias": pd.DataFrame({
                "Intervalo CV": ["<=0.2500", "0.2501 - 0.5000", ">=0.5001"],
                "<=1.5500": ["0", "0", "G-98 <15 - 93,88%"],
                "1.5501 - 1.8500": ["0", "G-81 <80 - 98,77%", "G-19 <18 - 94,74%"],
                "1.8501 - 2.3000": ["G-53 <12 - 93,45%", "G-43 <25 - 99,00%", "0"],
                ">=2.3001": ["G-73 <17 - 94,52%", "G-15 <4 - 80,00%", "G-6 <17 - 99,00%"]
                }).set_index("Intervalo CV")
        },
        "Old_France Ligue 1": {
            "prob_filter": ("Probability_Away", "Avg_Bigger"),
            "additional_filters": [
                ("prob_Over_25_FT", ">=", 0.4501),
                ("prob_H", ">=", 0.3501)
                ],
            "df_referencias": pd.DataFrame({
                "Intervalo CV": ["<=0.4000", "0.4001 - 0.6500", ">=0.6501"],
                "<=1.4000": ["0", "0", "<51"],
                "1.4001 - 1.6000": ["0", "<24", "<16"],
                "1.6001 - 2.0000": ["<17", "<18", "0"],
                ">=2.0001": ["<18", "<19", "<31"]
                }).set_index("Intervalo CV")
        },
        "Old_France Ligue 2": {
            "prob_filter": ("Probability_Home", "p_Bigger"),
            "additional_filters": [
                ("Poisson_GS_A_1", ">=", 0.3001),
                ("prob_H", ">=", 0.4001)
                ],
            "df_referencias": pd.DataFrame({
                "Intervalo CV": ["<=0.2500", "0.2501 - 0.4500", ">=0.4501"],
                "<=1.6500": ["0", "0", "<20"],
                "1.6501 - 1.8500": ["0", "<28", "<16"],
                "1.8501 - 2.0500": ["<8", "<11", "0"],
                ">=2.0501": ["<17", "<17", "0"]
                }).set_index("Intervalo CV")
        },
        "Old_Germany Bundesliga": {
            "prob_filter": ("Probability_Away", "Avg_Bigger"),
            "additional_filters": [
                ("Poisson_GS_A_2", ">=", 0.1501),
                ("prob_H", ">=", 0.5501),
                ("prob_H", "<=", 0.95)
                ],
            "df_referencias": pd.DataFrame({
                "Intervalo CV": ["<=0.5000", "0.5001 - 0.7500", ">=0.7501"],
                "<=1.3000": ["0", "0", "< 50"],
                "1.3001 - 1.5000": ["0", "< 18", "< 50"],
                "1.5001 - 1.7900": ["< 100", "< 96", "0"],
                ">=1.7901": ["< 30", "0", "0"]
                }).set_index("Intervalo CV")
        },
        "Old_Germany 2. Bundesliga": {
            "prob_filter": ("Probability_Away", "Avg_Bigger"),
            "additional_filters": [
                ("prob_D", "<=", 0.3000),
                ("Avg_CG_Conceded_H_02", ">=", 0.2001),
                ("Avg_CG_Conceded_H_02", "<=", 1.0000)
                ],
            "df_referencias": pd.DataFrame({
                "Intervalo CV": ["<=0.2500", "0.2501 - 0.4500", ">=0.4501"],
                "<=1.6500": ["0", "<38", "<48"],
                "1.6501 - 1.9000": ["0", "<24", "<17"],
                "1.9001 - 2.2500": ["<96", "<30", "0"],
                ">=2.2501": ["<33", "<42", "<39"]
                }).set_index("Intervalo CV")
        },
        "Old_Greece Super League": {
            "prob_filter": ("Goal_Difference", "Bigger_Home"),
            "additional_filters": [
                ("Avg_CG_Conceded_A_02", ">=", 0.6001),
                ("prob_H", ">=", 0.4001)
                ],
            "df_referencias": pd.DataFrame({
                "Intervalo CV": ["<=0.4000", "0.4001 - 0.8000", ">=0.8001"],
                "<=1.2000": ["0", "0", "<109"],
                "1.2001 - 1.4500": ["0", "<14", "<90"],
                "1.4501 - 1.9000": ["<11", "<13", "0"],
                ">=1.9001": ["<28", "0", "0"]
                }).set_index("Intervalo CV")
        },
        "Old_INDIA - ISL": {
            "prob_filter": ("Probability_Home", "p_Bigger"),
            "additional_filters": [
                ("Poisson_GS_A_2", ">=", 0.2501)
                ],
            "df_referencias": pd.DataFrame({
                "Intervalo CV": ["<=0.3000", "0.3001 - 0.5000", ">=0.5001"],
                "<=1.5000": ["0", "0", "<21"],
                "1.5001 - 1.7000": ["0", "<30", "<36"],
                "1.7001 - 2.0000": ["<14", "<40", "0"],
                ">=2.0001": ["<49", "0", "0"]
                }).set_index("Intervalo CV")
        },
        "Old_Indonesia Liga 1": {
            "prob_filter": ("Probability_Away", "Avg_Bigger"),
            "additional_filters": [
                ("prob_BTTS_Yes_FT", ">=", 0.5001),
                ("prob_BTTS_Yes_FT", "<=", 0.6500),
                ("prob_H", ">=", 0.4001),
                ("prob_H", "<=", 0.8000)
                ],
            "df_referencias": pd.DataFrame({
                "Intervalo CV": ["<=0.3000", "0.3001 - 0.5500", ">=0.5501"],
                "<=1.4500": ["0", "0", "<37"],
                "1.4501 - 1.6500": ["0", "<31", "<51"],
                "1.6501 - 1.9500": ["<19", "<27", "0"],
                ">=1.9501": ["<13", "0", "0"]
                }).set_index("Intervalo CV")
        },
        "Old_Israel Israeli Premier League": {
            "prob_filter": ("Probability_Away", "Avg_Bigger"),
            "additional_filters": [
                ("prob_Under_25_FT", "<=", 0.6000),
                ("prob_Over_25_FT", ">=", 0.4501)
                ],
            "df_referencias": pd.DataFrame({
                "Intervalo CV": ["<=0.4000", "0.4001 - 0.7000", ">=0.7001"],
                "<=1.3500": ["0", "0", "<58"],
                "1.3501 - 1.6000": ["0", "<45", "<52"],
                "1.6001 - 2.0000": ["<20", "<52", "0"],
                ">=2.0001": ["<15", "<48", "0"]
                }).set_index("Intervalo CV")
        },
        "Old_Italy Serie A": {
            "prob_filter": ("Probability_Away", "Avg_Bigger"),
            "additional_filters": [
                ("Poisson_GS_A_3", ">=", 0.1001),
                ("prob_H", ">=", 0.3501)
                ],
            "df_referencias": pd.DataFrame({
                "Intervalo CV": ["<=0.5000", "0.5001 - 0.7500", ">=0.7501"],
                "<=1.3200": ["0", "<40", "<27"],
                "1.3201 - 1.5000": ["0", "<33", "<35"],
                "1.5001 - 1.7500": ["<51", "<62", "0"],
                ">=1.7501": ["<14", "0", "0"]
                }).set_index("Intervalo CV")
        },
        "Old_Italy Serie B": {
            "prob_filter": ("Goal_Difference", "Bigger_Home"),
            "additional_filters": [
                ("Poisson_GM_H_3", ">=", 0.1501),
                ("prob_A", ">=", 0.1001),
                ("prob_A", "<=", 0.3500)
                ],
            "df_referencias": pd.DataFrame({
                "Intervalo CV": ["<=0.2000", "0.2001 - 0.4000", ">=0.4001"],
                "<=1.7500": ["0", "<21", "<22"],
                "1.7501 - 2.0000": ["0", "<20", "<20"],
                "2.0001 - 2.2500": ["<18", "<19", "0"],
                ">=2.2501": ["<15", "0", "0"]
                }).set_index("Intervalo CV")
        },
        "Japan J1 League": {
            "prob_filter": ("Probability_Away", "Avg_Bigger"),
            "additional_filters": [
                ("Poisson_GS_A_1", ">=", 0.1501),
                ("Poisson_GS_A_1", "<=", 0.3500)
                ],
            "df_referencias": pd.DataFrame({
                "Intervalo CV": ["<=0.2500", "0.2501 - 0.4500", ">=0.4501"],
                "<=1.6000": ["0", "0", "G-107 <26 - 96,26%"],
                "1.6001 - 1.8000": ["0", "G-48 <9 - 89,58%", "G-63 <62 - 98,41%"],
                "1.8001 - 2.1000": ["G-12 <11 - 91,67%", "G-104 <17 - 94,23%", "G-2 <16 - 99,00%"],
                ">=2.1001": ["G-152 <21 - 95,39%", "G-17 <16 - 94,12%", "G-2 <20 - 99,00%"]
                }).set_index("Intervalo CV")
        },
        "Old_MEXICO - LIGA MX": {
            "prob_filter": ("Conceded_Goals", "Bigger_Away"),
            "additional_filters": [
                ("Poisson_GM_H_0", "<=", 0.3500),
                ("prob_H", ">=", 0.4501)
                ],
            "df_referencias": pd.DataFrame({
                "Intervalo CV": ["<=0.3500", "0.3501 - 0.5500", ">=0.5501"],
                "<=1.5000": ["0", "0", "<36"],
                "1.5001 - 1.7000": ["0", "<24", "<50"],
                "1.7001 - 1.9500": ["<27", "<33", "0"],
                ">=1.9501": ["<16", "0", "0"]
                }).set_index("Intervalo CV")
        },
        "Old_Netherlands Eredivisie": {
            "prob_filter": ("Probability_Away", "Avg_Bigger"),
            "additional_filters": [
                ("prob_Under_25_FT", "<=", 0.5000),
                ("prob_H", ">=", 0.4001)
                ],
            "df_referencias": pd.DataFrame({
                "Intervalo CV": ["<=0.5500", "0.5501 - 0.8500", ">=0.8501"],
                "<=1.2000": ["0", "0", "<160"],
                "1.2001 - 1.3800": ["0", "<95", "<32"],
                "1.3801 - 1.6500": ["<20", "<62", "0"],
                ">=1.6501": ["<79", "0", "0"]
                }).set_index("Intervalo CV")
        },
        "Norway Eliteserien": {
            "prob_filter": ("Conceded_Goals", "Bigger_Away"),
            "additional_filters": [
                ("prob_Under_25_FT", "<=", 0.5000),
                ("prob_H", ">=", 0.4001)
                ],
            "df_referencias": pd.DataFrame({
                "Intervalo CV": ["<=0.3500", "0.3501 - 0.6000", ">=0.6001"],
                "<=1.3500": ["0", "0", "G-129 <42 - 97,67%"],
                "1.3501 - 1.6000": ["0", "G-78 <38 - 97,44%", "G-26 <60 - 99,00%"],
                "1.6001 - 1.9500": ["G-41 <40 - 97,56%", "G-88 <21 - 95,45%", "0"],
                ">=1.9501": ["G_133 <13 - 92,48%", "0", "0"]
                }).set_index("Intervalo CV")
        },
        "Old_Portugal Liga NOS": {
            "prob_filter": ("Probability_Away", "Avg_Bigger"),
            "additional_filters": [
                ("Poisson_GM_A_3", "<=", 0.1000),
                ("prob_H", ">=", 0.4501)
                ],
            "df_referencias": pd.DataFrame({
                "Intervalo CV": ["<=0.5500", "0.5501 - 0.9000", ">=0.9001"],
                "<=1.1800": ["0", "0", "< 50"],
                "1.1801 - 1.3600": ["0", "< 18", "< 50"],
                "1.3601 - 1.6500": ["< 100", "< 96", "0"],
                ">=1.6501": ["< 30", "0", "0"]
                }).set_index("Intervalo CV")
        },
        "Old_Portugal LigaPro": {
            "prob_filter": ("Conceded_Goals", "Bigger_Away"),
            "additional_filters": [
                ("Poisson_GM_A_2", ">=", 0.0501),
                ("Poisson_GM_A_2", "<=", 0.2500),
                ("Poisson_GS_A_2", ">=", 0.2001),
                ("prob_H", ">=", 0.3501)
                ],
            "df_referencias": pd.DataFrame({
                "Intervalo CV": ["<=0.2000", "0.2001 - 0.4000", ">=0.4001"],
                "<=1.6500": ["0", "0", "<58"],
                "1.6501 - 1.9500": ["0", "<31", "<8"],
                "1.9501 - 2.2000": ["<14", "<16", "0"],
                ">=2.2001": ["<22", "0", "0"]
                }).set_index("Intervalo CV")
        },
        "Old_Qatar Stars League": {
            "prob_filter": ("Probability_Away", "Avg_Bigger"),
            "additional_filters": [
                ("Poisson_GM_H_1", ">=", 0.1001),
                ("prob_D", "<=", 0.3000)
                ],
            "df_referencias": pd.DataFrame({
                "Intervalo CV": ["<=0.4000", "0.4001 - 0.6000", ">=0.6001"],
                "<=1.4000": ["0", "0", "<66"],
                "1.4001 - 1.6500": ["0", "<51", "<15"],
                "1.6501 - 2.0000": ["<44", "<69", "0"],
                ">=2.0001": ["<17", "<50", "<9"]
                }).set_index("Intervalo CV")
        },
        "Old_Romania Liga I": {
            "prob_filter": ("Probability_Home", "p_Bigger"),
            "additional_filters": [
                ("prob_Over_25_FT", ">=", 0.4001),
                ("prob_H", ">=", 0.4501)
                ],
            "df_referencias": pd.DataFrame({
                "Intervalo CV": ["<=0.4000", "0.4001 - 0.6000", ">=0.6001"],
                "<=1.4000": ["0", "0", "<33"],
                "1.4001 - 1.6000": ["0", "<7", "<25"],
                "1.6001 - 1.8000": ["<23", "<19", "0"],
                ">=1.8001": ["<21", "0", "0"]
                }).set_index("Intervalo CV")
        },
        "Sweden Allsvenskan": {
            "prob_filter": ("Probability_Home", "p_Bigger"),
            "additional_filters": [
                ("prob_Over_25_FT", ">=", 0.5001),
                ("prob_A", "<=", 0.4000)
                ],
            "df_referencias": pd.DataFrame({
                "Intervalo CV": ["<=0.3500", "0.3501 - 0.6000", ">=0.6001"],
                "<=1.4000": ["0", "0", "G-116 <37 - 97,41%"],
                "1.4001 - 1.6500": ["0", "G-75 <36 - 97,33%", "G-44 <13 - 93,18%"],
                "1.6501 - 1.9500": ["G-34 <16 - 94,12%", "G-84 <20 - 95,24%", "0"],
                ">=1.9501": ["G-114 <18 - 94,74%", "0", "0"]
                }).set_index("Intervalo CV")
        },
        "Sweden Superettan": {
            "prob_filter": ("Probability_Home", "Avg_Bigger"),
            "additional_filters": [
                ("Avg_CG_Conceded_A_02", ">=", 0.5501),
                ("Avg_CG_Conceded_A_02", "<=", 1.1500),
                ("Poisson_GS_H_1", ">=", 0.2001)
                ],
            "df_referencias": pd.DataFrame({
                "Intervalo CV": ["<=0.1500", "0.1501 - 0.2500", ">=0.2501"],
                "<=2.2500": ["G-1 <18 - 99,00%", "G-73 <17 - 94,52%", "G-44 <21 - 95,45%"],
                "2.2501 - 2.5500": ["G-80 <12 - 92,50%", "G-26 <25 - 96,15%", "0"],
                "2.5501 - 3.0000": ["G-73 <35 - 97,26%", "G-44 <7 - 88,64%", "0"],
                ">=3.0001": ["0", "g-38 <17 - 99,00%", "G-75 <36 - 97,33%"]
                }).set_index("Intervalo CV")
        },
        "South Korea K League 1": {
            "prob_filter": ("Conceded_Goals", "Bigger_Away"),
            "additional_filters": [
                ("Poisson_GS_A_3", ">=", 0.1001),
                ("prob_H", ">=", 0.4001)
                ],
            "df_referencias": pd.DataFrame({
                "Intervalo CV": ["<=0.2000", "0.2001 - 0.3500", ">=0.3501"],
                "<=1.8000": ["0", "G-1 <15 - 99,00%", "G-103 <20 - 95,15%"],
                "1.8001 - 2.0000": ["0", "G-67 <16 - 94,03%", "G-21 <20 - 95,24%"],
                "2.0001 - 2.2000": ["G-26 <12 - 92,31%", "G-78 <7 - 88,46%", "0"],
                ">=2.2001": ["G-99 <19 - 94,95%", "G-1 <15 - 99,00%", "0"]
                }).set_index("Intervalo CV")
        },
        "Old_Spain La Liga": {
            "prob_filter": ("Probability_Home", "p_Bigger"),
            "additional_filters": [
                ("Poisson_GM_A_2", "<=", 0.2500),
                ("Poisson_GS_A_0", "<=", 0.3500),
                ("prob_H", ">=", 0.4001)
                ],
            "df_referencias": pd.DataFrame({
                "Intervalo CV": ["<=0.3500", "0.3501 - 0.6000", ">=0.6001"],
                "<=1.4300": ["0", "0", "<36"],
                "1.4301 - 1.7000": ["0", "<33", "<13"],
                "1.7001 - 1.9500": ["<43", "<19", "0"],
                ">=1.9501": ["<17", "0", "0"]
                }).set_index("Intervalo CV")
        },
        "Old_Spain Segunda División": {
            "prob_filter": ("Probability_Home", "p_Bigger"),
            "additional_filters": [
                ("Avg_CG_Scored_H_02", ">=", 0.7501),
                ("Avg_CG_Scored_H_02", "<=", 1.2000)
                ],
            "df_referencias": pd.DataFrame({
                "Intervalo CV": ["<=0.3000", "0.3001 - 0.4500", ">=0.4501"],
                "<=1.6600": ["0", "0", "<21"],
                "1.6601 - 1.8000": ["0", "<11", "<12"],
                "1.8001 - 2.0000": ["<10", "<21", "0"],
                ">=2.0001": ["<19", "0", "0"]
                }).set_index("Intervalo CV")
        },
        "Old_Thailand Thai League T1": {
            "prob_filter": ("Probability_Home", "p_Bigger"),
            "additional_filters": [
                ("Avg_CG_Scored_A_02", ">=", 0.3001),
                ("Avg_CG_Scored_A_02", "<=", 0.9500),
                ("Avg_CG_Conceded_A_02", ">=", 0.5001),
                ("Avg_CG_Conceded_A_02", "<=", 1.6000)
                ],
            "df_referencias": pd.DataFrame({
                "Intervalo CV": ["<=0.2500", "0.2501 - 0.5000", ">=0.5001"],
                "<=1.4000": ["0", "0", "<69"],
                "1.4001 - 1.6500": ["0", "<41", "<41"],
                "1.6501 - 2.0000": ["<14", "<15", "0"],
                ">=2.0001": ["<80", "0", "0"]
                }).set_index("Intervalo CV")
        },
        "Old_Turkey Süper Lig": {
            "prob_filter": ("Goal_Difference", "Bigger_Home"),
            "additional_filters": [
                ("Poisson_GM_A_2", ">=", 0.1001),
                ("Poisson_GM_A_2", "<=", 0.2500),
                ("Avg_CG_Scored_H_02", ">=", 0.4501),
                ("Avg_CG_Scored_H_02", "<=", 1.0500),
                ("prob_BTTS_No_FT", "<=", 0.6000)
                ],
            "df_referencias": pd.DataFrame({
                "Intervalo CV": ["<=0.2500", "0.2501 - 0.5500", ">=0.5501"],
                "<=1.5500": ["0", "0", "<51"],
                "1.5501 - 1.9500": ["0", "<24", "<16"],
                "1.9501 - 2.3500": ["<17", "<18", "0"],
                ">=2.3501": ["<18", "<19", "<31"]
                }).set_index("Intervalo CV")
        },
        "Old_Turkey 1. Lig": {
            "prob_filter": ("Probability_Home", "p_Bigger"),
            "additional_filters": [
                ("Poisson_GM_H_2", ">=", 0.1501),
                ("FT_Odd_A", ">=", 2.20)
                ],
            "df_referencias": pd.DataFrame({
                "Intervalo CV": ["<=0.3500", "0.3501 - 0.6000", ">=0.6001"],
                "<=1.4000": ["0", "0", "<28"],
                "1.4001 - 1.6500": ["0", "<21", "<29"],
                "1.6501 - 1.9000": ["<21", "<11", "0"],
                ">=1.9001": ["<12", "0", "0"]
                }).set_index("Intervalo CV")
        },
        "USA MLS": {
            "prob_filter": ("Goal_Difference", "Bigger_Home"),
            "additional_filters": [
                ("prob_A", "<=", 0.3000),
                ("Poisson_GS_A_1", "<=", 0.3500)
                ],
            "df_referencias": pd.DataFrame({
                "Intervalo CV": ["<=0.3500", "0.3501 - 0.5000", ">=0.5001"],
                "<=1.6000": ["0", "G-3 <25 - 99,00%", "G-237 <26 - 96,20%"],
                "1.6001 - 1.7500": ["0", "G-195 <19 - 94,87%", "G-73 <12 - 91,78%"],
                "1.7501 - 1.9000": ["G-49 <24 - 95,92%", "G-180 <35 - 97,22%", "0"],
                ">=1.9001": ["G-222 <18 - 94,59%", "G-3 <24 - 99,00%", "0"]
                }).set_index("Intervalo CV")
        }
    }
    st.subheader("Today's Games for Lay 0X1 - Fluffy Method")

    if data is not None:
        all_games = []  # Lista para armazenar todos os jogos filtrados
    
        for league, config in leagues_config.items():
            prob_filter_col, prob_filter_val = config["prob_filter"]
            df_referencias = config["df_referencias"]
    
            # Aplicar filtros
            filtered_data = data[data["League"] == league]
            filtered_data = filtered_data[filtered_data[prob_filter_col] == prob_filter_val]
    
            # Aplicar filtro adicional para '0x1_H' e '0x1_A'
            filtered_data = filtered_data[(filtered_data['Perc_0x1_H'] < 10) & (filtered_data['Perc_0x1_A'] < 10)]
    
            for col, op, val in config["additional_filters"]:
                if op == ">=":
                    filtered_data = filtered_data[filtered_data[col] >= val]
                elif op == "<=":
                    filtered_data = filtered_data[filtered_data[col] <= val]
    
            # Aplicar a função para calcular 'Odd_Justa_Lay_0x1'
            filtered_data["Odd_Justa_Lay_0x1"] = filtered_data.apply(
                lambda row: obter_referencia(row["CV_MO_FT"], row["FT_Odd_H"], df_referencias),
                axis=1
            )
    
            # Aplicar a função para calcular 'h2h_lay_0x1'
            filtered_data["h2h_lay_0x1"] = filtered_data.apply(
                lambda row: check_h2h_lay_0x1(row["Home"], row["Away"], historical_data),
                axis=1
            )
    
            # Adicionar os jogos filtrados à lista
            all_games.append(filtered_data)
    
        # Concatenar todos os DataFrames da lista em um único DataFrame
        if all_games:
            final_df = pd.concat(all_games, ignore_index=True)
            final_df = final_df.sort_values(by='Time', ascending=True)  # Ordenar por 'Time'
            final_df = drop_reset_index(final_df)
        
            # Adicionar a coluna com a soma de 'h2h_lay_0x1' para cada grupo de 'Home' e 'Away'
            final_df["Total_H2H_0x1_FT"] = final_df.groupby(['Home', 'Away'])['h2h_lay_0x1'].transform('sum')
        
            # List of columns to display
            columns_to_display = [
                'Time', 'League', 'Home', 'Away', 'Round', 'Odd_Justa_Lay_0x1', 'Total_H2H_0x1_FT', 'FT_Odd_H', 'FT_Odd_D', 'FT_Odd_A', 'CV_Match_Type', 
                'Perc_0x1_H', 'Perc_0x1_A', 'Perc_Over15FT_Home', 'Perc_Over15FT_Away', 'Perc_Over25FT_Home', 'Perc_Over25FT_Away', 'Perc_BTTS_Yes_Home', 'Perc_BTTS_Yes_Away', 'h2h_lay_0x1'
            ]
        
            # Ensure all columns exist in final_df
            columns_to_display = [col for col in columns_to_display if col in final_df.columns]
        
            # Exibir o DataFrame final
            if not final_df.empty:
                st.dataframe(final_df[columns_to_display], use_container_width=True, hide_index=True)
            else:
                st.warning("No games found with the specified criteria.")
    else:
        st.error("No Data Available for the Chosen Date")
        
with tab_views[1]:
    st.subheader('Todays Games for Lay 1x1 Based on Home Team')
    st.markdown('Keep The Operation until Green or close at 60 min. At Half Time if you have Profit Close the Operation')
    
    if data is not None:
        # Check if the required columns exist in the DataFrame
        required_columns = ["League", "Time", "Round", "Home", "Away", "FT_Odd_H", "FT_Odd_D", "FT_Odd_A", "CV_Match_Type", "Perc_Over25FT_Home", "Perc_Over25FT_Away"]
        
        # Apply filters for Lay 1x1 based on Home Team
        lay_1x1_home_flt0 = data[
            (data["FT_Odd_H"] < 1.80) &  # Home team odds less than 1.75
            (data["FT_Odd_Over25"] < 1.70)  # Over 2.5 goals odds less than 1.65
        ]
        lay_1x1_home_flt = lay_1x1_home_flt0.sort_values(by='Time', ascending=True)
        
        # Apply function to calculate 'h2h_lay_1x1'
        lay_1x1_home_flt["h2h_lay_1x1"] = lay_1x1_home_flt.apply(
            lambda row: check_h2h_lay_1x1(row["Home"], row["Away"], historical_data),
            axis=1
        )
        
        # Group by 'Home' and 'Away' and calculate the sum of 'h2h_lay_1x1' for each group
        lay_1x1_home_flt["sum_h2h_lay_1x1"] = lay_1x1_home_flt.groupby(['Home', 'Away'])['h2h_lay_1x1'].transform('sum')
        
        # Filter the final result where sum_h2h_lay_1x1 < 3
        lay_1x1_home_flt = lay_1x1_home_flt[lay_1x1_home_flt["sum_h2h_lay_1x1"] < 3]
        
        # Select only the desired columns
        lay_1x1_home_flt = lay_1x1_home_flt[required_columns + ["sum_h2h_lay_1x1"]]
        
        # Display the filtered data without the index
        if not lay_1x1_home_flt.empty:
            st.dataframe(lay_1x1_home_flt, use_container_width=True, hide_index=True)
        else:
            st.warning("No games found with the specified criteria.")
            
    st.subheader('Todays Games for Lay 1x1 Based on Away Team')
    st.markdown('Keep The Operation until Green or close at 60 min. At Half Time if you have Profit Close the Operation')
    
    if data is not None:
        # Check if the required columns exist in the DataFrame
        required_columns = ["League", "Time", "Home", "Away", "FT_Odd_H", "FT_Odd_D", "FT_Odd_A", "CV_Match_Type", "Perc_Over25FT_Home", "Perc_Over25FT_Away"]
        
        # Apply filters for Lay 1x1 based on Away Team
        lay_1x1_away_flt0 = data[
            (data["FT_Odd_A"] < 1.80) &  # Away team odds less than 1.75
            (data["FT_Odd_Over25"] < 1.70)  # Over 2.5 goals odds less than 1.65
        ]
        lay_1x1_away_flt = lay_1x1_away_flt0.sort_values(by='Time', ascending=True)
        
        # Apply function to calculate 'h2h_lay_1x1'
        lay_1x1_away_flt["h2h_lay_1x1"] = lay_1x1_away_flt.apply(
            lambda row: check_h2h_lay_1x1(row["Home"], row["Away"], historical_data),
            axis=1
        )
        
        # Group by 'Home' and 'Away' and calculate the sum of 'h2h_lay_1x1' for each group
        lay_1x1_away_flt["sum_h2h_lay_1x1"] = lay_1x1_away_flt.groupby(['Home', 'Away'])['h2h_lay_1x1'].transform('sum')
        
        # Filter the final result where sum_h2h_lay_1x1 < 3
        lay_1x1_away_flt = lay_1x1_away_flt[lay_1x1_away_flt["sum_h2h_lay_1x1"] < 3]
        
        # Select only the desired columns
        lay_1x1_away_flt = lay_1x1_away_flt[required_columns + ["sum_h2h_lay_1x1"]]
        
        # Display the filtered data without the index
        if not lay_1x1_away_flt.empty:
            st.dataframe(lay_1x1_away_flt, use_container_width=True, hide_index=True)
        else:
            st.warning("No games found with the specified criteria.")
    else:
        st.error("No Data Available for the Chosen Date")

with tab_views[2]:
    # Função para parsear intervalos
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
    
    # Função para obter referência
    def obter_referencia(cv_mo_ft, ft_odd_h, df_referencias):
        """Determina a referência com base nos intervalos de CV_Match_Odds e FT_Odd_H."""
        try:
            # Garantir que os valores sejam numéricos
            cv_mo_ft = float(cv_mo_ft) if not pd.isna(cv_mo_ft) else None
            ft_odd_h = float(ft_odd_h) if not pd.isna(ft_odd_h) else None
    
            if cv_mo_ft is None or ft_odd_h is None:
                return None  # Se os valores estiverem ausentes, retorna None
    
            # Determinar a linha correta baseada no intervalo de CV_Match_Odds
            linha = None
            for i, intervalo in enumerate(df_referencias.index):
                min_val, max_val = parse_interval(intervalo)
    
                if min_val <= cv_mo_ft <= max_val:
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
        "PORTUGAL - LIGA PORTUGAL": {
            "prob_filter": ("Probability_Home", "p_Bigger"),
            "additional_filters": [
                ("prob_H", ">=", 0.4001),
                ("Poisson_GM_A_3", "<=", 0.15)
            ],
            "df_referencias": pd.DataFrame({
                "Intervalo CV": ["<=0.2500", "0.2501 - 0.6000", ">=0.6001"],
                "<=1.3500": ["0 - 0%", "0 - 0%", "<1000 - 100%"],
                "1.3501 - 1.6000": ["0 - 0%", "<49 - 98,06%", "<73 - 100%"],
                "1.9001 - 2.1500": ["<45 - 97,87%", "<50 - 98,08%", "0 - 0%"],
                ">=2.1501": ["<40 - 97,63%", "<40 - 100%", "0 - 0%"]
                }).set_index("Intervalo CV")
        },
    }
    
    # Configuração do Streamlit
    st.subheader("Today's Games for Lay 1X3 - Fluffy Method")
    
    if lay_1x3 is not None:
        all_games = []  # Lista para armazenar todos os jogos filtrados
    
        for league, config in leagues_config.items():
            prob_filter_col, prob_filter_val = config["prob_filter"]
            df_referencias = config["df_referencias"]
    
            # Aplicar filtros
            filtered_data = lay_1x3[lay_1x3["League"] == league]
            filtered_data = filtered_data[filtered_data[prob_filter_col] == prob_filter_val]
    
            # Aplicar filtro adicional para '1x3_H' e '1x3_A'
            filtered_data = filtered_data[(filtered_data['Perc_1x3_H'] < 10) & (filtered_data['Perc_1x3_A'] < 10)]
    
            for col, op, val in config["additional_filters"]:
                if op == ">=":
                    filtered_data = filtered_data[filtered_data[col] >= val]
                elif op == "<=":
                    filtered_data = filtered_data[filtered_data[col] <= val]
    
            # Aplicar a função para calcular 'Odd_Justa_Lay_1x3'
            filtered_data["Fair_Odd_%_Lay_1x3"] = filtered_data.apply(
                lambda row: obter_referencia(row["CV_MO_FT"], row["FT_Odd_H"], df_referencias),
                axis=1
            )
    
            # Aplicar a função para calcular 'h2h_lay_1x3'
            filtered_data["h2h_lay_1x3"] = filtered_data.apply(
                lambda row: check_h2h_lay_1x3(row["Home"], row["Away"], historical_data),
                axis=1
            )
    
            # Adicionar os jogos filtrados à lista
            all_games.append(filtered_data)
    
        # Concatenar todos os DataFrames da lista em um único DataFrame
        if all_games:
            final_df = pd.concat(all_games, ignore_index=True)
            final_df = final_df.sort_values(by='Time', ascending=True)  # Ordenar por 'Time'
            final_df = drop_reset_index(final_df)
        
            # Adicionar a coluna com a soma de 'h2h_lay_0x1' para cada grupo de 'Home' e 'Away'
            final_df["sum_h2h_lay_1x3"] = final_df.groupby(['Home', 'Away'])['h2h_lay_1x3'].transform('sum')
        
            # List of columns to display
            columns_to_display = [
                'Time', 'League', 'Home', 'Away', 'Round', 'Fair_Odd_%_Lay_1x3', 'sum_h2h_lay_1x3', 'FT_Odd_H', 'FT_Odd_D', 'FT_Odd_A', 'CV_Match_Type', 
                'Perc_0x1_H', 'Perc_0x1_A', 'Perc_Over15FT_Home', 'Perc_Over15FT_Away', 'Perc_Over25FT_Home', 'Perc_Over25FT_Away', 'Perc_BTTS_Yes_Home', 'Perc_BTTS_Yes_Away', 'h2h_lay_1x3'
            ]
        
            # Ensure all columns exist in final_df
            columns_to_display = [col for col in columns_to_display if col in final_df.columns]
        
            # Exibir o DataFrame final
            if not final_df.empty:
                st.dataframe(final_df[columns_to_display], use_container_width=True, hide_index=True)
            else:
                st.warning("No games found with the specified criteria.")
    else:
        st.error("No Data Available for the Chosen Date")
        
with tab_views[3]:
    st.subheader('Todays Games for Lay Any Other Home Win')
    st.markdown('If you Get 2 Goals on the First Half, You must Exit the Operation')
    
    # Verificar se 'data' está disponível e contém as colunas necessárias
    required_columns = ["League", "Time", "Home", "Away", "FT_Odd_H", "FT_Odd_Over25", "FT_Odd_BTTS_Yes"]

    if data is not None and all(col in data.columns for col in required_columns):
        
        # Aplicar filtros
        flt = (
            (data["FT_Odd_H"] >= 2.00) & 
            (data["FT_Odd_Over25"] >= 1.60) & 
            (data["FT_Odd_BTTS_Yes"] <= 2.50) &
            (data["Perc_goleada_casa_H"] < 10) &
            (data["Perc_goleada_casa_A"] < 10)
        )
        df_LGP = data[flt].dropna().reset_index(drop=True)  # Filtrar e resetar índice

        def LayGoleada(df_LGP, historical_data):
            """ 
            Filtra jogos onde as equipes têm alto potencial de gols marcados e sofridos,
            considerando apenas os últimos 38 jogos dentro da liga.
            """

            required_cols = ["League", "Date", "Home", "Away", "FT_Goals_H", "FT_Goals_A"]
            
            if historical_data is None or not all(col in historical_data.columns for col in required_cols):
                st.warning("No Historical Data Available for the Chosen Date")
                return

            results = []  # Lista para armazenar os resultados

            try:
                for league in df_LGP["League"].unique():
                    df_league_hist = historical_data[historical_data["League"] == league]

                    if df_league_hist.empty:
                        continue  # Pula ligas sem histórico suficiente

                    # Ordenar jogos por data (assumindo formato AAAA-MM-DD)
                    df_league_hist = df_league_hist.sort_values(by="Date", ascending=False)

                    # Filtrar apenas os últimos 21 jogos para cada time
                    df_home = df_league_hist.groupby("Home").head(21)
                    df_away = df_league_hist.groupby("Away").head(21)

                    # ✅ Substituindo .append() por pd.concat()
                    df_filtered = pd.concat([df_home, df_away]).drop_duplicates()

                    # Contar quantos jogos cada equipe tem
                    team_games_count = df_filtered["Home"].value_counts().add(df_filtered["Away"].value_counts(), fill_value=0)

                    # Manter apenas times que tenham pelo menos 21 jogos
                    valid_teams = team_games_count[team_games_count >= 21].index

                    df_filtered = df_filtered[df_filtered["Home"].isin(valid_teams) & df_filtered["Away"].isin(valid_teams)]

                    # Se não houver equipes suficientes, pula essa liga
                    if df_filtered.empty:
                        continue

                    # Recalcular gols marcados e sofridos com base nesses últimos 21 jogos
                    Gols_Marcados_Home = df_filtered.groupby("Home")["FT_Goals_H"].sum()
                    Gols_Marcados_Away = df_filtered.groupby("Away")["FT_Goals_A"].sum()
                    Gols_Marcados = pd.concat([Gols_Marcados_Home, Gols_Marcados_Away], axis=1).fillna(0)
                    Gols_Marcados["Gols_Marcados"] = Gols_Marcados.sum(axis=1)
                    Gols_Marcados = Gols_Marcados[["Gols_Marcados"]].sort_values("Gols_Marcados", ascending=False)

                    Gols_Sofridos_Home = df_filtered.groupby("Home")["FT_Goals_A"].sum()
                    Gols_Sofridos_Away = df_filtered.groupby("Away")["FT_Goals_H"].sum()
                    Gols_Sofridos = pd.concat([Gols_Sofridos_Home, Gols_Sofridos_Away], axis=1).fillna(0)
                    Gols_Sofridos["Gols_Sofridos"] = Gols_Sofridos.sum(axis=1)
                    Gols_Sofridos = Gols_Sofridos[["Gols_Sofridos"]].sort_values("Gols_Sofridos", ascending=True)

                    # Ajustar seleção de times ofensivos e defensivos
                    top_scoring_teams = set(Gols_Marcados.iloc[:max(1, len(valid_teams) // 2)].index)
                    weak_defense_teams = set(Gols_Sofridos.iloc[:max(1, len(valid_teams) // 2)].index)

                    # Filtrar jogos da liga que atendem aos critérios
                    df_matches_league = df_LGP[df_LGP["League"] == league]

                    for _, row in df_matches_league.iterrows():
                        home, away, match_time = row["Home"], row["Away"], row["Time"]

                        if home in top_scoring_teams and away in top_scoring_teams and \
                            home in weak_defense_teams and away in weak_defense_teams:
                            # Adicionar todos os dados necessários à lista de resultados
                            results.append([
                                league, match_time, home, away,
                                row.get("FT_Odd_H", None),  # Usar .get() para evitar erros se a coluna não existir
                                row.get("FT_Odd_D", None),
                                row.get("FT_Odd_A", None),
                                row.get("CV_Match_Type", None),
                                row.get("Perc_Over25FT_Home", None),
                                row.get("Perc_Over25FT_Away", None),
                                row.get("Perc_goleada_casa_H", None),
                                row.get("Perc_goleada_casa_A", None)
                            ])

                # Verificar se há resultados antes de exibir
                if results:
                    df_results = pd.DataFrame(results, columns=["League", "Time","Home", "Away", "FT_Odd_H", "FT_Odd_D", "FT_Odd_A", "CV_Match_Type", "Perc_Over25FT_Home", "Perc_Over25FT_Away", "Perc_goleada_casa_H", "Perc_goleada_casa_A"])
                    df_results = df_results.sort_values(by="Time").reset_index(drop=True)
                    st.dataframe(df_results, use_container_width=True, hide_index=True)
                else:
                    st.warning("No games found with the specified criteria.")

            except KeyError as e:
                st.error(f"No Data Available for the Chosen Date): {e}")

        # Chamar a função
        LayGoleada(df_LGP, historical_data)

    else:
        st.error("No Data Available for the Chosen Date")
    
with tab_views[4]:
    st.markdown(f'#### Teste of Lay Any Other Win Score ####')
    
    if data is not None and historical_data is not None:
        
        # Filtrar os times da data selecionada
        home_teams = data['Home'].unique()
        away_teams = data['Away'].unique()
        
        # Função para buscar os últimos 21 jogos de um time
        def get_last_21_games(team, historical_data):
            team_games = historical_data[(historical_data['Home'] == team) | (historical_data['Away'] == team)]
            team_games = team_games.sort_values(by='Date', ascending=False).head(21)
            return team_games
        
        # Função para verificar as condições de "Lay any Other Home Win"
        def check_home_win_conditions(games, team, historical_data):
            # Verificar se o time nunca ganhou marcando 4 ou mais golos
            never_won_by_4_or_more = not any(
                (games['Home'] == team) & (games['FT_Goals_H'] >= 4) & (games['FT_Goals_H'] > games['FT_Goals_A']))
            # Verificar se mais de 80% dos jogos foram Under 3
            under_3_percentage_team = (games[(games['Home'] == team) & (games['FT_Goals_H'] < 3)].shape[0] / games[games['Home'] == team].shape[0]) >= 0.85
            under_3_percentage = (games[(games['FT_Goals_H'] + games['FT_Goals_A']) <= 3].shape[0] / games.shape[0]) >= 0.8
            
            # Verificar se o time da casa não venceu por 4 ou mais gols contra o time visitante em confrontos anteriores
            home_vs_away_games = historical_data[
                ((historical_data['Home'] == team) & (historical_data['Away'].isin(away_teams))) |
                ((historical_data['Away'] == team) & (historical_data['Home'].isin(home_teams)))
            ]
            never_won_by_4_or_more_vs_opponent = not any(
                (home_vs_away_games['Home'] == team) & (home_vs_away_games['FT_Goals_H'] >= 4) & (home_vs_away_games['FT_Goals_H'] > home_vs_away_games['FT_Goals_A'])
            )
            
            return never_won_by_4_or_more and under_3_percentage and never_won_by_4_or_more_vs_opponent and under_3_percentage_team
        
        # Função para verificar as condições de "Lay any Other Away Win"
        def check_away_win_conditions(games, team, historical_data):
            # Verificar se o time nunca ganhou marcando 4 ou mais golos
            never_won_by_4_or_more = not any(
                (games['Away'] == team) & (games['FT_Goals_A'] >= 4) & (games['FT_Goals_A'] > games['FT_Goals_H']))
            # Verificar se mais de 80% dos jogos foram Under 3
            under_3_percentage_team = (games[(games['Away'] == team) & (games['FT_Goals_A'] < 3)].shape[0] / games[games['Away'] == team].shape[0]) >= 0.85
            under_3_percentage = (games[(games['FT_Goals_H'] + games['FT_Goals_A']) <= 3].shape[0] / games.shape[0]) >= 0.8
            
            # Verificar se o time visitante não venceu por 4 ou mais gols contra o time da casa em confrontos anteriores
            away_vs_home_games = historical_data[
                ((historical_data['Away'] == team) & (historical_data['Home'].isin(home_teams))) |
                ((historical_data['Home'] == team) & (historical_data['Away'].isin(away_teams)))
            ]
            never_won_by_4_or_more_vs_opponent = not any(
                (away_vs_home_games['Away'] == team) & (away_vs_home_games['FT_Goals_A'] >= 4) & (away_vs_home_games['FT_Goals_A'] > away_vs_home_games['FT_Goals_H'])
            )
            
            return never_won_by_4_or_more and under_3_percentage and never_won_by_4_or_more_vs_opponent and under_3_percentage_team
        
        # Lista para armazenar os jogos que atendem às condições
        home_win_games = []
        away_win_games = []
        
        # Verificar as condições para cada time em casa
        for team in home_teams:
            last_21_games = get_last_21_games(team, historical_data)
            if check_home_win_conditions(last_21_games, team, historical_data):
                home_win_games.extend(data[data['Home'] == team].to_dict('records'))
        
        # Verificar as condições para cada time fora
        for team in away_teams:
            last_21_games = get_last_21_games(team, historical_data)
            if check_away_win_conditions(last_21_games, team, historical_data):
                away_win_games.extend(data[data['Away'] == team].to_dict('records'))
        
        # Exibir os resultados
        st.subheader('Lay any Other Home Win')
        if home_win_games:
            
            # Filtrar as colunas desejadas e aplicar os filtros adicionais
            home_win_df = pd.DataFrame(home_win_games)[
                ["League", "Time", "Home", "Away", "FT_Odd_H", "FT_Odd_D", "FT_Odd_A", "CV_Match_Type", "Perc_Over25FT_Home", "Perc_Over25FT_Away", "Perc_goleada_casa_H", "Perc_goleada_casa_A"]
            ]
            home_win_df = home_win_df[(home_win_df['Perc_goleada_casa_H'] < 10) & (home_win_df['Perc_goleada_casa_A'] < 10) & (home_win_df['FT_Odd_H'] > 1.80)]
            
            # Exibir o DataFrame sem o índice
            st.dataframe(home_win_df, use_container_width=True, hide_index=True)  # Use hide_index para remover o índice
        else:
            st.warning("No games found with the specified criteria.")
        
        st.subheader('Lay any Other Away Win')
        if away_win_games:
            
            # Filtrar as colunas desejadas e aplicar os filtros adicionais
            away_win_df = pd.DataFrame(away_win_games)[
                ["League", "Time", "Round", "Home", "Away", "FT_Odd_H", "FT_Odd_D", "FT_Odd_A", "CV_Match_Type", "Perc_Over25FT_Away", "Perc_Over25FT_Home", "Perc_goleada_away_A", "Perc_goleada_away_H"]
            ]
            away_win_df = away_win_df[(away_win_df['Perc_goleada_away_A'] < 10) & (away_win_df['Perc_goleada_away_H'] < 10) & (away_win_df['FT_Odd_A'] > 1.80)]
            
            # Exibir o DataFrame sem o índice
            st.dataframe(away_win_df, use_container_width=True, hide_index=True)  # Use hide_index para remover o índice
        else:
            st.warning("No games found with the specified criteria.")
    else:
        st.error("No Data Available for the Chosen Date")