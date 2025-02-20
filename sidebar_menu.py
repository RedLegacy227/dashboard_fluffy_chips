import streamlit as st

def show_sidebar():
    """Exibe dinamicamente o menu lateral baseado no status de login."""

    # Certificar que o estado de sessão está inicializado
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    # Se o usuário não estiver logado, exibe apenas "Login"
    if not st.session_state["logged_in"]:
        menu_items = {"Login": "Login"}
    else:
        # Usuário logado vê apenas estas páginas
        menu_items = {
            "Home": "1_Home",
            "Games Analyse": "2_Games-Analyse",
            "Methods": "3_Methods",
            "Backtest": "4_Backtest"
        }

    # Criar o menu lateral
    st.sidebar.title("📂 Navigation")
    page = st.sidebar.radio("Select a Page:", list(menu_items.keys()))

    # Redirecionar para a página escolhida
    st.session_state["redirect"] = menu_items[page]
    st.rerun()

