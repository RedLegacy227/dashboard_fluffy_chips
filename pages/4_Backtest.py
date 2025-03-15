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

df_base = df_base0[df_base0['Date'] < str(selected_date)]

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

#Creating the Final Result Column
def Result_FT(FT_Goals_H, FT_Goals_A):
    if FT_Goals_H > FT_Goals_A:
        return 'H'
    elif FT_Goals_H == FT_Goals_A:
        return 'D'
    else:
        return 'A'

#Creating the Ov or Un Column
def Result_Goals(Total_Goals_FT):
    if Total_Goals_FT > 2:
        return 'Ov'
    else:
        return 'Un'
    
#Creating the BTTS Column
def BTTS(FT_Goals_H, FT_Goals_A):
    if FT_Goals_H > 0 and FT_Goals_A > 0:
        return 'Yes'
    else:
        return 'No'

#Applying functions to the dataframe
df_base['Result_FT'] = df_base.apply(lambda row: Result_FT(row['FT_Goals_H'], row['FT_Goals_A']), axis=1)
df_base['Result_Goals'] = df_base.apply(lambda row: Result_Goals(row['FT_Goals_H'] + row['FT_Goals_A']), axis=1)
df_base['BTTS_FT'] = df_base.apply(lambda row: BTTS(row['FT_Goals_H'], row['FT_Goals_A']), axis=1)

#PPM
df_base['PPM_Home'] = (df_base['p_H'] * 3) + (df_base['p_D'] * 1).round(4)
df_base['PPM_Away'] = (df_base['p_A'] * 3) + (df_base['p_D'] * 1).round(4)

#Total Goals
df_base["Total_Goals_HT"] = df_base["HT_Goals_H"] + df_base["HT_Goals_A"]

#Goal Difference
df_base['G_Diff_H_HT'] = df_base['HT_Goals_H'] - df_base['HT_Goals_A']
df_base['G_Diff_A_HT'] = df_base['HT_Goals_A'] - df_base['HT_Goals_H']

#Value of Goal Diference
df_base['Value_G_Diff_H_HT'] = (df_base['G_Diff_H_HT'] * df_base['p_A']).round(4)
df_base['Value_G_Diff_A_HT'] = (df_base['G_Diff_A_HT'] * df_base['p_H']).round(4)

#Value of Scored Goals
df_base['Value_G_Scored_H_HT'] = (df_base['HT_Goals_H'] * df_base['p_A']).round(4)
df_base['Value_G_Scored_A_HT'] = (df_base['HT_Goals_A'] * df_base['p_H']).round(4)

#Value of Conceded Goals
df_base['Value_G_Conceded_H_HT'] = (df_base['HT_Goals_A'] * df_base['p_A']).round(4)
df_base['Value_G_Conceded_A_HT'] = (df_base['HT_Goals_H'] * df_base['p_H']).round(4)

df_base["ST_Goals_H"] = df_base["FT_Goals_H"] - df_base["HT_Goals_H"]
df_base["ST_Goals_A"] = df_base["FT_Goals_A"] - df_base["HT_Goals_A"]

#Total Goals
df_base["Total_Goals_ST"] = df_base["ST_Goals_H"] + df_base["ST_Goals_A"]

#Goal Difference
df_base['G_Diff_H_ST'] = df_base['ST_Goals_H'] - df_base['ST_Goals_A']
df_base['G_Diff_A_ST'] = df_base['ST_Goals_A'] - df_base['ST_Goals_H']

#Value of Goal Diference
df_base['Value_G_Diff_H_ST'] = (df_base['G_Diff_H_ST'] * df_base['p_A']).round(4)
df_base['Value_G_Diff_A_ST'] = (df_base['G_Diff_A_ST'] * df_base['p_H']).round(4)

#Value of Scored Goals
df_base['Value_G_Scored_H_ST'] = (df_base['ST_Goals_H'] * df_base['p_A']).round(4)
df_base['Value_G_Scored_A_ST'] = (df_base['ST_Goals_A'] * df_base['p_H']).round(4)

#Value of Conceded Goals
df_base['Value_G_Conceded_H_ST'] = (df_base['ST_Goals_A'] * df_base['p_A']).round(4)
df_base['Value_G_Conceded_A_ST'] = (df_base['ST_Goals_H'] * df_base['p_H']).round(4)

