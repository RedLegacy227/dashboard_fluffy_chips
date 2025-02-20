import streamlit as st
from auth import logout  # Ensure this function clears session state

st.set_page_config(page_title="Login - Fluffy Chips", page_icon="🔐")

# Redirect to login if not logged in
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.warning("🚫 Access denied. Please log in first.")
    st.session_state["redirect"] = "1_Home"
    st.stop()  # Stop further execution instead of rerun

# Sidebar Navigation
st.sidebar.title("📍 Navigation")

# Show "Admin Panel" only for admin users
if st.session_state.get("role") == "Admin":
    if st.sidebar.button("🔑 Admin Panel"):
        st.session_state["pages"] = "admin"

# Logout button
if st.sidebar.button("🚪 Logout"):
    logout()  # Ensure it resets session
    st.session_state.clear()
    st.experimental_rerun()  # Safe to call after state change

# Main Content
st.title("🔐 Login - Fluffy Chips Web Analyzer")
st.write(f"Welcome, **{st.session_state.get('username', 'Guest')}**!")
