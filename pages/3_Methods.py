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

# Load Data
with st.spinner("Fetching data..."):
    try:
        data = load_data(csv_file_url)
        if data is not None:
            data_Ov25_FT = data.copy()
            data_btts = data.copy()
            lay_home = data.copy()
            lay_away = data.copy()
        else:
            data_Ov25_FT = None
            data_btts = None
            lay_home = None
            lay_away = None
    except Exception as e:
        st.warning("No Data Available for the Chosen Date")
        data = None
        data_Ov25_FT = None
        data_btts = None
        lay_home = None
        lay_away = None

    try:
        historical_data = load_data(historical_data_url)
    except Exception as e:
        st.warning("No Historical Data Available for the Chosen Date")
        historical_data = None

    try:
        leagues_data = load_data(leagues_url)
    except Exception as e:
        st.warning("No Leagues Data Available for the Chosen Date")
        leagues_data = None

    try:
        elo_tilt_data = load_data(elo_tilt_url)
    except Exception as e:
        st.warning("No Elo & Tilt Data Available for the Chosen Date")
        elo_tilt_data = None

# Display Success Messages
if data is not None:
    st.success("Jogos do Dia loaded successfully!")
else:
    st.warning("No Data Available for the Chosen Date")

if historical_data is not None:
    st.success("Historical Data loaded successfully!")
else:
    st.warning("No Historical Data Available for the Chosen Date")

if leagues_data is not None:
    st.success("Leagues Data loaded successfully!")
else:
    st.warning("No Leagues Data Available for the Chosen Date")

if elo_tilt_data is not None:
    st.success("Elo & Tilt Data loaded successfully!")
else:
    st.warning("No Elo & Tilt Data Available for the Chosen Date")

