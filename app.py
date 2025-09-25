# app.py
import streamlit as st
import pandas as pd
import random
import json

# Initialize session state
if 'role' not in st.session_state:
    st.session_state.role = None
if 'exercises' not in st.session_state:
    st.session_state.exercises = []
if 'results' not in st.session_state:
    st.session_state.results = []

# ---------- Helper functions ----------
def add_exercise(text, solution, exercise_type):
    st.session_state.exercises.append({
        "text": text,
        "solution": solution,
        "type": exercise_type
    })

def score_answer(student_answer, solution):
    # Simple scoring: accuracy (exact match), fluency (length-based)
    accuracy = 1.0 if student_answer.strip() == solution.strip() else 0.5
    fluency = min(len(student_answer.split()) / len(solution.split()), 1.0)
    return round((accuracy + fluency)/2, 2)

def export_results():
    df = pd.DataFrame(st.session_state.results)
    df.to_csv("results.csv", index=False)
    st.download_button("Download Results CSV", df.to_csv(index=False), "results.csv", "text/csv")

def assign_badge(score):
    if score > 0.9:
        return "🏆 Gold"
    elif score > 0.75:
        return "🥈 Silver"
    elif score > 0.5:
        return "🥉 Bronze"
    else:
        return "💡 Try Again"

# ---------- Role Selection ----------
st.title("EduTrans Gamified Translation App")
role = st.radio("Select your role:", ["Instructor", "Student"])
st.session_state.role = role

# ---------- Instructor Panel ----------
if st.session_state.role == "Instructor":
    st.header("Instructor Dashboard")
    st.subheader("Add a New Exercise")
    ex_type = st.selectbox("Exercise Type", ["Edit", "Translate"])
    ex_text = st.text_area("Exercise Text")
    ex_solution = st.text_area("Solution / Correct Version")
    
    if st.button("Add Exercise"):
        if ex_text and ex_solution:
            add_exercise(ex_text, ex_solution, ex_type)
            st.success("Exercise added!")
        else:
            st.warning("Please fill in both text and solution.")

    if st.session_state.exercises:
        st.subheader("Existing Exercises")
        for i, ex in enumerate(st.session_state.exercises):
            st.write(f"**{i+1}. [{ex['type']}]** {ex['text']} -> {ex['solution']}")

    if st.session_state.results:
        st.subheader("Student Results")
        export_results()

# ---------- Student Panel ----------
elif st.session_state.role == "Student":
    st.header("Student Dashboard")
    
    if not st.session_state.exercises:
        st.info("No exercises available. Ask your instructor to add exercises.")
    else:
        ex_idx = st.number_input("Choose exercise number:", min_value=1, max_value=len(st.session_state.exercises), step=1) - 1
        exercise = st.session_state.exercises[ex_idx]
        
        st.subheader(f"Exercise {ex_idx+1} [{exercise['type']}]")
        st.write(exercise['text'])
        
        student_answer = st.text_area("Your Answer")
        
        if st.button("Submit Answer"):
            score = score_answer(student_answer, exercise['solution'])
            badge = assign_badge(score)
            
            st.success(f"Score: {score} | Badge: {badge}")
            
            # Save result
            st.session_state.results.append({
                "exercise": exercise['text'],
                "student_answer": student_answer,
                "score": score,
                "badge": badge
            })
            
            st.balloons()  # Fun gamification

        if st.session_state.results:
            st.subheader("Your Previous Results")
            for res in st.session_state.results:
                st.write(f"Exercise: {res['exercise']}")
                st.write(f"Answer: {res['student_answer']}")
                st.write(f"Score: {res['score']} | Badge: {res['badge']}")
                st.write("---")