#Total Goals
df_base["Total_Goals_FT"] = df_base["FT_Goals_H"] + df_base["FT_Goals_A"]

#Creating the Calculation of Points
df_base['Points_H'] = np.where(df_base['FT_Goals_H'] >  df_base['FT_Goals_A'], 3, np.where(df_base['FT_Goals_H'] == df_base['FT_Goals_A'], 1, 0))
df_base['Points_A'] = np.where(df_base['FT_Goals_A'] > df_base['FT_Goals_H'], 3, np.where(df_base['FT_Goals_H'] == df_base['FT_Goals_A'], 1, 0))

#Points Value
df_base['Value_Points_H'] = (df_base['Points_H'] * df_base['p_A']).round(4)
df_base['Value_Points_A'] = (df_base['Points_A'] * df_base['p_H']).round(4)

#Goal Difference
df_base['G_Diff_H_FT'] = df_base['FT_Goals_H'] - df_base['FT_Goals_A']
df_base['G_Diff_A_FT'] = df_base['FT_Goals_A'] - df_base['FT_Goals_H']

#Value of Goal Diference
df_base['Value_G_Diff_H_FT'] = (df_base['G_Diff_H_FT'] * df_base['p_A']).round(4)
df_base['Value_G_Diff_A_FT'] = (df_base['G_Diff_A_FT'] * df_base['p_H']).round(4)

#Value of Scored Goals
df_base['Value_G_Scored_H_FT'] = (df_base['FT_Goals_H'] * df_base['p_A']).round(4)
df_base['Value_G_Scored_A_FT'] = (df_base['FT_Goals_A'] * df_base['p_H']).round(4)

#Value of Conceded Goals
df_base['Value_G_Conceded_H_FT'] = (df_base['FT_Goals_A'] * df_base['p_A']).round(4)
df_base['Value_G_Conceded_A_FT'] = (df_base['FT_Goals_H'] * df_base['p_H']).round(4)

#Cost Of Goal Scored 1.0
df_base['CG_G_Scored_H_01'] = (df_base['FT_Goals_H'] / df_base['p_H']).round(4)
df_base['CG_G_Scored_A_01'] = (df_base['FT_Goals_A'] / df_base['p_A']).round(4)

#Cost Of Goal Conceded 1.0
df_base['CG_G_Conceded_H_01'] = (df_base['FT_Goals_A'] / df_base['p_H']).round(4)
df_base['CG_G_Conceded_A_01'] = (df_base['FT_Goals_H'] / df_base['p_A']).round(4)

#Cost Of Goal Scored 2.0
df_base['CG_G_Scored_H_02'] = ((df_base['FT_Goals_H'] / 2) + (df_base['p_H'] / 2)).round(4)
df_base['CG_G_Scored_A_02'] = ((df_base['FT_Goals_A'] / 2) + (df_base['p_A'] / 2)).round(4)

#Cost Of Goal Conceded 2.0
df_base['CG_G_Conceded_H_02'] = ((df_base['FT_Goals_A'] / 2) + (df_base['p_H'] / 2)).round(4)
df_base['CG_G_Conceded_A_02'] = ((df_base['FT_Goals_H'] / 2) + (df_base['p_A'] / 2)).round(4)

#Shots in Favor
df_base['Shots_H'] = (df_base['Shots off Goal_Home'])
df_base['Shots_A'] = (df_base['Shots off Goal_Away'])

#Shots Against Value
df_base['Shots_Against_H'] = (df_base['Shots off Goal_Away'])
df_base['Shots_Against_A'] = (df_base['Shots off Goal_Home'])

#Shots on Target in Favor Value
df_base['Shots_OT_H'] = (df_base['Shots on Goal_Home'])
df_base['Shots_OT_A'] = (df_base['Shots on Goal_Away'])

#Shots on Target Against Value
df_base['Shots_OT_Against_H'] = (df_base['Shots on Goal_Away'])
df_base['Shots_OT_Against_A'] = (df_base['Shots on Goal_Home'])

#Shots in Favour per Goal
df_base['Shots_per_Goal_H'] = (df_base['Shots off Goal_Home'] / df_base['FT_Goals_H'].replace(0, float('nan')))
df_base['Shots_per_Goal_A'] = (df_base['Shots off Goal_Away'] / df_base['FT_Goals_A'].replace(0, float('nan'))).round(4)

