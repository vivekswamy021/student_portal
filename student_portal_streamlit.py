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

# Create students table
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
# Streamlit App
# --------------------------
st.set_page_config(page_title="Student Portal", layout="centered")
st.title("🎓 Student Portal")

# Session State
if 'user' not in st.session_state:
    st.session_state['user'] = None

menu = ["Home", "Register", "Login"]
choice = st.sidebar.selectbox("Menu", menu)

# ---- Home ----
if choice == "Home":
    st.write("Welcome to the Student Portal!")
    if st.session_state['user']:
        st.success(f"Logged in as {st.session_state['user'][1]}")

# ---- Register ----
elif choice == "Register":
    st.subheader("Create Account")
    name = st.text_input("Full Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    course = st.text_input("Course")

    if st.button("Register"):
        if name and email and password and course:
            success = add_student(name, email, password, course)
            if success:
                st.success("Account created successfully! Please log in.")
            else:
                st.error("Email already registered!")
        else:
            st.warning("Please fill in all fields.")

# ---- Login ----
elif choice == "Login":
    st.subheader("Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        result = login_student(email, password)
        if result:
            st.session_state['user'] = result
            st.success(f"Welcome {result[1]} 👋")
        else:
            st.error("Invalid email or password.")

# ---- Dashboard after login ----
if st.session_state['user']:
    st.write("---")
    st.subheader("📊 Dashboard")
    user = st.session_state['user']
    st.write(f"**Name:** {user[1]}")
    st.write(f"**Email:** {user[2]}")
    st.write(f"**Course:** {user[4]}")
    
    # Placeholder for assignments
    st.subheader("📁 Assignments")
    uploaded_file = st.file_uploader("Upload Assignment")
    if uploaded_file:
        file_path = os.path.join("uploads", uploaded_file.name)
        os.makedirs("uploads", exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"Uploaded {uploaded_file.name}")
    
    # Logout button
    if st.button("Logout"):
        st.session_state['user'] = None
        st.success("Logged out successfully.")
        st.experimental_rerun()
