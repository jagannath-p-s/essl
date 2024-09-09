import streamlit as st
from zk import ZK
import pymysql
from datetime import datetime

# Constants
DEVICE_IP = '192.168.1.36'  # Replace with your device's IP
DEVICE_PORT = 4370
COMM_CODE = 123  # Communication Code (Comm Code)

# MySQL Database connection
def connect_db():
    return pymysql.connect(
        host="localhost",  # XAMPP MySQL host
        user="root",  # XAMPP MySQL user (usually 'root')
        password="",  # XAMPP MySQL password
        database="essl_custom"
    )

# Connect to eSSL device and fetch attendance data
def fetch_attendance():
    zk = ZK(DEVICE_IP, port=DEVICE_PORT, timeout=5, password=COMM_CODE)
    try:
        conn = zk.connect()
        conn.disable_device()

        # Fetch attendance logs from the device
        attendance = conn.get_attendance()
        data = []
        for log in attendance:
            data.append({
                'user_id': log.user_id,
                'timestamp': log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'status': log.status,
                'device_id': 1  # Manually assign the device ID
            })

        conn.enable_device()
        conn.disconnect()
        return data
    except Exception as e:
        st.error(f"Error: {e}")
        return []

# Insert attendance data into MySQL database
def insert_into_db(data):
    db = connect_db()
    cursor = db.cursor()
    for log in data:
        cursor.execute("""
            INSERT INTO attendance_logs (user_id, timestamp, status, device_id)
            VALUES (%s, %s, %s, %s)
        """, (log['user_id'], log['timestamp'], log['status'], log['device_id']))
    db.commit()
    cursor.close()
    db.close()

# Add new user to the device
def add_user(uid, name, privilege, password):
    zk = ZK(DEVICE_IP, port=DEVICE_PORT, timeout=5, password=COMM_CODE)
    try:
        conn = zk.connect()
        conn.disable_device()

        # Add the user to the device
        conn.set_user(uid=uid, name=name, privilege=privilege, password=password, user_id=str(uid))

        conn.enable_device()
        conn.disconnect()
        st.success(f"User {name} added successfully.")
    except Exception as e:
        st.error(f"Error adding user: {e}")

# Clear attendance logs from the device
def clear_logs():
    zk = ZK(DEVICE_IP, port=DEVICE_PORT, timeout=5, password=COMM_CODE)
    try:
        conn = zk.connect()
        conn.disable_device()

        # Clear all attendance logs on the device
        conn.clear_attendance()

        conn.enable_device()
        conn.disconnect()
        st.success("Attendance logs cleared successfully.")
    except Exception as e:
        st.error(f"Error clearing logs: {e}")

# Show data from MySQL database
def show_data_from_db():
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM attendance_logs")
    rows = cursor.fetchall()
    if rows:
        st.write(f"Displaying {len(rows)} logs:")
        st.table(rows)
    else:
        st.write("No logs found.")
    cursor.close()
    db.close()

# Streamlit app layout
st.title("eSSL Magnum Device Management")

# Fetch and display attendance logs
if st.button("Fetch Attendance"):
    attendance_data = fetch_attendance()
    if attendance_data:
        st.write(f"Fetched {len(attendance_data)} attendance logs.")
        st.table(attendance_data)

        # Insert the data into MySQL
        if st.button("Save to Database"):
            insert_into_db(attendance_data)
            st.success("Data saved to MySQL successfully!")

# Show data from MySQL database
if st.button("Show Attendance Logs from Database"):
    show_data_from_db()

# Clear logs from the device
if st.button("Clear Device Logs"):
    clear_logs()

# Add user section
st.header("Add New User to the Device")
with st.form("add_user_form"):
    uid = st.text_input("User ID")
    name = st.text_input("User Name")
    privilege = st.selectbox("Privilege Level", [0, 1, 2])  # 0 = Normal, 1 = Admin
    password = st.text_input("Password", type="password")
    submit_add_user = st.form_submit_button("Add User")
    if submit_add_user:
        if uid and name and password:
            add_user(int(uid), name, privilege, password)
        else:
            st.error("Please fill all the fields.")

# Footer
st.write("Developed by jagannath p s ")
