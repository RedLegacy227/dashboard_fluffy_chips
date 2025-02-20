import streamlit as st
import bcrypt
from database import get_users_collection

# Function to hash passwords securely using bcrypt
def hash_password(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt)

# Function to verify password using bcrypt
def verify_password(stored_password, entered_password):
    return bcrypt.checkpw(entered_password.encode(), stored_password)

# Function to verify login and fetch user role
def verify_login(username, password):
    users_collection = get_users_collection()
    
    # Find user in MongoDB collection (username is not hashed)
    user = users_collection.find_one({"username": username})
    
    if user and verify_password(user["password"], password):  # Compare password securely
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
    
    # Hash the password with bcrypt
    hashed_password = hash_password(password)

    # Check if user already exists
    if users_collection.find_one({"username": username}):
        st.warning(f"⚠️ User '{username}' already exists.")
    else:
        users_collection.insert_one({
            "username": username, 
            "password": hashed_password,  # Store bcrypt-hashed password
            "role": role
        })
        st.success(f"✅ User '{username}' added successfully with role '{role}'.")


