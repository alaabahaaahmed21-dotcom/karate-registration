import streamlit as st
import pandas as pd
from datetime import date
import io
from pathlib import Path
import base64
import requests

# ---------------------- GitHub Auto Backup ----------------------
GITHUB_TOKEN = "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"   # ← ضعي التوكن هنا
GITHUB_REPO = "alaabahaaahmed21-dotcom/karate-registration"
GITHUB_FILE_PATH = "athletes_data.csv"

def get_github_file_sha():
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        return r.json()["sha"]
    return None

def upload_to_github(csv_text):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}"
    sha = get_github_file_sha()

    data = {
        "message": "Auto update from Streamlit app",
        "content": base64.b64encode(csv_text.encode()).decode(),
    }
    if sha:
        data["sha"] = sha

    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    requests.put(url, json=data, headers=headers)

# ---------------------- Safe Rerun ----------------------
def safe_rerun():
    try:
        if hasattr(st, "rerun"):
            try:
                st.rerun()
                return
            except Exception:
                pass

        if hasattr(st, "experimental_rerun"):
            try:
                st.experimental_rerun()
                return
            except Exception:
                pass

        st.error("❌ Streamlit version does not support rerun. Please upgrade Streamlit.")
    except Exception as fatal:
        st.error("Unexpected error during rerun:")
        st.exception(fatal)

# ---------------------- Logos ----------------------
img1 = "https://raw.githubusercontent.com/alaabahaaahmed21-dotcom/karate-registration/main/logo1.png"
img2 = "https://raw.githubusercontent.com/alaabahaaahmed21-dotcom/karate-registration/main/logo2.png"
img3 = "https://raw.githubusercontent.com/alaabahaaahmed21-dotcom/karate-registration/main/logo3.png"
img4 = "https://raw.githubusercontent.com/alaabahaaahmed21-dotcom/karate-registration/main/logo4.png"

# ---------------------- CSS ----------------------
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

# ---------------------- Page State ----------------------
if "page" not in st.session_state:
    st.session_state.page = "select_championship"

DATA_FILE = Path("athletes_data.csv")

# ---------------------- Load + Save ----------------------
def load_data():
    cols = [
        "Championship", "Athlete Name", "Club", "Nationality", "Coach Name",
        "Phone Number", "Date of Birth", "Sex", "Player Code",
        "Belt Degree", "Competitions", "Federation", "Profile Picture"
    ]

    if DATA_FILE.exists():
        df = pd.read_csv(DATA_FILE)
        for c in cols:
            if c not in df.columns:
                df[c] = ""
        return df[cols]

    return pd.DataFrame(columns=cols)

# -------- Replace save_data with GitHub backup version --------
def save_data(df):
    df.to_csv(DATA_FILE, index=False)   # حفظ محلي
    try:
        csv_txt = df.to_csv(index=False)
        upload_to_github(csv_txt)       # رفع لجيتهب
    except Exception as e:
        st.warning(f"GitHub Backup Failed: {e}")

# ---------------------- Defaults ----------------------
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
    # African Master Course
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
                pic = st.file_uploader("Profile Picture", type=["png","jpg","jpeg"], key=f"pic{key_suffix}")

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
                    "Profile Picture": pic.name if pic else "",
                    "index": i,
                    "Championship": f"African Master Course - {course_type}"
                })

    # ------------------------------------------------------------
    # Other Championships
    # ------------------------------------------------------------
    else:

        st.session_state.club = st.text_input("Enter Club for all players", value=st.session_state.club)
        st.session_state.nationality = st.text_input("Enter Nationality for all players", value=st.session_state.nationality)
        st.session_state.coach_name = st.text_input("Enter Coach Name for all players", value=st.session_state.coach_name)
        st.session_state.phone_number = st.text_input("Enter Phone Number for the Coach", value=st.session_state.phone_number)
        num_players = st.number_input("Number of players to add:", min_value=1, value=1)

        for i in range(num_players):
            key_suffix = f"_{submit_count}_{i}"
            with st.expander(f"Player {i+1}"):
                athlete_name = st.text_input("Athlete Name", key=f"name{key_suffix}")
                dob = st.date_input("Date of Birth", min_value=date(1960,1,1),
                                    max_value=date.today(), key=f"dob{key_suffix}")
                sex = st.selectbox("Sex", ["Male", "Female"], key=f"sex{key_suffix}")
                code = st.text_input("Player Code", key=f"code{key_suffix}")
                belt = st.selectbox("Belt Degree", [
                    "Kyu Junior yellow 10","Kyu Junior yellow 9","Kyu Junior orange 8","Kyu Junior orange green 7",
                    "Kyu Junior green 6","Kyu Junior green blue 5","Kyu Junior blue 4","Kyu Junior blue 3",
                    "Kyu Junior brown 2","Kyu Junior brown 1","Kyu Senior yellow 7","Kyu Senior yellow 6",
                    "Kyu Senior orange 5","Kyu Senior orange 4","Kyu Senior green 3","Kyu Senior blue 2",
                    "Kyu Senior brown 1","Dan 1","Dan 2","Dan 3","Dan 4","Dan 5","Dan 6","Dan 7","Dan 8"
                ], key=f"belt{key_suffix}")

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
                    if federation == "Egyptian Traditional Karate Federation":
                        comp_list = [
                            "Individual Kata","Kata Team","Individual Kumite","Fuko Go",
                            "Inbo Mix","Inbo Male","Inbo Female","Kumite Team"
                        ]
                    else:
                        comp_list = [
                            "Individual Kata","Kata Team","Kumite Ibon","Kumite Nihon",
                            "Kumite Sanbon","Kumite Rote Shine"
                        ]
                else:
                    federation = ""
                    comp_list = [
                        "Individual Kata","Kata Team","Individual Kumite","Fuko Go",
                        "Inbo Mix","Inbo Male","Inbo Female","Kumite Team"
                    ]

                competitions = st.multiselect("Competitions", comp_list, key=f"comp{key_suffix}")
                pic = st.file_uploader("Profile Picture", type=["png","jpg","jpeg"], key=f"pic{key_suffix}")

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
                    "Profile Picture": pic.name if pic else "",
                    "index": i,
                    "Championship": st.session_state.selected_championship
                })

