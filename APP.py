import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import numpy as np

# ตั้งค่าการเชื่อมต่อกับ Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("m6stdattendance-8b44fcb49a31.json", scope)
client = gspread.authorize(creds)
sheet = client.open("M6_Attendance").sheet1

# อ่านข้อมูลนักเรียน
df_students = pd.read_excel("M6_std_namelist.xlsx")
df_students.drop(columns=['แผน', 'Gifted'], inplace=True)

# Streamlit app
st.title('M6 Attendance')

# เลือกห้อง
selected_class = st.selectbox('เลือกห้อง', df_students['ห้อง'].unique())

# แสดงรายชื่อนักเรียนของห้องที่เลือก
students_in_class = df_students[df_students['ห้อง'] == selected_class]
attendance_data = []

for index, row in students_in_class.iterrows():
    cols = st.columns([3, 1, 1, 1, 1])
    cols[0].text(f"{row['เลขที่']} {row['เลขประจำตัว']} {row['คำนำหน้า']} {row['ชื่อ']} {row['นามสกุล']}")

    checkbox_state = {
        'Late': st.checkbox("Late", key=f"Late_{index}"),
        'Absent': st.checkbox("Absent", key=f"Absent_{index}"),
        'Other': st.checkbox("Other", key=f"Other_{index}")
    }

    selected = [k for k, v in checkbox_state.items() if v]
    if len(selected) > 1:
        st.warning('Please select only one option.')
        checkbox_state[selected[0]] = False
        for state in selected[1:]:
            st.session_state[f"{state}_{index}"] = False

    other_details = st.text_input("Specify reason", key=f"Details_{index}", placeholder="Enter reason here...") if checkbox_state['Other'] else ""

    attendance = selected[0] if selected else ''
    reason = other_details if checkbox_state['Other'] else ''

    if attendance:
        attendance_data.append([datetime.now().strftime('%Y-%m-%d'), selected_class, row['เลขที่'], row['เลขประจำตัว'], row['ชื่อ'], row['นามสกุล'], attendance, reason])

if st.button("Save"):
    for record in attendance_data:
        sanitized_record = [int(item) if isinstance(item, (np.int64, pd.Int64Dtype)) else item for item in record]
        sheet.append_row(sanitized_record)
    st.success("Data saved successfully!")
    st.experimental_rerun()
