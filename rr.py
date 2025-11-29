import streamlit as st
import pandas as pd
from datetime import date
from pathlib import Path
import requests
import io

# ------------------ Google Sheet API ------------------
GOOGLE_SHEET_API = "https://script.google.com/macros/s/AKfycbyY6FaRazYHmDimh68UpOs2MY04Uc-t5LiI3B_CsYZIAuClBvQ2sBQYIf1unJN45aJU2g/exec"

def save_to_google_sheet(row):
    """Send a single row (dict) to Google Sheets via Apps Script Web App"""
    try:
        r = requests.post(GOOGLE_SHEET_API, json=row)
        return r.status_code == 200
    except:
        return False

# ------------------ Data File ------------------
DATA_FILE = Path("athletes_data.csv")

def load_data():
    cols = [
        "Championship", "Athlete Name", "Club", "Nationality", "Coach Name",
        "Phone Number", "Date of Birth", "Sex", "Player Code",
        "Belt Degree", "Competitions", "Federation"
    ]
    if DATA_FILE.exists():
        df = pd.read_csv(DATA_FILE)
        for c in cols:
            if c not in df.columns:
                df[c] = ""
        return df[cols]
    return pd.DataFrame(columns=cols)

def save_data(df):
    df.to_csv(DATA_FILE, index=False)
    for _, row in df.iterrows():
        save_to_google_sheet(row.to_dict())

# ------------------ Page State ------------------
if "page" not in st.session_state:
    st.session_state.page = "select_championship"
if "submit_count" not in st.session_state:
    st.session_state.submit_count = 0

# ------------------ Logos ------------------
logos = [
    "https://raw.githubusercontent.com/alaabahaaahmed21-dotcom/karate-registration/main/logo1.png",
    "https://raw.githubusercontent.com/alaabahaaahmed21-dotcom/karate-registration/main/logo2.png",
    "https://raw.githubusercontent.com/alaabahaaahmed21-dotcom/karate-registration/main/logo3.png",
    "https://raw.githubusercontent.com/alaabahaaahmed21-dotcom/karate-registration/main/logo4.png"
]

st.markdown("""
<style>
.image-row { display: flex; justify-content: center; gap: 10px; flex-wrap: nowrap; }
.image-row img { width: 80px; height: auto; }
</style>
""", unsafe_allow_html=True)

# ------------------ Page 1: Select Championship ------------------
if st.session_state.page == "select_championship":
    st.markdown(f"""<div class="image-row">{"".join([f'<img src="{img}">' for img in logos])}</div>""", unsafe_allow_html=True)
    st.title("🏆 Select Championship")
    
    championship = st.selectbox("Select Championship:", [
        "African Master Course",
        "African Open Traditional Karate Championship",
        "North Africa Unitied Karate Championship (General)"
    ])
    
    if st.button("Next ➜"):
        st.session_state.selected_championship = championship
        st.session_state.page = "registration"
        st.experimental_rerun()
    st.stop()

# ------------------ Page 2: Registration ------------------
st.markdown(f"""<div class="image-row">{"".join([f'<img src="{img}">' for img in logos])}</div>""", unsafe_allow_html=True)
st.markdown(f"<h3>🏆 Registration Form: {st.session_state.selected_championship}</h3>", unsafe_allow_html=True)

# ------------------ Common Fields ------------------
st.session_state.club = st.text_input("Enter Club for all players", value=st.session_state.get("club",""))
st.session_state.nationality = st.text_input("Enter Nationality for all players", value=st.session_state.get("nationality",""))
st.session_state.coach_name = st.text_input("Enter Coach Name for all players", value=st.session_state.get("coach_name",""))
st.session_state.phone_number = st.text_input("Enter Phone Number for the Coach", value=st.session_state.get("phone_number",""))

num_players = st.number_input("Number of players to add:", min_value=1, value=1)

belt_options = [
    "Kyu Junior yellow 10","Kyu Junior yellow 9","Kyu Junior orange 8","Kyu Junior orange green 7",
    "Kyu Junior green 6","Kyu Junior green blue 5","Kyu Junior blue 4","Kyu Junior blue 3",
    "Kyu Junior brown 2","Kyu Junior brown 1","Kyu Senior yellow 7","Kyu Senior yellow 6",
    "Kyu Senior orange 5","Kyu Senior orange 4","Kyu Senior green 3","Kyu Senior blue 2",
    "Kyu Senior brown 1","Dan 1","Dan 2","Dan 3","Dan 4","Dan 5","Dan 6","Dan 7","Dan 8"
]

