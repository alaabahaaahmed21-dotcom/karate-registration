import streamlit as st
import pandas as pd
from datetime import date
import io
from pathlib import Path
import requests

# ---------------- Google Sheet API ----------------
GOOGLE_SHEET_API = "https://script.google.com/macros/s/AKfycbyY6FaRazYHmDimh68UpOs2MY04Uc-t5LiI3B_CsYZIAuClBvQ2sBQYIf1unJN45aJU2g/exec"  

def save_to_google_sheet(row):
    try:
        r = requests.post(GOOGLE_SHEET_API, json=row)
        return r.status_code == 200
    except:
        return False

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
.image-row { display: flex; justify-content: center; gap: 10px; flex-wrap: nowrap; }
.image-row img { width: 80px; height: auto; }
</style>
""", unsafe_allow_html=True)

# ---------------- Page State ----------------
if "page" not in st.session_state:
    st.session_state.page = "select_championship"

DATA_FILE = Path("athletes_data.csv")

# ---------------- Bilingual Column Headers (English first) ----------------
BILINGUAL_COLS = {
    "Championship": "Championship / البطولة",
    "Athlete Name": "Athlete Name / اسم اللاعب", 
    "Club": "Club / النادي",
    "Nationality": "Nationality / الجنسية",
    "Coach Name": "Coach Name / اسم المدرب",
    "Phone Number": "Phone Number / رقم الهاتف",
    "Date of Birth": "Date of Birth / تاريخ الميلاد",
    "Sex": "Sex / الجنس",
    "Player Code": "Player Code / كود اللاعب",
    "Belt Degree": "Belt Degree / درجة الحزام",
    "Competitions": "Competitions / البطولات",
    "Federation": "Federation / الاتحاد"
}

# Bilingual Form Labels (English first)
BILINGUAL_LABELS = {
    "Athlete Name": "Athlete Name / اسم اللاعب",
    "Club": "Club / النادي", 
    "Nationality": "Nationality / الجنسية",
    "Coach Name": "Coach Name / اسم المدرب",
    "Phone Number": "Phone Number / رقم الهاتف",
    "Date of Birth": "Date of Birth / تاريخ الميلاد",
    "Sex": "Sex / الجنس",
    "Player Code": "Player Code / كود اللاعب",
    "Belt Degree": "Belt Degree / درجة الحزام",
    "Competitions": "Competitions / البطولات",
    "Federation": "Federation / الاتحاد",
    "Enter Club for all players": "Enter Club for all players / أدخل النادي لجميع اللاعبين",
    "Enter Nationality for all players": "Enter Nationality for all players / أدخل الجنسية لجميع اللاعبين", 
    "Enter Coach Name for all players": "Enter Coach Name for all players / أدخل اسم المدرب لجميع اللاعبين",
    "Enter Phone Number for the Coach": "Enter Phone Number for the Coach / أدخل رقم هاتف المدرب",
    "Number of players to add:": "Number of players to add: / عدد اللاعبين المراد إضافتهم",
    "Choose course type:": "Choose course type: / اختر نوع الدورة",
    "Select Federation": "Select Federation / اختر الاتحاد"
}

# ---------------- Load Data ----------------
def load_data():
    cols = list(BILINGUAL_COLS.keys())
    if DATA_FILE.exists():
        df = pd.read_csv(DATA_FILE)
        for c in cols:
            if c not in df.columns:
                df[c] = ""
        # Rename columns for display
        display_df = df.copy()
        display_df.rename(columns=BILINGUAL_COLS, inplace=True)
        return df, display_df
    return pd.DataFrame(columns=cols), pd.DataFrame(columns=list(BILINGUAL_COLS.values()))

# ---------------- Save Data ----------------
def save_data(df):
    new_rows = df.tail(len(athletes_data))
    df.to_csv(DATA_FILE, index=False)
    
    for _, row in new_rows.iterrows():
        ok = save_to_google_sheet({
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
            "Federation": row["Federation"]
        })
        if not ok:
            st.warning("⚠️ Failed to save some records to Google Sheets.")

# ---------------- Defaults ----------------
for key in ["club", "nationality", "coach_name", "phone_number", "submit_count", "num_players"]:
    if key not in st.session_state:
        st.session_state[key] = "" if key not in ["submit_count","num_players"] else 0

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
        "Please select the championship / يرجى اختيار البطولة المراد التسجيل فيها:",
        [
            "African Master Course",
            "African Open Traditional Karate Championship",
            "North Africa Unitied Karate Championship (General)"
        ]
    )

    if st.button("Next ➜ "):
        st.session_state.selected_championship = championship
        st.session_state.page = "registration"
        safe_rerun()

    st.stop()

# =====================================================
# PAGE 2 — Registration
# =====================================================
if st.session_state.page == "registration":
    if st.button("⬅ Back to Championship Selection / رجوع لاختيار البطولة"):
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
        course_type = st.selectbox(BILINGUAL_LABELS["Choose course type:"], ["Master", "General"])
        st.session_state.club = st.text_input(BILINGUAL_LABELS["Enter Club for all players"], value=st.session_state.club)
        num_players = st.number_input(BILINGUAL_LABELS["Number of players to add:"], min_value=1, value=1)

        belt_options = [
            "Kyu Junior yellow 10","Kyu Junior yellow 9","Kyu Junior orange 8","Kyu Junior orange green 7",
            "Kyu Junior green 6","Kyu Junior green blue 5","Kyu Junior blue 4","Kyu Junior blue 3",
            "Kyu Junior brown 2","Kyu Junior brown 1","Kyu Senior yellow 7","Kyu Senior yellow 6",
            "Kyu Senior orange 5","Kyu Senior orange 4","Kyu Senior green 3","Kyu Senior blue 2",
            "Kyu Senior brown 1","Dan 1","Dan 2","Dan 3","Dan 4","Dan 5","Dan 6","Dan 7","Dan 8"
        ]

        for i in range(num_players):
            key_suffix = f"_{submit_count}_{i}"
            with st.expander(f"Player {i+1} / اللاعب {i+1}"):
                athlete_name = st.text_input(BILINGUAL_LABELS["Athlete Name"], key=f"name{key_suffix}")
                dob = st.date_input(BILINGUAL_LABELS["Date of Birth"], min_value=date(1960,1,1),
                                    max_value=date.today(), key=f"dob{key_suffix}")
                nationality = st.text_input(BILINGUAL_LABELS["Nationality"], key=f"nat{key_suffix}")
                phone = st.text_input(BILINGUAL_LABELS["Phone Number"], key=f"phone{key_suffix}")
                sex = st.selectbox(BILINGUAL_LABELS["Sex"], ["Male", "Female"], key=f"sex{key_suffix}")
                code = st.text_input(BILINGUAL_LABELS["Player Code"], key=f"code{key_suffix}")
                belt = st.selectbox(BILINGUAL_LABELS["Belt Degree"], belt_options, key=f"belt{key_suffix}")

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
                    "index": i,
                    "Championship": f"African Master Course - {course_type}"
                })

    # ------------------------------------------------------------
    # Other Championships
    # ------------------------------------------------------------
    else:
        st.session_state.club = st.text_input(BILINGUAL_LABELS["Enter Club for all players"], value=st.session_state.club)
        st.session_state.nationality = st.text_input(BILINGUAL_LABELS["Enter Nationality for all players"], value=st.session_state.nationality)
        st.session_state.coach_name = st.text_input(BILINGUAL_LABELS["Enter Coach Name for all players"], value=st.session_state.coach_name)
        st.session_state.phone_number = st.text_input(BILINGUAL_LABELS["Enter Phone Number for the Coach"], value=st.session_state.phone_number)
        num_players = st.number_input(BILINGUAL_LABELS["Number of players to add:"], min_value=1, value=1)

        belt_options = [
            "Kyu Junior yellow 10","Kyu Junior yellow 9","Kyu Junior orange 8","Kyu Junior orange green 7",
            "Kyu Junior green 6","Kyu Junior green blue 5","Kyu Junior blue 4","Kyu Junior blue 3",
            "Kyu Junior brown 2","Kyu Junior brown 1","Kyu Senior yellow 7","Kyu Senior yellow 6",
            "Kyu Senior orange 5","Kyu Senior orange 4","Kyu Senior green 3","Kyu Senior blue 2",
            "Kyu Senior brown 1","Dan 1","Dan 2","Dan 3","Dan 4","Dan 5","Dan 6","Dan 7","Dan 8"
        ]

        for i in range(num_players):
            key_suffix = f"_{submit_count}_{i}"
            with st.expander(f"Player {i+1} / اللاعب {i+1}"):
                athlete_name = st.text_input(BILINGUAL_LABELS["Athlete Name"], key=f"name{key_suffix}")
                dob = st.date_input(BILINGUAL_LABELS["Date of Birth"], min_value=date(1960,1,1),
                                    max_value=date.today(), key=f"dob{key_suffix}")
                sex = st.selectbox(BILINGUAL_LABELS["Sex"], ["Male", "Female"], key=f"sex{key_suffix}")
                code = st.text_input(BILINGUAL_LABELS["Player Code"], key=f"code{key_suffix}")
                belt = st.selectbox(BILINGUAL_LABELS["Belt Degree"], belt_options, key=f"belt{key_suffix}")

                federation_champs = [
                    "African Open Traditional Karate Championship",
                    "North Africa Unitied Karate Championship (General)"
                ]
                if st.session_state.selected_championship in federation_champs:
                    federation = st.selectbox(
                        BILINGUAL_LABELS["Select Federation"],
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

                competitions = st.multiselect(BILINGUAL_LABELS["Competitions"], comp_list, key=f"comp{key_suffix}")

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
                    "index": i,
                    "Championship": st.session_state.selected_championship
                })

# ---------------- Submit ----------------
if st.button("Submit All / إرسال الكل"):
    df, display_df = load_data()
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
        competitions = athlete["Competitions"]
        championship = athlete["Championship"]

        existing_codes = set(df[df["Championship"] == championship]["Player Code"].astype(str))
        if code and code in existing_codes:
            errors_list.append(f"Player Code '{code}' already exists / كود اللاعب '{code}' موجود مسبقاً!")
            error = True

        if not name: error = True; errors_list.append("Athlete name is required / اسم اللاعب مطلوب.")
        if not code: error = True; errors_list.append("Player code is required / كود اللاعب مطلوب.")
        if not belt: error = True; errors_list.append("Belt degree is required / درجة الحزام مطلوبة.")
        if not club: error = True; errors_list.append("Club is required / النادي مطلوب.")
        if not nationality: error = True; errors_list.append("Nationality is required / الجنسية مطلوبة.")
        if st.session_state.selected_championship != "African Master Course":
            if competitions.strip() == "": error=True; errors_list.append("At least one competition is required / يجب اختيار مسابقة واحدة على الأقل.")
            if not coach: error=True; errors_list.append("Coach name is required / اسم المدرب مطلوب.")
        if not phone: error = True; errors_list.append("Phone number is required / رقم الهاتف مطلوب.")

    if error:
        st.error("Fix the following issues / يجب تصحيح الأخطاء التالية:")
        for m in errors_list:
            st.write("- ", m)
        st.stop()

    for athlete in athletes_data:
        df = pd.concat([df, pd.DataFrame([athlete])], ignore_index=True)

    save_data(df)
    st.success(f"✅ {len(athletes_data)} players registered successfully / تم تسجيل {len(athletes_data)} لاعب بنجاح!")

    for key in ["club","nationality","coach_name","phone_number"]:
        st.session_state[key] = ""
    st.session_state.submit_count += 1

    for i in range(num_players):
        key_suffix = f"_{st.session_state.submit_count}_{i}"
        for k in ["name","dob","sex","code","belt","comp","fed","nat","phone"]:
            k_full = f"{k}{key_suffix}"
            if k_full in st.session_state:
                st.session_state[k_full] = "" if k not in ["sex","dob"] else st.session_state[k_full]

    safe_rerun()

# ---------------- Admin Panel ----------------
st.sidebar.header("Admin Login")
admin_password = st.sidebar.text_input("Enter Admin Password", type="password")
if admin_password == "mobadr90":
    st.sidebar.success("Logged in as Admin ✅ / تم تسجيل الدخول كأدمن ✅")
    df, display_df = load_data()
    if df.empty:
        st.info("No data yet")
    else:
        # Use column_config for bilingual headers in admin panel
        column_config = {}
        for eng_col, bi_col in BILINGUAL_COLS.items():
            if eng_col in display_df.columns:
                column_config[eng_col] = st.column_config.TextColumn(bi_col)
        
        st.dataframe(display_df, use_container_width=True, column_config=column_config)
        
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