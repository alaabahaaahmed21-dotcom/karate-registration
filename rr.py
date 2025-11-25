import streamlit as st
import pandas as pd
from pathlib import Path

# -------- FILE SETUP --------
DATA_FILE = Path("athletes_data.csv")

# Function to load data
def load_data():
    if DATA_FILE.exists():
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=[
            "Athlete Name", "Club", "Nationality", "Date of Birth", "Sex", "Player Code",
            "Belt Degree", "Competitions"
        ])

# Function to save data
def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# -------- STREAMLIT UI --------
st.title("🏅 Karate Athlete Registration")

menu = st.sidebar.selectbox("Choose Page", ["Add Athlete", "View / Edit Data"])

# -------- PAGE 1 — ADD ATHLETE --------
if menu == "Add Athlete":
    st.header("Add New Athlete")

    with st.form("reg_form"):
        athlete_name = st.text_input("Athlete Name")
        club = st.text_input("Club")
        nationality = st.text_input("Nationality")
        dob = st.date_input("Date of Birth")
        sex = st.selectbox("Sex", ["Male", "Female"])
        player_code = st.text_input("Player Code")
        belt_degree = st.text_input("Belt Degree")

        competitions_list = [
            "Individual Kata",
            "Kata Team",
            "Individual Kumite",
            "Fuko Go",
            "Inbo Mix",
            "Inbo Male",
            "Inbo Female",
            "Kumite Team"
        ]

        competitions = st.multiselect("Choose Competitions", competitions_list)
        submitted = st.form_submit_button("Submit")

    if submitted:
        df = load_data()

        new_row = {
            "Athlete Name": athlete_name,
            "Club": club,
            "Nationality": nationality,
            "Date of Birth": dob,
            "Sex": sex,
            "Player Code": player_code,
            "Belt Degree": belt_degree,
            "Competitions": ", ".join(competitions)
        }

        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        save_data(df)

        st.success("Athlete registered successfully! 🎉")

# -------- PAGE 2 — VIEW/EDIT --------
if menu == "View / Edit Data":
    st.header("View & Edit Athlete Data")

    df = load_data()

    if df.empty:
        st.info("No data found yet.")
    else:
        st.dataframe(df, use_container_width=True)

        st.subheader("Edit Athlete by Player Code")

        code = st.text_input("Enter Player Code to Edit")
        if st.button("Load Athlete"):
            if code in df["Player Code"].values:
                athlete = df[df["Player Code"] == code].iloc[0]

                st.write("### Update Info:")

                name_edit = st.text_input("Athlete Name", athlete["Athlete Name"])
                club_edit = st.text_input("Club", athlete["Club"])
                belt_edit = st.text_input("Belt Degree", athlete["Belt Degree"])

                competitions_list = [
                    "Individual Kata",
                    "Kata Team",
                    "Individual Kumite",
                    "Fuko Go",
                    "Inbo Mix",
                    "Inbo Male",
                    "Inbo Female",
                    "Kumite Team"
                ]

                current_comps = athlete["Competitions"].split(", ") if pd.notna(athlete["Competitions"]) else []
                comps_edit = st.multiselect("Competitions", competitions_list, default=current_comps)

                if st.button("Save Changes"):
                    df.loc[df["Player Code"] == code, "Athlete Name"] = name_edit
                    df.loc[df["Player Code"] == code, "Club"] = club_edit
                    df.loc[df["Player Code"] == code, "Belt Degree"] = belt_edit
                    df.loc[df["Player Code"] == code, "Competitions"] = ", ".join(comps_edit)

                    save_data(df)
                    st.success("Data updated successfully!")
            else:
                st.error("Player Code not found!")
