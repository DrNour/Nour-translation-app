import streamlit as st
import hashlib
from db.models import SessionLocal, User

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed

def login():
    session = SessionLocal()
    st.sidebar.header("Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    role = None
    user_id = None

    if st.sidebar.button("Login"):
        user = session.query(User).filter_by(username=username).first()
        if user and verify_password(password, user.password):
            st.session_state["user"] = user.username
            st.session_state["role"] = user.role
            st.session_state["user_id"] = user.id
            st.sidebar.success(f"Welcome {user.username} ({user.role})")
        else:
            st.sidebar.error("Invalid credentials")

    if "user" in st.session_state:
        username = st.session_state["user"]
        role = st.session_state["role"]
        user_id = st.session_state["user_id"]

    return username, role, user_id

def register():
    session = SessionLocal()
    st.sidebar.subheader("Register")
    new_username = st.sidebar.text_input("New Username")
    new_password = st.sidebar.text_input("New Password", type="password")
    role = st.sidebar.selectbox("Role", ["student", "instructor"])

    if st.sidebar.button("Register"):
        if session.query(User).filter_by(username=new_username).first():
            st.sidebar.error("Username already exists")
        else:
            user = User(
                username=new_username,
                password=hash_password(new_password),
                role=role
            )
            session.add(user)
            session.commit()
            st.sidebar.success("User registered. Please login.")
