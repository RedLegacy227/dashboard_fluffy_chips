import streamlit as st
from auth import logout, add_user
from sidebar_menu import show_role_features

st.set_page_config(page_title="Admin Panel - Fluffy Chips", page_icon="🔑")
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.switch_page("Login.py")  # Redireciona para a página de login
# ✅ Show role-based features in the sidebar
show_role_features()

# Bloqueia acesso para não-admins
if st.session_state.get("role") != "Admin":
    st.error("❌ Access Denied: You are not an Admin.")
    st.stop()

# Interface do Admin
st.title("🔑 Admin Panel - Manage Users")
st.write("Only authorized admin users can access this page.")

# Criar usuário
new_username = st.text_input("New Username")
new_password = st.text_input("Password", type="password")
new_role = st.selectbox("Role", ["Viewer", "Editor", "Admin"])

if st.button("Create User"):
    if new_username and new_password:
        add_user(new_username, new_password, new_role)
        st.success(f"✅ User '{new_username}' created successfully!")
    else:
        st.warning("⚠️ Please enter both a username and a password.")