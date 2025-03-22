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
        st.error("No Data Available for the Chosen Date")
        data = None
        data_Ov25_FT = None
        data_btts = None
        lay_home = None
        lay_away = None

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
tabs = ['Back Home', 'Back Away', 'Lay Home', 'Lay Away', 'Over 1,5 FT', 'Under 1,5 FT', 'Over 2,5 FT', ' BTTS', 'Louro José', 'Best Teams']
tab_views = st.tabs(tabs)

with tab_views[0]:
    st.markdown(f'#### Todays Games for Back_Home - Method Automatic Pivot Table ####')

    # List of columns to display
    columns_to_display = [
        'Time', 'League', 'Home', 'Away', 'Round', 'FT_Odd_H', 'FT_Odd_D', 'FT_Odd_A', 'CV_Match_Type', 'Favorite', 'Perc_Home_Win_FT', 'Perc_Draw_Win_H_FT', 'Perc_Draw_Win_A_FT', 'Perc_Away_Win_FT'
    ]

    if data is not None:
        # Create a list to hold all filtered dataframes
        filtered_dataframes = []

        # Apply filters for each league and method
        back_home_Port_01_01_ft_flt = data[
            (data["League"] == 'PORTUGAL - LIGA PORTUGAL') &
            (data["Home_Score_Take"] == 'No') &
            (data["Away_Score_Take"] == 'Yes') &
            (data["Avg_G_Diff_A_FT_Value"] > -0.0900) &
            (data["Avg_G_Diff_A_FT_Value"] < 0.0250)
        ]
        filtered_dataframes.append(back_home_Port_01_01_ft_flt)

        back_home_Port_01_02_ft_flt = data[
            (data["League"] == 'PORTUGAL - LIGA PORTUGAL') &
            (data["Home_Score_Take"] == 'No') &
            (data["Away_Score_Take"] == 'Yes') &
            (data["Poisson_GS_A_2"] > 0.2520) &
            (data["Poisson_GS_A_2"] < 0.2710) &
            (data["Avg_Points_Away_FT"] > 0.9780) &
            (data["Avg_Points_Away_FT"] < 1.6950)
        ]
        filtered_dataframes.append(back_home_Port_01_02_ft_flt)

        back_home_Port_01_03_ft_flt = data[
            (data["League"] == 'PORTUGAL - LIGA PORTUGAL') &
            (data["Home_Score_Take"] == 'No') &
            (data["Away_Score_Take"] == 'Yes') &
            (data["Avg_Points_Away_FT"] > 0.9780) &
            (data["Avg_Points_Away_FT"] < 1.6950) &
            (data["Avg_G_Conceded_A_FT_Value"] > 1.5120) &
            (data["Avg_G_Conceded_A_FT_Value"] < 4.0670)
        ]
        filtered_dataframes.append(back_home_Port_01_03_ft_flt)

        back_home_Port_01_04_ft_flt = data[
            (data["League"] == 'PORTUGAL - LIGA PORTUGAL') &
            (data["DifPer_HomeDraw"] >= 6.46) &
            (data["DifPer_HomeDraw"] <= 9.28) &
            (data["Poisson_GS_H_0"] >= 0.50) &
            (data["Poisson_GS_H_0"] <= 0.55) &
            (data["H_BTTSN"] >= 1.12) &
            (data["H_BTTSN"] <= 1.22) &
            (data["Poisson_GS_H_2"] >= 0.10) &
            (data["Poisson_GS_H_2"] <= 0.13) &
            (data["Final_Avg_RPS_MO_A"] >= 3.94) & 
            (data["Final_Avg_RPS_MO_A"] <= 4.39)
        ]
        filtered_dataframes.append(back_home_Port_01_04_ft_flt)

        back_home_nacleague_01_01_ft_flt = data[
            (data["League"] == 'EUROPE - UEFA NATIONS LEAGUE') &
            (data["Angle_HomeAway"] >= -14.63) &
            (data["Angle_HomeAway"] <= -10.23) &
            (data["A_Un"] >= 0.20) &
            (data["A_Un"] <= 0.33) &
            (data["DifAbs_HomeDraw"] >= 0.28) &
            (data["DifAbs_HomeDraw"] <= 0.40) &
            (data["D_A"] >= 1.57) &
            (data["D_A"] <= 1.92) 
        ]
        filtered_dataframes.append(back_home_nacleague_01_01_ft_flt)
        
        back_home_argentina_01_01_ft_flt = data[
            (data["League"] == 'ARGENTINA - TORNEO BETANO') &
            (data["Final_Avg_G_Conceded_H_ST"] >= 0.04) &
            (data["Final_Avg_G_Conceded_H_ST"] <= 0.33) &
            (data["Final_Avg_RPS_BTTS_A"] >= 7.54) &
            (data["Final_Avg_RPS_BTTS_A"] <= 12.63) &
            (data["H_BTTSY"] >= 0.56) &
            (data["H_BTTSY"] <= 0.76) &
            (data["BTTSY_BTTSN"] >= 0.60) &
            (data["BTTSY_BTTSN"] <= 0.70) 
        ]
        filtered_dataframes.append(back_home_argentina_01_01_ft_flt)
        
        back_home_austria02_ft_flt = data[
            (data["League"] == 'AUSTRIA - 2. LIGA') &
            (data["DifAbs_HomeDraw"] >= 0.14) &
            (data["DifAbs_HomeDraw"] <= 0.19) &
            (data["D_Ov"] >= 0.51) &
            (data["D_Ov"] <= 0.59)  
        ]
        filtered_dataframes.append(back_home_austria02_ft_flt)
        
        # Concatenate all filtered dataframes
        df_ligas_back_home = pd.concat(filtered_dataframes, ignore_index=True)

        # Sort by 'Time' and select only the desired columns
        df_ligas_back_home = df_ligas_back_home[columns_to_display].sort_values(by='Time', ascending=True)

        # Display the final dataframe
        if not df_ligas_back_home.empty:
            st.dataframe(df_ligas_back_home, use_container_width=True, hide_index=True)
        else:
            st.warning("No games found with the specified criteria.")
    else:
        st.error("No Data Available for the Chosen Date")
        
