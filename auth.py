import streamlit as st
import hashlib
from database import get_users_collection

# Function to hash values securely
def hash_value(value):
    return hashlib.sha256(value.encode()).hexdigest()

# Function to verify login and fetch user role
def verify_login(username, password):
    users_collection = get_users_collection()
    
    # Generate hashed values
    hashed_username = hash_value(username)
    hashed_password = hash_value(password)
    
    # Find user in MongoDB collection
    user = users_collection.find_one({"username": hashed_username, "password": hashed_password})
    
    if user:
        return user  # Return full user document
    return None  # Return None if no user found

# Login screen
def login():
    st.title("🔒 Login - Fluffy Chips Web Analyzer")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = verify_login(username, password)
        if user:
            st.session_state["logged_in"] = True
            st.session_state["username"] = username  # Store raw username for session
            st.session_state["role"] = user.get("role", "viewer")  # Default role is "viewer"
            st.success(f"Welcome, {username}! Role: {st.session_state['role']}")

            # Redirect to Home_1.py
            st.session_state["redirect_to_Home_1"] = True
            st.experimental_rerun()
        else:
            st.error("Incorrect username or password.")

# Logout function
def logout():
    st.session_state["logged_in"] = False
    st.session_state["username"] = None
    st.session_state["role"] = None
    st.session_state["redirect_to_Home_1"] = False
    st.experimental_rerun()

# Admin-only function to add users with specific roles
def add_user(username, password, role="viewer"):
    users_collection = get_users_collection()
    
    # Hash username and password
    hashed_username = hash_value(username)
    hashed_password = hash_value(password)
    
    # Check if user already exists (by hashed username)
    if users_collection.find_one({"username": hashed_username}):
        st.warning(f"User '{username}' already exists.")
    else:
        users_collection.insert_one({"username": hashed_username, "password": hashed_password, "role": role})
        st.success(f"User '{username}' added successfully with role '{role}'.")

