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
                st.switch_page("pages/admin.py")

        elif st.session_state["role"] == "Editor":
            st.sidebar.subheader("📝 Editor Features")
            st.sidebar.write("- Edit and manage content")

        elif st.session_state["role"] == "Viewer":
            st.sidebar.subheader("👀 Viewer Features")
            st.sidebar.write("- View analytics and reports")

    st.sidebar.divider()

    # ✅ Logout button at the bottom
    if st.sidebar.button("🚪 Logout"):
        logout()  # Clears session state and redirects to Login
