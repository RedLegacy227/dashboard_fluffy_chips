import streamlit as st
from auth import login, logout

# Initialize session state for login
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# If the user successfully logs in, set the redirection flag
if "redirect_to_Home_1" not in st.session_state:
    st.session_state["redirect_to_Home_1"] = False

# Redirect to Home_1.py if the user is logged in
if st.session_state["logged_in"] and st.session_state["redirect_to_Home_1"]:
    st.session_state["redirect_to_Home_1"] = False  # Reset redirection flag
    st.switch_page("Home_1.py")  # Redirect to Home_1.py

# If the user is not logged in, show the login page
if not st.session_state["logged_in"]:
    login()
else:
    st.sidebar.button("🚪 Logout", on_click=logout)

    st.title("🏠 Home - Fluffy Chips Web Analyzer")
    st.write(f"Welcome, **{st.session_state['username']}**!")
    st.write("Here is the Web Analyzer.")
