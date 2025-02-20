import streamlit as st
from auth import logout  # Ensure you have a logout function in auth.py

def show_role_features():
    """Displays role-based features in the sidebar."""
    # ✅ Add role-based features inside the sidebar
    if "role" in st.session_state:
        st.sidebar.subheader("👤 User Features")

        if st.session_state["role"] == "Admin":
            st.sidebar.subheader("🔧 Admin Features")
            st.sidebar.write("- Manage users")
            if st.sidebar.button("Go to Admin Panel"):
                st.switch_page("pages/admin.py")  # Ensure the path is correct

        elif st.session_state["role"] == "Editor":
            st.sidebar.subheader("📝 Editor Features")
            st.sidebar.write("- Edit and manage content")

        elif st.session_state["role"] == "Viewer":
            st.sidebar.subheader("👀 Viewer Features")
            st.sidebar.write("- View analytics and reports")

    st.sidebar.divider()

    # Add a title in the sidebar
    st.sidebar.header("💰Bank for Correct Score")

    # Create input for the working bank (only once in the sidebar)
    banca = st.sidebar.number_input(
        "Insert the amount of your working Bank:",
        min_value=50,
        value=200,
        step=10,
        key="banca_input"
    )

    # Calculate stakes based on the inserted bank
    stake_5 = banca * 0.05
    stake_7 = banca * 0.07
    stake_10 = banca * 0.10
    stake_12 = banca * 0.12
    stake_15 = banca * 0.15

    # Display calculated stakes
    st.sidebar.write(f"5% Stake: **{stake_5:.2f}**")
    st.sidebar.write(f"7% Stake: **{stake_7:.2f}**")
    st.sidebar.write(f"10% Stake: **{stake_10:.2f}**")
    st.sidebar.write(f"12% Stake: **{stake_12:.2f}**")
    st.sidebar.write(f"15% Stake: **{stake_15:.2f}**")

    st.sidebar.divider()

    # ✅ Logout button at the bottom
    if st.sidebar.button("🚪 Logout"):
        logout()  # Clears session state and redirects to Login
