import streamlit as st
from db.models import SessionLocal, Exercise, Submission
from metrics.bleu import compute_bleu
from metrics.comet_eval import compute_comet
from metrics.errors import categorize_errors

def student_page(user_id):
    st.title("Student Dashboard")
    session = SessionLocal()
    exercises = session.query(Exercise).all()
    if not exercises:
        st.info("No exercises yet.")
        return

    choice = st.selectbox("Choose exercise", [e.id for e in exercises])
    exercise = session.query(Exercise).filter_by(id=choice).first()
    st.write("Source text:", exercise.source_text)

    translation = st.text_area("Your translation")
    if st.button("Submit"):
        bleu = compute_bleu("REFERENCE HERE", translation)
        comet = compute_comet(exercise.source_text, translation, "REFERENCE HERE")
        errors = categorize_errors("REFERENCE HERE", translation)

        submission = Submission(
            student_id=user_id,
            exercise_id=exercise.id,
            translation=translation,
            bleu=str(round(bleu,2)),
            comet=str(round(comet,2)),
            errors=errors
        )
        session.add(submission)
        session.commit()
        st.success(f"Submitted! BLEU: {bleu:.2f}, COMET: {comet:.2f}")
        st.subheader("Error Analysis")
        st.json(errors)

def run():
    if "user_id" in st.session_state and st.session_state["role"] == "student":
        student_page(st.session_state["user_id"])
    else:
        st.error("You must log in as a student.")

if __name__ == "__main__":
    run()
