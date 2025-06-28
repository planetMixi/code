import pandas as pd
import os

# List of subset filenames
subset_files = [
    "secom_zero_shot_subset1_results.csv",
    "secom_zero_shot_subset2_results.csv",
    "secom_zero_shot_subset3_results.csv",
    "secom_zero_shot_subset4_results.csv",
    "secom_zero_shot_subset5_results.csv",
]

# Read and concatenate all dataframes
combined_df = pd.concat([pd.read_csv(f) for f in subset_files], ignore_index=True)

# Save to a single output CSV
combined_df.to_csv("secom_zero_shot_results.csv", index=False)

print("Merged CSV saved as 'secom_zero_shot_results.csv'")
