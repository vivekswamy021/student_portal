# student_portal.py
import streamlit as st
import sqlite3

# ----- Database Setup -----
conn = sqlite3.connect('students.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS students
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              name TEXT, email TEXT UNIQUE, password TEXT, course TEXT)''')

conn.commit()

# ----- Helper Functions -----
def add_student(name, email, password, course):
    c.execute('INSERT INTO students (name, email, password, course) VALUES (?, ?, ?, ?)',
              (name, email, password, course))
    conn.commit()

def login_student(email, password):
    c.execute('SELECT * FROM students WHERE email=? AND password=?', (email, password))
    return c.fetchone()

# ----- Streamlit App -----
st.set_page_config(page_title="Student Portal", layout="centered")

st.title("🎓 Student Portal")

menu = ["Home", "Login", "Register"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Home":
    st.write("Welcome to the Student Portal!")

elif choice == "Register":
    st.subheader("Create Account")
    name = st.text_input("Full Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    course = st.text_input("Course")
    if st.button("Register"):
        add_student(name, email, password, course)
        st.success("Account created successfully! Please log in.")

elif choice == "Login":
    st.subheader("Login to your account")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        result = login_student(email, password)
        if result:
            st.success(f"Welcome {result[1]} 👋")
            st.write("### Dashboard")
            st.write(f"**Course:** {result[4]}")
            st.write("📚 Grades and assignments will appear here soon...")
        else:
            st.error("Invalid email or password.")
