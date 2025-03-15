import pandas as pd
import numpy as np
import streamlit as st
from PIL import Image
import os
import requests
from datetime import datetime
from auth import logout
from sidebar_menu import show_role_features
import matplotlib.pyplot as plt

# Streamlit App Title and Headers
st.set_page_config(page_title="BackTest - Fluffy Chips Web Analyser", page_icon="📈", layout="wide")
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.switch_page("Login.py")  # Redireciona para a página de login
# ✅ Show role-based features in the sidebar
show_role_features()
st.title("📈 BackTest - Fluffy Chips")
st.subheader('The place where you can do Backtest of your Strategies!!!')
st.write(f"Welcome, **{st.session_state['username']}**!")
st.write(f"Your role: **{st.session_state['role']}**")
st.divider()
st.subheader('_Sector Under Contrution_')

# Display Image
image_path = os.path.join(os.getcwd(), 'static', 'backtest.png')
if os.path.exists(image_path):
    st.image(image_path, use_container_width=True)
else:
    st.warning("Image not found. Please check the file path.")

st.divider()

def drop_reset_index(df):
    df = df.dropna()
    df = df.reset_index(drop=True)
    df.index += 1
    return df

def plot_profit_acu(dataframe, title_text):
    dataframe['Profit_acu'] = dataframe.Profit.cumsum()
    n_apostas = dataframe.shape[0]
    profit = round(dataframe.Profit_acu.tail(1).item(), 2)
    ROI = round((dataframe.Profit_acu.tail(1) / n_apostas * 100).item(), 2)
    drawdown = dataframe['Profit_acu'] - dataframe['Profit_acu'].cummax()
    drawdown_maximo = round(drawdown.min(), 2)
    winrate_medio = round((dataframe['Profit'] > 0).mean() * 100, 2)
    desvio_padrao = round(dataframe['Profit'].std(), 2)
    dataframe.Profit_acu.plot(title=title_text, xlabel='Entradas', ylabel='Stakes')
    print("Metodo:",title_text)
    print("Profit:", profit, "stakes em", n_apostas, "jogos")
    print("ROI:", ROI, "%")
    print("Drawdown Maximo Acumulado:", drawdown_maximo)
    print("Winrate Medio:", winrate_medio, "%")
    print("Desvio Padrao:", desvio_padrao)
    print("")

# URLs for CSV Files
historical_data_url = "https://raw.githubusercontent.com/RedLegacy227/main_data_base/main/df_base_original.csv"
    
# Select Date
selected_date = st.date_input("Select a date:", value=datetime.today())
formatted_date = selected_date.strftime("%Y-%m-%d")

@st.cache_data(ttl=0)
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

df_base0 = load_data(historical_data_url)
st.write(df_base0)
df_base = df_base0.Date < str(selected_date)
st.write(df_base)
if df_base is not None:
    st.success("Historical Data loaded successfully!")
#Odds Regression to find Double Chance Odds or Lay Odds
df_base['Lay_Away'] = 0.301 * df_base['FT_Odd_H'] + 0.642
df_base['Lay_Away'] = df_base['Lay_Away'].round(2)
df_base['Lay_Home'] = 0.309 * df_base['FT_Odd_A'] + 0.609
df_base['Lay_Home'] = df_base['Lay_Home'].round(2)

#Probabilities
df_base['p_H'] = (1 / df_base['FT_Odd_H']).round(4)
df_base['p_D'] = (1 / df_base['FT_Odd_D']).round(4)
df_base['p_A'] = (1 / df_base['FT_Odd_A']).round(4)
df_base['p_Over_05_HT'] = (1 / df_base['HT_Odd_Over05']).round(4)
df_base['p_Under_05_HT'] = (1 / df_base['HT_Odd_Under05']).round(4)
df_base['p_Over_05_FT'] = (1 / df_base['FT_Odd_Over05']).round(4)
df_base['p_Under_05_FT'] = (1 / df_base['FT_Odd_Under05']).round(4)
df_base['p_Over_15_FT'] = (1 / df_base['FT_Odd_Over15']).round(4)
df_base['p_Under_15_FT'] = (1 / df_base['FT_Odd_Under15']).round(4)
df_base['p_Over_25_FT'] = (1 / df_base['FT_Odd_Over25']).round(4)
df_base['p_Under_25_FT'] = (1 / df_base['FT_Odd_Under25']).round(4)
df_base['p_BTTS_Yes_FT'] = (1 / df_base['Odd_BTTS_Yes']).round(4)
df_base['p_BTTS_No_FT'] = (1 / df_base['Odd_BTTS_No']).round(4)

