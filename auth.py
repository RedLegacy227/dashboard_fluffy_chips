import streamlit as st
import bcrypt
from database import get_users_collection

# Function to hash passwords securely using bcrypt
def hash_password(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt)  # Returns bytes

# Function to verify password using bcrypt
def verify_password(stored_password, entered_password):
    """Ensure stored password is bytes before checking"""
    if isinstance(stored_password, str):
        stored_password = stored_password.encode()  # Convert stored hash to bytes
    
    return bcrypt.checkpw(entered_password.encode(), stored_password)

# Function to verify login and fetch user role
def verify_login(username, password):
    users_collection = get_users_collection()
    
    # Find user in MongoDB collection
    user = users_collection.find_one({"username": username})
    
    if user and verify_password(user["password"], password):  # Compare password securely
        return user  # Return full user document
    return None  # Return None if no user found

# Login screen
def login():
    st.title("🔒 Login - Fluffy Chips Web Analyzer")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = verify_login(username, password)
        if user:
            st.session_state["logged_in"] = True
            st.session_state["username"] = username  # Store raw username for session
            st.session_state["role"] = user.get("role", "viewer")  # Default role is "viewer"
            st.success(f"Welcome, {username}! Role: {st.session_state['role']}")

            # ✅ Set redirect flag before switching page
            st.session_state["redirect_to_Home_1"] = True
            st.switch_page("1_Home")  # ✅ Corrected navigation
        else:
            st.error("Incorrect username or password.")

# Logout function
def logout():
    for key in list(st.session_state.keys()):
        del st.session_state[key]  # Clear session state
    
    st.switch_page("Login.py")  # ✅ Redirect to login after logout

# Admin-only function to add users with specific roles
def add_user(username, password, role="viewer"):
    users_collection = get_users_collection()
    
    # Hash the password with bcrypt
    hashed_password = hash_password(password)

    # Check if user already exists
    if users_collection.find_one({"username": username}):
        st.warning(f"⚠️ User '{username}' already exists.")
    else:
        users_collection.insert_one({
            "username": username, 
            "password": hashed_password.decode(),  # Store bcrypt-hashed password as string
            "role": role
        })
        st.success(f"✅ User '{username}' added successfully with role '{role}'.")