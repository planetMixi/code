import sys
import pandas as pd
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from nltk.translate.meteor_score import meteor_score
from nltk.tokenize import word_tokenize

def compute_average_bleu_score(csv_path):
    df = pd.read_csv(csv_path)
    references = df["original_message"].astype(str)
    hypotheses = df["generated_secom_message"].astype(str)
    smoothing = SmoothingFunction().method1
    scores = [
        sentence_bleu([ref.split()], hyp.split(), smoothing_function=smoothing)
        for ref, hyp in zip(references, hypotheses)
    ]
    average_bleu = sum(scores) / len(scores)
    return average_bleu

def compute_average_meteor_score(csv_path):
    df = pd.read_csv(csv_path)
    references = df["original_message"].astype(str)
    hypotheses = df["generated_secom_message"].astype(str)
    scores = [
        meteor_score([word_tokenize(ref)], word_tokenize(hyp))
        for ref, hyp in zip(references, hypotheses)
    ]
    average_meteor = sum(scores) / len(scores)
    return average_meteor

def compute_average_compliance(csv_path):
    df = pd.read_csv(csv_path)
    col1 = 'original_message_score'
    col2 = 'generated_secom_message_score'
    if col1 not in df.columns or col2 not in df.columns:
        raise ValueError(f"Missing columns: '{col1}', '{col2}'")
    avg1 = df[col1].astype(float).mean()
    avg2 = df[col2].astype(float).mean()
    return avg1, avg2

def compute_metadata_match_percentage(csv_path):
    df = pd.read_csv(csv_path)
    match_columns = [
        'cwe_id_match', 'cvss_base_score_match', 'cvss_severity_match',
        'score_source_match', 'attack_vector_match', 'attack_complexity_match',
        'privileges_required_match', 'user_interaction_match', 'scope_match',
        'confidentiality_match', 'integrity_match', 'availability_match'
    ]
    match_percentage = df[match_columns].astype(float).mean().mean() * 100
    return match_percentage

def compute_cvss_differentials(csv_path):
    df = pd.read_csv(csv_path)
    original = df["original_cvss_score"].astype(float)
    generated = df["generated_cvss_score"].astype(float)
    diffs = abs(original - generated)
    avg_diff = diffs.mean()
    return avg_diff

def compute_cvss_exact_match(csv_path):
    df = pd.read_csv(csv_path)
    matches = (df["original_cvss_score"] == df["generated_cvss_score"])
    match_percentage = (matches.sum() / len(matches)) * 100
    return match_percentage

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python all_metrics.py <path_to_csv_file>")
        sys.exit(1)

    csv_path = sys.argv[1]

    print(f"Processing file: {csv_path}\n")

    bleu = compute_average_bleu_score(csv_path)
    print(f"1. Average BLEU Score: {bleu:.4f}")

    meteor = compute_average_meteor_score(csv_path)
    print(f"2. Average METEOR Score: {meteor:.4f}")

    orig_score, gen_score = compute_average_compliance(csv_path)
    print(f"3. Avg Original Message Score: {orig_score:.4f}")
    print(f"   Avg Generated Message Score: {gen_score:.4f}")

    metadata_match = compute_metadata_match_percentage(csv_path)
    print(f"4. Metadata Match %: {metadata_match:.2f}%")

    cvss_diff = compute_cvss_differentials(csv_path)
    print(f"5. Avg CVSS Score Difference: {cvss_diff:.4f}")

    cvss_match = compute_cvss_exact_match(csv_path)
    print(f"6. CVSS Exact Match %: {cvss_match:.2f}%")
