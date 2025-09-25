import streamlit as st
from utils.auth import login, register

def main():
    st.set_page_config(page_title="Translation LMS", layout="wide")

    username, role, user_id = login()
    register()

    if username:
        st.sidebar.info(f"Logged in as {username} ({role})")
        st.sidebar.write("Go to pages → Student or Instructor")

if __name__ == "__main__":
    main()
