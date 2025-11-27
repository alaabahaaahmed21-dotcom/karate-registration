import streamlit as st
import pandas as pd
from datetime import date
import io
from pathlib import Path
from collections import Counter

# -------- Safe Rerun Function --------
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

# -------- PAGE LOGIC --------
if "page" not in st.session_state:
    st.session_state.page = "select_championship"

# -------- FILE SETUP --------
DATA_FILE = Path("athletes_data.csv")

def load_data():
    required_cols = [
        "Championship",
        "Athlete Name", "Club", "Nationality", "Coach Name", "Phone Number",
        "Date of Birth", "Sex", "Player Code", "Belt Degree", "Competitions", "Federation", "Profile Picture"
    ]
    if DATA_FILE.exists():
        df = pd.read_csv(DATA_FILE)
        for col in required_cols:
            if col not in df.columns:
                df[col] = ""
        return df[required_cols]
    else:
        return pd.DataFrame(columns=required_cols)

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# -------- SESSION STATE DEFAULTS --------
for key in ["club", "nationality", "coach_name", "phone_number", "submit_count"]:
    if key not in st.session_state:
        st.session_state[key] = "" if key != "submit_count" else 0

# -------- FIRST PAGE: SELECT CHAMPIONSHIP --------
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
            "North Africa Traditional Karate Championship",
            "United Karate Championship (General)"
        ]
    )

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

    st.markdown(f"""
    <div class="image-row">
        <img src="{img1}">
        <img src="{img2}">
        <img src="{img3}">
        <img src="{img4}">
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        f"<h3 style='text-align: left; color: black; margin-top: 10px;'>🏆 Registration Form: {st.session_state.selected_championship}</h3>",
        unsafe_allow_html=True
    )

    athletes_data = []
    submit_count = st.session_state.submit_count

    # -------- African Master Course FORM --------
    if st.session_state.selected_championship == "African Master Course":

        course_type = st.selectbox("Choose course type:", ["Master", "General"])
        st.session_state.club = st.text_input("Enter Club for all players", value=st.session_state.club)
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
                st.markdown(f"<label>Athlete Name</label>", unsafe_allow_html=True)
                athlete_name = st.text_input("", key=f"name{key_suffix}")

                st.markdown("<label>Date of Birth</label>", unsafe_allow_html=True)
                dob = st.date_input("", min_value=date(1960,1,1), max_value=date.today(), key=f"dob{key_suffix}")

                st.markdown("<label>Nationality</label>", unsafe_allow_html=True)
                nationality = st.text_input("", key=f"nationality{key_suffix}")

                st.markdown("<label>Phone Number</label>", unsafe_allow_html=True)
                phone_number = st.text_input("", key=f"phone{key_suffix}")

                st.markdown("<label>Sex</label>", unsafe_allow_html=True)
                sex = st.selectbox("", ["Male", "Female"], key=f"sex{key_suffix}")

                st.markdown("<label>Player Code</label>", unsafe_allow_html=True)
                player_code = st.text_input("", key=f"code{key_suffix}")

                st.markdown("<label>Belt Degree</label>", unsafe_allow_html=True)
                belt_degree = st.selectbox("", belt_options, key=f"belt{key_suffix}")

                st.markdown("<label>Put your profile picture</label>", unsafe_allow_html=True)
                profile_pic = st.file_uploader("", type=["png","jpg","jpeg"], key=f"profile{key_suffix}")

                athletes_data.append({
                    "Athlete Name": athlete_name.strip(),
                    "Club": st.session_state.club.strip(),
                    "Nationality": nationality.strip(),
                    "Coach Name": "",
                    "Phone Number": phone_number.strip(),
                    "Date of Birth": str(dob),
                    "Sex": sex,
                    "Player Code": player_code.strip(),
                    "Belt Degree": belt_degree,
                    "Competitions": "",
                    "Federation": "",
                    "Profile Picture": profile_pic.name if profile_pic else "",
                    "index": i,
                    "Championship": f"African Master Course - {course_type}"
                })

    # -------- North Africa & United Championships FORM --------
    else:
        st.session_state.club = st.text_input("Enter Club for all players", value=st.session_state.club)
        st.session_state.nationality = st.text_input("Enter Nationality for all players", value=st.session_state.nationality)
        st.session_state.coach_name = st.text_input("Enter Coach Name for all players", value=st.session_state.coach_name)
        st.session_state.phone_number = st.text_input("Enter Phone Number for the Coach", value=st.session_state.phone_number)
        num_players = st.number_input("Number of players to add:", min_value=1, value=1, step=1)

        for i in range(num_players):
            with st.expander(f"Player {i+1}"):
                key_suffix = f"_{submit_count}_{i}"
                st.markdown("<label>Athlete Name</label>", unsafe_allow_html=True)
                athlete_name = st.text_input("", key=f"name{key_suffix}")

                st.markdown("<label>Date of Birth</label>", unsafe_allow_html=True)
                dob = st.date_input("", min_value=date(1960,1,1), max_value=date.today(), key=f"dob{key_suffix}")

                st.markdown("<label>Sex</label>", unsafe_allow_html=True)
                sex = st.selectbox("", ["Male", "Female"], key=f"sex{key_suffix}")

                st.markdown("<label>Player Code</label>", unsafe_allow_html=True)
                player_code = st.text_input("", key=f"code{key_suffix}")

                st.markdown("<label>Belt Degree</label>", unsafe_allow_html=True)
                belt_degree = st.selectbox("", [
                    "Kyu Junior yellow 10","Kyu Junior yellow 9","Kyu Junior orange 8","Kyu Junior orange green 7",
                    "Kyu Junior green 6","Kyu Junior green blue 5","Kyu Junior blue 4","Kyu Junior blue 3",
                    "Kyu Junior brown 2","Kyu Junior brown 1","Kyu Senior yellow 7","Kyu Senior yellow 6",
                    "Kyu Senior orange 5","Kyu Senior orange 4","Kyu Senior green 3","Kyu Senior blue 2",
                    "Kyu Senior brown 1","Dan 1","Dan 2","Dan 3","Dan 4","Dan 5","Dan 6","Dan 7","Dan 8"
                ], key=f"belt{key_suffix}")

                if st.session_state.selected_championship == "North Africa Traditional Karate Championship":
                    federation = st.selectbox("Select Federation", ["Egyptian Traditional Karate Federation", "Unified General Federation"], key=f"federation{key_suffix}")
                    if federation == "Egyptian Traditional Karate Federation":
                        competitions_list = [
                            "Individual kata","Kata team","Individual kumite","Fuko go",
                            "Inbo mix","Inbo male","Inbo female","Kumite team"
                        ]
                    else:
                        competitions_list = [
                            "Individual kata","Kata team","Kumite Ibon","Kumite Nihon",
                            "Kumite Sanbon","Kumite Rote shine"
                        ]
                else:
                    federation = ""
                    competitions_list = [
                        "Individual Kata","Kata Team","Individual Kumite","Fuko Go",
                        "Inbo Mix","Inbo Male","Inbo Female","Kumite Team"
                    ]

                st.markdown("<label>Competitions</label>", unsafe_allow_html=True)
                competitions = st.multiselect("", competitions_list, key=f"comp{key_suffix}")

                st.markdown("<label>Put your profile picture</label>", unsafe_allow_html=True)
                profile_pic = st.file_uploader("", type=["png","jpg","jpeg"], key=f"profile{key_suffix}")

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
                    "Competitions List": competitions,
                    "Federation": federation,
                    "Profile Picture": profile_pic.name if profile_pic else "",
                    "index": i,
                    "Championship": st.session_state.selected_championship
                })

# -------- Submit Button --------
if st.button("Submit All Players"):
    error_found = False
    df = load_data()
    count = 0

    # reset flags
    for i in range(len(athletes_data)):
        st.session_state[f"name_empty_{i}"] = False
        st.session_state[f"code_empty_{i}"] = False
        st.session_state[f"belt_empty_{i}"] = False
        if st.session_state.selected_championship != "African Master Course":
            st.session_state[f"comp_empty_{i}"] = False

    # validate required fields
    for athlete in athletes_data:
        idx = athlete.get("index", 0)
        if not athlete["Athlete Name"]:
            st.session_state[f"name_empty_{idx}"] = True
            error_found = True
        if not athlete["Player Code"]:
            st.session_state[f"code_empty_{idx}"] = True
            error_found = True
        if not athlete["Belt Degree"]:
            st.session_state[f"belt_empty_{idx}"] = True
            error_found = True
        if st.session_state.selected_championship != "African Master Course" and len(athlete.get("Competitions List", [])) == 0:
            st.session_state[f"comp_empty_{idx}"] = True
            error_found = True

    # check duplicates
    pairs_in_form = [
        (a["Player Code"], a["Championship"])
        for a in athletes_data if a["Player Code"]
    ]
    counter_pairs = Counter(pairs_in_form)
    dup_pairs = [pair for pair, cnt in counter_pairs.items() if cnt > 1]

    if dup_pairs:
        st.error(f"Duplicate Player Codes detected: {', '.join([f'{c} ({champ})' for c, champ in dup_pairs])}")
        error_found = True

    if error_found:
        st.warning("Please fill all required fields and remove duplicates.")
    else:
        for athlete in athletes_data:
            df = pd.concat([df, pd.DataFrame([athlete])], ignore_index=True)
        save_data(df)
        st.success(f"✅ {len(athletes_data)} players submitted successfully!")
        st.session_state.submit_count += 1
        safe_rerun()