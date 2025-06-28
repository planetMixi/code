import pandas as pd
import os

# List of subset filenames
subset_files = [
    "secom_zero_shot_rq2_subset1.csv",
    "secom_zero_shot_rq2_subset2.csv",
    "secom_zero_shot_rq2_subset3.csv",
    "secom_zero_shot_rq2_subset4.csv",
    "secom_zero_shot_rq2_subset5.csv",
]

# Read and concatenate all dataframes
combined_df = pd.concat([pd.read_csv(f) for f in subset_files], ignore_index=True)

# Save to a single output CSV
combined_df.to_csv("secom_zero_shot_rq2_results.csv", index=False)

print("Merged CSV saved as 'secom_zero_shot_rq2_results.csv'")
