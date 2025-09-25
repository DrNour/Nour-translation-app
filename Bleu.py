import sacrebleu

def compute_bleu(reference: str, hypothesis: str) -> float:
    return sacrebleu.corpus_bleu([hypothesis], [[reference]]).score