athletes_data = []

for i in range(num_players):
    key = f"{st.session_state.submit_count}_{i}"
    with st.expander(f"Player {i+1}"):
        name = st.text_input("Athlete Name", key=f"name_{key}")
        dob = st.date_input("Date of Birth", min_value=date(1960,1,1), max_value=date.today(), key=f"dob_{key}")
        sex = st.selectbox("Sex", ["Male","Female"], key=f"sex_{key}")
        code = st.text_input("Player Code", key=f"code_{key}")
        belt = st.selectbox("Belt Degree", belt_options, key=f"belt_{key}")

        federation = ""
        competitions = []
        if st.session_state.selected_championship != "African Master Course":
            federation = st.selectbox("Select Federation", ["Egyptian Traditional Karate Federation", "United General Federation"], key=f"fed_{key}")
            if federation=="Egyptian Traditional Karate Federation":
                competitions = st.multiselect("Competitions", ["Individual Kata","Kata Team","Individual Kumite","Fuko Go","Inbo Mix","Inbo Male","Inbo Female","Kumite Team"], key=f"comp_{key}")
            else:
                competitions = st.multiselect("Competitions", ["Individual Kata","Kata Team","Kumite Ibon","Kumite Nihon","Kumite Sanbon","Kumite Rote Shine"], key=f"comp_{key}")

    athletes_data.append({
        "Athlete Name": name.strip(),
        "Club": st.session_state.club.strip(),
        "Nationality": st.session_state.nationality.strip(),
        "Coach Name": st.session_state.coach_name.strip(),
        "Phone Number": st.session_state.phone_number.strip(),
        "Date of Birth": str(dob),
        "Sex": sex,
        "Player Code": code.strip(),
        "Belt Degree": belt,
        "Competitions": ", ".join(competitions),
        "Federation": federation,
        "Championship": st.session_state.selected_championship
    })

# ------------------ Submit ------------------
if st.button("Submit All"):
    df = load_data()
    error = False
    errors_list = []

    for athlete in athletes_data:
        # Validate required fields
        required = ["Athlete Name","Player Code","Belt Degree","Club","Nationality"]
        if st.session_state.selected_championship != "African Master Course":
            required += ["Coach Name","Phone Number","Competitions"]
        for field in required:
            value = athlete[field]
            if not value or (field=="Competitions" and value.strip()==""):
                errors_list.append(f"{field} is required for {athlete['Athlete Name'] or 'Unnamed'}")
                error = True
        # Check duplicate code
        existing_codes = set(df[df["Championship"]==athlete["Championship"]]["Player Code"].astype(str))
        if athlete["Player Code"] in existing_codes:
            errors_list.append(f"Player Code '{athlete['Player Code']}' already exists!")
            error = True

    if error:
        st.error("Fix the following issues:")
        for msg in errors_list:
            st.write("- ", msg)
        st.stop()

    df = pd.concat([df, pd.DataFrame(athletes_data)], ignore_index=True)
    save_data(df)
    st.success(f"✅ {len(athletes_data)} players registered successfully!")
    st.session_state.submit_count += 1

    # Clear dynamic fields
    for k in list(st.session_state.keys()):
        if any(p in k for p in ["name_","dob_","sex_","code_","belt_","comp_","fed_"]):
            st.session_state.pop(k)

# ------------------ Admin Panel ------------------
st.sidebar.header("Admin Login")
admin_password = st.sidebar.text_input("Enter Admin Password", type="password")
if admin_password == "mobadr90":
    st.sidebar.success("Logged in as Admin ✅")
    df = load_data()
    if df.empty:
        st.info("No data yet.")
    else:
        st.dataframe(df, use_container_width=True)
        buffer = io.BytesIO()
        df.to_excel(buffer, index=False, engine="openpyxl")
        buffer.seek(0)
        filename = st.session_state.get("selected_championship","athletes").replace(" ","_")
        st.download_button("📥 Download Excel", buffer, file_name=f"{filename}.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
