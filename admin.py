import streamlit as st
from auth import logout, add_user

# Define admin users (hardcoded for security)
ADMIN_USERS = ["admin", "superuser"]

# Redirect to login page if not logged in
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.switch_page("Home.py")

# Check if the logged-in user is an admin
if st.session_state["username"] not in ADMIN_USERS:
    st.error("Access Denied: You are not an admin.")
    st.stop()

# Admin Page UI
st.title("🔑 Admin Panel - Manage Users")
st.write("Only authorized admin users can access this page.")

# User creation form
new_username = st.text_input("New Username")
new_password = st.text_input("New Password", type="password")

if st.button("Create User"):
    if new_username and new_password:
        add_user(new_username, new_password)
    else:
        st.warning("Please enter both a username and a password.")

# Logout button
st.sidebar.button("🚪 Logout", on_click=logout)
