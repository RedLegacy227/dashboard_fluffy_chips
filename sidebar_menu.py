import streamlit as st

def show_sidebar():
    """Dynamically displays the sidebar menu based on login status."""

    # Ensure session state is initialized
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    # ✅ Get the current page from the query params, defaulting to "Login"
    selected_page = st.query_params.get("page", ["Login"])[0]

    # Define available pages
    if not st.session_state["logged_in"]:
        menu_items = {"Login": "Login.py"}
    else:
        menu_items = {
            "Home": "1_Home",
            "Games Analyse": "2_Games-Analyse",
            "Methods": "3_Methods",
            "Backtest": "4_Backtest"
        }

    # ✅ Ensure selected_page exists in menu_items.values()
    if selected_page not in menu_items.values():
        selected_page = "Login.py"  # Default back to "Login" if invalid

    # Create sidebar menu
    st.sidebar.title("📂 Navigation")
    page = st.sidebar.radio("Select a Page:", list(menu_items.keys()), index=list(menu_items.values()).index(selected_page))

    # ✅ Update the query parameter to track selected page
    st.query_params.from_dict({"page": menu_items[page]})
    st.rerun()