#Shots Against per Goal
df_base['Shots_per_Goal_Against_H'] = (df_base['Shots off Goal_Away'] / df_base['FT_Goals_A'].replace(0, float('nan'))).round(4)
df_base['Shots_per_Goal_Against_A'] = (df_base['Shots off Goal_Home'] / df_base['FT_Goals_H'].replace(0, float('nan'))).round(4)

#Shots on Target in Favor per Goal
df_base['Shots_OT_per_Goal_H'] = (df_base['Shots on Goal_Home'] / df_base['FT_Goals_H'].replace(0, float('nan'))).round(4)
df_base['Shots_OT_per_Goal_A'] = (df_base['Shots on Goal_Away'] / df_base['FT_Goals_A'].replace(0, float('nan'))).round(4)

#Shots on Target Against per Goal
df_base['Shots_OT_per_Goal_Against_H'] = (df_base['Shots on Goal_Away'] / df_base['FT_Goals_A'].replace(0, float('nan'))).round(4).fillna(0)
df_base['Shots_OT_per_Goal_Against_A'] = (df_base['Shots on Goal_Home'] / df_base['FT_Goals_H'].replace(0, float('nan'))).round(4).fillna(0)

#Goal Attempts in Favor Value
df_base['Goal_Attempt_H'] = (df_base['Goal Attempts_Home'])
df_base['Goal_Attempt_A'] = (df_base['Goal Attempts_Away'])

#Goal Attempts Against Value
df_base['Goal_Attempt_Against_H'] = (df_base['Goal Attempts_Away'])
df_base['Goal_Attempt_Against_A'] = (df_base['Goal Attempts_Home'])

#Goal Attempts in Favor per Goal
df_base['Goal_Attempts_per_Goal_H'] = (df_base['Goal Attempts_Home'] / df_base['FT_Goals_H'].replace(0, float('nan'))).round(4)
df_base['Goal_Attempts_per_Goal_A'] = (df_base['Goal Attempts_Away'] / df_base['FT_Goals_A'].replace(0, float('nan'))).round(4)

#Goal Attempts Against per Goal
df_base['Goal_Attempts_per_Goal_Against_H'] = (df_base['Goal Attempts_Away'] / df_base['FT_Goals_A'].replace(0, float('nan'))).round(4)
df_base['Goal_Attempts_per_Goal_Against_A'] = (df_base['Goal Attempts_Home'] / df_base['FT_Goals_H'].replace(0, float('nan'))).round(4)

#Ball Possession in Favor Value
df_base['Ball_Possession_H'] = (df_base['Ball Possession_Home'])
df_base['Ball_Possession_A'] = (df_base['Ball Possession_Away'])

#Ball Possession Against Value
df_base['Ball_Possession_Against_H'] = (df_base['Ball Possession_Away'])
df_base['Ball_Possession_Against_A'] = (df_base['Ball Possession_Home'])

#Corners in Favor Value
df_base['Corners_H'] = (df_base['Corner Kicks_Home'])
df_base['Corners_A'] = (df_base['Corner Kicks_Away'])

#Corners Against Value
df_base['Corners_Against_H'] = (df_base['Corner Kicks_Away'])
df_base['Corners_Against_A'] = (df_base['Corner Kicks_Home'])

#Yellow Cards 
df_base['Yellow_Cards_H'] = (df_base['Yellow Cards_Home'])
df_base['Yellow_Cards_A'] = (df_base['Yellow Cards_Away'])

#Yellow Cards 
df_base['Red_Cards_H'] = (df_base['Red Cards_Home'])
df_base['Red_Cards_A'] = (df_base['Red Cards_Away'])

#RPS Match Odds - Lower than 0,33 Tendency - Above Asymmetry
df_base['RPS_MO'] = np.where(df_base['Result_FT'] == "H", 0.5 * ((1 / df_base['FT_Odd_H'] - 1)**2 + (1 / df_base['FT_Odd_D'])**2 + (1 / df_base['FT_Odd_A'])**2), np.where(df_base['Result_FT'] == "D", 0.5 * ((1 / df_base['FT_Odd_H'])**2 + (1 / df_base['FT_Odd_D'] - 1)**2 + (1 / df_base['FT_Odd_A'])**2), 0.5 * ((1 / df_base['FT_Odd_H'])**2 + (1 / df_base['FT_Odd_D'])**2 + (1 / df_base['FT_Odd_A'] - 1)**2)))
df_base['RPS_MO'] = df_base['RPS_MO'].round(4)

