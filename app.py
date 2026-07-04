import streamlit as st

import sqlite3
import pandas as pd

import os
from database import create_tables
from dashboard import dashboard
from report import report_dashboard

from capture_faces import capture_faces
from recognize_faces import recognize_faces
from streamlit_option_menu import option_menu
from capture_faces import capture_faces
from recognize_faces import recognize_faces
from train_model import train_faces

from auth import (
    login,
    register_faculty,
    register_student,
    change_password,
    create_default_admin
)

DB_PATH = 'database/attendance.db'

create_tables()
create_default_admin()
st.set_page_config(page_title="AI Attendance System", layout="wide")

st.title("AI-Powered Attendance System")


if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

if "role" not in st.session_state:
    st.session_state.role = ""

menu = []
 
# if not st.session_state.logged_in:
    # menu.extend(["Login"])
# else:
    # menu.extend(["Logout", "Change Password"])

menu = [
    "Home",
    "Login",
]

if st.session_state.logged_in:
    # menu = [
        # "Logout",
        # "Change Password"
    # ]
    if st.session_state.role == "admin":
        menu.extend([
            "Logout",
            "Register Faculty",
            "Add Student",
            "Train Model",
            "Mark Attendance",
            "Dashboard",
            "Reports",
            "Change Password"
        ])
        st.success(f"Logged in as {st.session_state.role}")
    elif st.session_state.role == "faculty":
        menu.extend([
            "Logout",
            "Add Student",
            "Train Model",
            "Mark Attendance", 
            "Dashboard",
            "Reports",
            "Change Password"
        ])
        st.success(f"Logged in as {st.session_state.role}")



# SIDEBAR
with st.sidebar:
    choice = option_menu(
        menu_title="AI Attendance",
        options=menu,
        icons=[
            "🏠",   # Home
            "box-arrow-in-right",   # Login
            "box-arrow-in-left",    # LogOut
            "person-badge",         # Register Faculty
            "person-plus",          # Add Student
            "cpu",                  # Train Model
            "camera-video",         # Mark Attendance
            "speedometer2",         # Dashboard
            "bar-chart-line"        # Reports
        ],
        menu_icon="grid-fill",
        #default_index=0,
    )
    



# --------------------------
# LOGIN FUNCTION
# --------------------------


if choice == "Login":

    st.subheader("Enter your Credentials")

    username = st.text_input("Username")
    password = st.text_input("Password", type='password')

    if st.button("Login"):
        db_role=login(username, password)
        if not db_role=="":
            st.success("Login Successful")
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.role = db_role
            st.success("Login Successful")
            username=""
            password=""
            # st.rerun()
            # st.markdown(
                # "<h2 style='text-align: center;'>AI Based Attendance System</h2>",
                # unsafe_allow_html=True
            # )
            st.rerun()
        else:
            st.error("Invalid Credentials")
# LOGOUT FUNCTION
elif choice == "Logout":
    st.session_state.logged_in = False
    st.session_state.role = None
    st.success("✅ Logged out successfully")
    st.rerun()
# REGISTER FACULTY    
elif choice == "Register Faculty":

    st.subheader("Register Faculty")

    username = st.text_input("Username")
    password = st.text_input("Password", type='password')
    
    # Validation
    if username.strip() == "":
        st.error("UserName is required.")
    elif len(username) < 3:
        st.error("User name must be atleast 3 characters long.")
    elif password.strip() == "":
        st.error("Password required.")
    else:
        try:
            if st.button("Register"):
                register_faculty(username, password)
                st.success("Faculty Registered Successfully")
                st.rerun()        
        except Exception as e:
             st.error(f"Error during registration: {e}")                        

