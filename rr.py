import streamlit as st
import pandas as pd
from datetime import date, datetime
import io
from pathlib import Path
import requests
import logging
import re
import hashlib
from streamlit.crypto import Crypto  # للتشفير

# =====================================================
# ---------------- إعدادات الـ Logging -----------------
# =====================================================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =====================================================
# ---------------- Google Sheet API -------------------
# =====================================================
GOOGLE_SHEET_API = st.secrets.get("GOOGLE_SHEET_API", "https://script.google.com/macros/s/AKfycbyY6FaRazYHmDimh68UpOs2MY04Uc-t5LiI3B_CsYZIAuClBvQ2sBQYIf1unJN45aJU2g/exec")

def save_to_google_sheet(row, championship):
    """✅ تحسين: إرسال فقط البيانات الجديدة مع logging"""
    try:
        # إضافة timestamp وchampionship لتجنب التكرار
        row_with_meta = row.copy()
        row_with_meta['timestamp'] = datetime.now().isoformat()
        row_with_meta['championship'] = championship
        
        r = requests.post(GOOGLE_SHEET_API, json=row_with_meta, timeout=10)
        if r.status_code == 200:
            logger.info(f"✅ Google Sheet saved: {row['Athlete Name']}")
            return True
        else:
            logger.error(f"❌ Google Sheet failed: {r.status_code} - {r.text}")
            return False
    except Exception as e:
        logger.error(f"❌ Google Sheet error: {str(e)}")
        return False

def safe_rerun():
    """✅ تحسين: استخدام st.rerun() الحديث فقط"""
    try:
        st.rerun()
    except:
        st.experimental_rerun()

# =====================================================
# ---------------- الأمان - تشفير كلمة المرور ---------
# =====================================================
def hash_password(password):
    """تشفير كلمة المرور"""
    return hashlib.sha256(password.encode()).hexdigest()

ADMIN_HASH = hash_password("mobadr90")  # في الإنتاج: استخدم st.secrets["ADMIN_HASH"]

# =====================================================
# ---------------- Validation Functions --------------
# =====================================================
PHONE_REGEX = r'^\+?[\d\s\-\(\)]{10,15}$'
CODE_REGEX = r'^[A-Z0-9\-_]{3,20}$'

def validate_phone(phone):
    return bool(re.match(PHONE_REGEX, phone))

def validate_code(code):
    return bool(re.match(CODE_REGEX, code))

def validate_age(dob):
    age = date.today().year - dob.year
    return 5 <= age <= 80  # حدود منطقية للاعبي الكاراتيه

# =====================================================
# ---------------- Logos ------------------------------
# =====================================================
@st.cache_data
def load_logos():
    return {
        "img1": "https://raw.githubusercontent.com/alaabahaaahmed21-dotcom/karate-registration/main/logo1.png",
        "img2": "https://raw.githubusercontent.com/alaabahaaahmed21-dotcom/karate-registration/main/logo2.png",
        "img3": "https://raw.githubusercontent.com/alaabahaaahmed21-dotcom/karate-registration/main/logo3.png",
        "img4": "https://raw.githubusercontent.com/alaabahaaahmed21-dotcom/karate-registration/main/logo4.png"
    }

