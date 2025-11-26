import streamlit as st
import pandas as pd
from datetime import date
import io
from pathlib import Path

# ---- روابط الصور من GitHub RAW ----
img1 = "https://raw.githubusercontent.com/alaabahaaahmed21-dotcom/karate-registration/main/logo1.png"
img2 = "https://raw.githubusercontent.com/alaabahaaahmed21-dotcom/karate-registration/main/logo2.png"
img3 = "https://raw.githubusercontent.com/alaabahaaahmed21-dotcom/karate-registration/main/logo3.png"
img4 = "https://raw.githubusercontent.com/alaabahaaahmed21-dotcom/karate-registration/main/logo4.png"

# -------- FILE SETUP --------
DATA_FILE = Path("athletes_data.csv")

def load_data():
    if DATA_FILE.exists():
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=[
            "Championship",
            "Athlete Name", "Club", "Nationality", "Coach Name", "Phone Number",
            "Date of Birth", "Sex", "Player Code", "Belt Degree", "Competitions"
        ])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# ---------- SESSION STATE ----------
if "page" not in st.session_state:
    st.session_state.page = "select_championship"

for key in ["club", "nationality", "coach_name", "phone_number"]:
    if key not in st.session_state:
        st.session_state[key] = ""

# ╔══════════════════════════════════╗
#   🟦 Admin Panel ثابت في كل الصفحات
# ╚══════════════════════════════════╝
st.sidebar.header("Admin Login")
admin_password = st.sidebar.text_input("Enter Admin Password", type="password")

if admin_password == "mobadr90":
    st.sidebar.success("Logged in as Admin ✅")

    df_admin = load_data()

    if df_admin.empty:
        st.sidebar.info("No data found yet.")
    else:
        excel_buffer = io.BytesIO()
        df_admin.to_excel(excel_buffer, index=False)
        excel_buffer.seek(0)

        st.sidebar.download_button(
            label="📥 Download All Data",
            data=excel_buffer,
            file_name="Karate_Registration.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# ╔══════════════════════════════════╗
#         🟧 صفحة اختيار البطولة
# ╚══════════════════════════════════╝
if st.session_state.page == "select_championship":

    st.title("🏆 Select Championship")

    championship = st.selectbox(
        "Please select the championship:",
        [
            "African Master Course",
            "North Africa Traditional Karate Championship",
            "Unified Karate Championship (General)"
        ]
    )

    if st.button("Next ➜"):
        st.session_state.selected_championship = championship
        st.session_state.page = "registration"
        st.stop()

# ╔══════════════════════════════════╗
#           🟩 صفحة التسجيل
# ╚══════════════════════════════════╝
if st.session_state.page == "registration":

    if st.button("⬅ Back"):
        st.session_state.page = "select_championship"
        st.stop()

    st.markdown(f"### Registration Form: {st.session_state.selected_championship}")

    # -------- بيانات مشتركة --------
    st.session_state.club = st.text_input("Club", value=st.session_state.club)
    st.session_state.nationality = st.text_input("Nationality", value=st.session_state.nationality)
    st.session_state.coach_name = st.text_input("Coach Name", value=st.session_state.coach_name)
    st.session_state.phone_number = st.text_input("Phone Number", value=st.session_state.phone_number)

    num_players = st.number_input("Number of players:", min_value=1, value=1, step=1)

    competitions_list = [
        "Individual Kata","Kata Team","Individual Kumite","Fuko Go",
        "Inbo Mix","Inbo Male","Inbo Female","Kumite Team"
    ]

    belt_options = [
        "Kyu Junior yellow 10","Kyu Junior yellow 9","Kyu Junior orange 8","Kyu Junior orange green 7",
        "Kyu Junior green 6","Kyu Junior green blue 5","Kyu Junior blue 4","Kyu Junior blue 3",
        "Kyu Junior brown 2","Kyu Junior brown 1","Kyu Senior yellow 7","Kyu Senior yellow 6",
        "Kyu Senior orange 5","Kyu Senior orange 4","Kyu Senior green 3","Kyu Senior blue 2",
        "Kyu Senior brown 1","Dan 1","Dan 2","Dan 3","Dan 4","Dan 5","Dan 6","Dan 7","Dan 8"
    ]

    # -------- جمع بيانات اللاعبين --------
    athletes_data = []

    for i in range(num_players):
        with st.expander(f"Player {i+1}"):

            athlete_name = st.text_input("Athlete Name", key=f"name{i}")
            dob = st.date_input("Date of Birth", min_value=date(1960,1,1), max_value=date.today(), key=f"dob{i}")
            sex = st.selectbox("Sex", ["Male", "Female"], key=f"sex{i}")
            player_code = st.text_input("Player Code", key=f"code{i}")
            belt_degree = st.selectbox("Belt Degree", belt_options, key=f"belt{i}")
            competitions = st.multiselect("Competitions", competitions_list, key=f"comp{i}")

            athletes_data.append({
                "Championship": st.session_state.selected_championship,
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
            })

    # ╔══════════════════════════════════╗
    #           🔘 زر SUBMIT
    # ╚══════════════════════════════════╝
    if st.button("Submit All"):

        df = load_data()
        errors = False

        # ---- التحقق من المدخلات العامة ----
        if not st.session_state.club.strip():
            st.error("Club is required!")
            errors = True
        if not st.session_state.nationality.strip():
            st.error("Nationality is required!")
            errors = True
        if not st.session_state.coach_name.strip():
            st.error("Coach Name is required!")
            errors = True
        if not st.session_state.phone_number.strip():
            st.error("Phone Number is required!")
            errors = True

        # ---- تحقق من اللاعبين ----
        codes = [a["Player Code"] for a in athletes_data]
        if len(codes) != len(set(codes)):
            st.error("⚠ Some Player Codes are duplicated!")
            errors = True

        for a in athletes_data:
            if not a["Athlete Name"]:
                st.error("Missing athlete name!")
                errors = True
            if not a["Player Code"]:
                st.error("Missing player code!")
                errors = True
            if not a["Competitions"]:
                st.error("Competitions cannot be empty!")
                errors = True

            # تحقق لو الكود موجود من قبل
            if a["Player Code"] in df["Player Code"].values:
                st.error(f"Player Code {a['Player Code']} already exists!")
                errors = True

        if errors:
            st.stop()

        # ---- حفظ بعد الضغط فقط ----
        df = pd.concat([df, pd.DataFrame(athletes_data)], ignore_index=True)
        save_data(df)

        st.success(f"{len(athletes_data)} players registered successfully!")

