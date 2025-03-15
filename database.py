from pymongo import MongoClient
import os
import streamlit as st  # Import Streamlit for Secrets

# Get MongoDB URI from Streamlit Secrets or Environment Variables
MONGO_URI = st.secrets["connections"]["MONGO_URI"] if "connections" in st.secrets else os.getenv("MONGO_URI")

# Raise error if MONGO_URI is not set
if not MONGO_URI:
    raise ValueError("❌ MONGO_URI is not set in Streamlit secrets or environment variables.")

# Connect to MongoDB Atlas
def get_database():
    client = MongoClient(MONGO_URI)
    return client["Fluffy_Chips_Web_Analyser"]  # Replace with your actual database name

# Get the users collection
def get_users_collection():
    db = get_database()
    return db["users"]

# Get the users collection
def get_users_collection():
    db = get_database()
    return db["variables_games"]