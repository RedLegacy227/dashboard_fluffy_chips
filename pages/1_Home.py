import pandas as pd
import streamlit as st
from PIL import Image
import base64
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
from datetime import datetime
import requests
from auth import logout

st.title('_Fluffy Chips Web Analyzer_')
st.subheader('The place where you can Analyse Football Matches!!!')
st.divider()
st.image(os.path.join(os.getcwd(), 'static', 'tatics.jpg'))
st.divider()
# Redirect to login page if the user is not logged in
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.switch_page("1_Home.py")  # Redirect to login page
st.subheader('_Games Of The Day_')
st.write(f"Welcome, **{st.session_state['username']}**!")
st.write(f"Your role: **{st.session_state['role']}**")
# Features based on roles
if st.session_state["role"] == "Admin":
    st.subheader("🔧 Admin Features")
    st.write("- Manage users")
    if st.button("Go to Admin Panel"):
        st.switch_page("admin.py")

elif st.session_state["role"] == "Editor":
    st.subheader("📝 Editor Features")
    st.write("- Edit and manage content")

elif st.session_state["role"] == "Viewer":
    st.subheader("👀 Viewer Features")
    st.write("- View analytics and reports")

# Logout button
st.sidebar.button("🚪 Logout", on_click=logout)
# URL base do GitHub para os arquivos CSV
github_base_url = "https://raw.githubusercontent.com/RedLegacy227/jogos_do_dia_sem_variaveis/main/"
# Escolher uma data
selected_date = st.date_input("Select a date:", value=datetime.today())
formatted_date = selected_date.strftime("%Y-%m-%d")
# Construir a URL do arquivo baseado na data
csv_file_name = f'jogos_do_dia_{formatted_date}.csv'
csv_file_url = github_base_url + csv_file_name
# Tentar carregar o arquivo
try:
    response = requests.get(csv_file_url)

    if response.status_code == 200:
        # Carregar o CSV em um DataFrame
        data = pd.read_csv(csv_file_url)
        
        # Lista de colunas irrelevantes a serem removidas
        columns_to_remove = ['Unnamed: 0.1', 'Unnamed: 0', 'Id']  # Colunas especificadas para remoção
        filtered_data = data.drop(columns=[col for col in columns_to_remove if col in data.columns], errors='ignore')
        
        # Mostrar o DataFrame filtrado
        if not filtered_data.empty:
            st.write(f"Matches Available for {formatted_date}:")
            st.dataframe(filtered_data)
        else:
            st.warning("No data available after filtering.")
    else:
        st.warning(f"No matches found for the selected date: {formatted_date}.")
except Exception as e:
    st.error(f"Error loading file: {e}")

