import streamlit as st
import pandas as pd
import sacrebleu
import bert_score
from unbabel_comet import download_model, load_from_checkpoint


# ---------------------------
# Load COMET model with caching
# ---------------------------
@st.cache_resource
def load_comet():
    model_path = download_model("Unbabel/wmt22-comet-da")
    model = load_from_checkpoint(model_path)
    return model


# ---------------------------
# Translation Evaluation
# ---------------------------
def evaluate_translation(system_output, reference, source):
    scores = {}

    # BLEU
    bleu = sacrebleu.corpus_bleu([system_output], [[reference]])
    scores["BLEU"] = bleu.score

    # BERTScore
    P, R, F1 = bert_score.score([system_output], [reference], lang="en", verbose=False)
    scores["BERTScore"] = F1.mean().item()

    # COMET
    comet_model = load_comet()
    comet_data = [{"src": source, "mt": system_output, "ref": reference}]
    comet_score = comet_model.predict(comet_data, batch_size=8, gpus=0)
    scores["COMET"] = comet_score.system_score

    return scores


# ---------------------------
# Streamlit App
# ---------------------------
def main():
    st.title("🌍 Translation Evaluation App")
    st.write("Evaluate translations using **BLEU, BERTScore, and COMET**")

    with st.form("translation_form"):
        source = st.text_area("Source Text", height=120)
        reference = st.text_area("Reference Translation", height=120)
        system_output = st.text_area("System Translation", height=120)
        submitted = st.form_submit_button("Evaluate")

    if submitted:
        if not source or not reference or not system_output:
            st.warning("⚠️ Please fill in all fields.")
        else:
            with st.spinner("Evaluating... ⏳"):
                scores = evaluate_translation(system_output, reference, source)

            st.success("✅ Evaluation complete!")
            st.write("### Scores")
            st.json(scores)

            df = pd.DataFrame([scores])
            st.dataframe(df)


if __name__ == "__main__":
    main()