#RPS Over/Under - Lower than 0,50 Tendency - Above Asymmetry
df_base['RPS_OV_UN'] = np.where(df_base['Result_Goals'] == "OV",(1 / df_base['FT_Odd_Over25'] - 1)**2 + (1 / df_base['FT_Odd_Under25'])**2,(1 / df_base['FT_Odd_Over25'])**2 + (1 / df_base['FT_Odd_Under25'] - 1)**2)
df_base['RPS_OV_UN'] = df_base['RPS_OV_UN'].round(4)

#RPS BTTS - Lower than 0,50 Tendency - Above Asymmetry
df_base['RPS_BTTS'] = np.where(df_base['BTTS_FT'] == "Yes",(1 / df_base['Odd_BTTS_Yes'] - 1)**2 + (1 / df_base['Odd_BTTS_No'])**2,(1 / df_base['Odd_BTTS_Yes'])**2 + (1 / df_base['Odd_BTTS_No'] - 1)**2)
df_base['RPS_BTTS'] = df_base['RPS_BTTS'].round(4)

# Define weights
weights = {
    "w_saldo_golos": 30,       # Goal difference (most important)
    "w_shots_on_goal": 20,     # Shots on target
    "w_shots_off_goal": 15,    # Shots off target
    "w_points": 10,            # Points
    "w_corners": 7,            # Corners
    "w_possession": 5,         # Possession
    "penalty_no_goals": 50,    # Penalty for not scoring
    "penalty_draw_goals": 60,  # Penalty for a draw with goals
    "penalty_draw_no_goals": 70,  # Penalty for a goalless draw
    "penalty_advantage_loss_to_draw": 80,  # Penalty for losing a lead to a draw
    "penalty_advantage_loss_to_lost": 120,  # Penalty for losing a lead to a loss
    "recover_advantage_loss_to_draw": 75,  # Reward for recovering from a loss to a draw
    "recover_advantage_loss_to_win": 115,  # Reward for recovering from a loss to a win
}

def calculate_penalties(df, weights):
    """
    Calculate penalties and rewards for home and away teams.
    """
    # Penalty for not scoring
    df['Goal_Penalty_Home'] = np.where(df['FT_Goals_H'] == 0, weights['penalty_no_goals'], 0)
    df['Goal_Penalty_Away'] = np.where(df['FT_Goals_A'] == 0, weights['penalty_no_goals'], 0)

    # Penalty for draws
    df['Draw_Penalty_Home'] = np.where(
        df['FT_Goals_H'] == df['FT_Goals_A'],
        np.where(df['FT_Goals_H'] > 0, weights['penalty_draw_goals'], weights['penalty_draw_no_goals']),
        0
    )
    df['Draw_Penalty_Away'] = df['Draw_Penalty_Home']

    # Penalty for losing a lead to a draw
    df['Advantage_Loss_Penalty_Home_Draw'] = np.where(
        (df['HT_Goals_H'] > df['HT_Goals_A']) & (df['FT_Goals_H'] == df['FT_Goals_A']),
        (df['HT_Goals_H'] - df['HT_Goals_A']) * weights['penalty_advantage_loss_to_draw'],
        0
    )

    # Penalty for losing a lead to a loss
    df['Advantage_Loss_Penalty_Home_Lost'] = np.where(
        (df['HT_Goals_H'] > df['HT_Goals_A']) & (df['FT_Goals_H'] < df['FT_Goals_A']),
        (df['HT_Goals_H'] - df['HT_Goals_A']) * weights['penalty_advantage_loss_to_lost'],
        0
    )

    # Reward for recovering from a disadvantage to a draw
    df['Disadvantage_Recovery_Away_Draw'] = df['Advantage_Loss_Penalty_Home_Draw'] * (
        weights['recover_advantage_loss_to_draw'] / weights['penalty_advantage_loss_to_draw']
    )

    # Reward for recovering from a disadvantage to a win
    df['Disadvantage_Recovery_Away_Win'] = df['Advantage_Loss_Penalty_Home_Lost'] * (
        weights['recover_advantage_loss_to_win'] / weights['penalty_advantage_loss_to_lost']
    )

    # Reward for a comeback (Home and Away)
    df['Reviravolta_Home'] = np.where(
        (df['HT_Goals_H'] < df['HT_Goals_A']) & (df['FT_Goals_H'] > df['FT_Goals_A']),
        (df['HT_Goals_A'] - df['HT_Goals_H']) * weights['recover_advantage_loss_to_win'],
        0
    )
    df['Reviravolta_Away'] = np.where(
        (df['HT_Goals_A'] < df['HT_Goals_H']) & (df['FT_Goals_A'] > df['FT_Goals_H']),
        (df['HT_Goals_H'] - df['HT_Goals_A']) * weights['recover_advantage_loss_to_win'],
        0
    )

    return df

