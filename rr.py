import streamlit as st
import pandas as pd
from datetime import date
import io
from pathlib import Path

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
.stDateInput>div>div>input {
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
        "Date of Birth", "Sex", "Player Code", "Belt Degree", "Competitions"
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
            "Unified Karate Championship (General)"
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
                name_color = "black"
                code_color = "black"
                belt_color = "black"

                if st.session_state.get(f"name_empty_{i}", False):
                    name_color = "red"
                if st.session_state.get(f"code_empty_{i}", False):
                    code_color = "red"
                if st.session_state.get(f"belt_empty_{i}", False):
                    belt_color = "red"

                key_suffix = f"_{submit_count}_{i}"

                st.markdown(f"<label style='color:{name_color}'>Athlete Name</label>", unsafe_allow_html=True)
                athlete_name = st.text_input("", key=f"name{key_suffix}")

                st.markdown("<label>Date of Birth</label>", unsafe_allow_html=True)
                dob = st.date_input("", min_value=date(1960,1,1), max_value=date.today(), key=f"dob{key_suffix}")

                st.markdown("<label>Nationality</label>", unsafe_allow_html=True)
                nationality = st.text_input("", key=f"nationality{key_suffix}")

                st.markdown("<label>Phone Number</label>", unsafe_allow_html=True)
                phone_number = st.text_input("", key=f"phone{key_suffix}")

                st.markdown("<label>Sex</label>", unsafe_allow_html=True)
                sex = st.selectbox("", ["Male", "Female"], key=f"sex{key_suffix}")

                st.markdown(f"<label style='color:{code_color}'>Player Code</label>", unsafe_allow_html=True)
                player_code = st.text_input("", key=f"code{key_suffix}")

                st.markdown(f"<label style='color:{belt_color}'>Belt Degree</label>", unsafe_allow_html=True)
                belt_degree = st.selectbox("", belt_options, key=f"belt{key_suffix}")

                athletes_data.append({
                    "Athlete Name": athlete_name.strip(),
                    "Club": "",
                    "Nationality": nationality.strip(),
                    "Coach Name": "",
                    "Phone Number": phone_number.strip(),
                    "Date of Birth": str(dob),
                    "Sex": sex,
                    "Player Code": player_code.strip(),
                    "Belt Degree": belt_degree,
                    "Competitions": "",
                    "index": i,
                    "Championship": f"African Master Course - {course_type}"
                })

    # -------- Old Championships FORM --------
    else:
        st.session_state.club = st.text_input("Enter Club for all players", value=st.session_state.club)
        st.session_state.nationality = st.text_input("Enter Nationality for all players", value=st.session_state.nationality)
        st.session_state.coach_name = st.text_input("Enter Coach Name for all players", value=st.session_state.coach_name)
        st.session_state.phone_number = st.text_input("Enter Phone Number for the Coach", value=st.session_state.phone_number)

        num_players = st.number_input("Number of players to add:", min_value=1, value=1, step=1)

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

        for i in range(num_players):
            with st.expander(f"Player {i+1}"):
                name_color = "black"
                code_color = "black"
                comp_color = "black"
                belt_color = "black"

                if st.session_state.get(f"name_empty_{i}", False):
                    name_color = "red"
                if st.session_state.get(f"code_empty_{i}", False):
                    code_color = "red"
                if st.session_state.get(f"belt_empty_{i}", False):
                    belt_color = "red"
                if st.session_state.get(f"comp_empty_{i}", False):
                    comp_color = "red"

                key_suffix = f"_{submit_count}_{i}"

                st.markdown(f"<label style='color:{name_color}'>Athlete Name</label>", unsafe_allow_html=True)
                athlete_name = st.text_input("", key=f"name{key_suffix}")

                st.markdown("<label>Date of Birth</label>", unsafe_allow_html=True)
                dob = st.date_input("", min_value=date(1960,1,1), max_value=date.today(), key=f"dob{key_suffix}")

                st.markdown("<label>Sex</label>", unsafe_allow_html=True)
                sex = st.selectbox("", ["Male", "Female"], key=f"sex{key_suffix}")

                st.markdown(f"<label style='color:{code_color}'>Player Code</label>", unsafe_allow_html=True)
                player_code = st.text_input("", key=f"code{key_suffix}")

                st.markdown(f"<label style='color:{belt_color}'>Belt Degree</label>", unsafe_allow_html=True)
                belt_degree = st.selectbox("", belt_options, key=f"belt{key_suffix}")

                st.markdown(f"<label style='color:{comp_color}'>Competitions</label>", unsafe_allow_html=True)
                competitions = st.multiselect("", competitions_list, key=f"comp{key_suffix}")

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
                    "index": i,
                    "Championship": st.session_state.selected_championship
                })

    # -------- Submit Button --------
    if st.button("Submit All"):
        error_found = False
        df = load_data()
        count = 0

        # reset flags for current number of players
        for i in range(max(1, len(athletes_data))):
            st.session_state[f"name_empty_{i}"] = False
            st.session_state[f"code_empty_{i}"] = False
            st.session_state[f"belt_empty_{i}"] = False
            if st.session_state.selected_championship != "African Master Course":
                st.session_state[f"comp_empty_{i}"] = False

        # First: validate required fields (mark empties)
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
  # Build (code, championship) pairs for this submission
        pairs_in_form = [
            (a["Player Code"], a["Championship"])
            for a in athletes_data
            if a["Player Code"]
        ]

        # check duplicates inside SAME submission
        from collections import Counter
        counter_pairs = Counter(pairs_in_form)
        dup_pairs = [pair for pair, cnt in counter_pairs.items() if cnt > 1]
 if dup_pairs:
            nice = [f"{code} (in {champ})" for code, champ in dup_pairs]
            st.error(f"⚠️ Same player code repeated twice in the same championship: {', '.join(nice)}")
            error_found = True
   # check duplicates against saved file based on (code + championship)
        if not df.empty:
            existing_pairs = set(zip(df["Player Code"].astype(str), df["Championship"].astype(str)))
        else:
            existing_pairs = set()

        conflicts = [
            (code, champ)
            for code, champ in pairs_in_form
            if (code, champ) in existing_pairs
        ]if conflicts:
            nice_conf = [f"{code} (in {champ})" for code, champ in conflicts]
            st.error(f"⚠️ These Player Codes already registered in the same championship: {', '.join(nice_conf)}")
            error_found = True

        if error_found:
@@ -336,32 +354,33 @@
                row.pop("index", None)
                df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
                count += 1
 save_data(df)
            st.success(f"{count} players registered successfully!")

            for key in ["club", "nationality", "coach_name", "phone_number"]:
                st.session_state[key] = ""

            st.session_state.submit_count += 1
            safe_rerun()

# -------- Admin Panel (Sidebar) --------
st.sidebar.header("Admin Login")
admin_password = st.sidebar.text_input("Enter Admin Password", type="password")

if admin_password == "mobadr90":
    st.sidebar.success("Logged in as Admin ✅")
    df = load_data()
    if df.empty:
        st.info("No data found yet.")
    else:
        st.dataframe(df, use_container_width=True)
        excel_buffer = io.BytesIO()
        df.to_excel(excel_buffer, index=False, engine='openpyxl')
        excel_buffer.seek(0)
        championship_name = st.session_state.get("selected_championship", "athletes_data").replace(" ", "_")
        st.download_button(
            label="📥 Download Excel",
            data=excel_buffer,
            file_name=f"{championship_name}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
