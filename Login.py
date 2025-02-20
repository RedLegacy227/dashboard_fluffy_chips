import streamlit as st
from auth import verify_login

# Set page config
st.set_page_config(page_title="Login - Fluffy Chips", page_icon="🔐", layout="wide")

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = None
if "role" not in st.session_state:
    st.session_state["role"] = None

# Title
st.title("🔐 Login - Fluffy Chips Web Analyzer")

# Check if the user is already logged in
if st.session_state["logged_in"]:
    # Display welcome message and role
    st.write(f"Welcome, **{st.session_state['username']}**!")
    st.write(f"Your role: **{st.session_state['role']}**")
    st.success("✅ Login Successful")

    # Optionally, provide a button to log out
    if st.button("Logout"):
        st.session_state["logged_in"] = False
        st.session_state["username"] = None
        st.session_state["role"] = None
        st.rerun()  # Refresh the page to show the login form again
else:
    # Show the login form
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login_button = st.button("Login")

    if login_button:
        user = verify_login(username, password)
        if user:
            # Update session state
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.session_state["role"] = user.get("role", "viewer")

            # Display success message and redirect to Home
            st.success(f"✅ Welcome, {username}!")
            st.switch_page("pages/1_Home.py")  # Ensure path matches your pages folder
        else:
            st.error("❌ Incorrect username or password.")
