import pandas as pd
import numpy as np
import streamlit as st
from PIL import Image
import os
import base64
import requests
from datetime import datetime
from auth import logout

# Streamlit App Title and Headers
st.title('_Fluffy Chips Web Analyzer_')
st.subheader('The place where you can Analyse Football Matches!!!')
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
    st.switch_page("Home.py")  # Redirect to login page
# Logout button
st.sidebar.button("🚪 Logout", on_click=logout)
# Features based on roles
if st.session_state["role"] == "admin":
    st.subheader("🔧 Admin Features")
    st.write("- Manage users")
    if st.button("Go to Admin Panel"):
        st.switch_page("admin.py")

elif st.session_state["role"] == "editor":
    st.subheader("📝 Editor Features")
    st.write("- Edit and manage content")

elif st.session_state["role"] == "viewer":
    st.subheader("👀 Viewer Features")
    st.write("- View analytics and reports")

# Logout button
st.sidebar.button("🚪 Logout", on_click=logout)