import streamlit as st
import hashlib
from database import get_users_collection

# Function to verify login from MongoDB
def verify_login(username, password):
    users_collection = get_users_collection()
    
    # Generate hashed password
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    # Find user in MongoDB collection
    user = users_collection.find_one({"username": username, "password": hashed_password})
    
    return user is not None  # Return True if user exists

# Login screen
def login():
    st.title("🔒 Login - Fluffy Chips Web Analyzer")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if verify_login(username, password):
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.success(f"Welcome, {username}!")
            
            # Redirect to Home_1.py
            st.session_state["redirect_to_Home_1"] = True
            st.experimental_rerun()
        else:
            st.error("Incorrect username or password.")

# Logout function
def logout():
    st.session_state["logged_in"] = False
    st.session_state["username"] = None
    st.session_state["redirect_to_Home_1"] = False
    st.experimental_rerun()

# Admin-only function to add users
def add_user(username, password):
    users_collection = get_users_collection()
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    # Check if user already exists
    if users_collection.find_one({"username": username}):
        st.warning(f"User '{username}' already exists.")
    else:
        users_collection.insert_one({"username": username, "password": hashed_password, "role": "user"})
        st.success(f"User '{username}' added successfully.")
