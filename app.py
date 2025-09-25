import streamlit as st
import pandas as pd
import os
from transformers import pipeline
from nltk.translate.bleu_score import sentence_bleu
from comet_ml import download_model, load_from_checkpoint
from bert_score import score

# Set up the app
st.title("Interactive Translation App")
st.sidebar.title("Navigation")
app_mode = st.sidebar.selectbox("Choose the app mode", ["Instructor", "Student"])

# Define the instructor and student roles
if app_mode == "Instructor":
    st.header("Instructor Mode")
    
    # Upload student submissions
    st.subheader("Student Submissions")
    uploaded_files = st.file_uploader("Choose student submissions", accept_multiple_files=True)
    
    # View student progress
    st.subheader("Student Progress")
    student_progress = pd.DataFrame(columns=["Student", "Accuracy", "Fluency"])
    st.dataframe(student_progress)
    
    # Assign exercises
    st.subheader("Assign Exercises")
    exercise_text = st.text_area("Enter the exercise text")
    if st.button("Assign Exercise"):
        st.write(f"Exercise assigned: {exercise_text}")
    
    # Add new exercises
    st.subheader("Add New Exercises")
    new_exercise_text = st.text_area("Enter the new exercise text")
    if st.button("Add Exercise"):
        st.write(f"New exercise added: {new_exercise_text}")

elif app_mode == "Student":
    st.header("Student Mode")
    
    # Translate text interactively
    st.subheader("Translate Text")
    text_to_translate = st.text_area("Enter the text to translate")
    translation_model = pipeline("translation", model="Helsinki-NLP/opus-mt-en-de")
    translated_text = translation_model(text_to_translate)[0]["translation_text"]
    st.write(f"Translated text: {translated_text}")
    
    # Assess translation quality
    st.subheader("Assess Translation Quality")
    reference_text = st.text_area("Enter the reference translation")
    bleu_score = sentence_bleu([reference_text.split()], translated_text.split())
    comet_model = load_from_checkpoint("wmt-large-da-estimator")
    comet_score = comet_model.predict(src_text=text_to_translate, mt_text=translated_text, ref_text=reference_text)
    bert_score, _, _ = score(translated_text, reference_text, lang="en")
    st.write(f"BLEU score: {bleu_score:.2f}")
    st.write(f"COMET score: {comet_score:.2f}")
    st.write(f"BERT score: {bert_score:.2f}")
    
    # Submit translation
    st.subheader("Submit Translation")
    submitted_translation = st.text_area("Enter your translation")
    if st.button("Submit Translation"):
        st.write(f"Translation submitted: {submitted_translation}")
