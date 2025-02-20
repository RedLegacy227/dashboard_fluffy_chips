import streamlit as st
from auth import logout, add_user, hash_password
from ui_helpers import add_logout_button  # ✅ Função para evitar duplicação

# Configuração da página
st.set_page_config(page_title="Admin Panel - Fluffy Chips", page_icon="🔑")

# Redireciona para login se o usuário não estiver autenticado
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.session_state["redirect"] = "1_Home"  # Define para onde redirecionar
    st.rerun()

# Verifica se o usuário tem permissão de administrador
if st.session_state.get("role") != "Admin":
    st.error("❌ Access Denied: You are not an Admin.")
    st.stop()

# Interface do Painel de Administração
st.title("🔑 Admin Panel - Manage Users")
st.write("Only authorized admin users can access this page.")

# Formulário para criação de usuário
new_username = st.text_input("New Username")
new_password = st.text_input("New Password", type="password")
new_role = st.selectbox("Role", ["Viewer", "Editor", "Admin"])  # Opções de função

if st.button("Create User"):
    if new_username and new_password:
        hashed_password = hash_password(new_password)  # ✅ Hash da senha com bcrypt
        add_user(new_username, hashed_password, new_role)
        st.success(f"✅ User '{new_username}' created successfully!")
    else:
        st.warning("⚠️ Please enter both a username and a password.")

# Adiciona botão de logout na barra lateral
add_logout_button()

