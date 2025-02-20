import streamlit as st
from auth import verify_login

st.set_page_config(page_title="Login - Fluffy Chips", page_icon="🔐")

# Inicializar estado de sessão para login
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

st.title("🔐 Login - Fluffy Chips Web Analyzer")

username = st.text_input("Username")
password = st.text_input("Password", type="password")
login_button = st.button("Login")

# Processamento de login
if login_button:
    user = verify_login(username, password)
    if user:
        st.session_state["logged_in"] = True
        st.session_state["username"] = username
        st.session_state["role"] = user.get("role", "viewer")

        st.success(f"✅ Bem-vindo, {username} ({st.session_state['role']})!")

        # Redirecionamento seguro
        if "redirect" in st.session_state:
            target_page = st.session_state.pop("redirect")
            st.experimental_rerun()
        else:
            st.experimental_rerun()
    else:
        st.error("❌ Usuário ou senha incorretos.")

# Impedir acesso não autorizado
if not st.session_state["logged_in"]:
    st.warning("🚫 Acesso negado. Faça login primeiro.")
    st.stop()
