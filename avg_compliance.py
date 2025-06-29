import pandas as pd

def compute_average_compliance(csv_path):
    df = pd.read_csv(csv_path)

    col1 = 'original_message_score'
    col2 = 'generated_secom_message_score'

    if col1 not in df.columns or col2 not in df.columns:
        raise ValueError(f"One or both columns not found: '{col1}', '{col2}'")

    avg1 = df[col1].astype(float).mean()
    avg2 = df[col2].astype(float).mean()

    print(f"Average Original Message Score ({col1}): {avg1:.4f}")
    print(f"Average Generated Message Score ({col2}): {avg2:.4f}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python compute_compliance_fixed_cols.py <csv_path>")
        sys.exit(1)

    csv_path = sys.argv[1]
    compute_average_compliance(csv_path)
