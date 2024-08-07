import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import numpy as np
import time  # Import time module for sleep

# ตั้งค่าการเชื่อมต่อกับ Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("m6stdattendance-8b44fcb49a31.json", scope)
client = gspread.authorize(creds)
sheet = client.open("M6_Attendance").sheet1

# ฟังก์ชันโหลดข้อมูลที่ใช้ cache
@st.cache_data
def load_data(file):
    return pd.read_excel(file)

df_students = load_data("M6_std_namelist.xlsx")
df_students.drop(columns=['แผน', 'Gifted'], inplace=True)

# ส่วนหัวของ Streamlit app
st.title('M6 Attendance(เช็กแถว)')

# เลือกห้อง
selected_class = st.selectbox('เลือกห้อง', df_students['ห้อง'].unique())

# แสดงรายชื่อนักเรียนของห้องที่เลือก
students_in_class = df_students[df_students['ห้อง'] == selected_class]
attendance_data = []

for index, row in students_in_class.iterrows():
    cols = st.columns([3, 1, 1, 1, 1])  # Adjusted column widths to accommodate more space for labels
    with cols[0]:
        st.write(f"{row['เลขที่']} {row['เลขประจำตัว']} {row['คำนำหน้า']} {row['ชื่อ']} {row['นามสกุล']}")

    late_status = cols[1].checkbox("Late", key=f"Late_{index}")
    absent_status = cols[2].checkbox("Absent", key=f"Absent_{index}")
    other_status = cols[3].checkbox("Other", key=f"Other_{index}")

    if other_status:
        other_details = st.text_input("Specify reason", key=f"Details_{index}", placeholder="Enter reason here...")

    attendance = 'Late' if late_status else ('Absent' if absent_status else ('Other' if other_status else ''))
    reason = other_details if other_status else ''

    if attendance:
        attendance_data.append([datetime.now().strftime('%Y-%m-%d'), selected_class, row['เลขที่'], row['เลขประจำตัว'], row['ชื่อ'], row['นามสกุล'], attendance, reason])

if st.button("บันทึก"):
    for record in attendance_data:
        sanitized_record = [int(item) if isinstance(item, (np.int64, pd.Int64Dtype)) else item for item in record]
        sheet.append_row(sanitized_record)
    st.success("บันทึกข้อมูลเรียบร้อยแล้ว!")
    time.sleep(10)  # Wait for 10 seconds before clearing cache and rerunning
    st.cache_data.clear()  # Clear all cached data
    
    # Set a query parameter to force a refresh
    st.experimental_set_query_params(rerun=1)