with tab_views[1]:
    st.markdown(f'#### Back Away - Method Automatic Pivot Table ####')

    # List of columns to display
    columns_to_display = [
        'Time', 'League', 'Home', 'Away', 'Round', 'FT_Odd_H', 'FT_Odd_D', 'FT_Odd_A', 'CV_Match_Type', 'Favorite', 'Perc_Home_Win_FT', 'Perc_Draw_Win_H_FT', 'Perc_Draw_Win_A_FT', 'Perc_Away_Win_FT'
    ]

    if data is not None:
        # Create a list to hold all filtered dataframes
        filtered_dataframes = []

        # Apply filters for each league and method
        back_away_argentina01_ft_flt = data[
            (data["League"] == 'ARGENTINA - TORNEO BETANO') &
            (data["Poisson_GS_A_1"] >= 0.20) &
            (data["Poisson_GS_A_1"] <= 0.27)
        ]
        filtered_dataframes.append(back_away_argentina01_ft_flt)

        back_away_portugal01_ft_flt = data[
            (data["League"] == 'PORTUGAL - LIGA PORTUGAL') &
            (data["DifAbs_DrawAway"] >= 0.17) &
            (data["DifAbs_DrawAway"] <= 0.25)
        ]
        filtered_dataframes.append(back_away_portugal01_ft_flt)
        
        back_away_austria02_ft_flt = data[
            (data["League"] == 'AUSTRIA - 2. LIGA') &
            (data["D_A"] >= 0.92) &
            (data["D_A"] <= 1.17) &
            (data["Final_Avg_G_Conceded_A_ST"] >= 0.03) &
            (data["Final_Avg_G_Conceded_A_ST"] <= 0.30) &
            (data["DifPer_HomeAway"] >= 0.58) &
            (data["DifPer_HomeAway"] <= 1.71)  
        ]
        filtered_dataframes.append(back_away_austria02_ft_flt)
        
        back_away_austria01_ft_flt = data[
            (data["League"] == 'AUSTRIA - BUNDESLIGA') &
            (data["Poisson_GM_H_0"] >= 0.20) &
            (data["Poisson_GM_H_0"] <= 0.56) 
        ]
        filtered_dataframes.append(back_away_austria01_ft_flt)
        
        # Concatenate all filtered dataframes
        df_ligas_back_away = pd.concat(filtered_dataframes, ignore_index=True)

        # Sort by 'Time' and select only the desired columns
        df_ligas_back_away = df_ligas_back_away[columns_to_display].sort_values(by='Time', ascending=True)

        # Display the final dataframe
        if not df_ligas_back_away.empty:
            st.dataframe(df_ligas_back_away, use_container_width=True, hide_index=True)
        else:
            st.warning("No games found with the specified criteria.")
    else:
        st.error("No Data Available for the Chosen Date")
        
with tab_views[2]:
    st.markdown(f"#### Todays Games for Lay Home ####")
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
                st.warning("No games found with the specified criteria.")
        except Exception as e:
            st.error(f"Erro ao carregar ou processar os dados para Back Home: {e}")
    else:
        st.error("No Data Available for the Chosen Date")

with tab_views[3]:
    st.markdown(f"#### Todays Games for Lay Away ####")
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
                st.warning("No games found with the specified criteria.")
        except Exception as e:
            st.error(f"No Data Available for the Chosen Date: {e}")
    else:
        st.error("No Data Available for the Chosen Date")