# Create Tabs
tabs = ['Lay 0 x 1', 'Goleada Home', 'Over 1,5 FT', 'Lay Home', 'Lay Away', 'Under 1,5 FT', 'Back Home', 'Lay 1x1', 'Any Other Win', 'Louro José', 'Best Teams', 'Over 2,5 FT', ' BTTS']
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
        "EUROPE - CHAMPIONS LEAGUE": {
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
        "ARGENTINA - TORNEO BETANO": {
            "prob_filter": ("Probability_Home", "p_Bigger"),
            "additional_filters": [
                ("prob_Under_25_FT", "<=", 0.75),
                ("Poisson_GM_H_2", ">=", 0.1501)
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
        "CROATIA - HNL": {
            "prob_filter": ("Probability_Away", "Avg_Bigger"),
            "additional_filters": [
                ("prob_BTTS_No_FT", ">=", 0.5001),
                ("Poisson_GM_H_0", "<=", 0.30),
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
        "EGYPT - PREMIER LEAGUE": {
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
        "ENGLAND - PREMIER LEAGUE": {
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
        "ENGLAND - CHAMPIONSHIP": {
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
        "ENGLAND - LEAGUE ONE": {
            "prob_filter": ("Probability_Away", "Avg_Bigger"),
            "additional_filters": [
                ("prob_A", "<=", 0.30),
                ("prob_D", "<=", 0.30)
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
        "FRANCE - LIGUE 2": {
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
        "GERMANY - BUNDESLIGA": {
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
        "GERMANY - 2. BUNDESLIGA": {
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
        "GREECE - SUPER LEAGUE": {
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
        "INDIA - ISL": {
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
        "INDONESIA - LIGA 1": {
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
        "ISRAEL - LIGAT HA'AL": {
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
        "ITALY - SERIE A": {
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
        "ITALY - SERIE B": {
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
        "JAPAN - J1 LEAGUE": {
            "prob_filter": ("Probability_Away", "Avg_Bigger"),
            "additional_filters": [
                ("Poisson_GM_H_0", "<=", 0.3000),
                ("prob_D", ">=", 0.1501),
                ("prob_D", "<=", 0.3000)
                ],
            "df_referencias": pd.DataFrame({
                "Intervalo CV": ["<=0.3000", "0.3001 - 0.5000", ">=0.5001"],
                "<=1.5500": ["0", "0", "<25"],
                "1.5501 - 1.7500": ["0", "<40", "<13"],
                "1.7501 - 2.0500": ["<9", "<12", "0"],
                ">=2.0501": ["<16", "<18", "<19"]
                }).set_index("Intervalo CV")
        },
        "MEXICO - LIGA MX": {
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
        "NETHERLANDS - EREDIVISIE": {
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
        "NETHERLANDS - EERSTE DIVISIE": {
            "prob_filter": ("Conceded_Goals", "Bigger_Away"),
            "additional_filters": [
                ("Poisson_GS_A_2", ">=", 0.2001),
                ("prob_H", ">=", 0.4501)
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
        "PORTUGAL - LIGA PORTUGAL 2": {
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
        "QATAR - QSL": {
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
        "ROMANIA - SUPERLIGA": {
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
        "SAUDI ARABIA - SAUDI PROFESSIONAL LEAGUE": {
            "prob_filter": ("Scored_Goals", "Bigger_Home"),
            "additional_filters": [
                ("Poisson_GS_A_2", ">=", 0.1501),
                ("Poisson_GS_A_2", "<=", 0.3000),
                ("prob_H", ">=", 0.3001)
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
        "SPAIN - LALIGA2": {
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
        "THAILAND - THAI LEAGUE 1": {
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
        "TURKEY - SUPER LIG": {
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
        "TURKEY - 1. LIG": {
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
        "USA - MLS": {
            "prob_filter": ("Probability_Away", "Avg_Bigger"),
            "additional_filters": [
                ("prob_H", ">=", 0.5001),
                ("prob_Over_25_FT", ">=", 0.5501)
                ],
            "df_referencias": pd.DataFrame({
                "Intervalo CV": ["<=0.4500", "0.4501 - 0.6000", ">=0.6001"],
                "<=1.4500": ["0", "0", "<60"],
                "1.4501 - 1.6000": ["0", "<19", "<40"],
                "1.6001 - 1.7500": ["<29", "<17", "0"],
                ">=1.7501": ["<34", "0", "0"]
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
            final_df["sum_h2h_lay_0x1"] = final_df.groupby(['Home', 'Away'])['h2h_lay_0x1'].transform('sum')
        
            # List of columns to display
            columns_to_display = [
                'Time', 'League', 'Home', 'Away', 'Round', 'Odd_Justa_Lay_0x1', 'sum_h2h_lay_0x1', 'FT_Odd_H', 'FT_Odd_D', 'FT_Odd_A', 'CV_Match_Type', 
                'Perc_0x1_H', 'Perc_0x1_A', 'Perc_Over15FT_Home', 'Perc_Over15FT_Away', 'Perc_Over25FT_Home', 'Perc_Over25FT_Away', 'Perc_BTTS_Yes_Home', 'Perc_BTTS_Yes_Away', 'h2h_lay_0x1'
            ]
        
            # Ensure all columns exist in final_df
            columns_to_display = [col for col in columns_to_display if col in final_df.columns]
        
            # Exibir o DataFrame final
            st.dataframe(final_df[columns_to_display], use_container_width=True, hide_index=True)
        else:
            st.info("No games found with the specified criteria.")
    else:
        st.info("No Data Available for the Chosen Date")

with tab_views[1]:
    st.subheader('Todays Games for Lay Any Other Home Win')
    st.markdown('If you Get 2 Goals on the First Half, You must Exit the Operation')
    
    # Verificar se 'data' está disponível e contém as colunas necessárias
    required_columns = ["League", "Time", "Home", "Away", "FT_Odd_H", "FT_Odd_Over25", "FT_Odd_BTTS_Yes"]

    if data is not None and all(col in data.columns for col in required_columns):
        
        # Aplicar filtros
        flt = (
            (data["FT_Odd_H"] >= 1.50) & 
            (data["FT_Odd_Over25"] >= 1.50) & 
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
                                row.get("Round", None),
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
                    df_results = pd.DataFrame(results, columns=["League", "Time","Round", "Home", "Away", "FT_Odd_H", "FT_Odd_D", "FT_Odd_A", "CV_Match_Type", "Perc_Over25FT_Home", "Perc_Over25FT_Away", "Perc_goleada_casa_H", "Perc_goleada_casa_A"])
                    df_results = df_results.sort_values(by="Time").reset_index(drop=True)
                    st.dataframe(df_results, use_container_width=True, hide_index=True)
                else:
                    st.info("No games found with the specified criteria.")

            except KeyError as e:
                st.error(f"No Data Available for the Chosen Date): {e}")

        # Chamar a função
        LayGoleada(df_LGP, historical_data)

    else:
        st.info("No Data Available for the Chosen Date")

with tab_views[2]:
    st.subheader('Todays Games for Over 1,5 FT')
    st.markdown('If the Odd is less than 1.45, you must wait for it to reach minimum 1.45')
    if data is not None:
        # Aplicar os filtros
        over_15_ft_flt = data[
            ((data["Perc_Over15FT_Home"] + data["Perc_Over15FT_Away"]) / 2 > 65) &
            ((data["Perc_BTTS_Yes_FT_Home"] + data["Perc_BTTS_Yes_FT_Away"]) / 2 > 65) &
            (data["Avg_G_Scored_H_FT"] > 1) &
            (data["CV_Avg_G_Scored_H_FT"] < 1) &
            (data["Avg_G_Scored_A_FT"] > 1) &
            (data["CV_Avg_G_Scored_A_FT"] < 1) &
            (data["Avg_G_Conceded_H_FT"] > 1) &
            (data["CV_Avg_G_Conceded_H_FT"] < 1) &
            (data["Avg_G_Conceded_A_FT"] > 1) &
            (data["CV_Avg_G_Conceded_A_FT"] < 1)
        ]
        over_15_ft_flt = over_15_ft_flt.sort_values(by='Time', ascending=True)

        # Selecionar apenas as colunas desejadas
        selected_columns = ["League", "Time", "Home", "Away", "FT_Odd_H", "FT_Odd_D", "FT_Odd_A", "CV_Match_Type", "Perc_Over15FT_Home", "Perc_Over15FT_Away", "Perc_Over25FT_Home", "Perc_Over25FT_Away"]
        selected_columns = [col for col in selected_columns if col in over_15_ft_flt.columns]
        over_15_ft_flt = over_15_ft_flt[selected_columns]

        # Exibir os dados filtrados
        if not over_15_ft_flt.empty:
            st.dataframe(over_15_ft_flt, use_container_width=True, hide_index=True)
        else:
            st.info("No games found with the specified criteria.")
    else:
        st.info("No Data Available for the Chosen Date")

with tab_views[3]:
    st.subheader("Todays Games for Lay Home")
    try:
        lay_home['VAR1'] = np.sqrt((lay_home['FT_Odd_H'] - lay_home['FT_Odd_A'])**2)
        lay_home['VAR2'] = np.degrees(np.arctan((lay_home['FT_Odd_A'] - lay_home['FT_Odd_H']) / 2))
        lay_home['VAR3'] = np.degrees(np.arctan((lay_home['FT_Odd_D'] - lay_home['FT_Odd_A']) / 2))
    except KeyError as e:
        st.error(f"No Games Available for Lay Home: {e}")
    
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
                st.dataframe(lay_home_flt[['League', 'Time', 'Home', 'Away', 'Round', 'FT_Odd_H', 'FT_Odd_A', 'FT_Odd_D', 'Odd_Home_Justa', 'Odd_Away_Justa', 'Avg_Points_Home_FT', 'PPJ_Home', 'CV_Avg_Points_Home_FT', 'Avg_Points_Away_FT', 'PPJ_Away', 'CV_Avg_Points_Away_FT', 'CV_Match_Type', 'Elo_Home', 'Tilt_Home', 'Elo_Away', 'Tilt_Away', 'Elo_Difference', 'Avg_Power_Ranking_H', 'CV_Avg_Power_Ranking_H', 'Avg_Power_Ranking_A', 'CV_Avg_Power_Ranking_A']], use_container_width=True, hide_index=True)
            else:
                st.info("No games found with the specified criteria.")
        except Exception as e:
            st.error(f"Erro ao carregar ou processar os dados para Back Home: {e}")
    else:
        st.info("No Data Available for the Chosen Date")

with tab_views[4]:
    st.subheader("Todays Games for Lay Away")
    try:
        lay_away['VAR1'] = np.sqrt((lay_away['FT_Odd_H'] - lay_away['FT_Odd_A'])**2)
        lay_away['VAR2'] = np.degrees(np.arctan((lay_away['FT_Odd_A'] - lay_away['FT_Odd_H']) / 2))
        lay_away['VAR3'] = np.degrees(np.arctan((lay_away['FT_Odd_D'] - lay_away['FT_Odd_A']) / 2))
    except KeyError as e:
        st.error(f"No Games Available for Lay Away: {e}")
    
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
                st.dataframe(lay_away_flt[['League', 'Time', 'Round', 'Home', 'Away', 'FT_Odd_H', 'FT_Odd_A', 'FT_Odd_D', 'Odd_Home_Justa', 'Odd_Away_Justa', 'Avg_Points_Home_FT', 'PPJ_Home', 'CV_Avg_Points_Home_FT', 'Avg_Points_Away_FT', 'PPJ_Away', 'CV_Avg_Points_Away_FT', 'CV_Match_Type', 'Elo_Home', 'Tilt_Home', 'Elo_Away', 'Tilt_Away', 'Elo_Difference', 'Avg_Power_Ranking_H', 'CV_Avg_Power_Ranking_H', 'Avg_Power_Ranking_A', 'CV_Avg_Power_Ranking_A']], use_container_width=True, hide_index=True)
            else:
                st.info("No games found with the specified criteria.")
        except Exception as e:
            st.error(f"No Data Available for the Chosen Date: {e}")
    else:
        st.info("No Data Available for the Chosen Date")
        
with tab_views[5]:
    st.subheader('Todays Games for Under 1,5 FT')
    st.markdown('Croatia Method 1')
    if data is not None:
        # Aplicar os filtros
        under_15_croatia_01_ft_flt = data[
            (data["League"] == 'CROATIA - HNL') &
            (data["Points"] == 'Points_Home') &
            (data["RPS_OVUnd"] == 'Bigger_Away') &
            (data["Poisson_GS_H_2"] > 0.1660) &
            (data["Poisson_GS_H_2"] < 0.2610) &
            (data["Avg_CG_Scored_A_02"] > 0.5550) &
            (data["Avg_CG_Scored_A_02"] < 0.8390)
        ]
        under_15_croatia_01_ft_flt = under_15_croatia_01_ft_flt.sort_values(by='Time', ascending=True)

        # Exibir os dados filtrados
        if not under_15_croatia_01_ft_flt.empty:
            st.dataframe(under_15_croatia_01_ft_flt, use_container_width=True, hide_index=True)
        else:
            st.info("No games found with the specified criteria.")
    else:
        st.info("Dados indisponíveis para a data selecionada.")
    st.markdown('Croatia Method 2')
    if data is not None:
        # Aplicar os filtros
        under_15_croatia_02_ft_flt = data[
            (data["League"] == 'CROATIA - HNL') &
            (data["Points"] == 'Points_Home') &
            (data["RPS_OVUnd"] == 'Bigger_Away') &
            (data["Poisson_GS_H_2"] > 0.1660) &
            (data["Poisson_GS_H_2"] < 0.2610) &
            (data["Avg_CG_Conceded_H_02"] > 0.7080) &
            (data["Avg_CG_Conceded_H_02"] < 0.9270)
        ]
        under_15_croatia_02_ft_flt = under_15_croatia_02_ft_flt.sort_values(by='Time', ascending=True)

        # Exibir os dados filtrados
        if not under_15_croatia_02_ft_flt.empty:
            st.dataframe(under_15_croatia_02_ft_flt, use_container_width=True, hide_index=True)
        else:
            st.info("No games found with the specified criteria.")
    else:
        st.info("No Data Available for the Chosen Date")
    st.markdown('Croatia Method 3')
    if data is not None:
        # Aplicar os filtros
        under_15_croatia_03_ft_flt = data[
            (data["League"] == 'CROATIA - HNL') &
            (data["Points"] == 'Points_Home') &
            (data["RPS_OVUnd"] == 'Bigger_Away') &
            (data["prob_G_Scored_H"] > 0.9020) &
            (data["prob_G_Scored_H"] < 1.5720) &
            (data["prob_G_Conceded_H"] > 0.9370) &
            (data["prob_G_Conceded_H"] < 1.3880)
        ]
        under_15_croatia_03_ft_flt = under_15_croatia_03_ft_flt.sort_values(by='Time', ascending=True)

        # Exibir os dados filtrados
        if not under_15_croatia_03_ft_flt.empty:
            st.dataframe(under_15_croatia_03_ft_flt, use_container_width=True, hide_index=True)
        else:
            st.info("No games found with the specified criteria.")
    else:
        st.info("No Data Available for the Chosen Date")
        
with tab_views[6]:
    st.subheader('Todays Games for Back_Home')
    st.markdown('Portugal - Liga Portugal 1 - Method 1')
    if data is not None:
        # Aplicar os filtros
        back_home_Port_01_01_ft_flt = data[
            (data["League"] == 'PORTUGAL - LIGA PORTUGAL') &
            (data["Home_Score_Take"] == 'No') &
            (data["Away_Score_Take"] == 'Yes') &
            (data["Avg_G_Diff_A_FT_Value"] > -0.0900) &
            (data["Avg_G_Diff_A_FT_Value"] < 0.0250)
        ]
        back_home_Port_01_01_ft_flt = back_home_Port_01_01_ft_flt.sort_values(by='Time', ascending=True)
        
        # Exibir os dados filtrados
        if not back_home_Port_01_01_ft_flt.empty:
            st.dataframe(back_home_Port_01_01_ft_flt, use_container_width=True, hide_index=True)
        else:
            st.info("No games found with the specified criteria.")
    else:
        st.info("No Data Available for the Chosen Date")
    st.markdown('Portugal - Liga Portugal 1 - Method 2')
    if data is not None:
        # Aplicar os filtros
        back_home_Port_01_02_ft_flt = data[
            (data["League"] == 'PORTUGAL - LIGA PORTUGAL') &
            (data["Home_Score_Take"] == 'No') &
            (data["Away_Score_Take"] == 'Yes') &
            (data["Poisson_GS_A_2"] > 0.2520) &
            (data["Poisson_GS_A_2"] < 0.2710) &
            (data["Avg_Points_Away_FT"] > 0.9780) &
            (data["Avg_Points_Away_FT"] < 1.6950)
        ]
        back_home_Port_01_02_ft_flt = back_home_Port_01_02_ft_flt.sort_values(by='Time', ascending=True)
        
        # Exibir os dados filtrados
        if not back_home_Port_01_02_ft_flt.empty:
            st.dataframe(back_home_Port_01_02_ft_flt, use_container_width=True, hide_index=True)
        else:
            st.info("No games found with the specified criteria.")
    else:
        st.info("No Data Available for the Chosen Date")
    st.markdown('Portugal - Liga Portugal 1 - Method 3')
    if data is not None:
        # Aplicar os filtros
        back_home_Port_01_03_ft_flt = data[
            (data["League"] == 'PORTUGAL - LIGA PORTUGAL') &
            (data["Home_Score_Take"] == 'No') &
            (data["Away_Score_Take"] == 'Yes') &
            (data["Avg_Points_Away_FT"] > 0.9780) &
            (data["Avg_Points_Away_FT"] < 1.6950) &
            (data["Avg_G_Conceded_A_FT_Value"] > 1.5120) &
            (data["Avg_G_Conceded_A_FT_Value"] < 4.0670)
        ]
        back_home_Port_01_03_ft_flt = back_home_Port_01_03_ft_flt.sort_values(by='Time', ascending=True)
        
        # Exibir os dados filtrados
        if not back_home_Port_01_03_ft_flt.empty:
            st.dataframe(back_home_Port_01_03_ft_flt, use_container_width=True, hide_index=True)
        else:
            st.info("No games found with the specified criteria.")
    else:
        st.info("No Data Available for the Chosen Date")
        
with tab_views[7]:
    st.subheader('Todays Games for Lay 1x1 Based on Home Team')
    st.markdown('Keep The Operation until Green or close at 60 min. At Half Time if you have Profit Close the Operation')
    
    if data is not None:
        # Check if the required columns exist in the DataFrame
        required_columns = ["League", "Time", "Round", "Home", "Away", "FT_Odd_H", "FT_Odd_D", "FT_Odd_A", "CV_Match_Type", "Perc_Over25FT_Home", "Perc_Over25FT_Away"]
        
        # Apply filters for Lay 1x1 based on Home Team
        lay_1x1_home_flt0 = data[
            (data["FT_Odd_H"] < 1.75) &  # Home team odds less than 1.75
            (data["FT_Odd_Over25"] < 1.65)  # Over 2.5 goals odds less than 1.65
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
            st.info("No games found with the specified criteria.")
            
    st.subheader('Todays Games for Lay 1x1 Based on Away Team')
    st.markdown('Keep The Operation until Green or close at 60 min. At Half Time if you have Profit Close the Operation')
    
    if data is not None:
        # Check if the required columns exist in the DataFrame
        required_columns = ["League", "Time", "Home", "Away", "FT_Odd_H", "FT_Odd_D", "FT_Odd_A", "CV_Match_Type", "Perc_Over25FT_Home", "Perc_Over25FT_Away"]
        
        # Apply filters for Lay 1x1 based on Away Team
        lay_1x1_away_flt0 = data[
            (data["FT_Odd_A"] < 1.75) &  # Away team odds less than 1.75
            (data["FT_Odd_Over25"] < 1.65)  # Over 2.5 goals odds less than 1.65
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
            st.info("No games found with the specified criteria.")
    else:
        st.info("No Data Available for the Chosen Date")
        
with tab_views[8]:
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
            home_win_df = home_win_df[(home_win_df['Perc_goleada_casa_H'] < 10) & (home_win_df['Perc_goleada_casa_A'] < 10)]
            
            # Exibir o DataFrame sem o índice
            st.dataframe(home_win_df, use_container_width=True, hide_index=True)  # Use hide_index para remover o índice
        else:
            st.info("No games found with the specified criteria.")
        
        st.subheader('Lay any Other Away Win')
        if away_win_games:
            
            # Filtrar as colunas desejadas e aplicar os filtros adicionais
            away_win_df = pd.DataFrame(away_win_games)[
                ["League", "Time", "Round", "Home", "Away", "FT_Odd_H", "FT_Odd_D", "FT_Odd_A", "CV_Match_Type", "Perc_Over25FT_Away", "Perc_Over25FT_Home", "Perc_goleada_away_A", "Perc_goleada_away_H"]
            ]
            away_win_df = away_win_df[(away_win_df['Perc_goleada_away_A'] < 10) & (away_win_df['Perc_goleada_away_H'] < 10)]
            
            # Exibir o DataFrame sem o índice
            st.dataframe(away_win_df, use_container_width=True, hide_index=True)  # Use hide_index para remover o índice
        else:
            st.info("No games found with the specified criteria.")
    else:
        st.info("No Data Available for the Chosen Date")
        
with tab_views[9]:
    st.markdown('#### Best Teams for Louro José ####')
    
    if data is not None:
        # Apply the extra filter conditions
        conditions = [
            (data['Avg_G_Scored_H_ST'] > 1) & (data['Avg_G_Conceded_A_ST'] > 1),
            (data['Avg_G_Scored_A_ST'] > 1) & (data['Avg_G_Conceded_H_ST'] > 1),
            (data['Avg_G_Scored_H_ST'] > 1) & (data['Avg_G_Scored_A_ST'] > 1),
            (data['Avg_G_Conceded_H_ST'] > 1) & (data['Avg_G_Conceded_A_ST'] > 1)
        ]
        
        # Combine conditions using logical OR
        combined_condition = conditions[0]
        for condition in conditions[1:]:
            combined_condition |= condition
        
        # Filter data
        df_louro_jose = data[combined_condition].drop_duplicates(subset=['Home'])
        
        # Sort by 'Time' (ensure 'Time' is in a sortable format)
        df_louro_jose = df_louro_jose.sort_values(by='Time', ascending=True)
        
        # Define columns to display
        columns_to_display = [
            'League', 'Time', 'Round', 'Home', 'Away', 'FT_Odd_Over25', 'FT_Odd_BTTS_Yes', 'CV_Match_Type',
            'CV_Avg_G_Scored_H_ST', 'CV_Avg_G_Scored_A_ST', 'Perc_Over15ST_Home', 'Perc_Over15ST_Away', 
            'Perc_Over15FT_Home', 'Perc_Over15FT_Away', 'Perc_Over25FT_Home', 'Perc_Over25FT_Away'
        ]
        
        # Check if columns exist in the DataFrame
        columns_to_display = [col for col in columns_to_display if col in df_louro_jose.columns]
        
        # Display the final DataFrame
        st.dataframe(df_louro_jose[columns_to_display], use_container_width=True, hide_index=True)
    else:
        st.info("No games found with the specified criteria.")

with tab_views[10]:
    st.markdown(f'#### Best Teams with > 60% Probability - Last 11 Games ####')
    if data is not None:
        # Apply the extra filter conditions
        flt_home_SFW = data[data['Perc_Scored_First_and_Won_H'] > 60]
        flt_home_SFD = data[data['Perc_Scored_First_and_Draw_H'] > 60]
        flt_home_SFL = data[data['Perc_Scored_First_and_Lost_H'] > 60]
        flt_home_CFW = data[data['Perc_Conceded_First_and_Won_H'] > 60]
        flt_home_CFD = data[data['Perc_Conceded_First_and_Draw_H'] > 60]
        flt_home_CFL = data[data['Perc_Conceded_First_and_Lost_H'] > 60]
        flt_home_DilV = data[data['Perc_Dilatou_Vantagem_1_Golo_H'] > 50]
        flt_away_SFW = data[data['Perc_Scored_First_and_Won_A'] > 60]
        flt_away_SFD = data[data['Perc_Scored_First_and_Draw_A'] > 60]
        flt_away_SFL = data[data['Perc_Scored_First_and_Lost_A'] > 60]
        flt_away_CFW = data[data['Perc_Conceded_First_and_Won_A'] > 60]
        flt_away_CFD = data[data['Perc_Conceded_First_and_Draw_A'] > 60]
        flt_away_CFL = data[data['Perc_Conceded_First_and_Lost_A'] > 60]
        flt_away_DilV = data[data['Perc_Dilatou_Vantagem_1_Golo_A'] > 50]
        
        # Define columns to display
        columns_to_display = [
            'League', 'Time', 'Round', 'Home', 'Away', 'CV_Match_Type', 'Perc_Home_Win_FT', 'Perc_Draw_Win_H_FT', 
            'Perc_Draw_Win_A_FT', 'Perc_Away_Win_FT' ]
        
        # Check if columns exist in the DataFrame
        columns_to_display = [col for col in columns_to_display if col in data.columns]
        
        # Display the final DataFrame
        st.markdown('#### Home Scored First and Won ####')
        if not flt_home_SFW.empty:
            st.dataframe(flt_home_SFW[columns_to_display], use_container_width=True, hide_index=True)
        else:
            st.info("No Games available with minimum stats.")
        
        st.markdown('#### Home Scored First and Draw ####')
        if not flt_home_SFD.empty:
            st.dataframe(flt_home_SFD[columns_to_display], use_container_width=True, hide_index=True)
        else:
            st.info("No Games available with minimum stats.")
        
        st.markdown('#### Home Scored First and Lost ####')
        if not flt_home_SFL.empty:
            st.dataframe(flt_home_SFL[columns_to_display], use_container_width=True, hide_index=True)
        else:
            st.info("No Games available with minimum stats.")
        
        st.markdown('#### Home Conceded First and Won ####')
        if not flt_home_CFW.empty:
            st.dataframe(flt_home_CFW[columns_to_display], use_container_width=True, hide_index=True)
        else:
            st.info("No Games available with minimum stats.")
        
        st.markdown('#### Home Conceded First and Draw ####')
        if not flt_home_CFD.empty:
            st.dataframe(flt_home_CFD[columns_to_display], use_container_width=True, hide_index=True)
        else:
            st.info("No Games available with minimum stats.")
        
        st.markdown('#### Home Conceded First and Lost ####')
        if not flt_home_CFL.empty:
            st.dataframe(flt_home_CFL[columns_to_display], use_container_width=True, hide_index=True)
        else:
            st.info("No Games available with minimum stats.")
        
        st.markdown('#### Home After winning by one scored the second ####')
        if not flt_home_DilV.empty:
            st.dataframe(flt_home_DilV[columns_to_display], use_container_width=True, hide_index=True)
        else:
            st.info("No Games available with minimum stats.")
        
        st.markdown('#### Away Scored First and Won ####')
        if not flt_away_SFW.empty:
            st.dataframe(flt_away_SFW[columns_to_display], use_container_width=True, hide_index=True)
        else:
            st.info("No Games available with minimum stats.")
        
        st.markdown('#### Away Scored First and Draw ####')
        if not flt_away_SFD.empty:
            st.dataframe(flt_away_SFD[columns_to_display], use_container_width=True, hide_index=True)
        else:
            st.info("No Games available with minimum stats.")
        
        st.markdown('#### Away Scored First and Lost ####')
        if not flt_away_SFL.empty:
            st.dataframe(flt_away_SFL[columns_to_display], use_container_width=True, hide_index=True)
        else:
            st.info("No Games available with minimum stats.")
        
        st.markdown('#### Away Conceded First and Won ####')
        if not flt_away_CFW.empty:
            st.dataframe(flt_away_CFW[columns_to_display], use_container_width=True, hide_index=True)
        else:
            st.info("No Games available with minimum stats.")
        
        st.markdown('#### Away Conceded First and Draw ####')
        if not flt_away_CFD.empty:
            st.dataframe(flt_away_CFD[columns_to_display], use_container_width=True, hide_index=True)
        else:
            st.info("No Games available with minimum stats.")
        
        st.markdown('#### Away Conceded First and Lost ####')
        if not flt_away_CFL.empty:
            st.dataframe(flt_away_CFL[columns_to_display], use_container_width=True, hide_index=True)
        else:
            st.info("No Games available with minimum stats.")
        
        st.markdown('#### Away After winning by one scored the second ####')
        if not flt_away_DilV.empty:
            st.dataframe(flt_away_DilV[columns_to_display], use_container_width=True, hide_index=True)
        else:
            st.info("No Games available with minimum stats.")
    else:
        st.info("No games found with the specified criteria.")
        
with tab_views[11]:
    st.markdown(f'#### Over 2,5 FT - Teste ####')
    st.markdown(f'#### Cost of Goal 2.0 ####')
    
    if data_Ov25_FT is not None:
        CG02_data_Ov25_FT = data_Ov25_FT[
            (data_Ov25_FT['Perc_Over25FT_Home'] >= 60) & (data_Ov25_FT['Perc_Over25FT_Away'] > 60) &
            (data_Ov25_FT['Perc_BTTS_Yes_FT_Home'] >= 60) & (data_Ov25_FT['Perc_BTTS_Yes_FT_Away'] >= 60) &
            (data_Ov25_FT['Avg_CG_Scored_H_02'] >= 0.8) & (data_Ov25_FT['Avg_CG_Scored_A_02'] >= 0.8) &
            (data_Ov25_FT['Avg_CG_Conceded_H_02'] >= 0.8) & (data_Ov25_FT['Avg_CG_Conceded_A_02'] > 0.8) &
            (data_Ov25_FT['CV_Avg_CG_Scored_H_02'] <= 0.7) & (data_Ov25_FT['CV_Avg_CG_Scored_A_02'] < 0.7) &
            (data_Ov25_FT['CV_Avg_CG_Conceded_H_02'] <= 0.7) & (data_Ov25_FT['CV_Avg_CG_Conceded_A_02'] <= 0.7)
            ]
    
    # Display the final DataFrame
        if not CG02_data_Ov25_FT.empty:
            # Define columns to display
            columns_to_display = [
                'League', 'Time', 'Round', 'Home', 'Away', 'CV_Match_Type', 'Perc_Over25FT_Home', 'Perc_Over25FT_Away', 
                'Perc_BTTS_Yes_FT_Home', 'Perc_BTTS_Yes_FT_Away' ]
            st.dataframe(CG02_data_Ov25_FT[columns_to_display], use_container_width=True, hide_index=True)
        else:
            st.info("No games found with the specified criteria.")
        
    st.markdown(f'#### Normal Average ####')
    
    if data_Ov25_FT is not None:
        avg_data_Ov25_FT = data_Ov25_FT[
            (data_Ov25_FT['Perc_Over25FT_Home'] > 55) & (data_Ov25_FT['Perc_Over25FT_Away'] > 55) &
            (data_Ov25_FT['Perc_BTTS_Yes_FT_Home'] > 55) & (data_Ov25_FT['Perc_BTTS_Yes_FT_Away'] > 55) &
            (data_Ov25_FT['Avg_G_Scored_H_FT_Value'] > 1) & (data_Ov25_FT['Avg_G_Scored_A_FT_Value'] > 1) &
            (data_Ov25_FT['Avg_G_Conceded_H_FT_Value'] > 1) & (data_Ov25_FT['Avg_G_Conceded_A_FT_Value'] > 1) &
            (data_Ov25_FT['CV_Avg_G_Scored_H_FT_Value'] < 1) & (data_Ov25_FT['CV_Avg_G_Scored_A_FT_Value'] < 1) &
            (data_Ov25_FT['CV_Avg_G_Conceded_H_FT_Value'] < 1) & (data_Ov25_FT['CV_Avg_G_Conceded_A_FT_Value'] < 1)
            ]
    
    # Display the final DataFrame
        if not avg_data_Ov25_FT.empty:
            # Define columns to display
            columns_to_display = [
                'League', 'Time', 'Round', 'Home', 'Away', 'CV_Match_Type', 'Perc_Over25FT_Home', 'Perc_Over25FT_Away', 
                'Perc_BTTS_Yes_FT_Home', 'Perc_BTTS_Yes_FT_Away' ]
            st.dataframe(avg_data_Ov25_FT[columns_to_display], use_container_width=True, hide_index=True)
        else:
            st.info("No games found with the specified criteria.")
    else:
        st.info("Data is empty.")
        
with tab_views[12]:
    st.markdown(f'#### Games with High Probability for BTTS Yes ####')
    
    if data_btts is not None:
        base_btts = data_btts[
            (((data_btts['Avg_G_Scored_H_FT'] + data_btts['Avg_G_Conceded_H_FT']) + (data_btts['Avg_G_Scored_A_FT'] + data_btts['Avg_G_Conceded_A_FT'])) / 2 >= 2.70) &
            ((data_btts['Avg_G_Scored_H_FT'] + data_btts['Avg_G_Conceded_A_FT']) /2 > 1.42) & 
            ((data_btts['Avg_G_Scored_A_FT'] + data_btts['Avg_G_Conceded_H_FT']) /2 > 1.42) &
            (data_btts['Perc_BTTS_Yes_FT_Home'] > 50) & (data_btts['Perc_BTTS_Yes_FT_Away'] > 50) & 
            (data_btts['Perc_Over25FT_Home'] > 50) & (data_btts['Perc_Over25FT_Away'] > 50)
            ]
        
    # Display the final DataFrame
        if not base_btts.empty:
            # Define columns to display
            columns_to_display = [
                'League', 'Time', 'Round', 'Home', 'Away', 'CV_Match_Type', 'Perc_Over25FT_Home', 'Perc_Over25FT_Away', 
                'Perc_BTTS_Yes_FT_Home', 'Perc_BTTS_Yes_FT_Away' ]
            st.dataframe(base_btts[columns_to_display], use_container_width=True, hide_index=True)
        else:
            st.warning("No games found with the specified criteria.")
    else:
        st.info("Data is empty.")