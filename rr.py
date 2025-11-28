import streamlit as st
import pandas as pd
from datetime import date
import io
import requests

# ---------------------- GOOGLE SHEET API ----------------------
GOOGLE_SHEET_API = "https://script.google.com/macros/s/AKfycbyY6FaRazYHmDimh68UpOs2MY04Uc-t5LiI3B_CsYZIAuClBvQ2sBQYIf1unJN45aJU2g/exec"

def save_to_google_sheet(row):
    """Send a single row (dict) to Google Sheets via Apps Script Web App"""
    try:
        r = requests.post(GOOGLE_SHEET_API, json=row)
        return r.status_code == 200
    except Exception as e:
        st.error(f"Error saving to Google Sheets: {e}")
        return False

def upload_image_to_drive(image_file):
    """Upload image as Base64 to Google Apps Script"""
    if image_file is None:
        return ""
    try:
        import base64
        encoded_string = base64.b64encode(image_file.read()).decode()
        payload = {
            "imageBase64": encoded_string,
            "imageType": image_file.type,
            "imageName": image_file.name
        }
        r = requests.post(GOOGLE_SHEET_API, json=payload)
        if r.status_code == 200:
            return r.json().get("imageUrl", "")
        else:
            return ""
    except Exception as e:
        st.warning(f"Failed to upload image: {e}")
        return ""

# ---------------------- Safe Rerun ----------------------
def safe_rerun():
    try:
        if hasattr(st, "rerun"):
            st.rerun()
        elif hasattr(st, "experimental_rerun"):
            st.experimental_rerun()
    except:
        pass

# ---------------------- Session Defaults ----------------------
if "page" not in st.session_state:
    st.session_state.page = "select_championship"

if "submit_count" not in st.session_state:
    st.session_state.submit_count = 0

if "club" not in st.session_state:
    st.session_state.club = ""

if "nationality" not in st.session_state:
    st.session_state.nationality = ""

if "coach_name" not in st.session_state:
    st.session_state.coach_name = ""

if "phone_number" not in st.session_state:
    st.session_state.phone_number = ""

DATA_FILE = "athletes_data.csv"

def load_data():
    cols = [
        "Championship", "Athlete Name", "Club", "Nationality", "Coach Name",
        "Phone Number", "Date of Birth", "Sex", "Player Code",
        "Belt Degree", "Competitions", "Federation", "Profile Picture"
    ]
    try:
        df = pd.read_csv(DATA_FILE)
        for c in cols:
            if c not in df.columns:
                df[c] = ""
        return df[cols]
    except:
        return pd.DataFrame(columns=cols)

def save_data(df):
    df.to_csv(DATA_FILE, index=False)
    for _, row in df.iterrows():
        save_to_google_sheet({
            "Championship": row["Championship"],
            "Athlete Name": row["Athlete Name"],
            "Club": row["Club"],
            "Nationality": row["Nationality"],
            "Coach Name": row["Coach Name"],
            "Phone Number": row["Phone Number"],
            "Date of Birth": row["Date of Birth"],
            "Sex": row["Sex"],
            "Player Code": row["Player Code"],
            "Belt Degree": row["Belt Degree"],
            "Competitions": row["Competitions"],
            "Federation": row["Federation"],
            "Profile Picture": row["Profile Picture"]
        })

# ---------------------- Page 1: Select Championship ----------------------
if st.session_state.page == "select_championship":
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

# ---------------------- Page 2: Registration ----------------------
if st.session_state.page == "registration":
    if st.button("⬅ Back to Championship Selection"):
        st.session_state.page = "select_championship"
        safe_rerun()

    st.title(f"🏆 Registration Form: {st.session_state.selected_championship}")
    
    athletes_data = []
    submit_count = st.session_state.submit_count

    # ---------------------- Number of Players ----------------------
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
            dob = st.date_input("Date of Birth", min_value=date(1960,1,1), max_value=date.today(), key=f"dob{key_suffix}")
            sex = st.selectbox("Sex", ["Male", "Female"], key=f"sex{key_suffix}")
            code = st.text_input("Player Code", key=f"code{key_suffix}")
            belt = st.selectbox("Belt Degree", belt_options, key=f"belt{key_suffix}")
            competitions = st.text_input("Competitions", key=f"comp{key_suffix}")
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
                "Competitions": competitions.strip(),
                "Federation": "",
                "Profile Picture": upload_image_to_drive(pic) if pic else "",
                "index": i,
                "Championship": st.session_state.selected_championship
            })

# ---------------------- Submit ----------------------
if st.button("Submit All"):
    df = load_data()
    error = False
    errors_list = []

    # التحقق من التكرار والحقول المطلوبة
    for athlete in athletes_data:
        name = athlete["Athlete Name"]
        code = athlete["Player Code"]
        existing_codes = set(df[df["Championship"] == athlete["Championship"]]["Player Code"].astype(str))
        if code in existing_codes:
            errors_list.append(f"Player Code '{code}' already exists in {athlete['Championship']}!")
            error = True
        if not name:
            errors_list.append("Athlete name is required."); error=True
        if not code:
            errors_list.append("Player code is required."); error=True
        if not athlete["Club"]:
            errors_list.append("Club is required."); error=True

    if error:
        st.error("Fix the following issues:")
        for m in errors_list:
            st.write("- ", m)
        st.stop()

    # إضافة اللاعبين للـ CSV و Google Sheet
    for athlete in athletes_data:
        df = pd.concat([df, pd.DataFrame([athlete])], ignore_index=True)
    save_data(df)

    st.success(f"✅ {len(athletes_data)} players registered successfully!")

    # إعادة تهيئة الحقول بعد Submit
    st.session_state.submit_count += 1
    st.session_state.club = ""
    st.session_state.nationality = ""
    st.session_state.coach_name = ""
    st.session_state.phone_number = ""
    safe_rerun()

# ---------------------- Admin Panel ----------------------
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
        st.download_button(
            "📥 Download Excel",
            buffer,
            file_name="athletes.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