with tab_views[4]:
    st.markdown(f'#### Todays Games for Over 1,5 FT ####')
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
            st.warning("No games found with the specified criteria.")
    else:
        st.error("No Data Available for the Chosen Date")

with tab_views[5]:
    st.markdown(f'#### Todays Games for Under 1,5 FT ####')
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
            st.warning("No games found with the specified criteria.")
    else:
        st.error("Dados indisponíveis para a data selecionada.")
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
            st.warning("No games found with the specified criteria.")
    else:
        st.error("No Data Available for the Chosen Date")
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
            st.warning("No games found with the specified criteria.")
    else:
        st.error("No Data Available for the Chosen Date")
        
with tab_views[6]:
    st.markdown(f'#### Over 2,5 FT ####')
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
            st.warning("No games found with the specified criteria.")
        
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
            st.warning("No games found with the specified criteria.")
    else:
        st.error("Data is empty.")
        
with tab_views[7]:
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
        st.error("Data is empty.")
        
with tab_views[8]:
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
        st.warning("No games found with the specified criteria.")

with tab_views[9]:
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
            st.warning("No games found with the specified criteria.")
        
        st.markdown('#### Home Scored First and Draw ####')
        if not flt_home_SFD.empty:
            st.dataframe(flt_home_SFD[columns_to_display], use_container_width=True, hide_index=True)
        else:
            st.warning("No games found with the specified criteria.")
        
        st.markdown('#### Home Scored First and Lost ####')
        if not flt_home_SFL.empty:
            st.dataframe(flt_home_SFL[columns_to_display], use_container_width=True, hide_index=True)
        else:
            st.warning("No games found with the specified criteria.")
        
        st.markdown('#### Home Conceded First and Won ####')
        if not flt_home_CFW.empty:
            st.dataframe(flt_home_CFW[columns_to_display], use_container_width=True, hide_index=True)
        else:
            st.warning("No games found with the specified criteria.")
        
        st.markdown('#### Home Conceded First and Draw ####')
        if not flt_home_CFD.empty:
            st.dataframe(flt_home_CFD[columns_to_display], use_container_width=True, hide_index=True)
        else:
            st.warning("No games found with the specified criteria.")
        
        st.markdown('#### Home Conceded First and Lost ####')
        if not flt_home_CFL.empty:
            st.dataframe(flt_home_CFL[columns_to_display], use_container_width=True, hide_index=True)
        else:
            st.warning("No games found with the specified criteria.")
        
        st.markdown('#### Home After winning by one scored the second ####')
        if not flt_home_DilV.empty:
            st.dataframe(flt_home_DilV[columns_to_display], use_container_width=True, hide_index=True)
        else:
            st.warning("No games found with the specified criteria.")
        
        st.markdown('#### Away Scored First and Won ####')
        if not flt_away_SFW.empty:
            st.dataframe(flt_away_SFW[columns_to_display], use_container_width=True, hide_index=True)
        else:
            st.warning("No games found with the specified criteria.")
        
        st.markdown('#### Away Scored First and Draw ####')
        if not flt_away_SFD.empty:
            st.dataframe(flt_away_SFD[columns_to_display], use_container_width=True, hide_index=True)
        else:
            st.warning("No games found with the specified criteria.")
        
        st.markdown('#### Away Scored First and Lost ####')
        if not flt_away_SFL.empty:
            st.dataframe(flt_away_SFL[columns_to_display], use_container_width=True, hide_index=True)
        else:
            st.warning("No games found with the specified criteria.")
        
        st.markdown('#### Away Conceded First and Won ####')
        if not flt_away_CFW.empty:
            st.dataframe(flt_away_CFW[columns_to_display], use_container_width=True, hide_index=True)
        else:
            st.warning("No games found with the specified criteria.")
        
        st.markdown('#### Away Conceded First and Draw ####')
        if not flt_away_CFD.empty:
            st.dataframe(flt_away_CFD[columns_to_display], use_container_width=True, hide_index=True)
        else:
            st.warning("No games found with the specified criteria.")
        
        st.markdown('#### Away Conceded First and Lost ####')
        if not flt_away_CFL.empty:
            st.dataframe(flt_away_CFL[columns_to_display], use_container_width=True, hide_index=True)
        else:
            st.warning("No games found with the specified criteria.")
        
        st.markdown('#### Away After winning by one scored the second ####')
        if not flt_away_DilV.empty:
            st.dataframe(flt_away_DilV[columns_to_display], use_container_width=True, hide_index=True)
        else:
            st.warning("No games found with the specified criteria.")
    else:
        st.error("Data is empty.")
        
