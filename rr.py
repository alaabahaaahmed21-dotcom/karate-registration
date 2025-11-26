import streamlit as st
import pandas as pd
from datetime import date
import io
from pathlib import Path

# ---- روابط الصور من GitHub RAW ----
logos = [
    "https://raw.githubusercontent.com/alaabahaaahmed21-dotcom/karate-registration/main/logo1.png",
    "https://raw.githubusercontent.com/alaabahaaahmed21-dotcom/karate-registration/main/logo2.png",
    "https://raw.githubusercontent.com/alaabahaaahmed21-dotcom/karate-registration/main/logo3.png",
    "https://raw.githubusercontent.com/alaabahaaahmed21-dotcom/karate-registration/main/logo4.png"
]

# ---- CSS ----
st.markdown("""
<style>
.image-row { display: flex; justify-content: center; gap: 10px; flex-wrap: nowrap; }
.image-row img { width: 70px; height: auto; }
body { background-color: white; color: black; }
.stTextInput>div>div>input, 
.stNumberInput>div>div>input,
.stSelectbox>div>div>div>select,
.stMultiselect>div>div>div>div>div,
.stDateInput>div>div>input { background-color: #f0f0f0; color: black; }
</style>
""", unsafe_allow_html=True)

# -------- FILE SETUP --------
DATA_FILE = Path("athletes_data.csv")
def load_data():
    if DATA_FILE.exists(): return pd.read_csv(DATA_FILE)
    return pd.DataFrame(columns=[
        "Championship","Athlete Name","Club","Nationality","Coach Name","Phone Number",
        "Date of Birth","Sex","Player Code","Belt Degree","Competitions"
    ])
def save_data(df): df.to_csv(DATA_FILE, index=False)

# -------- SESSION STATE DEFAULTS --------
if "page" not in st.session_state: st.session_state.page = "select_championship"
for key in ["club","nationality","coach_name","phone_number"]: 
    if key not in st.session_state: st.session_state[key] = ""

# -------- Helper to show logos --------
def show_logos(): 
    st.markdown('<div class="image-row">' + ''.join([f'<img src="{l}">' for l in logos]) + '</div>', unsafe_allow_html=True)

# -------- FIRST PAGE: SELECT CHAMPIONSHIP --------
if st.session_state.page == "select_championship":
    show_logos()
    st.title("🏆 Select Championship")
    championship = st.selectbox("Please select the championship you want to register for:", [
        "African Master Course",
        "North Africa Traditional Karate Championship",
        "Unified Karate Championship (General)"
    ])
    if st.button("Next ➜"):
        st.session_state.selected_championship = championship
        st.session_state.page = "registration"
        st.experimental_rerun()
    st.stop()

