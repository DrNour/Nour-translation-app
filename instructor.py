import streamlit as st
import pandas as pd
from db.models import SessionLocal, Exercise, Submission

def instructor_page():
    st.title("Instructor Dashboard")
    session = SessionLocal()

    st.header("Add Exercise")
    src_text = st.text_area("Source text")
    tgt_lang = st.text_input("Target language")
    if st.button("Save Exercise"):
        ex = Exercise(source_text=src_text, target_lang=tgt_lang)
        session.add(ex)
        session.commit()
        st.success("Exercise added")

    st.header("All Submissions")
    submissions = session.query(Submission).all()
    if submissions:
        data = []
        for s in submissions:
            data.append({
                "Student": s.student.username,
                "Exercise": s.exercise.id,
                "Translation": s.translation,
                "BLEU": s.bleu,
                "COMET": s.comet,
                "Errors": s.errors
            })
        df = pd.DataFrame(data)
        st.dataframe(df)
        st.download_button("Download CSV", df.to_csv(index=False), "submissions.csv")

def run():
    if "role" in st.session_state and st.session_state["role"] == "instructor":
        instructor_page()
    else:
        st.error("You must log in as an instructor.")

if __name__ == "__main__":
    run()
