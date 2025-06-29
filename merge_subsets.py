import pandas as pd
import os

# List of subset filenames
subset_files = [
    "secom_zero_shot_cwe79.csv",
    "secom_zero_shot_cwe400.csv",
    "secom_zero_shot_cwe787.csv",
    "secom_zero_shot_cwe20.csv",
    "secom_zero_shot_cwe125.csv",
]

# Read and concatenate all dataframes
combined_df = pd.concat([pd.read_csv(f) for f in subset_files], ignore_index=True)

# Save to a single output CSV
combined_df.to_csv("secom_zero_shot_results.csv", index=False)

print("Merged CSV saved as 'secom_zero_shot_results.csv'")
