import streamlit as st
from auth import login, logout

# Initialize session state for login
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# If logged in and redirect flag is set, go to Home_1.py
if st.session_state.get("redirect_to_Home_1", False):
    st.session_state["redirect_to_Home_1"] = False  # Reset flag
    st.switch_page("Home_1.py")

# If not logged in, show login page
if not st.session_state["logged_in"]:
    login()
else:
    st.sidebar.title("📍 Navigation")

    # Show "Admin Panel" only for admin users
    if st.session_state.get("role") == "admin":
        if st.sidebar.button("🔑 Admin Panel"):
            st.switch_page("admin.py")

    st.sidebar.button("🚪 Logout", on_click=logout)