# =====================================================
# ---------------- CSS تحسين UI ----------------------
# =====================================================
st.markdown("""
<style>
.image-row { 
    display: flex; 
    justify-content: center; 
    gap: 15px; 
    flex-wrap: nowrap; 
    margin-bottom: 20px;
}
.image-row img { 
    width: 90px; 
    height: auto; 
    border-radius: 10px;
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}
.stExpander > div > div {
    border-radius: 10px;
    border: 1px solid #ddd;
}
.success-box {
    background-color: #d4edda;
    border: 1px solid #c3e6cb;
    border-radius: 5px;
    padding: 10px;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# ---------------- Page State -------------------------
# =====================================================
if "page" not in st.session_state:
    st.session_state.page = "select_championship"
    st.session_state.validation_errors = []

DATA_FILE = Path("athletes_data.csv")

# =====================================================
# ---------------- Bilingual headers ------------------
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
    "Federation": "Federation / الاتحاد",
    "Timestamp": "Timestamp / الوقت"
}

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
    "Enter Coach Name for all players": "Enter Coach Name / أدخل اسم المدرب",
    "Enter Phone Number for the Coach": "Enter Phone Number for the Coach / أدخل رقم هاتف المدرب",
    "Number of players to add:": "Number of players to add: / عدد اللاعبين المراد إضافتهم",
    "Choose course type:": "Choose course type: / اختر نوع الدورة",
    "Select Federation": "Select Federation / اختر الاتحاد"
}

# =====================================================
# ---------------- Load/Save Data (Cached) -----------
# =====================================================
@st.cache_data
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

def save_data(df):
    """✅ تحسين: حفظ موثوق مع logging"""
    try:
        df.to_csv(DATA_FILE, index=False)
        logger.info(f"✅ CSV saved: {len(df)} records")
        return True
    except Exception as e:
        logger.error(f"❌ CSV save failed: {str(e)}")
        return False

# =====================================================
# ================= PAGE 1: Championship ==============
# =====================================================
if st.session_state.page == "select_championship":
    logos = load_logos()
    
    st.markdown(f"""
    <div class="image-row">
        <img src="{logos['img1']}">
        <img src="{logos['img2']}">
        <img src="{logos['img3']}">
        <img src="{logos['img4']}">
    </div>
    """, unsafe_allow_html=True)

    st.title("🏆 Select Championship / اختر البطولة")
    
    championship = st.selectbox(
        "Please select the championship / يرجى اختيار البطولة:",
        [
            "African Master Course / الماستر كورس الافريقى",
            "African Open Traditional Karate Championship / بطولة افريقيا المفتوحة للكاراتيه التقليدي",
            "North Africa United Karate Championship / بطولة شمال افريقيا للكارتيه الموحد"
        ]
    )

    if st.button("Next/التالي ➜", type="primary"):
        st.session_state.selected_championship = championship
        st.session_state.page = "registration"
        st.session_state.validation_errors = []
        safe_rerun()
    st.stop()

# =====================================================
# ================= PAGE 2: Registration ==============
# =====================================================
if st.session_state.page == "registration":
    # Back button
    col1, col2 = st.columns([1, 8])
    with col1:
        if st.button("⬅ Back / رجوع"):
            st.session_state.page = "select_championship"
            safe_rerun()
    
    # Logos
    logos = load_logos()
    st.markdown(f"""
    <div class="image-row">
        <img src="{logos['img1']}">
        <img src="{logos['img2']}">
        <img src="{logos['img3']}">
        <img src="{logos['img4']}">
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        f"<h2>🏆 Registration Form: {st.session_state.selected_championship}</h2>",
        unsafe_allow_html=True
    )

    # Initialize defaults
    for key in ["club", "nationality", "coach_name", "phone_number"]:
        if key not in st.session_state:
            st.session_state[key] = ""

    athletes_data = []
    
    with st.spinner("جاري تحضير النموذج..."):
        # African Master Course
        if st.session_state.selected_championship.startswith("African Master Course"):
            course_type = st.selectbox(BILINGUAL_LABELS["Choose course type:"], 
                                     ["Master / ماستر", "General / جنرال"])
            
            st.session_state.club = st.text_input(
                BILINGUAL_LABELS["Enter Club for all players"], 
                value=st.session_state.club,
                help="النادي لجميع اللاعبين"
            )
            
            num_players = st.number_input(
                BILINGUAL_LABELS["Number of players to add:"], 
                min_value=1, max_value=20, value=1
            )

            belt_options = [  # اختصار للمساحة
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
                with st.expander(f"👤 Player {i+1} / اللاعب {i+1}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        athlete_name = st.text_input(
                            BILINGUAL_LABELS["Athlete Name"], 
                            key=f"name_mc_{i}"
                        )
                        dob = st.date_input(
                            BILINGUAL_LABELS["Date of Birth"], 
                            min_value=date(1960,1,1), 
                            max_value=date.today(),
                            key=f"dob_mc_{i}"
                        )
                    
                    with col2:
                        sex = st.selectbox(
                            BILINGUAL_LABELS["Sex"], 
                            ["Male / ذكر", "Female / انثى"], 
                            key=f"sex_mc_{i}"
                        )
                        code = st.text_input(
                            BILINGUAL_LABELS["Player Code"], 
                            key=f"code_mc_{i}",
                            help="مثال: EGY-001 أو LIB-ABC"
                        )
                    
                    belt = st.selectbox(
                        BILINGUAL_LABELS["Belt Degree"], 
                        belt_options, 
                        key=f"belt_mc_{i}"
                    )
                    
                    # Individual validation feedback
                    if code and not validate_code(code):
                        st.error("❌ كود اللاعب غير صحيح (3-20 حرف، أرقام وحروف كبيرة فقط)")
                    if dob and not validate_age(dob):
                        st.error("❌ العمر خارج النطاق (5-80 سنة)")

                    athletes_data.append({
                        "Athlete Name": athlete_name.strip(),
                        "Club": st.session_state.club.strip(),
                        "Nationality": "",
                        "Coach Name": "",
                        "Phone Number": "",
                        "Date of Birth": str(dob),
                        "Sex": sex,
                        "Player Code": code.strip(),
                        "Belt Degree": belt,
                        "Competitions": "",
                        "Federation": "",
                        "Championship": f"African Master Course - {course_type}",
                        "Timestamp": datetime.now().isoformat()
                    })

        # Other Championships
        else:
            col1, col2 = st.columns(2)
            with col1:
                st.session_state.club = st.text_input(
                    BILINGUAL_LABELS["Enter Club for all players"], 
                    value=st.session_state.club
                )
                st.session_state.nationality = st.text_input(
                    BILINGUAL_LABELS["Enter Nationality for all players"], 
                    value=st.session_state.get("nationality", "")
                )
            
            with col2:
                st.session_state.coach_name = st.text_input(
                    BILINGUAL_LABELS["Enter Coach Name for all players"], 
                    value=st.session_state.coach_name
                )
                st.session_state.phone_number = st.text_input(
                    BILINGUAL_LABELS["Enter Phone Number for the Coach"], 
                    value=st.session_state.phone_number,
                    help="مثال: +20123456789"
                )

            num_players = st.number_input(
                BILINGUAL_LABELS["Number of players to add:"], 
                min_value=1, max_value=20, value=1
            )

            # Competitions lists
            egyptian_competitions = [
                "Individual Kata / كاتا فردي", "Kata Team / كاتا جماعي",
                "Individual Kumite / كوميتيه فردي", "Fuko Go / فوكو جو",
                "Inbo Mix / إنبو مختلط", "Inbo Male / إنبو ذكور", 
                "Inbo Female / إنبو إناث", "Kumite Team / كوميتيه جماعي"
            ]
            
            united_competitions = [
                "Individual Kata / كاتا فردي", "Kata Team / كاتا جماعي",
                "Kumite Ibon / كوميتيه إيبون", "Kumite Nihon / كوميتيه نيهون",
                "Kumite Sanbon / كوميتيه سانبون", "Kumite Rote Shine / كوميتيه روت شاين"
            ]

            belt_options = [  # نفس القائمة المختصرة
                *[f"Kyu Junior {' '.join(b.split()[2:])} / {' '.join(b.split()[3:])}" for b in 
                  ["yellow 10 / أصفر 10 كيو ناشئين", "yellow 9 / أصفر 9 كيو ناشئين",
                   "orange 8 / برتقالي 8 كيو ناشئين", "orange green 7 / برتقالي أخضر 7 كيو ناشئين",
                   "green 6 / أخضر 6 كيو ناشئين", "green blue 5 / أخضر أزرق 5 كيو ناشئين",
                   "blue 4 / أزرق 4 كيو ناشئين", "blue 3 / أزرق 3 كيو ناشئين",
                   "brown 2 / بني 2 كيو ناشئين", "brown 1 / بني 1 كيو ناشئين"]],
                *[f"Kyu Senior {' '.join(b.split()[2:])} / {' '.join(b.split()[3:])}" for b in 
                  ["yellow 7 / أصفر 7 كيو كبار", "yellow 6 / أصفر 6 كيو كبار",
                   "orange 5 / برتقالي 5 كيو كبار", "orange 4 / برتقالي 4 كيو كبار",
                   "green 3 / أخضر 3 كيو كبار", "blue 2 / أزرق 2 كيو كبار", "brown 1 / بني 1 كيو كبار"]],
                *[f"Dan {i} / دان {i}" for i in range(1, 9)]
            ]

            federation_champs = [
                "African Open Traditional Karate Championship / بطولة افريقيا المفتوحة للكاراتيه التقليدي",
                "North Africa United Karate Championship / بطولة شمال افريقيا للكارتيه الموحد"
            ]

            for i in range(num_players):
                with st.expander(f"👤 Player {i+1} / اللاعب {i+1}"):
                    col1, col2, col3 = st.columns([1,1,1])
                    
                    with col1:
                        athlete_name = st.text_input(BILINGUAL_LABELS["Athlete Name"], key=f"name_{i}")
                        dob = st.date_input(BILINGUAL_LABELS["Date of Birth"], 
                                          min_value=date(1960,1,1), max_value=date.today(), 
                                          key=f"dob_{i}")
                    
                    with col2:
                        sex = st.selectbox(BILINGUAL_LABELS["Sex"], 
                                         ["Male / ذكر", "Female / انثى"], key=f"sex_{i}")
                        code = st.text_input(BILINGUAL_LABELS["Player Code"], key=f"code_{i}")
                    
                    with col3:
                        belt = st.selectbox(BILINGUAL_LABELS["Belt Degree"], belt_options, key=f"belt_{i}")

                    # Federation & Competitions
                    if st.session_state.selected_championship in federation_champs:
                        federation = st.selectbox(
                            BILINGUAL_LABELS["Select Federation"],
                            ["Egyptian Traditional Karate Federation / الاتحاد المصري للكاراتيه التقليدي", 
                             "United General Committee / لجنة الجنرال الموحد"],
                            key=f"fed_{i}"
                        )
                        comp_list = egyptian_competitions if "Egyptian" in federation else united_competitions
                    else:
                        federation = ""
                        comp_list = egyptian_competitions

                    competitions = st.multiselect(
                        BILINGUAL_LABELS["Competitions"], 
                        comp_list, 
                        key=f"comp_{i}"
                    )

                    # Real-time validation
                    if code and not validate_code(code):
                        st.error("❌ كود اللاعب غير صحيح")
                    if st.session_state.phone_number and not validate_phone(st.session_state.phone_number):
                        st.error("❌ رقم الهاتف غير صحيح")

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
                        "Championship": st.session_state.selected_championship,
                        "Timestamp": datetime.now().isoformat()
                    })

    # =====================================================
    # ---------------- Submit Button (Enhanced) ----------
    # =====================================================
    if st.button("🚀 Submit All Players / إرسال جميع اللاعبين", type="primary", use_container_width=True):
        with st.spinner("جاري التحقق والحفظ..."):
            df, _ = load_data()
            errors = []
            championship = st.session_state.selected_championship

            for idx, athlete in enumerate(athletes_data):
                # Comprehensive validation
                name = athlete["Athlete Name"]
                code = athlete["Player Code"]
                belt = athlete["Belt Degree"]
                club = athlete["Club"]
                nationality = athlete["Nationality"]
                coach = athlete["Coach Name"]
                phone = athlete["Phone Number"]
                competitions = athlete["Competitions"]
                dob = athlete["Date of Birth"]

                # Duplicate check
                existing_codes = set(df[df["Championship"] == championship]["Player Code"].dropna().astype(str))
                if code and code in existing_codes:
                    errors.append(f"❌ Player {idx+1}: كود '{code}' موجود مسبقاً!")

                # Required fields
                if not name.strip():
                    errors.append(f"❌ Player {idx+1}: اسم اللاعب مطلوب")
                if not code.strip():
                    errors.append(f"❌ Player {idx+1}: كود اللاعب مطلوب")
                if not belt:
                    errors.append(f"❌ Player {idx+1}: درجة الحزام مطلوبة")
                if not club.strip():
                    errors.append(f"❌ النادي مطلوب")
                if not nationality.strip():
                    errors.append(f"❌ الجنسية مطلوبة")
                
                # Championship-specific
                if not championship.startswith("African Master Course"):
                    if not competitions:
                        errors.append(f"❌ Player {idx+1}: اختر مسابقة واحدة على الأقل")
                    if not coach.strip():
                        errors.append(f"❌ اسم المدرب مطلوب")
                
                # Format validation
                if code and not validate_code(code):
                    errors.append(f"❌ Player {idx+1}: كود غير صحيح")
                if phone and not validate_phone(phone):
                    errors.append(f"❌ رقم الهاتف غير صحيح")
                try:
                    dob_date = date.fromisoformat(dob)
                    if not validate_age(dob_date):
                        errors.append(f"❌ Player {idx+1}: العمر خارج النطاق")
                except:
                    errors.append(f"❌ Player {idx+1}: تاريخ ميلاد غير صحيح")

            # Show errors or save
            if errors:
                st.error("🔴 يرجى تصحيح الأخطاء التالية:")
                for error in errors[:10]:  # Max 10 errors
                    st.error(error)
                if len(errors) > 10:
                    st.warning(f"... و {len(errors)-10} خطأ آخر")
                st.stop()
            
            else:
                # Save to CSV
                for athlete in athletes_data:
                    new_row = pd.DataFrame([athlete])
                    df = pd.concat([df, new_row], ignore_index=True)

                csv_saved = save_data(df)
                
                # Save to Google Sheets
                gsheet_success = 0
                for athlete in athletes_data:
                    if save_to_google_sheet(athlete, championship):
                        gsheet_success += 1

                # Success message
                st.markdown("""
                <div class="success-box">
                    <h3>✅ تم التسجيل بنجاح!</h3>
                    <ul>
                        <li>💾 CSV: """ + ("موحفظ" if csv_saved else "فشل") + """</li>
                        <li>📊 Google Sheets: """ + str(gsheet_success) + "/" + str(len(athletes_data)) + """</li>
                        <li>👥 اللاعبين: """ + str(len(athletes_data)) + """</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)

                # Reset form
                st.session_state.submit_count = st.session_state.get("submit_count", 0) + 1
                for key in ["club", "nationality", "coach_name", "phone_number"]:
                    st.session_state[key] = ""
                st.rerun()

# =====================================================
# ---------------- Admin Panel (Secure) --------------
# =====================================================
with st.sidebar:
    st.header("🔐 Admin Panel")
    admin_password = st.text_input("Admin Password / كلمة المرور", type="password")
    
    if st.button("Login / تسجيل الدخول", key="admin_login"):
        if hash_password(admin_password) == ADMIN_HASH:
            st.session_state.admin_logged_in = True
            st.success("✅ تم تسجيل الدخول كـ Admin")
            st.rerun()
        else:
            st.error("❌ كلمة المرور خاطئة")
            st.session_state.admin_logged_in = False

if st.session_state.get("admin_logged_in", False):
    st.sidebar.success("👨‍💼 Admin Mode Active")
    
    df, display_df = load_data()
    
    if not df.empty:
        st.subheader("📋 جميع البيانات")
        
        column_config = {
            BILINGUAL_COLS.get(col, col): st.column_config.TextColumn(BILINGUAL_COLS.get(col, col))
            for col in df.columns if col in BILINGUAL_COLS or col in BILINGUAL_COLS.values()
        }
        
        st.dataframe(display_df, use_container_width=True, column_config=column_config, height=400)
        
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            selected_champ = st.selectbox("فلتر حسب البطولة:", df["Championship"].unique())
        with col2:
            date_filter = st.date_input("من تاريخ:", value=date.today())
        
        filtered_df = df[
            (df["Championship"] == selected_champ) & 
            (pd.to_datetime(df["Date of Birth"]) >= date_filter)
        ]
        
        if not filtered_df.empty:
            st.dataframe(filtered_df, use_container_width=True)
        
        # Enhanced Excel export
        try:
            buffer = io.BytesIO()
            df.to_excel(buffer, index=False, engine="openpyxl")
            buffer.seek(0)
            
            filename = st.session_state.selected_championship.replace(" ", "_").replace("/", "_")
            
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    "📥 Download Excel",
                    buffer.getvalue(),
                    file_name=f"karate_{filename}_{date.today()}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            with col2:
                st.download_button(
                    "💾 Download CSV",
                    df.to_csv(index=False).encode(),
                    file_name=f"karate_{filename}_{date.today()}.csv"
                )
        except ImportError:
            st.warning("📦 تثبيت openpyxl: `pip install openpyxl`")
        
        # Stats
        st.metric("إجمالي اللاعبين", len(df))
        st.metric("آخر تحديث", df["Timestamp"].max() if "Timestamp" in df else "غير معروف")
        
    else:
        st.info("لا توجد بيانات بعد")

else:
    st.sidebar.info("🔐 أدخل كلمة المرور في الشريط الجانبي")
