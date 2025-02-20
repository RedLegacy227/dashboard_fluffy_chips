import streamlit as st
from auth import verify_login

st.set_page_config(page_title="Login - Fluffy Chips", page_icon="🔐")

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

st.title("🔐 Login - Fluffy Chips Web Analyzer")

username = st.text_input("Username")
password = st.text_input("Password", type="password")
login_button = st.button("Login")

if login_button:
    user = verify_login(username, password)
    if user:  # ✅ Now correctly verifies bcrypt passwords
        st.session_state["logged_in"] = True
        st.session_state["username"] = username
        st.session_state["role"] = user.get("role", "viewer")

        st.success(f"✅ Welcome, {username}!")

        # ✅ Redirect to Home (1_Home.py)
        st.query_params.from_dict({"page": "1_Home"})
        st.rerun()
    else:
        st.error("❌ Incorrect username or password.")

# Prevent unauthorized access
if not st.session_state["logged_in"]:
    st.warning("🚫 Access denied. Please log in first.")
    st.stop()
