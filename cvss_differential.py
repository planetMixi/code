import pandas as pd

def compute_avg_cvss_diff(csv_path):
    df = pd.read_csv(csv_path)

    # Compute absolute difference
    df['cvss_diff'] = abs(df['original_cvss'].astype(float) - df['generated_cvss'].astype(float))
    avg_diff = df['cvss_diff'].mean()

    print(f"Average CVSS differential: {avg_diff:.2f}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python cvss_differential.py <csv_path>")
        sys.exit(1)

    compute_avg_cvss_diff(sys.argv[1])
