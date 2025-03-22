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
    