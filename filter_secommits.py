#!/usr/bin/env python3
import pandas as pd

# Read the JSON file
df = pd.read_json("dataset/secommits.json", orient="table")

# Iterate over the dataframe and print the files column
for index, row in df.iterrows():
    df.at[index, 'list_files'] = str(eval(row['files']).keys())
    df.at[index, 'num_files'] = len(eval(row['files']).keys())
    
# Filter to include only rows where:
# 1. num_files equals 1
# 2. dataset is 'osv'
# 3. cwe_id is not null or empty
# 4. files do not include .md, .txt, .rst, .txt, .toml, test/ or tests/
df_filtered = df[
    (df['num_files'] == 1) &  # heuristic 1
    (df['dataset'] == 'osv') &  # heuristic 2
    (df['cwe_id'].notna()) &  # heuristic 3
    (df['cwe_id'] != '{}') & # heuristic 3
    (~df['list_files'].str.contains(r'\.md|\.txt|\.rst|\.txt|\.toml|test/|tests/')) # heuristic 4
]

# Save the filtered dataframe to a JSON file in table format
foutput = "dataset/secommits_filtered.json"
df_filtered.to_json(foutput, orient="table")

print(f"Total rows processed: {len(df)}")
print(f"Rows following the heuristics: {len(df_filtered)}")
print(f"Filtered data saved to '{foutput}'")