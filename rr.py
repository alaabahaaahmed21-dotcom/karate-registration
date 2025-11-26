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
    width: 70px;
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

# -------- SESSION STATE DEFAULTS --------
if "page" not in st.session_state:
    st.session_state.page = "select_championship"

for key in ["club", "nationality", "coach_name", "phone_number"]:
    if key not in st.session_state:
        st.session_state[key] = ""

# ---- دالة لعرض اللوجوهات ----
def show_logos():
    st.markdown(f"""
    <div class="image-row">
        <img src="{img1}">
        <img src="{img2}">
        <img src="{img3}">
        <img src="{img4}">
    </div>
    """, unsafe_allow_html=True)

# -------- FIRST PAGE: SELECT CHAMPIONSHIP --------
if st.session_state.page == "select_championship":
    show_logos()
    st.title("🏆 Select Championship")

    championship = st.selectbox(
        "Please select the championship you want to register for:",
        [
            "African Master Course",
            "North Africa Traditional Karate Championship",
            "Unified Karate Championship (General)"
        ]
    )

    if st.butt
