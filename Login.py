import streamlit as st
from auth import logout

st.set_page_config(page_title="Home - Fluffy Chips", page_icon="🏠")

# Redirect to login if not logged in
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.warning("🚫 Access denied. Please log in first.")
    st.switch_page("Login")  # ✅ Redirect to login page

# Navigation
st.sidebar.title("📍 Navigation")

# Show "Admin Panel" only for admin users
if st.session_state.get("role") == "admin":
    if st.sidebar.button("🔑 Admin Panel"):
        st.switch_page("admin")  # ✅ Corrected path

# Logout button
st.sidebar.button("🚪 Logout", on_click=logout)

# Main content
st.title("🏠 Home - Fluffy Chips Web Analyzer")
st.write(f"Welcome, **{st.session_state['username']}**!")