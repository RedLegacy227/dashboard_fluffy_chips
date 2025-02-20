import streamlit as st
from auth import verify_login
from sidebar_menu import show_sidebar  # ✅ Importa o menu lateral dinâmico

st.set_page_config(page_title="Login - Fluffy Chips", page_icon="🔐")
# Exibir a barra lateral com páginas dinâmicas
show_sidebar()
# Inicializar estado de sessão para login
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

st.title("🔐 Login - Fluffy Chips Web Analyzer")

username = st.text_input("Username")
password = st.text_input("Password", type="password")
login_button = st.button("Login")

if login_button:
    user = verify_login(username, password)
    if user:
        st.session_state["logged_in"] = True
        st.session_state["username"] = username
        st.session_state["role"] = user.get("role", "viewer")

        st.success(f"✅ Bem-vindo, {username}!")

        # Redirecionar para "Home" após login
        st.session_state["redirect"] = "1_Home"
        st.rerun()
    else:
        st.error("❌ Usuário ou senha incorretos.")

# Impedir acesso não autorizado
if not st.session_state["logged_in"]:
    st.warning("🚫 Acesso negado. Faça login primeiro.")
    st.stop()