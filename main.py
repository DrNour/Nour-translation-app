import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, Text
from sacrebleu.metrics import BLEU

# ========================
# DATABASE SETUP
# ========================
engine = create_engine("sqlite:///translations.db")
meta = MetaData()

students = Table(
    "students", meta,
    Column("id", Integer, primary_key=True),
    Column("name", String),
    Column("role", String),  # instructor or student
)

exercises = Table(
    "exercises", meta,
    Column("id", Integer, primary_key=True),
    Column("title", String),
    Column("source_text", Text),
    Column("reference_translation", Text),
)

submissions = Table(
    "submissions", meta,
    Column("id", Integer, primary_key=True),
    Column("student_name", String),
    Column("exercise_id", Integer),
    Column("translation", Text),
    Column("bleu", String),
    Column("bertscore", String),
    Column("comet", String),
    Column("errors", Text),
)

meta.create_all(engine)


# ========================
# LAZY LOAD MODELS
# ========================
@st.cache_resource
def load_bertscore():
    from bert_score import score
    return score

@st.cache_resource
def load_comet():
    from comet import download_model, load_from_checkpoint
    model_path = download_model("Unbabel/wmt22-comet-da")
    return load_from_checkpoint(model_path)


# ========================
# HELPER FUNCTIONS
# ========================
def evaluate_translation(src, hyp, ref):
    """Compute BLEU, BERTScore, COMET, simple error categorization."""
    # BLEU
    bleu = BLEU()
    bleu_score = bleu.corpus_score([hyp], [[ref]]).score

    # BERTScore
    bert_scorer = load_bertscore()
    P, R, F1 = bert_scorer([hyp], [ref], lang="en")
    bert_score = F1.mean().item()

    # COMET
    comet_model = load_comet()
    data = [{"src": src, "mt": hyp, "ref": ref}]
    comet_score = comet_model.predict(data, batch_size=8, gpus=0)["score"]

    # Error categorization (toy demo)
    errors = []
    if len(hyp.split()) < 0.7 * len(ref.split()):
        errors.append("Omission")
    if any(w not in ref for w in hyp.split()):
        errors.append("Lexical choice issue")
    if hyp[0].islower():
        errors.append("Grammar: capitalization")

    return bleu_score, bert_score, comet_score, "; ".join(errors)


def add_exercise(title, src, ref):
    ins = exercises.insert().values(title=title, source_text=src, reference_translation=ref)
    with engine.begin() as conn:
        conn.execute(ins)


def add_submission(student_name, ex_id, translation, scores):
    bleu, bert, comet, errors = scores
    ins = submissions.insert().values(
        student_name=student_name,
        exercise_id=ex_id,
        translation=translation,
        bleu=f"{bleu:.2f}",
        bertscore=f"{bert:.2f}",
        comet=f"{comet:.2f}",
        errors=errors
    )
    with engine.begin() as conn:
        conn.execute(ins)


# ========================
# UI
# ========================
st.title("🌍 Interactive Translation Training Platform")

role = st.sidebar.radio("Select Role", ["Instructor", "Student"])

if role == "Instructor":
    st.header("📚 Instructor Dashboard")
    action = st.radio("Choose action", ["Add Exercise", "View Submissions"])

    if action == "Add Exercise":
        with st.form("add_exercise"):
            title = st.text_input("Exercise Title")
            src = st.text_area("Source Text")
            ref = st.text_area("Reference Translation")
            submitted = st.form_submit_button("Save Exercise")
            if submitted:
                add_exercise(title, src, ref)
                st.success("✅ Exercise added!")

    elif action == "View Submissions":
        df = pd.read_sql(submissions.select(), engine)
        if df.empty:
            st.info("No submissions yet.")
        else:
            st.dataframe(df)
            st.download_button("Download Submissions (CSV)", df.to_csv(index=False), "submissions.csv")


elif role == "Student":
    st.header("🧑‍🎓 Student Workspace")
    student_name = st.text_input("Enter your name")

    # List available exercises
    ex_df = pd.read_sql(exercises.select(), engine)
    if ex_df.empty:
        st.warning("No exercises available yet. Wait for instructor to add.")
    else:
        ex_id = st.selectbox("Choose Exercise", ex_df["id"])
        row = ex_df[ex_df["id"] == ex_id].iloc[0]
        st.subheader("Source Text")
        st.write(row["source_text"])

        translation = st.text_area("Enter your translation")

        if st.button("Submit Translation"):
            scores = evaluate_translation(
                row["source_text"], translation, row["reference_translation"]
            )
            add_submission(student_name, int(ex_id), translation, scores)
            st.success("✅ Submission saved!")
            st.write(f"**BLEU:** {scores[0]:.2f}")
            st.write(f"**BERTScore:** {scores[1]:.2f}")
            st.write(f"**COMET:** {scores[2]:.2f}")
            st.write(f"**Errors:** {scores[3]}")
