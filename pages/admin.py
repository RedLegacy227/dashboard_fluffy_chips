import streamlit as st
from auth import logout, add_user
from ui_helpers import add_logout_button

st.set_page_config(page_title="Admin Panel - Fluffy Chips", page_icon="🔑")

# Redireciona para login se não estiver autenticado
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.session_state["redirect"] = "1_Home"
    st.rerun()

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

# Adiciona botão de logout na barra lateral
add_logout_button()