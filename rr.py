import streamlit as st
import pandas as pd
from datetime import date
import io
from pathlib import Path
import requests

# =====================================================
# ---------------- Google Sheet API -------------------
# =====================================================

GOOGLE_SHEET_API = "https://script.google.com/macros/s/AKfycbyY6FaRazYHmDimh68UpOs2MY04Uc-t5LiI3B_CsYZIAuClBvQ2sBQYIf1unJN45aJU2g/exec"

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

    # Send only the last added row (one row)
    if not df.empty:
        last_row = df.iloc[-1].to_dict()
        save_to_google_sheet(last_row)




# =====================================================
# ---------------- Logos ------------------------------
# =====================================================

img1 = "https://raw.githubusercontent.com/alaabahaaahmed21-dotcom/karate-registration/main/logo1.png"
img2 = "https://raw.githubusercontent.com/alaabahaaahmed21-dotcom/karate-registration/main/logo2.png"
img3 = "https://raw.githubusercontent.com/alaabahaaahmed21-dotcom/karate-registration/main/logo3.png"
img4 = "https://raw.githubusercontent.com/alaabahaaahmed21-dotcom/karate-registration/main/logo4.png"

# =====================================================
# ---------------- CSS --------------------------------
# =====================================================

st.markdown("""
<style>
.image-row { display: flex; justify-content: center; gap: 10px; flex-wrap: nowrap; }
.image-row img { width: 80px; height: auto; }
</style>
""", unsafe_allow_html=True)

# =====================================================
# ---------------- Page State --------------------------
# =====================================================

if "page" not in st.session_state:
    st.session_state.page = "select_championship"

DATA_FILE = Path("athletes_data.csv")

# =====================================================
# ---------------- Bilingual headers -------------------
# =====================================================

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
    "Competitions": "Competitions / المسابقات",
    "Federation": "Federation / الاتحاد"
}

# =====================================================
# ---------------- Form Labels -------------------------
# =====================================================

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
    "Competitions": "Competitions / المسابقات",
    "Federation": "Federation / الاتحاد",
    "Enter Club for all players": "Enter Club for all players / أدخل النادي لجميع اللاعبين",
    "Enter Nationality for all players": "Enter Nationality for all players / أدخل الجنسية لجميع اللاعبين",
    "Enter Coach Name for all players": "Enter Coach Name  / أدخل اسم المدرب",
    "Enter Phone Number for the Coach": "Enter Phone Number for the Coach / أدخل رقم هاتف المدرب",
    "Number of players to add:": "Number of players to add: / عدد اللاعبين المراد إضافتهم",
    "Choose course type:": "Choose course type: / اختر نوع الدورة",
    "Select Federation": "Select Federation / اختر الاتحاد"
}

# =====================================================
# ---------------- Load Data ---------------------------
# =====================================================

def load_data():
    cols = list(BILINGUAL_COLS.keys())
    if DATA_FILE.exists():
        df = pd.read_csv(DATA_FILE)
        for c in cols:
            if c not in df.columns:
                df[c] = ""
        display_df = df.copy()
        display_df.rename(columns=BILINGUAL_COLS, inplace=True)
        return df, display_df
    return pd.DataFrame(columns=cols), pd.DataFrame(columns=list(BILINGUAL_COLS.values()))


# =====================================================
# ---------------- Initialize Session State ------------
# =====================================================

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

# =====================================================
# ================= PAGE 1 =============================
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
        "Please select the championship / يرجى اختيار البطولة:",
        [
            "African Master Course / الماستر كورس الافريقى",
            "African Open Traditional Karate Championship / بطولة افريقيا المفتوحة للكاراتيه التقليدي",
            "North Africa United Karate Championship / بطولة شمال افريقيا للكارتيه الموحد"
        ]
    )

    if st.button("Next/التالي ➜"):
        st.session_state.selected_championship = championship
        st.session_state.page = "registration"
        safe_rerun()

    st.stop()

# =====================================================
# ================= PAGE 2 — Registration =============
# =====================================================

