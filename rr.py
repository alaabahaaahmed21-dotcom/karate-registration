error = False
errors_list = []

for idx, athlete in enumerate(athletes_data):
    # جمع كل الحقول المطلوبة
    required_fields = [
        ("Athlete Name", athlete.get("Athlete Name", "").strip()),
        ("Player Code", athlete.get("Player Code", "").strip()),
        ("Belt Degree", athlete.get("Belt Degree", "")),
        ("Club", athlete.get("Club", "").strip()),
        ("Nationality", athlete.get("Nationality", "").strip()),
        ("Coach Name", athlete.get("Coach Name", "").strip()),
        ("Phone Number", athlete.get("Phone Number", "").strip()),
        ("Date of Birth", athlete.get("Date of Birth", "").strip()),
        ("Sex", athlete.get("Sex", "").strip())
    ]
    
    # للبطولات التي تتطلب الاتحاد والمنافسات
    if st.session_state.selected_championship in [
        "African Open Traditional Karate Championship",
        "North Africa Unitied Karate Championship (General)"
    ]:
        required_fields.append(("Federation", athlete.get("Federation", "").strip()))
        if len(athlete.get("Competitions List", [])) == 0:
            errors_list.append(f"Player #{idx+1}: Please select at least one competition.")
            error = True

    # تحقق من كل حقل
    for field_name, value in required_fields:
        if not value:
            errors_list.append(f"Player #{idx+1}: {field_name} is missing.")
            error = True

# لو في خطأ نوقف التسجيل
if error:
    st.error("⚠️ Please fill all required fields before submitting:")
    for msg in errors_list:
        st.write(f"- {msg}")
    st.stop()