#Proportion among Probabilities
df_base['H_D'] = (df_base['p_H'] / df_base['p_D']).round(4)
df_base['H_A'] = (df_base['p_H'] / df_base['p_A']).round(4)
df_base['D_H'] = (df_base['p_D'] / df_base['p_H']).round(4)
df_base['D_A'] = (df_base['p_D'] / df_base['p_A']).round(4)
df_base['A_H'] = (df_base['p_A'] / df_base['p_H']).round(4)
df_base['A_D'] = (df_base['p_A'] / df_base['p_D']).round(4)
df_base['Ov_Un'] = (df_base['p_Over_25_FT'] / df_base['p_Under_25_FT']).round(4)
df_base['UN_Ov'] = (df_base['p_Under_25_FT'] / df_base['p_Over_25_FT']).round(4)
df_base['BTTSY_BTTSN'] = (df_base['p_BTTS_Yes_FT'] / df_base['p_BTTS_No_FT']).round(4)
df_base['BTTSN_BTTSY'] = (df_base['p_BTTS_No_FT'] / df_base['p_BTTS_Yes_FT']).round(4)

#Absolute Difference between Probabilities
df_base['DifAbs_HomeAway'] = np.abs(df_base['p_H'] - df_base['p_A']).round(4)
df_base['DifAbs_HomeDraw'] = np.abs(df_base['p_H'] - df_base['p_D']).round(4)
df_base['DifAbs_DrawAway'] = np.abs(df_base['p_D'] - df_base['p_A']).round(4)
df_base['DifAbs_OvUn'] = np.abs(df_base['p_Over_25_FT'] - df_base['p_Under_25_FT']).round(4)
df_base['DifAbs_BTTSYBTTSN'] = np.abs(df_base['p_BTTS_Yes_FT'] - df_base['p_BTTS_No_FT']).round(4)

#Disparity Angle between Probabilities
df_base['Angle_HomeAway'] = np.degrees(np.arctan((df_base['p_A'] - df_base['p_H']) / 2)).round(4)
df_base['Angle_HomeDraw'] = np.degrees(np.arctan((df_base['p_D'] - df_base['p_H']) / 2)).round(4)
df_base['Angle_DrawAway'] = np.degrees(np.arctan((df_base['p_A'] - df_base['p_D']) / 2)).round(4)
df_base['Angle_UnOv'] = np.degrees(np.arctan((df_base['p_Under_25_FT'] - df_base['p_Over_25_FT']) / 2)).round(4)
df_base['Angle_BTTSNBTTSY'] = np.degrees(np.arctan((df_base['p_BTTS_No_FT'] - df_base['p_BTTS_Yes_FT']) / 2)).round(4)

#Percentage Differences between Probabilities
df_base['DifPer_HomeAway'] = (np.abs(df_base['p_H'] - df_base['p_A']) / df_base['p_A']).round(4)
df_base['DifPer_HomeDraw'] = (np.abs(df_base['p_H'] - df_base['p_D']) / df_base['p_D']).round(4)
df_base['DifPer_DrawAway'] = (np.abs(df_base['p_D'] - df_base['p_A']) / df_base['p_A']).round(4)
df_base['DifPer_OvUnUn'] = (np.abs(df_base['p_Over_25_FT'] - df_base['p_Under_25_FT']) / df_base['p_Under_25_FT']).round(4)
df_base['DifPer_BTTSYN_No'] = (np.abs(df_base['p_BTTS_Yes_FT'] - df_base['p_BTTS_No_FT']) / df_base['p_BTTS_No_FT']).round(4)