def calculate_power_ranking(df, weights):
    """
    Calculate Power Ranking for home and away teams.
    """
    # Home Power Ranking
    df['Power_Ranking_Home'] = (
        100 +
        weights['w_saldo_golos'] * df['Value_G_Diff_H_FT'] +
        weights['w_shots_on_goal'] * (df['Shots_OT_H'] - df['Shots_OT_Against_H']) +
        weights['w_shots_off_goal'] * (df['Shots_H'] - df['Shots_Against_H']) +
        weights['w_points'] * df['Value_Points_H'] +
        weights['w_corners'] * (df['Corners_H'] - df['Corners_Against_H']) +
        weights['w_possession'] * (df['Ball_Possession_H'] - df['Ball_Possession_Against_H']) -
        df['Goal_Penalty_Home'] -
        df['Draw_Penalty_Home'] -
        df['Advantage_Loss_Penalty_Home_Draw'] -
        df['Advantage_Loss_Penalty_Home_Lost'] +
        df['Reviravolta_Home']
    )

    # Away Power Ranking
    df['Power_Ranking_Away'] = (
        100 +
        weights['w_saldo_golos'] * df['Value_G_Diff_A_FT'] +
        weights['w_shots_on_goal'] * (df['Shots_OT_A'] - df['Shots_OT_Against_A']) +
        weights['w_shots_off_goal'] * (df['Shots_A'] - df['Shots_Against_A']) +
        weights['w_points'] * df['Value_Points_A'] +
        weights['w_corners'] * (df['Corners_A'] - df['Corners_Against_A']) +
        weights['w_possession'] * (df['Ball_Possession_A'] - df['Ball_Possession_Against_A']) -
        df['Goal_Penalty_Away'] -
        df['Draw_Penalty_Away'] -
        df['Disadvantage_Recovery_Away_Draw'] -
        df['Disadvantage_Recovery_Away_Win'] +
        df['Reviravolta_Away']
    )

    return df

def adjust_rankings(df):
    """
    Adjust and round the final rankings.
    """
    df['Value_Power_Ranking_Home'] = (df['Power_Ranking_Home']).round(4)
    df['Value_Power_Ranking_Away'] = (df['Power_Ranking_Away']).round(4)
    return df

# Main function to execute the pipeline
def calculate_final_rankings(df, weights):
    """
    Calculate final Power Rankings for home and away teams.
    """
    # Check for missing columns
    required_columns = [
        'FT_Goals_H', 'FT_Goals_A', 'HT_Goals_H', 'HT_Goals_A',
        'Value_G_Diff_H_FT', 'Value_G_Diff_A_FT', 'Shots_OT_H', 'Shots_OT_A',
        'Shots_H', 'Shots_A', 'Value_Points_H', 'Value_Points_A',
        'Corners_H', 'Corners_A', 'Ball_Possession_H',
        'Ball_Possession_A', 'p_A', 'p_H'
    ]
    if not all(column in df.columns for column in required_columns):
        raise ValueError("Input DataFrame is missing required columns.")

    # Calculate penalties and rewards
    df = calculate_penalties(df, weights)

    # Calculate Power Rankings
    df = calculate_power_ranking(df, weights)

    # Adjust and round rankings
    df = adjust_rankings(df)

    return df

df_base = calculate_final_rankings(df_base, weights)

st.write(df_base.tail(20))
    
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
    