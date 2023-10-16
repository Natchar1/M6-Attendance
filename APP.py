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
    cols = st.columns([3, 1, 1])
    cols[0].text(f"{row['เลขที่']} {row['เลขประจำตัว']} {row['คำนำหน้า']} {row['ชื่อ']} {row['นามสกุล']}")

    late_status = cols[1].checkbox("Late", key=f"Late_{index}")
    absent_status = cols[2].checkbox("Absent", key=f"Absent_{index}")

    # ป้องกันไม่ให้ late และ absent ถูก check พร้อมกัน
    if late_status and absent_status:
        st.warning("คุณไม่สามารถเลือก 'Late' และ 'Absent' พร้อมกันได้!")
        late_status = False
        absent_status = False

    attendance = 'Late' if late_status else ('Absent' if absent_status else '')

    # บันทึกข้อมูลเฉพาะเมื่อเลือกตัวเลือกสายหรือขาด
    if attendance:
        attendance_data.append([datetime.now().strftime('%Y-%m-%d'), selected_class, row['เลขที่'], row['เลขประจำตัว'], row['ชื่อ'],row['นามสกุล'], attendance])


if st.button("บันทึก"):
    for record in attendance_data:
        # Convert all int64 values to int
        sanitized_record = [int(item) if isinstance(item, (np.int64, pd.Int64Dtype)) else item for item in record]
        sheet.append_row(sanitized_record)
    st.success("บันทึกข้อมูลเรียบร้อยแล้ว!")