# ------------------------------------------------------------
# SUBMIT BUTTON
# ------------------------------------------------------------
if st.session_state.page == "registration":

    if st.button("Submit All"):

        df = load_data()
        error = False
        errors_list = []

        current_champ_codes = set(
            df[df["Championship"] == st.session_state.selected_championship]["Player Code"].astype(str).values
        )

        for athlete in athletes_data:
            idx = athlete["index"]
            name = athlete["Athlete Name"]
            code = athlete["Player Code"]
            belt = athlete["Belt Degree"]
            comps = athlete.get("Competitions List", [])
            club = athlete["Club"]
            nationality = athlete["Nationality"]
            coach = athlete["Coach Name"]
            phone = athlete["Phone Number"]

            if not name:
                errors_list.append(f"Player #{idx+1}: Athlete Name is missing.")
                error = True
            if not code:
                errors_list.append(f"Player #{idx+1}: Player Code is missing.")
                error = True
            if not belt:
                errors_list.append(f"Player #{idx+1}: Belt Degree is missing.")
                error = True
            if st.session_state.selected_championship != "African Master Course" and comps == []:
                errors_list.append(f"Player #{idx+1}: Select at least one competition.")
                error = True
            if not club:
                errors_list.append(f"Player #{idx+1}: Club is missing.")
                error = True
            if not nationality:
                errors_list.append(f"Player #{idx+1}: Nationality is missing.")
                error = True
            if not coach and st.session_state.selected_championship != "African Master Course":
                errors_list.append(f"Player #{idx+1}: Coach Name is missing.")
                error = True
            if not phone:
                errors_list.append(f"Player #{idx+1}: Phone Number is missing.")
                error = True

            if code and code in current_champ_codes:
                errors_list.append(f"Player #{idx+1}: Code '{code}' already exists!")
                error = True
            else:
                current_champ_codes.add(code)

        batch_codes = [a["Player Code"] for a in athletes_data if a["Player Code"]]
        dupes = {c for c in batch_codes if batch_codes.count(c) > 1}
        for d in dupes:
            idxs = [i+1 for i,a in enumerate(athletes_data) if a["Player Code"] == d]
            errors_list.append(f"Duplicate code '{d}' in players {idxs}.")
            error = True

        if error:
            st.error("⚠️ Fix errors before submitting:")
            for m in errors_list:
                st.write("-", m)
            st.stop()

        for athlete in athletes_data:
            df = pd.concat([df, pd.DataFrame([athlete])], ignore_index=True)
        save_data(df)

        st.success(f"✅ {len(athletes_data)} players registered successfully!")

        for key in ["club", "nationality", "coach_name", "phone_number"]:
            st.session_state[key] = ""

        for k in list(st.session_state.keys()):
            if any(x in k for x in ["name_","dob_","sex_","code_","belt_","comp_","pic_","fed_","nat_","phone_"]):
                del st.session_state[k]

        st.session_state.submit_count += 1
        st.rerun()

# ---------------------- ADMIN PANEL ----------------------
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