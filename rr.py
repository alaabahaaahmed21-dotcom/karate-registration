import streamlit as st
import pandas as pd
from datetime import date
from pathlib import Path

# -------- Safe Rerun Function --------
def safe_rerun():
    try:
        if hasattr(st, "rerun"):
            st.rerun()
            return
        if hasattr(st, "experimental_rerun"):
            st.experimental_rerun()
            return
        st.error("❌ Streamlit version does not support rerun. Please upgrade Streamlit.")
    except Exception as fatal:
        st.error("Unexpected error during rerun:")
        st.exception(fatal)

# ---- روابط الصور من GitHub RAW ----
img1 = "https://raw.githubusercontent.com/alaabahaaahmed21-dotcom/karate-registration/main/logo1.png"
img2 = "https://raw.githubusercontent.com/alaabahaaahmed21-dotcom/karate-registration/main/logo2.png"
img3 = "https://raw.githubusercontent.com/alaabahaaahmed21-dotcom/karate-registration/main/logo3.png"
img4 = "https://raw.githubusercontent.com/alaabahaaahmed21-dotcom/karate-registration/main/logo4.png"

# ---- CSS للصور والخلفية ----
st.markdown("""
<style>
.image-row {
    display: flex;
    justify-content: center;
    gap: 10px;
    flex-wrap: nowrap;
}
.image-row img {
    width: 90px;
    height: auto;
}
body {
    background-color: white;
    color: black;
}
.stTextInput>div>div>input, 
.stNumberInput>div>div>input,
.stSelectbox>div>div>div>select,
.stMultiselect>div>div>div>div>div,
.stDateInput>div>div>input,
.stFileUploader>div>div>input {
    background-color: #f0f0f0;
    color: black;
}
</style>
""", unsafe_allow_html=True)

# -------- SESSION STATE & PAGE --------
if "page" not in st.session_state:
    st.session_state.page = "select_championship"
if "submit_count" not in st.session_state:
    st.session_state.submit_count = 0

# -------- FILE SETUP --------
DATA_FILE = Path("athletes_data.csv")

def load_data():
    cols = [
        "Championship","Athlete Name","Club","Nationality","Coach Name","Phone Number",
        "Date of Birth","Sex","Player Code","Belt Degree","Competitions","Federation","Profile Picture"
    ]
    if DATA_FILE.exists():
        df = pd.read_csv(DATA_FILE)
        for col in cols:
            if col not in df.columns:
                df[col] = ""
        return df[cols]
    else:
        return pd.DataFrame(columns=cols)

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# -------- Utility Function to Display Logos --------
def display_logos():
    st.markdown(f"""
    <div class="image-row">
        <img src="{img1}">
        <img src="{img2}">
        <img src="{img3}">
        <img src="{img4}">
    </div>
    """, unsafe_allow_html=True)

# -------- Registration Form Function --------
def registration_form(championship, submit_count):
    athletes_data = []
    st.session_state.club = st.text_input("Enter Club for all players", value=st.session_state.get("club", ""))
    st.session_state.nationality = st.text_input("Enter Nationality for all players", value=st.session_state.get("nationality", ""))
    st.session_state.coach_name = st.text_input("Enter Coach Name for all players", value=st.session_state.get("coach_name", ""))
    st.session_state.phone_number = st.text_input("Enter Phone Number for the Coach", value=st.session_state.get("phone_number", ""))

    num_players = st.number_input("Number of players to add:", min_value=1, value=1, step=1)

    belt_options = [
        "Kyu Junior yellow 10","Kyu Junior yellow 9","Kyu Junior orange 8","Kyu Junior orange green 7",
        "Kyu Junior green 6","Kyu Junior green blue 5","Kyu Junior blue 4","Kyu Junior blue 3",
        "Kyu Junior brown 2","Kyu Junior brown 1","Kyu Senior yellow 7","Kyu Senior yellow 6",
        "Kyu Senior orange 5","Kyu Senior orange 4","Kyu Senior green 3","Kyu Senior blue 2",
        "Kyu Senior brown 1","Dan 1","Dan 2","Dan 3","Dan 4","Dan 5","Dan 6","Dan 7","Dan 8"
    ]

    for i in range(num_players):
        with st.expander(f"Player {i+1}"):
            key_suffix = f"_{submit_count}_{i}"
            athlete_name = st.text_input("Athlete Name", key=f"name{key_suffix}")
            dob = st.date_input("Date of Birth", min_value=date(1960,1,1), max_value=date.today(), key=f"dob{key_suffix}")
            sex = st.selectbox("Sex", ["Male", "Female"], key=f"sex{key_suffix}")
            player_code = st.text_input("Player Code", key=f"code{key_suffix}")
            belt_degree = st.selectbox("Belt Degree", belt_options, key=f"belt{key_suffix}")

            # Competitions & Federation
            competitions_list, federation = [], ""
            if championship == "North Africa Traditional Karate Championship":
                federation = st.selectbox("Select Federation", ["Egyptian Traditional Karate Federation","Unified General Federation"], key=f"federation{key_suffix}")
                competitions_list = ["Individual kata","Kata team","Individual kumite","Fuko go","Inbo mix","Inbo male","Inbo female","Kumite team"] if federation=="Egyptian Traditional Karate Federation" else ["Individual kata","Kata team","Kumite Ibon","Kumite Nihon","Kumite Sanbon","Kumite Rote shine"]
            elif championship == "United Karate Championship (General)":
                competitions_list = ["Individual Kata","Kata Team","Individual Kumite","Fuko Go","Inbo Mix","Inbo Male","Inbo Female","Kumite Team"]

            competitions = st.multiselect("Competitions", competitions_list, key=f"comp{key_suffix}")
            profile_pic = st.file_uploader("Profile Picture", type=["png","jpg","jpeg"], key=f"profile{key_suffix}")

            athletes_data.append({
                "Athlete Name": athlete_name.strip(),
                "Club": st.session_state.club.strip(),
                "Nationality": st.session_state.nationality.strip(),
                "Coach Name": st.session_state.coach_name.strip(),
                "Phone Number": st.session_state.phone_number.strip(),
                "Date of Birth": str(dob),
                "Sex": sex,
                "Player Code": player_code.strip(),
                "Belt Degree": belt_degree,
                "Competitions": ", ".join(competitions),
                "Federation": federation,
                "Profile Picture": profile_pic.name if profile_pic else "",
                "Championship": championship
            })
    return athletes_data

# -------- PAGE LOGIC --------
if st.session_state.page == "select_championship":
    display_logos()
    st.title("🏆 Select Championship")
    championship = st.selectbox("Please select the championship you want to register for:", [
        "African Master Course",
        "North Africa Traditional Karate Championship",
        "United Karate Championship (General)"
    ])
    if st.button("Next ➜"):
        st.session_state.selected_championship = championship
        st.session_state.page = "registration"
        safe_rerun()
    st.stop()

# -------- Registration Page --------
if st.session_state.page == "registration":
    if st.button("⬅ Back to Championship Selection"):
        st.session_state.page = "select_championship"
        safe_rerun()

    display_logos()
    st.markdown(f"<h3 style='text-align:left;'>🏆 Registration Form: {st.session_state.selected_championship}</h3>", unsafe_allow_html=True)

    athletes_data = registration_form(st.session_state.selected_championship, st.session_state.submit_count)

    if st.button("Submit All Players"):
        if athletes_data:
            df_existing = load_data()
            df_new = pd.DataFrame(athletes_data)
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
            save_data(df_combined)
            st.success(f"{len(athletes_data)} player(s) added successfully!")
            st.session_state.submit_count += 1
            safe_rerun()