import streamlit as st

st.set_page_config(page_title="Login - Fluffy Chips", page_icon="🔐")

# Simulated authentication
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False  # Ensure default state

# Mock login form (Replace with actual authentication)
st.title("🔐 Login - Fluffy Chips Web Analyzer")
username = st.text_input("Username", key="username_input")
password = st.text_input("Password", type="password", key="password_input")
login_button = st.button("Login")

# Simulated authentication logic
if login_button:
    if username == "admin" and password == "password":  # Replace with real auth
        st.session_state["logged_in"] = True
        st.session_state["username"] = username
        st.session_state["role"] = "admin"

        # Redirect if a previous page was set
        if "redirect" in st.session_state:
            target_page = st.session_state.pop("redirect")
            st.success(f"✅ Redirecting to {target_page}...")
            st.experimental_rerun()  # Safe to rerun after session change
    else:
        st.error("❌ Invalid username or password.")

# Prevent non-logged-in users from accessing this page
if not st.session_state["logged_in"]:
    st.warning("🚫 Access denied. Please log in first.")
    st.stop()
