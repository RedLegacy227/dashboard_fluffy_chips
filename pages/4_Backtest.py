import pandas as pd
import numpy as np
import streamlit as st
from PIL import Image
import os
import base64
import requests
from datetime import datetime
from auth import logout
from ui_helpers import add_logout_button  # ✅ Importa a função para evitar duplicação
from sidebar_menu import show_sidebar  # ✅ Importa o menu lateral dinâmico

# Streamlit App Title and Headers
st.set_page_config(page_title="BackTest - Fluffy Chips", page_icon="📈")
# Exibir a barra lateral com páginas dinâmicas
show_sidebar()
st.title("📈 BackTest - Fluffy Chips")
st.subheader('The place where you can do Backtest of your Strategies!!!')
st.divider()
st.subheader('_Sector Under Contrution_')

# Display Image
image_path = os.path.join(os.getcwd(), 'static', 'backtest.png')
if os.path.exists(image_path):
    st.image(image_path, use_container_width=True)
else:
    st.warning("Image not found. Please check the file path.")

st.divider()
# Redirect to login page if the user is not logged in
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.switch_page("Login.py")  # Redirect to login page
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

# Adiciona o botão de logout apenas uma vez
add_logout_button()