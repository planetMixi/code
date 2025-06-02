import pandas as pd
import os

# Input files
zero_shot_path = "secom_zero_shot_100_cleaned.csv"
one_shot_path = "secom_oneshot_results.csv"
output_path = "secom_comparison_zero_vs_one_shot.csv"

# Load both datasets
zero_shot_df = pd.read_csv(zero_shot_path)
one_shot_df = pd.read_csv(one_shot_path)

# Merge on vuln_id
comparison_df = pd.merge(
    zero_shot_df,
    one_shot_df,
    on="vuln_id",
    suffixes=("_zero_shot", "_one_shot")
)

# Save to file
comparison_df.to_csv(output_path, index=False)

print(f" Comparison saved to {output_path}")
