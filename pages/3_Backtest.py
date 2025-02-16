import pandas as pd
import numpy as np
import streamlit as st
from PIL import Image
import os
import base64
import requests
from datetime import datetime

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