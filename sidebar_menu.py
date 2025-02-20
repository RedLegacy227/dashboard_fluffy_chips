import streamlit as st

def show_sidebar():
    """Dynamically displays the sidebar menu based on login status."""
    
    # Ensure session state is initialized
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    # ✅ Get the current page from the query params
    selected_page = st.query_params.get("page", "Login")

    # Show only "Login" if the user is not logged in
    if not st.session_state["logged_in"]:
        menu_items = {"Login": "Login"}
    else:
        # Show these pages only after login
        menu_items = {
            "Home": "1_Home",
            "Games Analyse": "2_Games-Analyse",
            "Methods": "3_Methods",
            "Backtest": "4_Backtest"
        }

    # Create sidebar menu
    st.sidebar.title("📂 Navigation")
    page = st.sidebar.radio("Select a Page:", list(menu_items.keys()), index=list(menu_items.values()).index(selected_page))

    # ✅ Update the query parameter to track selected page
    st.query_params.from_dict({"page": menu_items[page]})
    st.rerun()

