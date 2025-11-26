import streamlit as st
import pandas as pd
import os
import io

st.set_page_config(page_title="Karate Registration", layout="wide")

# --------------------------- LOGIN SYSTEM ---------------------------

USERNAME = "admin"
PASSWORD = "1234"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

def login_screen():
    st.title("🔐 Login")

    user = st.text_input("Username")
    pw = st.text_input("Password", type="password")

    if st.button("Login"):
        if user == USERNAME and pw == PASSWORD:
            st.session_state.logged_in = True
            st.session_state.is_admin = True
            st.success("Admin Login Successful!")
        else:
            st.error("Incorrect username or password!")

# Stop until logged in
if not st.session_state.logged_in:
    login_screen()
    st.stop()

# --------------------------- LOGOUT ---------------------------
if st.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.is_admin = False
    st.rerun()

# --------------------------- Storage file ---------------------------
FILE_PATH = "players_data.csv"

def load_data():
    if os.path.exists(FILE_PATH):
        return pd.read_csv(FILE_PATH)
    return pd.DataFrame(columns=[
        "Club", "Athlete Name", "Nationality", "Date of Birth", "Sex",
        "Player Code", "Belt Degree", "Competitions"
    ])

def save_data(df):
    df.to_csv(FILE_PATH, index=False)

def to_excel_bytes(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Athletes")
    return output.getvalue()

df = load_data()

# --------------------------- Lists ---------------------------
SEX_LIST = ["Male", "Female"]

COMPETITIONS_LIST = [
    "Kata Individual Male", "Kata Individual Female",
    "Kata Team Male", "Kata Team Female",
    "Kumite Male", "Kumite Female",
    "Inbo Male", "Inbo Female", "Inbo Mix"
]

BELT_LIST = [
    "Kyu Junior yellow 10","Kyu Junior yellow 9","Kyu Junior orange 8" ,
    "Kyu Junior orange green 7","Kyu Junior green 6","Kyu Junior green blue 5",
    "Kyu Junior blue 4","Kyu Junior blue 3","Kyu Junior brown 2","Kyu Junior brown 1",
    "Kyu Senior yellow 7","Kyu Senior yellow 6","Kyu Senior orange 5","Kyu Senior orange 4",
    "Kyu Senior green 3","Kyu Senior blue 2","Kyu Senior brown 1",
    "Dan 1","Dan 2","Dan 3","Dan 4","Dan 5","Dan 6","Dan 7","Dan 8"
]

# --------------------------- Main Menu ---------------------------
menu = st.sidebar.selectbox("Menu", ["Add Players", "View Data", "Edit / Delete Player", "Admin Panel"])

# --------------------------- Add Players ---------------------------
if menu == "Add Players":
    st.header("🏆 Karate Championship Registration")
    club_name = st.text_input("Enter Club for all players")
    num_players = st.number_input("Number of players to add:", min_value=1, step=1)

    if club_name and num_players:
        for i in range(int(num_players)):
            st.subheader(f"Player {i+1}")
            name = st.text_input(f"Athlete Name {i+1}", key=f"name{i}")
            nationality = st.text_input(f"Nationality {i+1}", key=f"nat{i}")
            dob = st.date_input(f"Date of Birth {i+1}", key=f"dob{i}")
            sex = st.selectbox(f"Sex {i+1}", SEX_LIST, key=f"sex{i}")
            player_code = st.text_input(f"Player Code {i+1}", key=f"code{i}")
            belt_degree = st.selectbox(f"Belt Degree {i+1}", BELT_LIST, key=f"belt{i}")
            competitions = st.multiselect(f"Choose Competitions {i+1}", COMPETITIONS_LIST, key=f"comp{i}")

            if st.button(f"Save Player {i+1}", key=f"save{i}"):
                new_row = {
                    "Club": club_name,
                    "Athlete Name": name,
                    "Nationality": nationality,
                    "Date of Birth": dob,
                    "Sex": sex,
                    "Player Code": player_code,
                    "Belt Degree": belt_degree,
                    "Competitions": ", ".join(competitions)
                }
                df.loc[len(df)] = new_row
                save_data(df)
                st.success(f"Player {i+1} registered successfully!")

# --------------------------- View Data ---------------------------
elif menu == "View Data":
    st.header("📋 Registered Players")
    st.dataframe(df)

# --------------------------- Edit / Delete ---------------------------
elif menu == "Edit / Delete Player":
    st.header("✏️ Edit or Delete Player")
    if df.empty:
        st.warning("No players registered yet.")
    else:
        names = df["Athlete Name"].tolist()
        selected_name = st.selectbox("Choose a player:", names)
        athlete = df[df["Athlete Name"] == selected_name].iloc[0]

        name_edit = st.text_input("Athlete Name", athlete["Athlete Name"])
        nationality_edit = st.text_input("Nationality", athlete["Nationality"])
        dob_edit = st.date_input("Date of Birth", pd.to_datetime(athlete["Date of Birth"]))
        sex_edit = st.selectbox("Sex", SEX_LIST, index=SEX_LIST.index(athlete["Sex"]))
        code_edit = st.text_input("Player Code", athlete["Player Code"])
        belt_edit = st.selectbox("Belt Degree", BELT_LIST,
                                 index=(BELT_LIST.index(athlete["Belt Degree"]) if athlete["Belt Degree"] in BELT_LIST else 0))
        competitions_edit = st.multiselect("Competitions", COMPETITIONS_LIST, default=athlete["Competitions"].split(", "))

        if st.button("Update Player"):
            idx = df[df["Athlete Name"] == selected_name].index[0]
            df.loc[idx] = [
                df.loc[idx, "Club"], name_edit, nationality_edit, dob_edit,
                sex_edit, code_edit, belt_edit, ", ".join(competitions_edit)
            ]
            save_data(df)
            st.success("Player updated successfully!")

        if st.button("Delete Player"):
            df.drop(df[df["Athlete Name"] == selected_name].index, inplace=True)
            save_data(df)
            st.success("Player deleted successfully!")

# --------------------------- Admin Panel ---------------------------
elif menu == "Admin Panel":
    st.header("⚙️ Admin Panel — Data Export")
    if not st.session_state.is_admin:
        st.error("Admin only. You cannot export data.")
    else:
        st.success("You have admin access. You can export the data below.")

        # CSV Download
        csv = df.to_csv(index=False).encode()
        st.download_button("📥 Download CSV", data=csv, file_name="players_data.csv", mime="text/csv")

        # Excel Download
        excel_bytes = io.BytesIO()
        with pd.ExcelWriter(excel_bytes, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Athletes")
        st.download_button("📥 Download Excel", data=excel_bytes.getvalue(),
                           file_name="players_data.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")