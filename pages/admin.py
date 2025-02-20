import streamlit as st
from auth import logout, add_user
from ui_helpers import add_logout_button  # ✅ Importa a função para evitar duplicação

# Redirect to login page if not logged in
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.switch_page("1_Home.py")

# Check if the logged-in user is an admin
if st.session_state.get("role") != "Admin":
    st.error("❌ Access Denied: You are not an Admin.")
    st.stop()


# Admin Page UI
st.title("🔑 Admin Panel - Manage Users")
st.write("Only authorized admin users can access this page.")

# User creation form
new_username = st.text_input("New Username")
new_password = st.text_input("New Password", type="password")
new_role = st.selectbox("Role", ["Viewer", "Editor", "Admin"])  # Now includes "editor" role

if st.button("Create User"):
    if new_username and new_password:
        add_user(new_username, new_password, new_role)
    else:
        st.warning("Please enter both a username and a password.")

# Adiciona o botão de logout apenas uma vez
add_logout_button()
