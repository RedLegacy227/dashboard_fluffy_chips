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
⚽ Algeria Ligue 1  
⚽ Argentina Primera División  
⚽ Australia A-League  
⚽ Australia New South Wales NPL  
⚽ Austria 2. Liga  
⚽ Austria Bundesliga  
⚽ Belarus Vysheyshaya Liga  
⚽ Belgium First Division B  
⚽ Belgium Pro League  
⚽ Bosnia and Herzegovina Premier League of Bosnia  
⚽ Brazil Serie A  
⚽ Brazil Serie B  
⚽ Brazil Serie C  
⚽ Bulgaria First League  
⚽ Canada Canadian Premier League  
⚽ Chile Primera B  
⚽ Chile Primera División  
⚽ China China League One  
⚽ China Chinese Super League  
⚽ Croatia Druga HNL  
⚽ Croatia Prva HNL  
⚽ Czech Republic FNL  
⚽ Czech Republic First League  
⚽ Denmark Superliga  
⚽ Egypt Egyptian Premier League  
⚽ England Championship  
⚽ England EFL League One  
⚽ England EFL League Two  
⚽ England Premier League  
⚽ Estonia Meistriliiga  
⚽ Europe UEFA Champions League  
⚽ FYR Macedonia First Football League  
⚽ Faroe Islands Faroe Islands Premier League  
⚽ Finland Veikkausliiga  
⚽ France Ligue 1  
⚽ France Ligue 2  
⚽ France National  
⚽ Georgia Erovnuli Liga  
⚽ Germany 2. Bundesliga  
⚽ Germany 3. Liga  
⚽ Germany Bundesliga  
⚽ Greece Super League  
⚽ Hungary NB I  
⚽ Hungary NB II  
⚽ Iceland Úrvalsdeild  
⚽ Indonesia Liga 1  
⚽ Iran Persian Gulf Pro League  
⚽ Israel Israeli Premier League  
⚽ Israel Liga Leumit  
⚽ Italy Serie A  
⚽ Italy Serie B  
⚽ Jamaica Jamaica National Premier League  
⚽ Japan J1 League  
⚽ Japan J2 League  
⚽ Jordan Jordanian Pro League  
⚽ Kazakhstan Kazakhstan Premier League  
⚽ Luxembourg National Division  
⚽ Malaysia Super League  
⚽ Montenegro Montenegrin First League  
⚽ Morocco Botola Pro  
⚽ Netherlands Eerste Divisie  
⚽ Netherlands Eredivisie  
⚽ Nigeria NPFL  
⚽ Northern Ireland NIFL Premiership  
⚽ Norway Eliteserien  
⚽ Norway First Division  
⚽ Norway Toppserien  
⚽ Oman Professional League   
⚽ Paraguay Division Profesional  
⚽ Poland 1. Liga  
⚽ Poland Ekstraklasa  
⚽ Portugal Campeonato de Portugal Group A  
⚽ Portugal Campeonato de Portugal Group B  
⚽ Portugal Campeonato de Portugal Group C  
⚽ Portugal Campeonato de Portugal Group D  
⚽ Portugal Liga 3  
⚽ Portugal Liga NOS  
⚽ Portugal LigaPro  
⚽ Qatar Stars League  
⚽ Republic of Ireland First Division  
⚽ Republic of Ireland Premier Division  
⚽ Romania Liga I  
⚽ Saudi Arabia Professional League  
⚽ Scotland Championship  
⚽ Scotland Premiership  
⚽ Serbia Prva Liga  
⚽ Serbia SuperLiga  
⚽ Singapore S.League  
⚽ Slovakia Super Liga  
⚽ Slovenia PrvaLiga  
⚽ South Africa Premier Soccer League  
⚽ South America Copa Libertadores  
⚽ South Korea K League 1  
⚽ South Korea K League 2  
⚽ Spain La Liga  
⚽ Spain Primera Division RFEF Group 1  
⚽ Spain Primera Division RFEF Group 2  
⚽ Spain Segunda División  
⚽ Spain Segunda División RFEF Group 2  
⚽ Spain Segunda División RFEF Group 3  
⚽ Spain Segunda División RFEF Group 4  
⚽ Spain Segunda División RFEF Group 5  
⚽ Sweden Allsvenskan  
⚽ Sweden Damallsvenskan  
⚽ Sweden Superettan  
⚽ Switzerland Challenge League  
⚽ Switzerland Super League  
⚽ Taiwan Taiwan Football Premier League  
⚽ Thailand Thai League T1  
⚽ Tunisia Ligue 1  
⚽ Turkey 1. Lig  
⚽ Turkey Süper Lig  
⚽ UAE Arabian Gulf League  
⚽ USA MLS  
⚽ USA MLS Next Pro  
⚽ USA USL Championship  
⚽ Ukraine Ukrainian Premier League  
⚽ Uruguay Primera División  
⚽ Uzbekistan Uzbekistan Super League  
⚽ Vietnam V.League 1  
⚽ Wales Welsh Premier League  
""")