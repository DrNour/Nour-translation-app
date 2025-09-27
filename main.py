import streamlit as st
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import sacrebleu
from bert_score import score as bert_score

# -----------------------------
# Translation Evaluation Function
# -----------------------------
def evaluate_translation(reference_texts, translated_texts):
    """
    Evaluate translations using BLEU, TER, and BERTScore
    """
    # BLEU
    bleu = sacrebleu.corpus_bleu(translated_texts, [reference_texts])
    
    # TER
    ter = sacrebleu.corpus_ter(translated_texts, [reference_texts])
    
    # BERTScore
    P, R, F1 = bert_score(translated_texts, reference_texts, lang='en', rescale_with_baseline=True)
    
    results = {
        "BLEU": bleu.score,
        "TER": ter.score,
        "BERTScore F1": float(F1.mean())
    }
    return results

# -----------------------------
# Streamlit App
# -----------------------------
st.title("Translation Evaluation App")

st.markdown("""
This app evaluates machine-translated text using BLEU, TER, and BERTScore.
""")

reference_text = st.text_area("Enter Reference Text", "")
translated_text = st.text_area("Enter Translated Text", "")

if st.button("Evaluate"):
    if not reference_text.strip() or not translated_text.strip():
        st.error("Please enter both reference and translated text.")
    else:
        scores = evaluate_translation([reference_text], [translated_text])
        st.subheader("Evaluation Scores")
        st.write(f"BLEU Score: {scores['BLEU']:.2f}")
        st.write(f"TER Score: {scores['TER']:.2f}")
        st.write(f"BERTScore F1: {scores['BERTScore F1']:.4f}")
