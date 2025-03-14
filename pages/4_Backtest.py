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

# URLs for CSV Files
github_base_url = "https://raw.githubusercontent.com/RedLegacy227/jogos_do_dia_com_variaveis/main/"
historical_data_url = "https://raw.githubusercontent.com/RedLegacy227/main_data_base/main/df_base_original.csv"

# Get the current date and format it
current_date = datetime.now()
formatted_date = current_date.strftime('%Y-%m-%d')

# Construct the CSV File URL
csv_file_name = f'df_jogos_do_dia_{formatted_date}.csv'
csv_file_url = github_base_url + csv_file_name

# Load the CSV file
try:
    data = pd.read_csv(csv_file_url)
except Exception as e:
    st.error(f"Error loading {csv_file_url}: {e}")
    data = pd.DataFrame()

if not data.empty:
    # Filter data based on given conditions
    filtered_data = data[
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

    # Load historical data
    try:
        historical_data = pd.read_csv(historical_data_url)
    except Exception as e:
        st.error(f"Error loading historical data: {e}")
        historical_data = pd.DataFrame()

    if not historical_data.empty:
        # Check for games with 2 or more goals
        filtered_data = filtered_data.merge(historical_data, on="game_id")  # Adjust merge key as needed
        filtered_data["Profit"] = np.where(
            (filtered_data["FT_Goals_H"] + filtered_data["FT_Goals_A"]) >= 2,
            filtered_data["FT_Odd_Over15"] - 1,
            -1
        )

        # Plot accumulated profit
        def plot_profit_acu(dataframe, title_text):
            dataframe['Profit_acu'] = dataframe.Profit.cumsum()
            dataframe['Investimento'] = 1
            n_apostas = dataframe.shape[0]
            profit = round(dataframe.Profit_acu.tail(1).item(), 2)
            dataframe['Investimento_acu'] = dataframe.Investimento.cumsum()
            ROI = round(((dataframe.Profit_acu.tail(1) / dataframe.Investimento_acu.tail(1)) * 100).item(), 2)
            drawdown = dataframe['Profit_acu'] - dataframe['Profit_acu'].cummax()
            drawdown_maximo = round(drawdown.min(), 2)
            winrate_medio = round((dataframe['Profit'] > 0).mean() * 100, 2)
            desvio_padrao = round(dataframe['Profit'].std(), 2)

            ax = dataframe.Profit_acu.plot(title=title_text, xlabel='Entradas', ylabel='Stakes')
            ax.set_title(title_text)
            ax.set_xlabel('Entradas')
            ax.set_ylabel('Stakes')

            print("Metodo:", title_text)
            print("Profit:", profit, "stakes em", n_apostas, "jogos")
            print("ROI:", ROI, "%")
            print("Drawdown Maximo Acumulado:", drawdown_maximo)
            print("Winrate Medio:", winrate_medio, "%")
            print("Desvio Padrao:", desvio_padrao)
            print("")

            plt.show()

        plot_profit_acu(filtered_data, "Profit Acumulado - Estratégia Over 1.5 FT")
    else:
        st.warning("Historical data is empty. Cannot proceed with profit calculation.")
else:
    st.warning("No data loaded. Cannot proceed with filtering and profit calculation.")