#Relation between MO and Over/Under Probabilities
df_base['H_Ov'] = (df_base['p_H'] / df_base['p_Over_25_FT']).round(4)
df_base['D_Ov'] = (df_base['p_D'] / df_base['p_Over_25_FT']).round(4)
df_base['A_Ov'] = (df_base['p_A'] / df_base['p_Over_25_FT']).round(4)
df_base['H_Un'] = (df_base['p_H'] / df_base['p_Under_25_FT']).round(4)
df_base['D_Un'] = (df_base['p_D'] / df_base['p_Under_25_FT']).round(4)
df_base['A_Un'] = (df_base['p_A'] / df_base['p_Under_25_FT']).round(4)

#Relation between MO and BTTS Yes and Btts No Probabilities
df_base['H_BTTSY'] = (df_base['p_H'] / df_base['p_BTTS_Yes_FT']).round(4)
df_base['D_BTTSY'] = (df_base['p_D'] / df_base['p_BTTS_Yes_FT']).round(4)
df_base['A_BTTSY'] = (df_base['p_A'] / df_base['p_BTTS_Yes_FT']).round(4)
df_base['H_BTTSN'] = (df_base['p_H'] / df_base['p_BTTS_No_FT']).round(4)
df_base['D_BTTSN'] = (df_base['p_D'] / df_base['p_BTTS_No_FT']).round(4)
df_base['A_BTTSN'] = (df_base['p_A'] / df_base['p_BTTS_No_FT']).round(4)

#Calculate the Coefficient of Variation MO (CV) - 0 to 0.10 Super Balanced Game - 0.11 to 0.30 Balanced game - 0.31 to 1 Unbalanced Game
desvpad_MO = df_base[['p_H', 'p_D', 'p_A']].std(axis=1)
average_MO = df_base[['p_H', 'p_D', 'p_A']].mean(axis=1)
CV_MO = desvpad_MO / average_MO
df_base['CV_MO_FT'] = CV_MO.round(4)

#Calculate the Coefficient of Variation Over/Under (CV) - 0 to 0.10 Super Balanced Game - 0.11 to 0.30 Balanced game - 0.31 to 1 Unbalanced Game
desvpad_OvUn = df_base[['p_Over_25_FT', 'p_Under_25_FT']].std(axis=1)
average_OvUn = df_base[['p_Over_25_FT', 'p_Under_25_FT']].mean(axis=1)
CV_OvUn = desvpad_OvUn / average_OvUn
df_base['CV_OvUn_FT'] = CV_OvUn.round(4)

#Calculate the Coefficient of Variation BTTS Yes/BTTS No (CV) - 0 to 0.10 Super Balanced Game - 0.11 to 0.30 Balanced game - 0.31 to 1 Unbalanced Game
desvpad_BTTS = df_base[['p_BTTS_Yes_FT', 'p_BTTS_No_FT']].std(axis=1)
average_BTTS = df_base[['p_BTTS_Yes_FT', 'p_BTTS_No_FT']].mean(axis=1)
CV_BTTS = desvpad_BTTS / average_BTTS
df_base['CV_BTTS_FT'] = CV_BTTS.round(4)

st.write(df_base)
    
# List of strategies
strategies = [
    'Lay 0 x 1', 'Goleada Home', 'Over 1,5 FT', 'Lay Home', 'Lay Away', 'Under 1,5 FT', 'Back Home', 'Lay 1x1', 'Lay any Other Win Home', 'Lay any Other Win Home','Louro José'
]

# Select strategy
selected_strategy = st.selectbox("Choose a strategy:", strategies)

if selected_strategy == 'Lay 0 x 1':
    st.write("You have selected the 'Lay 0 x 1' strategy.")
    backtest_lay_0x1 = df_base.copy()

    backtest_lay_0x1['Lay_0x1'] = np.where((backtest_lay_0x1['FT_Goals_H'] == 0) & (backtest_lay_0x1['FT_Goals_A'] == 1), 0, 1)
    