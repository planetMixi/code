import pandas as pd
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction

def compute_average_bleu_score(csv_path):
    # Load the dataset
    df = pd.read_csv(csv_path)

    # Extract relevant columns and convert to string
    references = df["original_message"].astype(str)
    hypotheses = df["generated_secom_message"].astype(str)

    # Prepare smoothing function
    smoothing = SmoothingFunction().method1

    # Compute BLEU scores
    scores = [
        sentence_bleu([ref.split()], hyp.split(), smoothing_function=smoothing)
        for ref, hyp in zip(references, hypotheses)
    ]

    # Compute and return the average BLEU score
    average_bleu = sum(scores) / len(scores)
    return average_bleu

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python compute_bleu.py <path_to_csv_file>")
        sys.exit(1)

    csv_path = sys.argv[1]
    avg_bleu = compute_average_bleu_score(csv_path)
    print(f"Average BLEU Score: {avg_bleu:.4f}")
