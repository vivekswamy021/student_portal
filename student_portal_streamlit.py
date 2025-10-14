import streamlit as st
import sqlite3
import hashlib
import os

# --------------------------
# Database Setup
# --------------------------
DB_FILE = "students.db"
conn = sqlite3.connect(DB_FILE, check_same_thread=False)
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT UNIQUE,
    password TEXT,
    course TEXT
)
''')
conn.commit()

# --------------------------
# Helper Functions
# --------------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def add_student(name, email, password, course):
    password_hash = hash_password(password)
    c.execute('SELECT * FROM students WHERE email=?', (email,))
    if c.fetchone():
        return False
    c.execute('INSERT INTO students (name, email, password, course) VALUES (?, ?, ?, ?)',
              (name, email, password_hash, course))
    conn.commit()
    return True

def login_student(email, password):
    password_hash = hash_password(password)
    c.execute('SELECT * FROM students WHERE email=? AND password=?', (email, password_hash))
    return c.fetchone()

# --------------------------
# Streamlit App Setup
# --------------------------
st.set_page_config(page_title="Student Portal", layout="centered")
st.title("🎓 Student Portal")

# --------------------------
# Session State Initialization
# --------------------------
if 'user' not in st.session_state:
    st.session_state['user'] = None
if 'page' not in st.session_state:
    st.session_state['page'] = "Home"

# --------------------------
# Sidebar Navigation
# --------------------------
if st.session_state['user']:
    sidebar_options = ["Dashboard", "Logout"]
else:
    sidebar_options = ["Home", "Register", "Login"]

choice = st.sidebar.radio("Go to", sidebar_options)
st.session_state['page'] = choice

# --------------------------
# Pages
# --------------------------

# ----- Home -----
if st.session_state['page'] == "Home":
    st.write("Welcome to the Student Portal!")
    if st.session_state['user']:
        st.success(f"Logged in as {st.session_state['user'][1]}")

# ----- Register -----
elif st.session_state['page'] == "Register":
    st.subheader("Create Account")
    name = st.text_input("Full Name", key="reg_name")
    email = st.text_input("Email", key="reg_email")
    password = st.text_input("Password", type="password", key="reg_pass")
    course = st.text_input("Course", key="reg_course")

    if st.button("Register", key="register_btn"):
        if name and email and password and course:
            success = add_student(name, email, password, course)
            if success:
                st.success("Account created successfully! Please log in.")
                st.session_state['page'] = "Login"
            else:
                st.error("Email already registered!")
        else:
            st.warning("Please fill in all fields.")

    # ----- Clickable Link to Login -----
    st.markdown("Already have an account?")
    # Simulate a link using a button with minimal styling
    if st.button("Login here", key="login_link"):
        st.session_state['page'] = "Login"

# ----- Login -----
elif st.session_state['page'] == "Login":
    st.subheader("Login")
    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_pass")

    if st.button("Login", key="login_btn"):
        result = login_student(email, password)
        if result:
            st.session_state['user'] = result
            st.success(f"Welcome {result[1]} 👋")
            st.session_state['page'] = "Dashboard"
        else:
            st.error("Invalid email or password.")

# ----- Dashboard -----
elif st.session_state['page'] == "Dashboard":
    if st.session_state['user']:
        st.subheader("📊 Dashboard")
        user = st.session_state['user']
        st.write(f"**Name:** {user[1]}")
        st.write(f"**Email:** {user[2]}")
        st.write(f"**Course:** {user[4]}")

        # Assignments Upload
        st.subheader("📁 Assignments")
        uploaded_file = st.file_uploader("Upload Assignment")
        if uploaded_file:
            os.makedirs("uploads", exist_ok=True)
            file_path = os.path.join("uploads", uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success(f"Uploaded {uploaded_file.name}")

        # Logout
        if st.button("Logout", key="logout_btn"):
            st.session_state['user'] = None
            st.session_state['page'] = "Home"
            st.success("Logged out successfully.")
    else:
        st.warning("Please login first.")
        st.session_state['page'] = "Login"