if st.session_state.page == "registration":

    if st.button("⬅ Back / رجوع"):
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
        f"<h3>🏆 Registration Form: {st.session_state.selected_championship}</h3>",
        unsafe_allow_html=True
    )

    athletes_data = []

    # ✅ Fixed: submit_count مباشرة من session_state
    submit_count = st.session_state.submit_count

    if st.session_state.selected_championship.startswith("African Master Course"):

        course_type = st.selectbox(BILINGUAL_LABELS["Choose course type:"], ["Master / ماستر ", "General / جنرال"])
        st.session_state.club = st.text_input(BILINGUAL_LABELS["Enter Club for all players"], value=st.session_state.club)
        num_players = st.number_input(BILINGUAL_LABELS["Number of players to add:"], min_value=1, value=1)

        belt_options = [
            "Kyu Junior yellow 10 / أصفر 10 كيو ناشئين", "Kyu Junior yellow 9 / أصفر 9 كيو ناشئين",
            "Kyu Junior orange 8 / برتقالي 8 كيو ناشئين", "Kyu Junior orange green 7 / برتقالي أخضر 7 كيو ناشئين",
            "Kyu Junior green 6 / أخضر 6 كيو ناشئين", "Kyu Junior green blue 5 / أخضر أزرق 5 كيو ناشئين",
            "Kyu Junior blue 4 / أزرق 4 كيو ناشئين", "Kyu Junior blue 3 / أزرق 3 كيو ناشئين",
            "Kyu Junior brown 2 / بني 2 كيو ناشئين", "Kyu Junior brown 1 / بني 1 كيو ناشئين",
            "Kyu Senior yellow 7 / أصفر 7 كيو كبار", "Kyu Senior yellow 6 / أصفر 6 كيو كبار",
            "Kyu Senior orange 5 / برتقالي 5 كيو كبار", "Kyu Senior orange 4 / برتقالي 4 كيو كبار",
            "Kyu Senior green 3 / أخضر 3 كيو كبار", "Kyu Senior blue 2 / أزرق 2 كيو كبار",
            "Kyu Senior brown 1 / بني 1 كيو كبار",
            "Dan 1 / دان 1", "Dan 2 / دان 2", "Dan 3 / دان 3", "Dan 4 / دان 4",
            "Dan 5 / دان 5", "Dan 6 / دان 6", "Dan 7 / دان 7", "Dan 8 / دان 8"
        ]

        for i in range(num_players):
            suffix = f"_{submit_count}_{i}"
            with st.expander(f"Player {i+1}"):
                athlete_name = st.text_input(BILINGUAL_LABELS["Athlete Name"], key=f"name{suffix}")
                dob = st.date_input(BILINGUAL_LABELS["Date of Birth"], min_value=date(1960,1,1), max_value=date.today(), key=f"dob{suffix}")
                nationality = st.text_input(BILINGUAL_LABELS["Nationality"], key=f"nat{suffix}")
                phone = st.text_input(BILINGUAL_LABELS["Phone Number"], key=f"phone{suffix}")
                sex = st.selectbox(BILINGUAL_LABELS["Sex"], ["Male / ذكر", "Female / انثى"], key=f"sex{suffix}")
                code = st.text_input(BILINGUAL_LABELS["Player Code"], key=f"code{suffix}")
                belt = st.selectbox(BILINGUAL_LABELS["Belt Degree"], belt_options, key=f"belt{suffix}")

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
        st.session_state.club = st.text_input(BILINGUAL_LABELS["Enter Club for all players"], value=st.session_state.club)
        st.session_state.nationality = st.text_input(BILINGUAL_LABELS["Enter Nationality for all players"], value=st.session_state.nationality)
        st.session_state.coach_name = st.text_input(BILINGUAL_LABELS["Enter Coach Name for all players"], value=st.session_state.coach_name)
        st.session_state.phone_number = st.text_input(BILINGUAL_LABELS["Enter Phone Number for the Coach"], value=st.session_state.phone_number)
        num_players = st.number_input(BILINGUAL_LABELS["Number of players to add:"], min_value=1, value=1)

        belt_options = [
            "Kyu Junior yellow 10 / أصفر 10 كيو ناشئين", "Kyu Junior yellow 9 / أصفر 9 كيو ناشئين",
            "Kyu Junior orange 8 / برتقالي 8 كيو ناشئين", "Kyu Junior orange green 7 / برتقالي أخضر 7 كيو ناشئين",
            "Kyu Junior green 6 / أخضر 6 كيو ناشئين", "Kyu Junior green blue 5 / أخضر أزرق 5 كيو ناشئين",
            "Kyu Junior blue 4 / أزرق 4 كيو ناشئين", "Kyu Junior blue 3 / أزرق 3 كيو ناشئين",
            "Kyu Junior brown 2 / بني 2 كيو ناشئين", "Kyu Junior brown 1 / بني 1 كيو ناشئين",
            "Kyu Senior yellow 7 / أصفر 7 كيو كبار", "Kyu Senior yellow 6 / أصفر 6 كيو كبار",
            "Kyu Senior orange 5 / برتقالي 5 كيو كبار", "Kyu Senior orange 4 / برتقالي 4 كيو كبار",
            "Kyu Senior green 3 / أخضر 3 كيو كبار", "Kyu Senior blue 2 / أزرق 2 كيو كبار",
            "Kyu Senior brown 1 / بني 1 كيو كبار",
            "Dan 1 / دان 1", "Dan 2 / دان 2", "Dan 3 / دان 3", "Dan 4 / دان 4",
            "Dan 5 / دان 5", "Dan 6 / دان 6", "Dan 7 / دان 7", "Dan 8 / دان 8"
        ]

        egyptian_competitions = [
            "Individual Kata / كاتا فردي", "Kata Team / كاتا جماعي", "Individual Kumite / كوميتيه فردي",
            "Fuko Go / فوكو جو", "Inbo Mix / إنبو مختلط", "Inbo Male / إنبو ذكور", "Inbo Female / إنبو إناث",
            "Kumite Team /كوميتيه جماعي "
        ]

        united_general_competitions = [
            "Individual Kata / كاتا فردي", "Kata Team / كاتا جماعي",
            "Kumite Ibon / كوميتيه إيبون", "Kumite Nihon / كوميتيه نيهون",
            "Kumite Sanbon / كوميتيه سانبون", "Kumite Rote Shine / كوميتيه روت شاين"
        ]

        for i in range(num_players):
            suffix = f"_{submit_count}_{i}"
            with st.expander(f"Player {i+1}"):
                athlete_name = st.text_input(BILINGUAL_LABELS["Athlete Name"], key=f"name{suffix}")
                dob = st.date_input(BILINGUAL_LABELS["Date of Birth"], min_value=date(1960,1,1), max_value=date.today(), key=f"dob{suffix}")
                sex = st.selectbox(BILINGUAL_LABELS["Sex"], ["Male / ذكر", "Female / انثى"], key=f"sex{suffix}")
                code = st.text_input(BILINGUAL_LABELS["Player Code"], key=f"code{suffix}")
                belt = st.selectbox(BILINGUAL_LABELS["Belt Degree"], belt_options, key=f"belt{suffix}")

                federation = ""
                comp_list = []

                federation_champs = [
                    "African Open Traditional Karate Championship / بطولة افريقيا المفتوحة للكاراتيه التقليدي",
                    "North Africa United Karate Championship / بطولة شمال افريقيا للكارتيه الموحد"
                ]

                if st.session_state.selected_championship in federation_champs:
                    federation = st.selectbox(
                        BILINGUAL_LABELS["Select Federation"],
                        ["Egyptian Traditional Karate Federation / الاتحاد المصري للكاراتيه التقليدي", 
                         "United General Committee / لجنة الجنرال الموحد"],
                        key=f"fed{suffix}"
                    )
                    comp_list = egyptian_competitions if "Egyptian" in federation else united_general_competitions
                else:
                    comp_list = ["Individual Kata / كاتا فردي","Kata Team / كاتا جماعي","Individual Kumite / كوميتيه فردي",
                                "Fuko Go / فوكو جو","Inbo Mix / إنبو مختلط","Inbo Male / إنبو ذكور",
                                "Inbo Female / إنبو إناث","Kumite Team / كوميتيه جماعي"]

                competitions = st.multiselect(BILINGUAL_LABELS["Competitions"], comp_list, key=f"comp{suffix}")

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

    # =====================================================
    # ---------------- Submit Button - ✅ Fixed 100% --------
    # =====================================================
    if st.button("Submit All / إرسال الكل") and athletes_data:

        df, _ = load_data()
        errors = []

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
                errors.append(f"❌ Player Code '{code}' already exists!")
            
            if not name: errors.append("❌ Athlete name is required.")
            if not code: errors.append("❌ Player code is required.")
            if not belt: errors.append("❌ Belt degree is required.")
            if not club: errors.append("❌ Club is required.")
            if not nationality: errors.append("❌ Nationality is required.")
            if not phone: errors.append("❌ Phone number is required.")
            
            if not championship.startswith("African Master Course"):
                if not competitions: errors.append("❌ At least one competition is required.")
                if not coach: errors.append("❌ Coach name is required.")

        if errors:
            st.error("Fix the following errors:")
            for e in errors:
                st.write("-", e)
        else:
            for athlete in athletes_data:
                df = pd.concat([df, pd.DataFrame([athlete])], ignore_index=True)

            save_data(df)
            st.success(f"✅ {len(athletes_data)} players registered successfully!")

            # ✅ Fixed: مباشرة من session_state بدون متغير وسيط
            st.session_state.submit_count += 1
            st.session_state.club = ""
            st.session_state.nationality = ""
            st.session_state.coach_name = ""
            st.session_state.phone_number = ""
            
            safe_rerun()

# =====================================================
# ---------------- Admin Panel -------------------------
# =====================================================

st.sidebar.header("Admin Login")
admin_password = st.sidebar.text_input("Enter Admin Password", type="password")

if admin_password == "mobadr90":
    st.sidebar.success("Logged in as Admin")
    df, display_df = load_data()
    if not df.empty:
        column_config = {
            bi_col: st.column_config.TextColumn(bi_col)
            for eng_col, bi_col in BILINGUAL_COLS.items()
            if bi_col in display_df.columns
        }
        st.dataframe(display_df, use_container_width=True, column_config=column_config)

        try:
            buffer = io.BytesIO()
            df.to_excel(buffer, index=False, engine="openpyxl")
            buffer.seek(0)
            filename = st.session_state.get("selected_championship", "athletes").replace(" ", "_")
            st.download_button(
                "📥 Download Excel", buffer.getvalue(),
                file_name=f"{filename}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except ImportError:
            st.warning("📦 Install openpyxl: `pip install openpyxl`")
else:
    st.sidebar.warning("Not logged in.")
