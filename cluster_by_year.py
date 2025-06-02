import json
import pandas as pd
import os

# Load input
input_file = "cleaned_diffs.jsonl"
output_dir = "clustered_by_year"
os.makedirs(output_dir, exist_ok=True)

records = []
with open(input_file, "r", encoding="utf-8") as f:
    for line in f:
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue

# Create DataFrame
df = pd.DataFrame(records)

# Extract year from vuln_id
def extract_year(vuln_id):
    if isinstance(vuln_id, str):
        parts = vuln_id.split("-")
        for part in parts:
            if part.isdigit() and len(part) == 4 and 2000 <= int(part) <= 2025:
                return part
    return "UNKNOWN"


df["vuln_year"] = df["vuln_id"].apply(extract_year)

# Group and save per year
for year, group in df.groupby("vuln_year"):
    filename = f"{output_dir}/commits_{year}.csv"
    group.drop(columns=["vuln_year"]).to_csv(filename, index=False)
    print(f"✅ Saved {len(group)} rows to {filename}")
