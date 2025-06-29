import pandas as pd

def compute_metadata_match_percentage(csv_path):
    df = pd.read_csv(csv_path)

    # These are the columns to consider
    match_columns = ['vuln_id_match', 'weakness_match', 'severity_match', 'cvss_match']

    # Check if all required columns exist
    for col in match_columns:
        if col not in df.columns:
            raise ValueError(f"Missing column: {col}")

    # Count total match flags and how many are True
    total_flags = len(df) * len(match_columns)
    total_matches = df[match_columns].astype(int).sum().sum()

    percentage = (total_matches / total_flags) * 100
    print(f"Metadata Match Percentage: {percentage:.2f}%")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python compute_metadata_match.py <csv_path>")
        sys.exit(1)

    csv_path = sys.argv[1]
    compute_metadata_match_percentage(csv_path)
