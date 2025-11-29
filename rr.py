import streamlit as st
import pandas as pd
from datetime import date
import io
from pathlib import Path
import requests

# ---------------- Disable warnings ----------------
st.warning = lambda *a, **k: None

# ---------------- Google Sheet API ----------------
GOOGLE_SHEET_API = "https://script.google.com/macros/s/AKfycbyY6FaRazYHmDimh68UpOs2MY04Uc-t5LiI3B_CsYZIAuClBvQ2sBQYIf1unJN45aJU2g/exec"  

def save_to_google_sheet(rows):
    """Send all rows at once to Google Sheets"""
    try:
        requests.post(GOOGLE_SHEET_API, json={"rows": rows})
        return True
    except:
        return True  # Prevent warnings

# ---------------- Safe Rerun ----------------
def safe_rerun():
    try:
        if hasattr(st, "rerun"):
            st.rerun()
        elif hasattr(st, "experimental_rerun"):
            st.experimental_rerun()
    except:
        pass

# ---------------- Logos ----------------
img1 = "https://raw.githubusercontent.com/alaabahaaahmed21-dotcom/karate-registration/main/logo1.png"
img2 = "https://raw.githubusercontent.com/alaabahaaahmed21-dotcom/karate-registration/main/logo2.png"
img3 = "https://raw.githubusercontent.com/alaabahaaahmed21-dotcom/karate-registration/main/logo3.png"
img4 = "https://raw.githubusercontent.com/alaabahaaahmed21-dotcom/karate-registration/main/logo4.png"

# ---------------- CSS ----------------
st.markdown("""
<style>
.image-row {
   display: flex;
   justify-content: center;
   gap: 10px;
   flex-wrap: nowrap;
}
.image-row img {
   width: 80px;
   height: auto;
}
</style>
""", unsafe_allow_html=True)

# ---------------- Page State ----------------
if "page" not in st.session_state:
    st.session_state.page = "select_championship"

DATA_FILE = Path("athletes_data.csv")

# ---------------- Load Data ----------------
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

# ---------------- Save Data ----------------
def save_data(df):
    df.to_csv(DATA_FILE, index=False)  # Save local copy
    rows = df.to_dict("records")
    save_to_google_sheet(rows)

# ---------------- Defaults ----------------
for key in ["club", "nationality", "coach_name", "phone_number", "submit_count"]:
    if key not in st.session_state:
        st.session_state[key] = "" if key != "submit_count" else 0

# =====================================================
# PAGE 1 — Select Championship
# =====================================================
if st.session_state.page == "select_championship":

    st.markdown(f"""
       <div class="image-row">
           <img src="{img1}">
           <img src="{img2}">
           <img src="{img3}">
           <img src="{img4}">
       </div>
       """, unsafe_allow_html=True)

    st.title("🏆 Select Championship")

    championship = st.selectbox(
        "Please select the championship you want to register for:",
        [
            "African Master Course",
            "African Open Traditional Karate Championship",
            "North Africa Unitied Karate Championship (General)"
        ]
    )

    if st.button("Next ➜"):
        st.session_state.selected_championship = championship
        st.session_state.page = "registration"
        safe_rerun()

    st.stop()

