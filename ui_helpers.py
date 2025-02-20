import streamlit as st
from auth import logout

def add_logout_button():
    """Adiciona o botão de logout na barra lateral apenas uma vez."""
    if "logout_button_shown" not in st.session_state:
        st.session_state["logout_button_shown"] = True
        st.sidebar.button("🚪 Logout", on_click=logout)