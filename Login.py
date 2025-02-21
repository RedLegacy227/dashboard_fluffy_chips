import streamlit as st
from auth import verify_login

# Set page config
st.set_page_config(page_title="Login - Fluffy Chips", page_icon="🔐", layout="wide")

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = None
if "role" not in st.session_state:
    st.session_state["role"] = None

# Title
st.title("🔐 Login - Fluffy Chips Web Analyzer")

# Check if the user is already logged in
if st.session_state["logged_in"]:
    # Display welcome message and role
    st.write(f"Welcome, **{st.session_state['username']}**!")
    st.write(f"Your role: **{st.session_state['role']}**")
    st.success("✅ Login Successful")

    # Optionally, provide a button to log out
    if st.button("Logout"):
        st.session_state["logged_in"] = False
        st.session_state["username"] = None
        st.session_state["role"] = None
        st.rerun()  # Refresh the page to show the login form again
else:
    # Show the login form
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login_button = st.button("Login")

    if login_button:
        user = verify_login(username, password)
        if user:
            # Update session state
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.session_state["role"] = user.get("role", "viewer")

            # Display success message and redirect to Home
            st.success(f"✅ Welcome, {username}!")
            st.switch_page("pages/1_Home.py")  # Ensure path matches your pages folder
        else:
            st.error("❌ Incorrect username or password.")
            
st.markdown(f"#### Leagues Supported ####")
st.markdown(f"""
⚽ ARGENTINA - TORNEO BETANO ✔️
⚽ AUSTRALIA - A-LEAGUE ✔️
⚽ AUSTRIA - 2. LIGA ✔️
⚽ AUSTRIA - BUNDESLIGA ✔️
⚽ BELGIUM - CHALLENGER PRO LEAGUE ✔️
⚽ BELGIUM - JUPILER PRO LEAGUE ✔️
⚽ BOLIVIA - DIVISION PROFESIONAL ✔️
⚽ BRAZIL - SERIE A BETANO ✔️
⚽ BRAZIL - SERIE B ✔️
⚽ BULGARIA - PARVA LIGA ✔️
⚽ CANADA - CANADIAN PREMIER LEAGUE ✔️
⚽ CHILE - LIGA DE PRIMERA ✔️
⚽ CHINA - SUPER LEAGUE ✔️
⚽ COSTA RICA - PRIMERA DIVISION ✔️
⚽ CROATIA - HNL ✔️
⚽ CZECH REPUBLIC - CHANCE LIGA ✔️
⚽ DENMARK - 1ST DIVISION ✔️
⚽ DENMARK - SUPERLIGA ✔️
⚽ ECUADOR - LIGA PRO ✔️
⚽ EGYPT - PREMIER LEAGUE ✔️
⚽ ENGLAND - CHAMPIONSHIP ✔️
⚽ ENGLAND - LEAGUE ONE ✔️
⚽ ENGLAND - LEAGUE TWO ✔️
⚽ ENGLAND - NATIONAL LEAGUE ✔️
⚽ ENGLAND - PREMIER LEAGUE ✔️
⚽ ESTONIA - MEISTRILIIGA ✔️
⚽ EUROPE - CHAMPIONS LEAGUE ✔️
⚽ EUROPE - CONFERENCE LEAGUE ✔️
⚽ EUROPE - EUROPA LEAGUE ✔️
⚽ FINLAND - VEIKKAUSLIIGA ✔️
⚽ FRANCE - LIGUE 1 ✔️
⚽ FRANCE - LIGUE 2 ✔️
⚽ GERMANY - 2. BUNDESLIGA ✔️
⚽ GERMANY - 3. LIGA ✔️
⚽ GERMANY - BUNDESLIGA ✔️
⚽ GREECE - SUPER LEAGUE ✔️
⚽ HUNGARY - OTP BANK LIGA ✔️
⚽ ICELAND - BESTA DEILD KARLA ✔️
⚽ INDIA - ISL ✔️
⚽ INDONESIA - LIGA 1 ✔️
⚽ IRELAND - PREMIER DIVISION ✔️
⚽ ISRAEL - LIGAT HA'AL ✔️
⚽ ITALY - SERIE A ✔️
⚽ ITALY - SERIE B ✔️
⚽ JAPAN - J1 LEAGUE ✔️
⚽ JAPAN - J2 LEAGUE ✔️
⚽ KAZAKHSTAN - PREMIER LEAGUE ✔️
⚽ LATVIA - VIRSLIGA ✔️
⚽ LITHUANIA - A LYGA ✔️
⚽ MALAYSIA - SUPER LEAGUE ✔️
⚽ MEXICO - LIGA MX ✔️
⚽ MOROCCO - BOTOLA PRO ✔️
⚽ NETHERLANDS - EERSTE DIVISIE ✔️
⚽ NETHERLANDS - EREDIVISIE ✔️
⚽ NORTHERN IRELAND - NIFL PREMIERSHIP ✔️
⚽ NORWAY - ELITESERIEN ✔️
⚽ NORWAY - OBOS-LIGAEN ✔️
⚽ PARAGUAY - COPA DE PRIMERA ✔️
⚽ PERU - LIGA 1 ✔️
⚽ POLAND - EKSTRAKLASA ✔️
⚽ PORTUGAL - LIGA 3 ✔️
⚽ PORTUGAL - LIGA PORTUGAL ✔️
⚽ PORTUGAL - LIGA PORTUGAL 2 ✔️
⚽ QATAR - QSL ✔️
⚽ ROMANIA - SUPERLIGA ✔️
⚽ SAUDI ARABIA - SAUDI PROFESSIONAL LEAGUE ✔️
⚽ SCOTLAND - CHAMPIONSHIP ✔️
⚽ SCOTLAND - PREMIERSHIP ✔️
⚽ SERBIA - SUPER LIGA ✔️
⚽ SINGAPORE - PREMIER LEAGUE ✔️
⚽ SLOVAKIA - NIKE LIGA ✔️
⚽ SLOVENIA - PRVA LIGA ✔️
⚽ SOUTH AMERICA - COPA LIBERTADORES ✔️
⚽ SOUTH AMERICA - COPA SUDAMERICANA ✔️
⚽ SOUTH KOREA - K LEAGUE 1 ✔️
⚽ SOUTH KOREA - K LEAGUE 2 ✔️
⚽ SPAIN - LALIGA ✔️
⚽ SPAIN - LALIGA2 ✔️
⚽ SWEDEN - ALLSVENSKAN ✔️
⚽ SWEDEN - SUPERETTAN✔️
⚽ SWITZERLAND - CHALLENGE LEAGUE ✔️
⚽ SWITZERLAND - SUPER LEAGUE ✔️
⚽ THAILAND - THAI LEAGUE 1 ✔️
⚽ TURKEY - 1. LIG ✔️
⚽ TURKEY - SUPER LIG ✔️
⚽ UKRAINE - PREMIER LEAGUE ✔️
⚽ URUGUAY - LIGA AUF URUGUAYA ✔️
⚽ USA - MLS ✔️
⚽ USA - USL CHAMPIONSHIP ✔️
⚽ VENEZUELA - LIGA FUTVE ✔️
⚽ WALES - CYMRU PREMIER ✔️
""")