# =====================================================
# PAGE 2 — Registration
# =====================================================
if st.session_state.page == "registration":

    if st.button("⬅ Back to Championship Selection"):
        st.session_state.page = "select_championship"
        safe_rerun()

    st.markdown(f"""
       <div class="image-row">
           <img src="{img1}">
           <img src="{img2}">
           <img src="{img3}">
           <img src="{img4}">
       </div>
       """, unsafe_allow_html=True)

    st.markdown(
        f"<h3 style='color:black'>🏆 Registration Form: {st.session_state.selected_championship}</h3>",
        unsafe_allow_html=True
    )

    athletes_data = []
    submit_count = st.session_state.submit_count

    # ------------------------------------------------------------
    # Championship Fields
    # ------------------------------------------------------------
    if st.session_state.selected_championship == "African Master Course":
        course_type = st.selectbox("Choose course type:", ["Master", "General"])
        st.session_state.club = st.text_input("Enter Club for all players", value=st.session_state.club)
        num_players = st.number_input("Number of players to add:", min_value=1, value=1)

        belt_options = [
            "Kyu Junior yellow 10","Kyu Junior yellow 9","Kyu Junior orange 8","Kyu Junior orange green 7",
            "Kyu Junior green 6","Kyu Junior green blue 5","Kyu Junior blue 4","Kyu Junior blue 3",
            "Kyu Junior brown 2","Kyu Junior brown 1","Kyu Senior yellow 7","Kyu Senior yellow 6",
            "Kyu Senior orange 5","Kyu Senior orange 4","Kyu Senior green 3","Kyu Senior blue 2",
            "Kyu Senior brown 1","Dan 1","Dan 2","Dan 3","Dan 4","Dan 5","Dan 6","Dan 7","Dan 8"
        ]

        for i in range(num_players):
            key_suffix = f"_{submit_count}_{i}"
            with st.expander(f"Player {i+1}"):
                athlete_name = st.text_input("Athlete Name", key=f"name{key_suffix}")
                dob = st.date_input("Date of Birth", min_value=date(1960,1,1),
                                    max_value=date.today(), key=f"dob{key_suffix}")
                nationality = st.text_input("Nationality", key=f"nat{key_suffix}")
                phone = st.text_input("Phone Number", key=f"phone{key_suffix}")
                sex = st.selectbox("Sex", ["Male", "Female"], key=f"sex{key_suffix}")
                code = st.text_input("Player Code", key=f"code{key_suffix}")
                belt = st.selectbox("Belt Degree", belt_options, key=f"belt{key_suffix}")

            athletes_data.append({
                "Athlete Name": athlete_name.strip(),
                "Club": st.session_state.club.strip(),
                "Nationality": nationality.strip(),
                "Coach Name": "",
                "Phone Number": phone.strip(),
                "Date of Birth": str(dob),
                "Sex": sex,
                "Player Code": code.strip(),
                "Belt Degree": belt,
                "Competitions": "",
                "Federation": "",
                "Championship": f"African Master Course - {course_type}"
            })

    else:
        # باقي البطولات
        st.session_state.club = st.text_input("Enter Club for all players", value=st.session_state.club)
        st.session_state.nationality = st.text_input("Enter Nationality for all players", value=st.session_state.nationality)
        st.session_state.coach_name = st.text_input("Enter Coach Name for all players", value=st.session_state.coach_name)
        st.session_state.phone_number = st.text_input("Enter Phone Number for the Coach", value=st.session_state.phone_number)
        num_players = st.number_input("Number of players to add:", min_value=1, value=1)

        belt_options = [
            "Kyu Junior yellow 10","Kyu Junior yellow 9","Kyu Junior orange 8","Kyu Junior orange green 7",
            "Kyu Junior green 6","Kyu Junior green blue 5","Kyu Junior blue 4","Kyu Junior blue 3",
            "Kyu Junior brown 2","Kyu Junior brown 1","Kyu Senior yellow 7","Kyu Senior yellow 6",
            "Kyu Senior orange 5","Kyu Senior orange 4","Kyu Senior green 3","Kyu Senior blue 2",
            "Kyu Senior brown 1","Dan 1","Dan 2","Dan 3","Dan 4","Dan 5","Dan 6","Dan 7","Dan 8"
        ]

        for i in range(num_players):
            key_suffix = f"_{submit_count}_{i}"
            with st.expander(f"Player {i+1}"):
                athlete_name = st.text_input("Athlete Name", key=f"name{key_suffix}")
                dob = st.date_input("Date of Birth", min_value=date(1960,1,1),
                                    max_value=date.today(), key=f"dob{key_suffix}")
                sex = st.selectbox("Sex", ["Male", "Female"], key=f"sex{key_suffix}")
                code = st.text_input("Player Code", key=f"code{key_suffix}")
                belt = st.selectbox("Belt Degree", belt_options, key=f"belt{key_suffix}")

                federation_champs = [
                    "African Open Traditional Karate Championship",
                    "North Africa Unitied Karate Championship (General)"
                ]

                if st.session_state.selected_championship in federation_champs:
                    federation = st.selectbox(
                        "Select Federation",
                        ["Egyptian Traditional Karate Federation", "United General Federation"],
                        key=f"fed{key_suffix}"
                    )
                    comp_list = ["Individual Kata","Kata Team","Individual Kumite","Fuko Go",
                                 "Inbo Mix","Inbo Male","Inbo Female","Kumite Team"] \
                        if federation=="Egyptian Traditional Karate Federation" else \
                        ["Individual Kata","Kata Team","Kumite Ibon","Kumite Nihon",
                         "Kumite Sanbon","Kumite Rote Shine"]
                else:
                    federation = ""
                    comp_list = ["Individual Kata","Kata Team","Individual Kumite","Fuko Go",
                                 "Inbo Mix","Inbo Male","Inbo Female","Kumite Team"]

                competitions = st.multiselect("Competitions", comp_list, key=f"comp{key_suffix}")

            athletes_data.append({
                "Athlete Name": athlete_name.strip(),
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

    # ---------------- Submit ----------------
    if st.button("Submit All"):

        df = load_data()
        error = False
        errors_list = []

        for athlete in athletes_data:
            name = athlete["Athlete Name"]
            code = athlete["Player Code"]
            belt = athlete["Belt Degree"]
            club = athlete["Club"]
            nationality = athlete["Nationality"]
            coach = athlete["Coach Name"]
            phone = athlete["Phone Number"]
            championship = athlete["Championship"]
            competitions = athlete["Competitions"]

            existing_codes = set(df[df["Championship"] == championship]["Player Code"].astype(str))
            if code and code in existing_codes:
                error = True

            if not name: error = True
            if not code: error = True
            if not belt: error = True
            if not club: error = True
            if not nationality: error = True
            if st.session_state.selected_championship != "African Master Course":
                if competitions.strip() == "": error = True
                if not coach: error = True
                if not phone: error = True

        if not error:
            for athlete in athletes_data:
                df = pd.concat([df, pd.DataFrame([athlete])], ignore_index=True)

            save_data(df)

            st.success(f"✅ {len(athletes_data)} players registered successfully!")

            # ---------- clear all dynamic fields ----------
            keys_to_clear = []
            for k in st.session_state.keys():
                if any(prefix in k for prefix in ["name_", "dob_", "nat_", "phone_", "sex_", "code_", "belt_", "comp_", "fed_"]):
                    keys_to_clear.append(k)
            for k in keys_to_clear:
                st.session_state[k] = ""

            for key in ["club","nationality","coach_name","phone_number"]:
                st.session_state[key] = ""

            st.session_state.submit_count += 1
            safe_rerun()

# ---------------- Admin Panel ----------------
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
        name = st.session_state.get("selected_championship","athletes").replace(" ","_")
        st.download_button(
            "📥 Download Excel",
            buffer,
            file_name=f"{name}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
