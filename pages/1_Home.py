import pandas as pd
import streamlit as st
from PIL import Image
import requests
import os
from datetime import datetime
from auth import logout
from sidebar_menu import show_role_features


st.set_page_config(page_title="Home - Fluffy Chips Web Analyser", page_icon="🏠")
# ✅ Show role-based features in the sidebar
show_role_features()
st.title("🏠 Home - Fluffy Chips")
st.subheader('The place where you can Analyse Football Matches!!!')
st.divider()

# Load image properly
st.image("static/tatics.jpg")  # ✅ Fixed image path
st.divider()

# Redirect to login page if the user is not logged in
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.switch_page("Login.py")  # ✅ Redirect to login page

# Welcome message
st.subheader('_Games Of The Day_')
st.write(f"Welcome, **{st.session_state['username']}**!")
st.write(f"Your role: **{st.session_state['role']}**")


# URL base for GitHub CSV files
github_base_url = "https://raw.githubusercontent.com/RedLegacy227/jogos_do_dia_sem_variaveis/main/"

# Choose a date
selected_date = st.date_input("Select a date:", value=datetime.today())
formatted_date = selected_date.strftime("%Y-%m-%d")

# Construct the CSV URL
csv_file_name = f'jogos_do_dia_{formatted_date}.csv'
csv_file_url = github_base_url + csv_file_name

# Load CSV file
try:
    response = requests.get(csv_file_url)

    if response.status_code == 200:
        # Load CSV into DataFrame
        data = pd.read_csv(csv_file_url)
        
        # Remove irrelevant columns
        columns_to_remove = ['Unnamed: 0.1', 'Unnamed: 0', 'Id']
        filtered_data = data.drop(columns=[col for col in columns_to_remove if col in data.columns], errors='ignore')
        
        # Display DataFrame
        if not filtered_data.empty:
            st.write(f"Matches Available for {formatted_date}:")
            st.dataframe(filtered_data)
        else:
            st.warning("No data available after filtering.")
    else:
        st.warning(f"No matches found for the selected date: {formatted_date}.")
except Exception as e:
    st.error(f"Error loading file: {e}")
