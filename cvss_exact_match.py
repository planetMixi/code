import pandas as pd

def compute_cvss_match_percentage(csv_path):
    df = pd.read_csv(csv_path)

    if 'original_cvss' not in df.columns or 'generated_cvss' not in df.columns:
        raise ValueError("Missing 'original_cvss' or 'generated_cvss' column in CSV.")

    matches = (df['original_cvss'].astype(float) == df['generated_cvss'].astype(float))
    match_percentage = matches.sum() / len(df) * 100

    print(f"Exact CVSS Match Rate: {match_percentage:.2f}%")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python cvss_match_rate.py <csv_path>")
        sys.exit(1)

    compute_cvss_match_percentage(sys.argv[1])