# -------- REGISTRATION PAGE --------
if st.session_state.page == "registration":
    show_logos()
    st.markdown(f"<h3 style='color:black;'>🏆 Registration Form: {st.session_state.selected_championship}</h3>", unsafe_allow_html=True)
    if st.button("⬅ Back to Championship Selection"):
        st.session_state.page = "select_championship"
        st.experimental_rerun()

    st.session_state.club = st.text_input("Enter Club for all players", value=st.session_state.club)
    st.session_state.nationality = st.text_input("Enter Nationality for all players", value=st.session_state.nationality)
    st.session_state.coach_name = st.text_input("Enter Coach Name for all players", value=st.session_state.coach_name)
    st.session_state.phone_number = st.text_input("Enter Phone Number for the Coach", value=st.session_state.phone_number)

    num_players = st.number_input("Number of players to add:", min_value=1, value=1, step=1)

    competitions_list = ["Individual Kata","Kata Team","Individual Kumite","Fuko Go",
                        "Inbo Mix","Inbo Male","Inbo Female","Kumite Team"]

    belt_options = [
        "Kyu Junior yellow 10","Kyu Junior yellow 9","Kyu Junior orange 8","Kyu Junior orange green 7",
        "Kyu Junior green 6","Kyu Junior green blue 5","Kyu Junior blue 4","Kyu Junior blue 3",
        "Kyu Junior brown 2","Kyu Junior brown 1","Kyu Senior yellow 7","Kyu Senior yellow 6",
        "Kyu Senior orange 5","Kyu Senior orange 4","Kyu Senior green 3","Kyu Senior blue 2",
        "Kyu Senior brown 1","Dan 1","Dan 2","Dan 3","Dan 4","Dan 5","Dan 6","Dan 7","Dan 8"
    ]

    athletes_data = []

    # -------- Player Inputs --------
    for i in range(num_players):
        # Initialize safely
        for key, default in [(f"name{i}",""), (f"code{i}",""), (f"belt{i}",belt_options[0]), (f"comp{i}",[])]:
            if key not in st.session_state: st.session_state[key] = default

        with st.expander(f"Player {i+1}"):
            athlete_name = st.text_input("Athlete Name", key=f"name{i}")
            dob = st.date_input("Date of Birth", min_value=date(1960,1,1), max_value=date.today(), key=f"dob{i}")
            sex = st.selectbox("Sex", ["Male","Female"], key=f"sex{i}")
            player_code = st.text_input("Player Code", key=f"code{i}")
            belt_degree = st.selectbox("Belt Degree", belt_options, key=f"belt{i}")
            competitions = st.multiselect("Competitions", competitions_list, key=f"comp{i}")

            athletes_data.append({
                "Athlete Name": athlete_name,
                "Club": st.session_state.club.strip(),
                "Nationality": st.session_state.nationality.strip(),
                "Coach Name": st.session_state.coach_name.strip(),
                "Phone Number": st.session_state.phone_number.strip(),
                "Date of Birth": str(dob),
                "Sex": sex,
                "Player Code": player_code,
                "Belt Degree": belt_degree,
                "Competitions": ", ".join(competitions),
                "Competitions List": competitions,
                "index": i,
                "Championship": st.session_state.selected_championship
            })

    # -------- Submit Button --------
    if st.button("Submit All"):
        error_found = False
        df = load_data()
        count = 0

        # Check repeated codes
        codes_in_form = [athlete["Player Code"] for athlete in athletes_data]
        if len(codes_in_form) != len(set(codes_in_form)):
            st.error("⚠️ Some Player Codes are repeated in this submission!")
            error_found = True

        # Check all required fields
        for athlete in athletes_data:
            idx = athlete["index"]
            if not athlete["Athlete Name"]: st.error(f"⚠️ Player {idx+1} Name is empty!"); error_found=True
            if not athlete["Player Code"]: st.error(f"⚠️ Player {idx+1} Code is empty!"); error_found=True
            if len(athlete["Competitions List"]) == 0: st.error(f"⚠️ Player {idx+1} must select at least one competition!"); error_found=True
            if athlete["Player Code"] in df["Player Code"].values: st.error(f"⚠️ Player Code {athlete['Player Code']} already exists!"); error_found=True

        if error_found: st.stop()
        # Add to DataFrame
        for athlete in athletes_data:
            df = pd.concat([df, pd.DataFrame([athlete])], ignore_index=True)
            count += 1
        save_data(df)
        st.success(f"{count} players registered successfully!")

        # Clear session_state safely
        for i in range(num_players):
            st.session_state[f"name{i}"] = ""
            st.session_state[f"code{i}"] = ""
            st.session_state[f"belt{i}"] = belt_options[0]
            st.session_state[f"comp{i}"] = []
        for key in ["club","nationality","coach_name","phone_number"]: st.session_state[key] = ""

# -------- Admin Panel --------
st.sidebar.header("Admin Login")
admin_password = st.sidebar.text_input("Enter Admin Password", type="password")
if admin_password == "mobadr90":
    st.sidebar.success("Logged in as Admin ✅")
    df = load_data()
    if not df.empty:
        st.dataframe(df,use_container_width=True)
        excel_buffer = io.BytesIO()
        df.to_excel(excel_buffer,index=False,engine='openpyxl')
        excel_buffer.seek(0)
        championship_name = st.session_state.get("selected_championship","athletes_data").replace(" ","_")
        st.download_button("📥 Download Excel", data=excel_buffer, file_name=f"{championship_name}.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        st.info("No data found yet.")