# ADD STUDENT
elif choice == "Add Student":

    st.subheader("📸 Student Registration & Face Capture")

    name = st.text_input("Student Name")
    roll = st.text_input("Roll Number")
    class_name = st.text_input("Class Name")
    email = st.text_input("Email")
    phone = st.text_input("Phone")
    
    # Initialize session state for face capture
    if "face_captured" not in st.session_state:
        st.session_state.face_captured = False
    
    # Number of samples to capture
    # num_samples = st.slider("Number of face samples to capture", 10, 50, 30)

    # Button to trigger face capture
    if st.button("Capture Faces"):
        
 # New Code
        # Validation
        if roll.strip() == "":
            st.error("Student ID is required.")
        elif not roll.isdigit():
            st.error("Student ID must be numeric.")
        elif len(roll) != 3:
            st.error("Student ID must be exactly 3 digits.")
        elif name.strip() == "":
            st.error("Student Name is required.")
        elif class_name.strip() == "":
            st.error("Class/Section is required.")
        else:
            try:
                sid = int(roll)    
                # Capture face samples
                capture_faces(sid, name)
                #capture_faces(sid, student_name, num_samples=num_samples)

                # Check if face samples exist
                dataset_path = f"dataset/user_{sid}"
                #path = f"dataset/user_{sid}"
                files = [f for f in os.listdir(dataset_path) if f.startswith(f"User.{sid}.")]
                if len(files) == 0:
                    st.error("❌ No face samples captured. Student data will not be saved.")
                    st.session_state.face_captured = False
                else:
                    st.info("✅ Face samples captured. Preview below:")
                    st.session_state.face_captured = True
                    # Show thumbnails of captured faces
                    cols = st.columns(5)
                    for i, file in enumerate(files[:10]):  # show up to 10 samples
                        img_path = os.path.join(dataset_path, file)
                        with cols[i % 5]:
                            st.image(img_path, caption=f"Sample {i+1}", width=120)

                    # Confirmation button before saving                        
            except Exception as e:
                st.error(f"Error during registration: {e}")
        
    if st.button("Save Student"):
        if st.session_state.face_captured:
            try:                           
                image_path = f"dataset/user_{roll}"
                if register_student(name,roll,class_name,email,phone,image_path):
                    st.success(f"Student {name} (ID: {roll}) registered successfully with face samples.")
                    image_path=""
                    name=""
                    roll=""
                    class_name=""
                    email=""
                    phone=""
                    
                    st.session_state.face_captured = False
                    st.rerun()
                else:
                    st.error("Data not Saved....")
        
            except Exception as e:
                st.error(f"Error during registration: {e}") 
        else:
            st.error("Capture face before saving the data......")

# TRAIN FACES
elif choice == "Train Model":

    st.subheader("Train AI Model")

    if st.button("Start Training"):

        train_faces()

        st.success("Face Training Completed")


# MARK ATTENDANCE
elif choice == "Mark Attendance":

    st.subheader("AI Attendance")

    st.warning("Press ESC to close webcam")

    if st.button("Start Attendance"):

        recognize_faces()
        

# DASHBOARD
elif choice == "Dashboard":
    dashboard()

# REPORTS
elif choice == "Reports":

    report_dashboard()
elif choice == "Change Password":

    st.subheader("📸 Change Password")

    userid = st.text_input("Enter User Name")
    oldpwd = st.text_input("Enter Old Password", type='password')
    newpwd = st.text_input("Enter New Password", type='password')
    rnewpwd = st.text_input("Repeat New Password", type='password')
    
    # Button to Reset Password
    if st.button("Reset Password"):
        
 # New Code
        # Validation
        if userid.strip() == "":
            st.error("User ID is required.")
        elif len(userid) < 3 or len(userid)>8 :
            st.error("User ID must be atleaset 3 and maximum of 8 character")
        elif oldpwd.strip() == "":
            st.error("Old Password is required.")
        elif newpwd.strip() == "":
            st.error("New Password is required.")
        elif rnewpwd.strip() == "":
            st.error("Re-enter New Password.")
        elif newpwd!=rnewpwd :
            st.error("Mismatch in New Password Entries")
        else:
            if change_password(userid, oldpwd, newpwd):
                st.success("✅ Password Change Successful")
            else:
                st.error("❌ Password Change not Successful, one of the information provided is incorrect")