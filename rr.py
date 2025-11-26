# -------- Submit Button --------
if st.button("Submit All"):
    if not st.session_state.club.strip():
        st.error("⚠️ Please enter a Club name before submitting!")
    elif not st.session_state.nationality.strip():
        st.error("⚠️ Please enter Nationality before submitting!")
    elif not st.session_state.coach_name.strip():
        st.error("⚠️ Please enter Coach Name before submitting!")
    elif not st.session_state.phone_number.strip():
        st.error("⚠️ Please enter Phone Number before submitting!")
    else:
        error_found = False
        df = load_data()
        count = 0

        # Reset missing field markers
        for i in range(num_players):
            st.session_state[f"name_empty_{i}"] = False
            st.session_state[f"code_empty_{i}"] = False
            st.session_state[f"belt_empty_{i}"] = False
            st.session_state[f"comp_empty_{i}"] = False

        # Check for repeated Player Codes in form
        codes_in_form = [athlete["Player Code"] for athlete in athletes_data]
        if len(codes_in_form) != len(set(codes_in_form)):
            st.error("⚠️ Some Player Codes are repeated in this submission!")
            error_found = True

        for athlete in athletes_data:
            idx = athlete["index"]
            if not athlete["Athlete Name"]:
                st.session_state[f"name_empty_{idx}"] = True
                error_found = True
            if not athlete["Player Code"]:
                st.session_state[f"code_empty_{idx}"] = True
                error_found = True
            if not athlete["Belt Degree"]:
                st.session_state[f"belt_empty_{idx}"] = True
                error_found = True
            if len(athlete["Competitions List"]) == 0:
                st.session_state[f"comp_empty_{idx}"] = True
                error_found = True
            if athlete["Player Code"] in df["Player Code"].values:
                st.error(f"⚠️ Player Code {athlete['Player Code']} already exists!")
                error_found = True

        if error_found:
            st.error("⚠️ Please fix the errors highlighted in red!")
        else:
            for athlete in athletes_data:
                df = pd.concat([df, pd.DataFrame([athlete])], ignore_index=True)
                count += 1
            save_data(df)

            # ---- حدد حالة النجاح ----
            st.session_state["submit_success"] = f"{count} players registered successfully!"

            # Clear all global inputs safely
            for key in ["club", "nationality", "coach_name", "phone_number"]:
                if key in st.session_state:
                    st.session_state[key] = ""

            # Clear individual player inputs safely
            for i in range(num_players):
                for k in ["name", "code", "belt", "comp", "dob", "sex"]:
                    key = f"{k}{i}"
                    if key in st.session_state:
                        del st.session_state[key]

            st.experimental_rerun()  # إعادة تحميل الصفحة بعد تعديل session_state

# -------- عرض رسالة النجاح بعد rerun --------
if "submit_success" in st.session_state:
    st.success(st.session_state["submit_success"])
    del st.session_state["submit_success"]
