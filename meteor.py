import pandas as pd
from nltk.translate.meteor_score import meteor_score
from nltk.tokenize import word_tokenize

def compute_average_meteor_score(csv_path):
    # Load the dataset
    df = pd.read_csv(csv_path)

    # Convert strings to tokenized lists
    references = df["original_message"].astype(str)
    hypotheses = df["generated_secom_message"].astype(str)

    scores = [
        meteor_score([word_tokenize(ref)], word_tokenize(hyp))
        for ref, hyp in zip(references, hypotheses)
    ]

    average_meteor = sum(scores) / len(scores)
    return average_meteor

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python meteor.py <path_to_csv_file>")
        sys.exit(1)

    csv_path = sys.argv[1]
    avg_meteor = compute_average_meteor_score(csv_path)

    print(f"Average METEOR Score: {avg_meteor:.4f}")
