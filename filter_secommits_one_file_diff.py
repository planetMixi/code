#!/usr/bin/env python3
import pandas as pd

# Read the JSON file
df = pd.read_json("dataset/secommits.json", orient="table")

# Iterate over the dataframe and print the files column
for index, row in df.iterrows():
    df.at[index, 'list_files'] = str(eval(row['files']).keys())
    df.at[index, 'num_files'] = len(eval(row['files']).keys())
    
# Filter to include only rows where num_files equals 1
df_filtered = df[df['num_files'] == 1]

# Save the filtered dataframe to a JSON file in table format
foutput = "dataset/secommits_single_file.json"
df_filtered.to_json(foutput, orient="table")

print(f"Total rows processed: {len(df)}")
print(f"Rows with exactly 1 file: {len(df_filtered)}")
print(f"Filtered data saved to '{foutput}'")